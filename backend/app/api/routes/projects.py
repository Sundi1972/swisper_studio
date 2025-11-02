"""
Project CRUD API endpoints

Following Langfuse patterns:
- Pagination starts at 1
- Soft deletes (deleted_at field)
- Strict validation
- Security (hash API keys)
"""

import math
import bcrypt
from datetime import datetime
from typing import Any
from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field, HttpUrl, field_validator
from sqlalchemy import select, func

from app.api.deps import APIKey, DBSession
from app.models import Project


router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ProjectCreate(BaseModel):
    """Request model for creating a project"""
    
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    swisper_url: HttpUrl = Field(..., description="Swisper instance URL")
    swisper_api_key: str = Field(..., min_length=10, description="Swisper API key")
    description: str | None = Field(None, max_length=1000, description="Project description")
    meta: dict[str, Any] | None = Field(None, description="Additional metadata")
    
    model_config = {"extra": "forbid"}  # Strict validation - reject unknown fields
    
    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Validate name is not whitespace only"""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty or whitespace only")
        return v.strip()


class ProjectUpdate(BaseModel):
    """Request model for updating a project"""
    
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    meta: dict[str, Any] | None = None
    
    model_config = {"extra": "forbid"}  # Strict validation
    
    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str | None) -> str | None:
        """Validate name is not whitespace only if provided"""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Name cannot be empty or whitespace only")
        return v.strip() if v else None


class ProjectResponse(BaseModel):
    """Response model for project (excludes sensitive data)"""
    
    id: str
    name: str
    swisper_url: str
    description: str | None
    meta: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    
    model_config = {"from_attributes": True}


class PaginationParams(BaseModel):
    """Pagination parameters (Langfuse pattern: page starts at 1)"""
    
    page: int = Field(default=1, ge=1, description="Page number (starts at 1)")
    limit: int = Field(default=50, ge=1, le=1000, description="Items per page (max 1000)")


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    
    page: int
    limit: int
    total_items: int
    total_pages: int


class ProjectListResponse(BaseModel):
    """Response model for project list with pagination"""
    
    data: list[ProjectResponse]
    meta: PaginationMeta


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    session: DBSession,
    api_key: APIKey,
) -> Project:
    """
    Create a new project.
    
    Projects represent connections to Swisper deployments.
    API keys are hashed before storage (security best practice).
    """
    # Hash API key before storage (Langfuse pattern: never store plaintext)
    hashed_key = bcrypt.hashpw(
        data.swisper_api_key.encode("utf-8"),
        bcrypt.gensalt()
    )
    
    # Create project
    project = Project(
        name=data.name,
        swisper_url=str(data.swisper_url).rstrip("/"),  # Remove trailing slash
        swisper_api_key=hashed_key.decode("utf-8"),
        description=data.description,
        meta=data.meta,
    )
    
    session.add(project)
    await session.commit()
    await session.refresh(project)
    
    return project


@router.get("/projects", response_model=ProjectListResponse)
async def list_projects(
    session: DBSession,
    api_key: APIKey,
    page: int = Query(default=1, ge=1, description="Page number (starts at 1)"),
    limit: int = Query(default=50, ge=1, le=1000, description="Items per page"),
) -> dict[str, Any]:
    """
    List all active projects with pagination.
    
    Following Langfuse pagination pattern:
    - Page starts at 1 (not 0)
    - Returns data + meta
    - Filters out soft-deleted projects
    """
    # Filter out soft-deleted (Langfuse pattern)
    base_stmt = select(Project).where(Project.deleted_at.is_(None))
    
    # Count total
    count_stmt = select(func.count()).select_from(Project).where(
        Project.deleted_at.is_(None)
    )
    total = await session.scalar(count_stmt) or 0
    
    # Paginate
    offset = (page - 1) * limit
    stmt = base_stmt.offset(offset).limit(limit).order_by(Project.created_at.desc())
    
    result = await session.execute(stmt)
    projects = result.scalars().all()
    
    # Calculate total pages
    total_pages = math.ceil(total / limit) if total > 0 else 0
    
    return {
        "data": projects,
        "meta": {
            "page": page,
            "limit": limit,
            "total_items": total,
            "total_pages": total_pages,
        }
    }


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    session: DBSession,
    api_key: APIKey,
) -> Project:
    """Get a project by ID (excludes soft-deleted)"""
    stmt = select(Project).where(
        Project.id == project_id,
        Project.deleted_at.is_(None)  # Don't return deleted projects
    )
    result = await session.execute(stmt)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
    
    return project


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    data: ProjectUpdate,
    session: DBSession,
    api_key: APIKey,
) -> Project:
    """
    Update a project.
    
    Only updates fields that are provided (partial updates supported).
    """
    stmt = select(Project).where(
        Project.id == project_id,
        Project.deleted_at.is_(None)
    )
    result = await session.execute(stmt)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
    
    # Update only provided fields (exclude_unset=True)
    update_dict = data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(project, field, value)
    
    # Update timestamp
    project.updated_at = datetime.utcnow()
    
    await session.commit()
    await session.refresh(project)
    
    return project


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    session: DBSession,
    api_key: APIKey,
) -> None:
    """
    Soft delete a project (Langfuse pattern).
    
    Sets deleted_at timestamp instead of actually deleting the record.
    Allows data recovery and maintains audit trail.
    """
    stmt = select(Project).where(
        Project.id == project_id,
        Project.deleted_at.is_(None)
    )
    result = await session.execute(stmt)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
    
    # Soft delete (Langfuse pattern)
    project.deleted_at = datetime.utcnow()
    
    await session.commit()

