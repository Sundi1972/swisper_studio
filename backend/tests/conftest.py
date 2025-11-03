"""
Pytest configuration and fixtures

Note: Using real database for tests (not mocks) as per cursor rules.
Test isolation via database cleanup between tests.

CRITICAL: Async event loop handling for database sessions.
Each test gets a new event loop, so we must create a new engine per test
to avoid "Future attached to a different loop" errors with AsyncPG.

CLEANUP: Tests clean up after themselves to avoid polluting the database.
Only keeps data for tests that are explicitly marked with @pytest.mark.keep_data.
"""

import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text

from app.main import app
from app.core.config import settings


@pytest.fixture(scope="function")
async def engine():
    """
    Create a test database engine for each test.
    
    CRITICAL: Uses NullPool to avoid connection pooling across event loops.
    Each test gets a fresh engine with the current event loop.
    """
    test_engine = create_async_engine(
        str(settings.DATABASE_URL),
        echo=False,  # Less verbose for tests
        poolclass=NullPool,  # NO pooling - creates fresh connections per test
    )
    
    yield test_engine
    
    # Clean up engine after test
    await test_engine.dispose()


@pytest.fixture(scope="function")
async def session(engine, request) -> AsyncGenerator[AsyncSession, None]:
    """
    Create test database session with automatic cleanup.
    
    Uses real PostgreSQL database from docker-compose.
    Each test gets its own session with a fresh engine (no event loop conflicts).
    
    Cleanup: After test completes, deletes all projects created during the test
    (which cascades to traces and observations due to FK constraints).
    
    To keep data (e.g., for manual inspection), mark test with @pytest.mark.keep_data.
    """
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    # Track project IDs created during this test for cleanup
    created_project_ids = []
    
    async with async_session_maker() as test_session:
        try:
            # Get initial project count
            result = await test_session.execute(text("SELECT id FROM projects WHERE deleted_at IS NULL"))
            initial_project_ids = {row[0] for row in result.fetchall()}
            
            yield test_session
            
            # After test: cleanup unless marked with keep_data
            if not hasattr(request.node, 'get_closest_marker') or not request.node.get_closest_marker('keep_data'):
                # Find new projects created during test
                result = await test_session.execute(text("SELECT id FROM projects WHERE deleted_at IS NULL"))
                final_project_ids = {row[0] for row in result.fetchall()}
                new_project_ids = final_project_ids - initial_project_ids
                
                if new_project_ids:
                    # Soft delete projects (cascades to traces/observations)
                    for proj_id in new_project_ids:
                        await test_session.execute(
                            text("UPDATE projects SET deleted_at = NOW() WHERE id = :id"),
                            {"id": proj_id}
                        )
                    await test_session.commit()
                    # Note: Not printing cleanup message to avoid noise in test output
        finally:
            await test_session.close()


@pytest.fixture(scope="function")
async def client(engine) -> AsyncGenerator[AsyncClient, None]:
    """
    Create test HTTP client with overridden database dependency.
    
    CRITICAL: Overrides app's get_session to use test engine (NullPool).
    This prevents event loop conflicts when API routes access database.
    """
    from app.core.database import get_session
    
    # Create test session factory from test engine
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    # Override dependency
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with async_session_maker() as session:
            try:
                yield session
            finally:
                await session.close()
    
    # Apply override
    app.dependency_overrides[get_session] = override_get_session
    
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as test_client:
            yield test_client
    finally:
        # Clean up override
        app.dependency_overrides.clear()


@pytest.fixture
def api_headers() -> dict[str, str]:
    """
    Valid API key headers for authenticated requests.
    """
    return {"X-API-Key": settings.API_KEY}


@pytest.fixture
def invalid_api_headers() -> dict[str, str]:
    """
    Invalid API key headers for testing authentication failures.
    """
    return {"X-API-Key": "invalid-key-12345"}


@pytest.fixture
def test_project_payload() -> dict:
    """
    Helper fixture: Standard project creation payload with 3 environments.
    
    Use this to create test projects in a consistent way.
    Points to mock SAP for testing.
    
    Note: Uses backend:8000 (Docker internal network) for backend tests.
    For browser/frontend, environments can be manually updated to localhost:8001.
    """
    return {
        "name": "Test Project",
        "description": "Test project description",
        "dev_environment": {
            "swisper_url": "http://backend:8000/api/v1/mock-swisper",
            "swisper_api_key": "mock_dev_key_12345"
        },
        "staging_environment": {
            "swisper_url": "http://backend:8000/api/v1/mock-swisper",
            "swisper_api_key": "mock_staging_key_12345"
        },
        "production_environment": {
            "swisper_url": "http://backend:8000/api/v1/mock-swisper",
            "swisper_api_key": "mock_prod_key_12345"
        }
    }


@pytest.fixture(scope="session", autouse=True)
async def cleanup_test_data():
    """
    Cleanup test data after entire test session.
    
    Runs once after all tests complete.
    Soft-deletes all projects EXCEPT those with "AAA" prefix (demo/UAT data).
    
    This ensures test pollution is cleaned up while preserving demo data.
    """
    yield  # Tests run here
    
    # After all tests: cleanup
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    from sqlalchemy import text
    
    cleanup_engine = create_async_engine(
        str(settings.DATABASE_URL),
        poolclass=NullPool,
    )
    
    async_session_maker = async_sessionmaker(cleanup_engine, class_=AsyncSession)
    
    async with async_session_maker() as cleanup_session:
        # Soft-delete all projects that don't start with "AAA" (test data)
        await cleanup_session.execute(
            text("""
                UPDATE projects 
                SET deleted_at = NOW() 
                WHERE deleted_at IS NULL 
                AND name NOT LIKE 'AAA%'
            """)
        )
        await cleanup_session.commit()
    
    await cleanup_engine.dispose()
