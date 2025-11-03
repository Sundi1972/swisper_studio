"""
RBAC (Role-Based Access Control) permission system

Defines permissions and provides role-based access checks.
"""

from functools import lru_cache

from app.models.user import User


class Permission:
    """
    Permission constants for RBAC.
    
    Use these constants when checking permissions instead of hardcoded strings.
    """
    
    # Project permissions
    VIEW_PROJECT = "project:view"
    EDIT_PROJECT = "project:edit"
    DELETE_PROJECT = "project:delete"
    
    # Config permissions
    VIEW_CONFIG = "config:view"
    EDIT_CONFIG = "config:edit"
    
    # User management (admin only)
    MANAGE_USERS = "user:manage"


# Role-based environment permissions matrix
# Format: {role: {environment: [permissions]}}
ENVIRONMENT_PERMISSIONS: dict[str, dict[str, list[str]]] = {
    "admin": {
        "dev": ["read", "write"],
        "staging": ["read", "write"],
        "production": ["read", "write"],
    },
    "developer": {
        "dev": ["read", "write"],
        "staging": ["read", "write"],
        "production": ["read"],  # Read-only in production
    },
    "qa": {
        "dev": ["read"],  # Read-only in dev
        "staging": ["read", "write"],
        "production": ["read"],  # Read-only in production
    },
    "viewer": {
        "dev": ["read"],
        "staging": ["read"],
        "production": ["read"],
    },
}


@lru_cache(maxsize=128)
def _get_role_permissions(role: str) -> dict[str, list[str]]:
    """
    Get permissions for a role (cached).
    
    Internal helper function with caching for performance.
    """
    return ENVIRONMENT_PERMISSIONS.get(role, ENVIRONMENT_PERMISSIONS["viewer"])


def can_edit_environment(user: User, environment: str) -> bool:
    """
    Check if user can edit config in specified environment.
    
    Args:
        user: User object with role attribute
        environment: Environment name (dev, staging, production)
        
    Returns:
        True if user can edit, False otherwise
        
    Examples:
        >>> admin = User(role="admin", is_active=True)
        >>> can_edit_environment(admin, "production")
        True
        
        >>> developer = User(role="developer", is_active=True)
        >>> can_edit_environment(developer, "production")
        False
        
        >>> inactive = User(role="admin", is_active=False)
        >>> can_edit_environment(inactive, "dev")
        False
    """
    # Inactive users have no permissions
    if not user.is_active:
        return False
    
    # Get permissions for this role (cached)
    role_permissions = _get_role_permissions(user.role)
    environment_permissions = role_permissions.get(environment, [])
    
    # Check if user has write permission
    return "write" in environment_permissions


def has_permission(user: User, permission: str) -> bool:
    """
    Check if user has a specific permission.
    
    Args:
        user: User object with role attribute
        permission: Permission constant from Permission class
        
    Returns:
        True if user has permission, False otherwise
        
    Examples:
        >>> admin = User(role="admin", is_active=True)
        >>> has_permission(admin, Permission.MANAGE_USERS)
        True
        
        >>> developer = User(role="developer", is_active=True)
        >>> has_permission(developer, Permission.MANAGE_USERS)
        False
    """
    # Inactive users have no permissions
    if not user.is_active:
        return False
    
    # Admin has all permissions
    if user.role == "admin":
        return True
    
    # Permission-specific checks for non-admin roles
    if permission == Permission.MANAGE_USERS:
        return False  # Only admin can manage users
    
    if permission == Permission.VIEW_PROJECT:
        return True  # All active users can view projects
    
    if permission == Permission.EDIT_PROJECT:
        return user.role in ["admin", "developer"]
    
    if permission == Permission.DELETE_PROJECT:
        return user.role == "admin"
    
    if permission == Permission.VIEW_CONFIG:
        return True  # All active users can view configs
    
    if permission == Permission.EDIT_CONFIG:
        # Config editing depends on environment (use can_edit_environment instead)
        return user.role in ["admin", "developer", "qa"]
    
    # Unknown permission defaults to denied
    return False


def is_admin(user: User) -> bool:
    """
    Check if user is an admin.
    
    Args:
        user: User object with role attribute
        
    Returns:
        True if user is admin, False otherwise
    """
    return user.is_active and user.role == "admin"

