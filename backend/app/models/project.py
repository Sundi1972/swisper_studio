"""
Project model - Represents a connection to a Swisper deployment

Based on Langfuse Project model (simplified for MVP).
Reference: langfuse/packages/shared/prisma/schema.prisma:130-186
"""

import uuid
from datetime import datetime
from typing import Any
from sqlalchemy import Column, JSON, Index
from sqlmodel import Field, SQLModel


class Project(SQLModel, table=True):
    """
    Represents a connection to one Swisper deployment.
    
    One SwisperStudio instance can manage multiple Swisper deployments
    (production, staging, development environments).
    
    Based on Langfuse Project model with simplifications:
    - No Organization (not multi-tenant for MVP)
    - Added swisper_url and swisper_api_key (our specific needs)
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
        description="Human-readable project name (e.g., 'Production Swisper')"
    )
    
    swisper_url: str = Field(
        ...,
        max_length=500,
        description="Swisper instance URL (e.g., 'https://swisper.company.com')"
    )
    
    swisper_api_key: str = Field(
        ...,
        description="Hashed API key for authenticating with Swisper instance"
    )
    
    # Optional fields
    description: str | None = Field(
        None,
        max_length=1000,
        description="Optional project description"
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
    
    __table_args__ = (
        Index("ix_projects_created_at", "created_at"),
        Index("ix_projects_deleted_at", "deleted_at"),
    )

