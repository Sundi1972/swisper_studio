"""Database connection and session management"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.core.config import settings

# Create async engine
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.ENVIRONMENT == "development",
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions.
    
    Usage:
        @app.get("/")
        async def route(session: AsyncSession = Depends(get_session)):
            ...
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_db_and_tables() -> None:
    """Create all database tables (for development/testing only)"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db_connection() -> None:
    """Close database connection (for application shutdown)"""
    await engine.dispose()


def get_async_session_factory():
    """
    Get async session factory for services.
    
    Returns a callable that creates async context manager for sessions.
    Used by observability consumer and other background services.
    """
    from contextlib import asynccontextmanager
    
    @asynccontextmanager
    async def session_factory():
        async with async_session() as session:
            yield session
    
    return session_factory
