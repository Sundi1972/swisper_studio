"""Shared API dependencies"""

from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.core.database import get_session
from app.core.security import verify_api_key

# Type aliases for dependency injection
DBSession = Annotated[AsyncSession, Depends(get_session)]
APIKey = Annotated[str, Depends(verify_api_key)]
