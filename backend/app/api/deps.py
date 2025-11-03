"""Shared API dependencies"""

from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPBearer

from app.core.database import get_session
from app.core.security import verify_api_key, get_current_user
from app.models.user import User

# Type aliases for dependency injection
DBSession = Annotated[AsyncSession, Depends(get_session)]
APIKey = Annotated[str, Depends(verify_api_key)]


# Authentication schemes
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user_or_api_key(
    session: AsyncSession = Depends(get_session),
    api_key: str | None = Security(api_key_header),
    credentials = Security(bearer_scheme),
) -> User | str:
    """
    Accept EITHER JWT token OR API key for authentication.
    
    Returns:
        User if JWT auth, or API key string if API key auth
        
    Raises:
        HTTPException: If neither auth method provided or both invalid
    """
    # Try JWT token first
    if credentials:
        try:
            user = await get_current_user(session, credentials)
            return user
        except HTTPException:
            # JWT failed, try API key
            pass
    
    # Try API key
    if api_key:
        try:
            verified_key = await verify_api_key(api_key)
            return verified_key
        except HTTPException:
            pass
    
    # Both failed
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required: Provide either JWT token (Authorization: Bearer) or API key (X-API-Key)",
        headers={"WWW-Authenticate": "Bearer"},
    )


# Type alias for flexible auth
Auth = Annotated[User | str, Depends(get_current_user_or_api_key)]
