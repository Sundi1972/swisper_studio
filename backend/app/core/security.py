"""
Security utilities - Authentication and authorization

Supports:
1. API Key authentication (for SDK/external integrations)
2. JWT token authentication (for frontend users)
"""

from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import decode_access_token
from app.core.config import settings
from app.core.database import get_session
from app.models.user import User

# Authentication schemes
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)


async def verify_api_key(api_key: str | None = Security(api_key_header)) -> str:
    """
    Verify API key from request header.
    
    For SDK integrations and external tools.
    Will be enhanced with project-specific API keys later.
    
    Args:
        api_key: API key from X-API-Key header
        
    Returns:
        Verified API key
        
    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return api_key


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    credentials = Security(bearer_scheme),
) -> User:
    """
    Get current user from JWT token.
    
    For frontend authentication.
    Validates JWT token and returns authenticated user.
    
    Args:
        session: Database session
        credentials: Bearer token from Authorization header
        
    Returns:
        Authenticated User object
        
    Raises:
        HTTPException: If token is missing, invalid, or user not found
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Decode JWT token
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user_id from token
    user_id: str | None = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Fetch user from database
    user = await session.get(User, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current user and verify they are an admin.
    
    For admin-only endpoints (user management, etc.).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User if they are an admin
        
    Raises:
        HTTPException: If user is not an admin (403 Forbidden)
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Admin role required. Current role: {current_user.role}",
        )
    
    return current_user


# Type aliases for dependency injection
APIKey = Annotated[str, Depends(verify_api_key)]
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentAdminUser = Annotated[User, Depends(get_current_admin_user)]
