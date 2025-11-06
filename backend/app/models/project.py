"""
Project model - Represents a customer project with multiple environments

Based on Langfuse Project model (simplified for MVP).
Reference: langfuse/packages/shared/prisma/schema.prisma:130-186

NOTE: swisper_url and api_key moved to ProjectEnvironment model
Each project now has 3 environments: dev, staging, production
"""

import uuid
from datetime import datetime
from typing import Any
from sqlalchemy import Column, JSON, Index
from sqlmodel import Field, SQLModel


class Project(SQLModel, table=True):
    """
    Represents a customer project with multiple environments.
    
    Each project has 3 environments (dev, staging, production).
    Connection details (swisper_url, api_key) are stored in ProjectEnvironment.
    
    Based on Langfuse Project model with simplifications:
    - No Organization (not multi-tenant for MVP)
    - Kept soft delete pattern (deleted_at)
    - Kept metadata JSON field for extensibility
    """
    
    __tablename__ = "projects"
    
    # Primary key (UUID instead of Langfuse's cuid for Python simplicity)
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique project identifier (UUID)"
    )
    
    # Core fields
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Human-readable project name (e.g., 'Customer A')"
    )
    
    # Optional fields
    description: str | None = Field(
        None,
        max_length=1000,
        description="Optional project description"
    )
    
    github_repo_url: str | None = Field(
        None,
        max_length=500,
        description="GitHub repository URL for config deployment (e.g., https://github.com/org/swisper)"
    )
    
    github_token: str | None = Field(
        None,
        max_length=500,
        description="GitHub Personal Access Token for pushing commits (scope: repo) - SENSITIVE!"
    )
    
    meta: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="Additional metadata (JSON)"
    )
    
    # Timestamps (Langfuse pattern)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the project was created"
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the project was last updated"
    )
    
    # Soft delete (Langfuse pattern)
    deleted_at: datetime | None = Field(
        None,
        description="When the project was soft-deleted (null if active)"
    )
    
    # Tracing control (Q2 feature)
    tracing_enabled: bool = Field(
        default=True,
        description="Whether tracing is enabled for this project (default: true)"
    )
    
    __table_args__ = (
        Index("ix_projects_created_at", "created_at"),
        Index("ix_projects_deleted_at", "deleted_at"),
        Index("ix_projects_tracing_enabled", "tracing_enabled"),
    )

