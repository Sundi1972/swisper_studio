"""Config Version API endpoints"""
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, and_, desc
import httpx

from app.api.deps import APIKey, DBSession
from app.models.config_version import ConfigVersion, ConfigDeployment
from app.models.project_environment import ProjectEnvironment

router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ConfigVersionCreate(BaseModel):
    """Request to create a config version"""
    table_name: str
    record_id: str
    config_data: Dict[str, Any]
    description: str | None = None
    created_by: str


class ConfigVersionResponse(BaseModel):
    """Response model for config version"""
    id: str
    project_id: str
    table_name: str
    record_id: str
    version_number: int
    config_data: Dict[str, Any]
    description: str | None
    created_by: str
    created_at: datetime
    parent_version_id: str | None
    
    model_config = {"from_attributes": True}


class DeployRequest(BaseModel):
    """Request to deploy a version to an environment"""
    version_id: str
    deployed_by: str


class DeploymentResponse(BaseModel):
    """Response model for deployment"""
    id: str
    version_id: str
    environment_id: str
    status: str
    deployed_by: str
    deployed_at: datetime
    error_message: str | None
    
    model_config = {"from_attributes": True}


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/projects/{project_id}/config/versions")
async def list_versions(
    project_id: str,
    session: DBSession,
    api_key: APIKey,
    table_name: str | None = Query(None, description="Filter by table name"),
    record_id: str | None = Query(None, description="Filter by record ID")
) -> list[ConfigVersionResponse]:
    """
    List config versions with optional filtering.
    
    Can filter by table_name and/or record_id.
    Returns versions in descending order (newest first).
    """
    statement = select(ConfigVersion).where(
        ConfigVersion.project_id == project_id
    )
    
    if table_name:
        statement = statement.where(ConfigVersion.table_name == table_name)
    if record_id:
        statement = statement.where(ConfigVersion.record_id == record_id)
    
    statement = statement.order_by(desc(ConfigVersion.created_at))
    
    result = await session.execute(statement)
    versions = result.scalars().all()
    
    return [ConfigVersionResponse.model_validate(v) for v in versions]


@router.post("/projects/{project_id}/config/versions", status_code=201)
async def create_version(
    project_id: str,
    data: ConfigVersionCreate,
    session: DBSession,
    api_key: APIKey
) -> ConfigVersionResponse:
    """
    Save a new config version.
    
    Auto-increments version_number based on latest version for this record.
    Tracks parent_version_id for lineage.
    """
    # Get latest version for this record
    latest_stmt = select(ConfigVersion).where(
        and_(
            ConfigVersion.project_id == project_id,
            ConfigVersion.table_name == data.table_name,
            ConfigVersion.record_id == data.record_id
        )
    ).order_by(desc(ConfigVersion.version_number))
    
    result = await session.execute(latest_stmt)
    latest = result.scalars().first()
    
    # Calculate next version number
    next_version = (latest.version_number + 1) if latest else 1
    
    # Create version
    version = ConfigVersion(
        project_id=project_id,
        table_name=data.table_name,
        record_id=data.record_id,
        version_number=next_version,
        config_data=data.config_data,
        description=data.description,
        created_by=data.created_by,
        parent_version_id=latest.id if latest else None
    )
    
    session.add(version)
    await session.commit()
    await session.refresh(version)
    
    return ConfigVersionResponse.model_validate(version)


@router.get("/projects/{project_id}/config/versions/{version_id}")
async def get_version(
    project_id: str,
    version_id: str,
    session: DBSession,
    api_key: APIKey
) -> ConfigVersionResponse:
    """Get a single config version by ID"""
    version = await session.get(ConfigVersion, version_id)
    if not version or version.project_id != project_id:
        raise HTTPException(status_code=404, detail="Version not found")
    
    return ConfigVersionResponse.model_validate(version)


@router.post("/projects/{project_id}/environments/{environment_id}/deploy")
async def deploy_version(
    project_id: str,
    environment_id: str,
    data: DeployRequest,
    session: DBSession,
    api_key: APIKey
):
    """
    Deploy a config version to an environment.
    
    Calls Swisper SAP endpoint to update config in target environment.
    Logs deployment success/failure in ConfigDeployment table.
    """
    # Get environment
    environment = await session.get(ProjectEnvironment, environment_id)
    if not environment or environment.project_id != project_id:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    # Get version
    version = await session.get(ConfigVersion, data.version_id)
    if not version or version.project_id != project_id:
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Call Swisper SAP endpoint to update config
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.put(
                f"{environment.swisper_url}/api/admin/config/{version.table_name}/{version.record_id}",
                json=version.config_data,
                headers={"Authorization": f"Bearer {environment.api_key}"}
            )
            
            if response.status_code != 200:
                # Log failure
                deployment = ConfigDeployment(
                    version_id=version.id,
                    environment_id=environment.id,
                    status='failed',
                    deployed_by=data.deployed_by,
                    error_message=response.text
                )
                session.add(deployment)
                await session.commit()
                raise HTTPException(
                    status_code=500,
                    detail=f"Deployment failed: {response.text}"
                )
    except httpx.RequestError as e:
        # Network error
        deployment = ConfigDeployment(
            version_id=version.id,
            environment_id=environment.id,
            status='failed',
            deployed_by=data.deployed_by,
            error_message=str(e)
        )
        session.add(deployment)
        await session.commit()
        raise HTTPException(
            status_code=500,
            detail=f"Deployment failed: {str(e)}"
        )
    
    # Log successful deployment
    deployment = ConfigDeployment(
        version_id=version.id,
        environment_id=environment.id,
        status='deployed',
        deployed_by=data.deployed_by
    )
    session.add(deployment)
    await session.commit()
    await session.refresh(deployment)
    
    # Standardized response format
    return {
        "success": True,
        "version": ConfigVersionResponse.model_validate(version).model_dump(),
        "deployment": DeploymentResponse.model_validate(deployment).model_dump()
    }


@router.get("/projects/{project_id}/environments/{environment_id}/current-config")
async def get_current_config(
    project_id: str,
    environment_id: str,
    session: DBSession,
    api_key: APIKey,
    table_name: str = Query(..., description="Config table name"),
    record_id: str = Query(..., description="Config record ID")
):
    """
    Get currently deployed version for an environment.
    
    Returns the latest successfully deployed version for a specific config record.
    """
    # Find latest successful deployment
    statement = (
        select(ConfigDeployment, ConfigVersion)
        .join(ConfigVersion, ConfigDeployment.version_id == ConfigVersion.id)
        .where(
            and_(
                ConfigDeployment.environment_id == environment_id,
                ConfigDeployment.status == 'deployed',
                ConfigVersion.table_name == table_name,
                ConfigVersion.record_id == record_id
            )
        )
        .order_by(desc(ConfigDeployment.deployed_at))
    )
    
    result = await session.execute(statement)
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=404,
            detail="No deployed version found for this config"
        )
    
    deployment, version = row
    
    # Standardized response format
    return {
        "version": ConfigVersionResponse.model_validate(version).model_dump(),
        "deployment": DeploymentResponse.model_validate(deployment).model_dump()
    }

