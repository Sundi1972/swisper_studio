"""
User model - User accounts with role-based access control

Simplified from Swisper implementation:
- No avatars or profile pictures
- No workspaces/organizations  
- No social login
- Focus on RBAC for config management
"""

import uuid
from datetime import datetime
from sqlalchemy import Index
from sqlmodel import Field, SQLModel

from app.models.enums import UserRole


class User(SQLModel, table=True):
    """
    User account with role-based access control.
    
    Roles determine permissions:
    - ADMIN: Full access to all projects and environments
    - DEVELOPER: Read/write dev/staging, read-only production
    - QA: Read/write staging, read-only dev/production
    - VIEWER: Read-only everywhere
    
    Security:
    - Passwords hashed with bcrypt (cost factor 12)
    - JWT tokens for authentication (24h expiration)
    - password_hash never exposed via API
    """
    
    __tablename__ = "users"
    
    # Primary key
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique user identifier (UUID)"
    )
    
    # Core fields
    email: str = Field(
        ...,
        unique=True,
        index=True,
        max_length=255,
        description="User email (unique, used for login)"
    )
    
    password_hash: str = Field(
        ...,
        max_length=255,
        description="Bcrypt password hash (NEVER expose via API)"
    )
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="User full name"
    )
    
    role: str = Field(
        default="viewer",
        max_length=20,
        description="User role (determines permissions): admin, developer, qa, viewer"
    )
    
    is_active: bool = Field(
        default=True,
        description="Whether user account is active (soft delete)"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the user was created"
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the user was last updated"
    )
    
    last_login: datetime | None = Field(
        None,
        description="Last successful login timestamp"
    )
    
    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_created_at", "created_at"),
        Index("ix_users_role", "role"),
        Index("ix_users_is_active", "is_active"),
    )

