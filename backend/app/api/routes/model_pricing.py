"""Model pricing API endpoints"""

from decimal import Decimal
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select

from app.api.deps import APIKey, DBSession
from app.models import ModelPricing


router = APIRouter()


class ModelPricingResponse(BaseModel):
    """Response model for model pricing"""
    
    id: str
    project_id: str | None
    hosting_provider: str
    model_name: str
    input_price_per_million: Decimal
    output_price_per_million: Decimal
    
    model_config = {"from_attributes": True}


@router.get("/projects/{project_id}/model-pricing", response_model=list[ModelPricingResponse])
async def get_project_model_pricing(
    project_id: str,
    session: DBSession,
    api_key: APIKey,
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
    api_key: APIKey,
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

