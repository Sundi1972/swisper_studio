"""
Integration tests for RBAC endpoint guards

Tests that API endpoints properly enforce role-based permissions.
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token
from app.models.user import User


@pytest.fixture
async def admin_user(session: AsyncSession) -> User:
    """Create an admin user for testing"""
    user = User(
        email=f"admin-{uuid.uuid4().hex[:8]}@test.com",  # Unique email
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOVDBQYnBPmR3JRMYBqHQTMfzJ8LqCT5u",
        name="Admin User",
        role="admin",
        is_active=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest.fixture
async def developer_user(session: AsyncSession) -> User:
    """Create a developer user for testing"""
    user = User(
        email=f"dev-{uuid.uuid4().hex[:8]}@test.com",  # Unique email
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOVDBQYnBPmR3JRMYBqHQTMfzJ8LqCT5u",
        name="Developer User",
        role="developer",
        is_active=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest.fixture
async def viewer_user(session: AsyncSession) -> User:
    """Create a viewer user for testing"""
    user = User(
        email=f"viewer-{uuid.uuid4().hex[:8]}@test.com",  # Unique email
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOVDBQYnBPmR3JRMYBqHQTMfzJ8LqCT5u",
        name="Viewer User",
        role="viewer",
        is_active=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest.fixture
async def inactive_user(session: AsyncSession) -> User:
    """Create an inactive user for testing"""
    user = User(
        email=f"inactive-{uuid.uuid4().hex[:8]}@test.com",  # Unique email
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOVDBQYnBPmR3JRMYBqHQTMfzJ8LqCT5u",
        name="Inactive User",
        role="admin",
        is_active=False,  # Deactivated
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


def create_auth_header(user: User) -> dict[str, str]:
    """Create Authorization header with JWT token for user"""
    token = create_access_token(
        data={
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
        }
    )
    return {"Authorization": f"Bearer {token}"}


class TestUserManagementEndpoints:
    """Test user management endpoints require admin role"""

    @pytest.mark.asyncio
    async def test_list_users_requires_admin(
        self,
        client: AsyncClient,
        admin_user: User,
        developer_user: User,
    ):
        """Only admin can list all users (GET /api/v1/users)"""
        # Admin can list users
        response = await client.get(
            "/api/v1/users",
            headers=create_auth_header(admin_user),
        )
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert len(data["users"]) >= 2  # At least admin and developer
        assert data["total"] >= 2
        assert data["limit"] == 100  # Default limit
        assert data["offset"] == 0  # Default offset

        # Developer cannot list users (403 Forbidden)
        response = await client.get(
            "/api/v1/users",
            headers=create_auth_header(developer_user),
        )
        assert response.status_code == 403
        assert "admin" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_update_user_role_requires_admin(
        self,
        client: AsyncClient,
        admin_user: User,
        developer_user: User,
        viewer_user: User,
    ):
        """Only admin can update user roles (PATCH /api/v1/users/{id})"""
        # Admin can update user role
        response = await client.patch(
            f"/api/v1/users/{viewer_user.id}",
            headers=create_auth_header(admin_user),
            json={"role": "developer"},
        )
        assert response.status_code == 200
        assert response.json()["role"] == "developer"

        # Developer cannot update user role (403 Forbidden)
        response = await client.patch(
            f"/api/v1/users/{viewer_user.id}",
            headers=create_auth_header(developer_user),
            json={"role": "admin"},  # Trying to escalate
        )
        assert response.status_code == 403


class TestAuthenticationRequired:
    """Test endpoints require valid authentication"""

    @pytest.mark.asyncio
    async def test_missing_jwt_token_returns_401(self, client: AsyncClient):
        """Request without JWT returns 401 Unauthorized"""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401
        assert "authentication" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_invalid_jwt_token_returns_401(self, client: AsyncClient):
        """Invalid JWT returns 401 Unauthorized"""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid-token-here"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_inactive_user_blocked(
        self,
        client: AsyncClient,
        inactive_user: User,
    ):
        """Inactive user gets 403 Forbidden"""
        response = await client.get(
            "/api/v1/auth/me",
            headers=create_auth_header(inactive_user),
        )
        assert response.status_code == 403
        assert "inactive" in response.json()["detail"].lower()


class TestHttpStatusCodes:
    """Test proper HTTP status codes for RBAC"""

    @pytest.mark.asyncio
    async def test_permission_denied_returns_403_not_404(
        self,
        client: AsyncClient,
        viewer_user: User,
        admin_user: User,
    ):
        """Permission failures return 403 Forbidden (not 404 Not Found)"""
        # Viewer tries to update a user (should get 403, not 404)
        response = await client.patch(
            f"/api/v1/users/{admin_user.id}",
            headers=create_auth_header(viewer_user),
            json={"role": "admin"},
        )
        
        # Should be 403 Forbidden (permission denied)
        # NOT 404 Not Found (which would leak user existence)
        assert response.status_code == 403
        assert "admin" in response.json()["detail"].lower()  # Contains "admin role required"

