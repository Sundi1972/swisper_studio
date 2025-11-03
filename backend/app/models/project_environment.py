"""Project environment models"""
import uuid
from datetime import datetime
from enum import Enum
from sqlmodel import Field, SQLModel, UniqueConstraint
from pydantic import field_validator


class EnvironmentType(str, Enum):
    """Environment types (dev, staging, production)"""
    DEV = "dev"
    STAGING = "staging"
    PRODUCTION = "production"


class ProjectEnvironment(SQLModel, table=True):
    """Environment within a project (dev, staging, production)"""
    __tablename__ = "project_environment"
    
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True
    )
    project_id: str = Field(foreign_key="projects.id", index=True)
    
    # Environment type (always one of: dev, staging, production)
    # Stored as VARCHAR in DB, validated via Pydantic
    env_type: str = Field(max_length=20, index=True)
    
    @field_validator("env_type")
    @classmethod
    def validate_env_type(cls, v: str) -> str:
        """Validate env_type is one of: dev, staging, production"""
        valid_types = {"dev", "staging", "production"}
        if v not in valid_types:
            raise ValueError(f"env_type must be one of {valid_types}, got: {v}")
        return v
    
    # Swisper instance connection
    swisper_url: str = Field(max_length=255)
    api_key: str = Field(max_length=255)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Unique constraint: one environment of each type per project
    __table_args__ = (
        UniqueConstraint('project_id', 'env_type', name='uq_project_env_type'),
    )

