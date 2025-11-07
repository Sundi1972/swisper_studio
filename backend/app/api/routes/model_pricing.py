"""Model pricing API endpoints"""

from decimal import Decimal
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import APIKey, DBSession, Auth
from app.models import ModelPricing


router = APIRouter()


class ModelPricingResponse(BaseModel):
    """Response model for model pricing"""
    
    id: str
    project_id: str | None
    hosting_provider: str
    model_name: str
    type: str
    description: str | None
    input_price_per_million: Decimal
    output_price_per_million: Decimal
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class ModelPricingCreate(BaseModel):
    """Request model for creating model pricing"""
    
    hosting_provider: str
    model_name: str
    type: str
    description: str | None = None
    input_price_per_million: Decimal
    output_price_per_million: Decimal


class ModelPricingUpdate(BaseModel):
    """Request model for updating model pricing"""
    
    hosting_provider: str | None = None
    model_name: str | None = None
    type: str | None = None
    description: str | None = None
    input_price_per_million: Decimal | None = None
    output_price_per_million: Decimal | None = None


@router.get("/projects/{project_id}/model-pricing", response_model=list[ModelPricingResponse])
async def get_project_model_pricing(
    project_id: str,
    session: DBSession,
    auth: Auth,  # Accept JWT or API key
) -> list[ModelPricing]:
    """
    Get all model pricing for a project.
    
    Returns both project-specific pricing and default pricing (project_id=NULL).
    Used by frontend configuration page to display current pricing.
    
    Phase 4 will add CRUD operations for managing pricing.
    For MVP (Phase 2), this is read-only.
    """
    # Get project-specific pricing
    project_stmt = select(ModelPricing).where(
        ModelPricing.project_id == project_id
    ).order_by(ModelPricing.hosting_provider, ModelPricing.model_name)
    
    project_result = await session.execute(project_stmt)
    project_pricing = project_result.scalars().all()
    
    # Get default pricing (shown as reference)
    default_stmt = select(ModelPricing).where(
        ModelPricing.project_id.is_(None)
    ).order_by(ModelPricing.hosting_provider, ModelPricing.model_name)
    
    default_result = await session.execute(default_stmt)
    default_pricing = default_result.scalars().all()
    
    # Combine: project-specific first, then defaults
    all_pricing = list(project_pricing) + list(default_pricing)
    
    return all_pricing


@router.get("/model-pricing/defaults", response_model=list[ModelPricingResponse])
async def get_default_model_pricing(
    session: DBSession,
    auth: Auth,  # Accept JWT or API key
) -> list[ModelPricing]:
    """
    Get default model pricing (applies to all projects without custom pricing).
    
    Returns pricing seeded during migration.
    Useful for showing available models and their costs.
    """
    stmt = select(ModelPricing).where(
        ModelPricing.project_id.is_(None)
    ).order_by(ModelPricing.hosting_provider, ModelPricing.model_name)
    
    result = await session.execute(stmt)
    pricing = result.scalars().all()
    
    return pricing


@router.get("/model-pricing", response_model=list[ModelPricingResponse])
async def list_all_model_pricing(
    session: DBSession,
    auth: Auth,
) -> list[ModelPricing]:
    """
    Get all model pricing entries (global only).
    
    Admin endpoint for cost management page.
    Returns all global pricing (project_id = NULL).
    """
    stmt = select(ModelPricing).where(
        ModelPricing.project_id.is_(None)
    ).order_by(ModelPricing.hosting_provider, ModelPricing.model_name)
    
    result = await session.execute(stmt)
    pricing = result.scalars().all()
    
    return pricing


@router.post("/model-pricing", response_model=ModelPricingResponse, status_code=status.HTTP_201_CREATED)
async def create_model_pricing(
    pricing_data: ModelPricingCreate,
    session: DBSession,
    auth: Auth,
) -> ModelPricing:
    """
    Create new global model pricing entry.
    
    Admin only. Creates pricing that applies to all projects.
    Validates uniqueness: (provider, model) combination must be unique.
    """
    # Create new pricing entry (global: project_id = None)
    new_pricing = ModelPricing(
        project_id=None,  # Global pricing
        hosting_provider=pricing_data.hosting_provider,
        model_name=pricing_data.model_name,
        type=pricing_data.type,
        description=pricing_data.description,
        input_price_per_million=pricing_data.input_price_per_million,
        output_price_per_million=pricing_data.output_price_per_million,
    )
    
    try:
        session.add(new_pricing)
        await session.commit()
        await session.refresh(new_pricing)
        return new_pricing
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Pricing for {pricing_data.hosting_provider}/{pricing_data.model_name} already exists"
        )


@router.put("/model-pricing/{pricing_id}", response_model=ModelPricingResponse)
async def update_model_pricing(
    pricing_id: str,
    pricing_data: ModelPricingUpdate,
    session: DBSession,
    auth: Auth,
) -> ModelPricing:
    """
    Update existing model pricing entry.
    
    Admin only. Updates pricing details.
    """
    # Get existing pricing
    stmt = select(ModelPricing).where(ModelPricing.id == pricing_id)
    result = await session.execute(stmt)
    pricing = result.scalar_one_or_none()
    
    if not pricing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model pricing {pricing_id} not found"
        )
    
    # Update fields
    if pricing_data.hosting_provider is not None:
        pricing.hosting_provider = pricing_data.hosting_provider
    if pricing_data.model_name is not None:
        pricing.model_name = pricing_data.model_name
    if pricing_data.type is not None:
        pricing.type = pricing_data.type
    if pricing_data.description is not None:
        pricing.description = pricing_data.description
    if pricing_data.input_price_per_million is not None:
        pricing.input_price_per_million = pricing_data.input_price_per_million
    if pricing_data.output_price_per_million is not None:
        pricing.output_price_per_million = pricing_data.output_price_per_million
    
    pricing.updated_at = datetime.utcnow()
    
    try:
        await session.commit()
        await session.refresh(pricing)
        return pricing
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Pricing for {pricing_data.hosting_provider}/{pricing_data.model_name} already exists"
        )


@router.delete("/model-pricing/{pricing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model_pricing(
    pricing_id: str,
    session: DBSession,
    auth: Auth,
) -> None:
    """
    Delete model pricing entry.
    
    Admin only. Permanently removes pricing.
    """
    # Get existing pricing
    stmt = select(ModelPricing).where(ModelPricing.id == pricing_id)
    result = await session.execute(stmt)
    pricing = result.scalar_one_or_none()
    
    if not pricing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model pricing {pricing_id} not found"
        )
    
    await session.delete(pricing)
    await session.commit()

