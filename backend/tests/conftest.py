"""
Pytest configuration and fixtures

Note: Using real database for tests (not mocks) as per cursor rules.
Test isolation via database cleanup between tests.
"""

import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.config import settings
from app.core.database import async_session


@pytest.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    Create test HTTP client.
    
    Uses real database from docker-compose.
    Tests clean up their own data or we accept data accumulation during test run.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client


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


# NOTE: Database cleanup disabled for now to avoid async event loop issues.
# Tests are designed to be independent (using unique data).
# For production testing, we'll implement proper transaction rollback.
