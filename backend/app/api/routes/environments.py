"""Environment API endpoints"""
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy import select

from app.api.deps import APIKey, DBSession, Auth
from app.models.project_environment import ProjectEnvironment

router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class EnvironmentCreate(BaseModel):
    """Request to create/update an environment"""
    swisper_url: HttpUrl
    swisper_api_key: str


class EnvironmentResponse(BaseModel):
    """Response model for environment (excludes API key)"""
    id: str
    project_id: str
    env_type: str
    swisper_url: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/projects/{project_id}/environments")
async def list_environments(
    project_id: str,
    session: DBSession,
    auth: Auth  # Accept JWT or API key
) -> list[EnvironmentResponse]:
    """
    List all environments for a project.
    
    Returns dev, staging, and production environments in order.
    API keys are excluded from response (security).
    """
    statement = select(ProjectEnvironment).where(
        ProjectEnvironment.project_id == project_id
    ).order_by(
        # Order: dev, staging, production (alphabetical)
        ProjectEnvironment.env_type
    )
    
    result = await session.execute(statement)
    environments = result.scalars().all()
    
    return [EnvironmentResponse.model_validate(env) for env in environments]


@router.put("/environments/{environment_id}")
async def update_environment(
    environment_id: str,
    data: EnvironmentCreate,
    session: DBSession,
    auth: Auth  # Accept JWT or API key
) -> EnvironmentResponse:
    """
    Update environment connection details.
    
    Can update swisper_url and api_key for an environment.
    Useful when Swisper instance moves or credentials change.
    """
    environment = await session.get(ProjectEnvironment, environment_id)
    if not environment:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    # Update fields
    environment.swisper_url = str(data.swisper_url).rstrip("/")
    environment.api_key = data.swisper_api_key  # TODO: Hash in later phase
    environment.updated_at = datetime.utcnow()
    
    session.add(environment)
    await session.commit()
    await session.refresh(environment)
    
    return EnvironmentResponse.model_validate(environment)

