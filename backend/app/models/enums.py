"""Enumerations for data models"""

from enum import Enum


class ObservationType(str, Enum):
    """Types of observations in a trace"""
    
    SPAN = "SPAN"              # Generic execution span
    GENERATION = "GENERATION"  # LLM generation
    EVENT = "EVENT"           # Single point event
    TOOL = "TOOL"             # Tool call
    AGENT = "AGENT"           # Agent execution


class UserRole(str, Enum):
    """
    User roles with different permission levels.
    
    Permissions by role:
    - ADMIN: Full access to all projects and all environments
    - DEVELOPER: Read/write dev & staging, read-only production
    - QA: Read/write staging, read-only dev & production
    - VIEWER: Read-only everywhere
    """
    
    ADMIN = "admin"
    DEVELOPER = "developer"
    QA = "qa"
    VIEWER = "viewer"
