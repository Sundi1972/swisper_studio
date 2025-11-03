"""Config versioning models"""
import uuid
from datetime import datetime
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON
from typing import Dict, Any


class ConfigVersion(SQLModel, table=True):
    """Version history for configurations"""
    __tablename__ = "config_version"
    
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True
    )
    project_id: str = Field(foreign_key="projects.id", index=True)
    
    # What config
    table_name: str = Field(max_length=100, index=True)
    record_id: str = Field(max_length=255, index=True)
    
    # Version info
    version_number: int = Field(index=True)
    
    # The actual config data (snapshot)
    config_data: Dict[str, Any] = Field(sa_column=Column(JSON))
    
    # Change tracking
    description: str | None = Field(default=None)
    created_by: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Parent version (for lineage tracking)
    parent_version_id: str | None = Field(
        default=None, 
        foreign_key="config_version.id"
    )


class ConfigDeployment(SQLModel, table=True):
    """Track which version is deployed to which environment"""
    __tablename__ = "config_deployment"
    
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True
    )
    
    # What and where
    version_id: str = Field(foreign_key="config_version.id", index=True)
    environment_id: str = Field(
        foreign_key="project_environment.id",
        index=True
    )
    
    # Deployment details
    status: str = Field(max_length=20, default="deployed")
    deployed_by: str = Field(max_length=255)
    deployed_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Error tracking
    error_message: str | None = Field(default=None)

