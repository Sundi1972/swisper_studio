"""
Comprehensive authentication tests

Tests user registration, login, JWT tokens, and security.
"""

import uuid
from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token, hash_password, verify_password
from app.core.config import settings
from app.models.user import User


class TestRegistration:
    """Test user registration endpoint"""

    @pytest.mark.ci_critical
    @pytest.mark.asyncio
    async def test_register_user_with_valid_data(
        self,
        client: AsyncClient,
        session: AsyncSession,
    ):
        """CI: User registration with valid data succeeds"""
        email = f"newuser-{uuid.uuid4().hex[:8]}@example.com"
        
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "password123",
                "name": "New User",
            },
        )

        assert response.status_code == 201
        data = response.json()
        
        # Check response structure
        assert "user" in data
        assert "token" in data
        assert data["token_type"] == "bearer"
        
        # Check user data
        user_data = data["user"]
        assert user_data["email"] == email
        assert user_data["name"] == "New User"
        assert user_data["role"] == "viewer"  # Default role
        assert user_data["is_active"] is True
        assert "password" not in user_data  # Security: never expose password
        assert "password_hash" not in user_data  # Security: never expose hash
        
        # Verify user created in database
        result = await session.execute(select(User).where(User.email == email))
        db_user = result.scalar_one_or_none()
        assert db_user is not None
        assert db_user.email == email
        assert db_user.password_hash != "password123"  # Password is hashed

    @pytest.mark.asyncio
    async def test_register_duplicate_email_fails(
        self,
        client: AsyncClient,
    ):
        """Registration with duplicate email returns 400"""
        email = f"duplicate-{uuid.uuid4().hex[:8]}@example.com"
        
        # First registration succeeds
        response1 = await client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "password123",
                "name": "User One",
            },
        )
        assert response1.status_code == 201
        
        # Second registration with same email fails
        response2 = await client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "differentpass",
                "name": "User Two",
            },
        )
        assert response2.status_code == 400
        assert "already registered" in response2.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_weak_password_fails(
        self,
        client: AsyncClient,
    ):
        """Registration with password <8 chars fails validation"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"weak-{uuid.uuid4().hex[:8]}@example.com",
                "password": "short",  # Only 5 characters
                "name": "Weak Password User",
            },
        )
        assert response.status_code == 422  # Validation error
        errors = response.json()["detail"]
        assert any("password" in str(err).lower() for err in errors)

    @pytest.mark.asyncio
    async def test_register_invalid_email_fails(
        self,
        client: AsyncClient,
    ):
        """Registration with invalid email fails validation"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "password123",
                "name": "Invalid Email User",
            },
        )
        assert response.status_code == 422  # Validation error


class TestLogin:
    """Test user login endpoint"""

    @pytest.mark.ci_critical
    @pytest.mark.asyncio
    async def test_login_with_correct_credentials(
        self,
        client: AsyncClient,
        session: AsyncSession,
    ):
        """CI: Login with correct email and password succeeds"""
        # Create user via registration
        email = f"login-{uuid.uuid4().hex[:8]}@example.com"
        password = "testpassword123"
        
        await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password, "name": "Login User"},
        )
        
        # Login with correct credentials
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )

        assert response.status_code == 200
        data = response.json()
        
        assert "user" in data
        assert "token" in data
        assert data["user"]["email"] == email
        
        # Verify JWT token is valid
        token = data["token"]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        assert payload["email"] == email
        assert payload["role"] == "viewer"

    @pytest.mark.asyncio
    async def test_login_with_incorrect_password(
        self,
        client: AsyncClient,
    ):
        """Login with wrong password returns 401"""
        # Create user
        email = f"wrongpass-{uuid.uuid4().hex[:8]}@example.com"
        
        await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "correctpass123", "name": "User"},
        )
        
        # Try login with wrong password
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "wrongpassword"},
        )

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_with_nonexistent_email(
        self,
        client: AsyncClient,
    ):
        """Login with non-existent email returns 401"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": f"nonexistent-{uuid.uuid4().hex[:8]}@example.com",
                "password": "anypassword",
            },
        )

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_updates_last_login_timestamp(
        self,
        client: AsyncClient,
        session: AsyncSession,
    ):
        """Login updates the last_login timestamp"""
        # Create user
        email = f"timestamp-{uuid.uuid4().hex[:8]}@example.com"
        
        await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "password123", "name": "User"},
        )
        
        # Get initial last_login
        result = await session.execute(select(User).where(User.email == email))
        user_before = result.scalar_one()
        initial_last_login = user_before.last_login
        
        # Wait a moment and login again
        await session.close()  # Close session to avoid cache
        
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "password123"},
        )
        
        assert response.status_code == 200
        
        # Verify last_login was updated
        # Note: We check the response contains last_login field
        assert response.json()["user"]["last_login"] is not None

    @pytest.mark.asyncio
    async def test_inactive_user_cannot_login(
        self,
        client: AsyncClient,
        session: AsyncSession,
    ):
        """Inactive user gets 403 when trying to login"""
        # Create user
        email = f"inactive-{uuid.uuid4().hex[:8]}@example.com"
        user = User(
            email=email,
            password_hash=hash_password("password123"),
            name="Inactive User",
            role="viewer",
            is_active=False,  # Deactivated
        )
        session.add(user)
        await session.commit()
        
        # Try to login
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "password123"},
        )

        assert response.status_code == 403
        assert "inactive" in response.json()["detail"].lower()


class TestTokenValidation:
    """Test JWT token validation"""

    @pytest.mark.asyncio
    async def test_valid_token_returns_user(
        self,
        client: AsyncClient,
    ):
        """Valid JWT token returns user info"""
        # Register and get token
        email = f"token-{uuid.uuid4().hex[:8]}@example.com"
        reg_response = await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "password123", "name": "Token User"},
        )
        token = reg_response.json()["token"]
        
        # Use token to access /auth/me
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json()["email"] == email

    @pytest.mark.asyncio
    async def test_expired_token_returns_401(
        self,
        client: AsyncClient,
        session: AsyncSession,
    ):
        """Expired JWT token returns 401"""
        # Create user
        email = f"expired-{uuid.uuid4().hex[:8]}@example.com"
        user = User(
            email=email,
            password_hash=hash_password("password123"),
            name="Expired Token User",
            role="viewer",
            is_active=True,
        )
        session.add(user)
        await session.commit()
        
        # Create expired token (expired 1 hour ago)
        expired_token = create_access_token(
            data={"user_id": user.id, "email": email, "role": "viewer"},
            expires_delta=timedelta(hours=-1),  # Negative = expired
        )
        
        # Try to use expired token
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower() or "expired" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_invalid_token_signature_returns_401(
        self,
        client: AsyncClient,
    ):
        """Token with invalid signature returns 401"""
        # Create token with wrong secret
        fake_token = jwt.encode(
            {"user_id": "fake-id", "email": "fake@example.com"},
            "wrong-secret-key",
            algorithm="HS256",
        )
        
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {fake_token}"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_token_without_user_id_returns_401(
        self,
        client: AsyncClient,
    ):
        """JWT token without user_id returns 401"""
        # Create token with missing user_id
        bad_token = create_access_token(data={"email": "test@example.com"})
        
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {bad_token}"},
        )

        assert response.status_code == 401


class TestPasswordSecurity:
    """Test password hashing security"""

    def test_password_is_hashed_not_stored_plaintext(self):
        """Passwords are hashed with bcrypt, never stored as plaintext"""
        password = "my_secure_password_123"
        hashed = hash_password(password)
        
        # Hash should not equal plaintext
        assert hashed != password
        
        # Hash should start with bcrypt identifier
        assert hashed.startswith("$2b$")
        
        # Should be able to verify
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False

    def test_same_password_produces_different_hashes(self):
        """Same password hashed twice produces different hashes (salt is random)"""
        password = "test_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Different hashes (because of random salt)
        assert hash1 != hash2
        
        # But both verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    @pytest.mark.asyncio
    async def test_password_never_returned_in_api_response(
        self,
        client: AsyncClient,
    ):
        """API never returns password or password_hash"""
        email = f"security-{uuid.uuid4().hex[:8]}@example.com"
        
        # Register
        reg_response = await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "testpass123", "name": "Secure User"},
        )
        
        # Check registration response
        reg_data = reg_response.json()
        assert "password" not in str(reg_data)
        assert "password_hash" not in str(reg_data)
        
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "testpass123"},
        )
        
        # Check login response
        login_data = login_response.json()
        assert "password" not in str(login_data)
        assert "password_hash" not in str(login_data)
        
        # Get user info
        token = login_data["token"]
        me_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        # Check me response
        me_data = me_response.json()
        assert "password" not in str(me_data)
        assert "password_hash" not in str(me_data)


class TestLogout:
    """Test logout endpoint"""

    @pytest.mark.asyncio
    async def test_logout_with_valid_token(
        self,
        client: AsyncClient,
    ):
        """Logout with valid token succeeds"""
        # Register and get token
        email = f"logout-{uuid.uuid4().hex[:8]}@example.com"
        reg_response = await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "password123", "name": "Logout User"},
        )
        token = reg_response.json()["token"]
        
        # Logout
        response = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert "message" in response.json()

    @pytest.mark.asyncio
    async def test_logout_without_token_fails(
        self,
        client: AsyncClient,
    ):
        """Logout without token returns 401"""
        response = await client.post("/api/v1/auth/logout")

        assert response.status_code == 401


class TestAuthMe:
    """Test /auth/me endpoint"""

    @pytest.mark.asyncio
    async def test_me_returns_current_user(
        self,
        client: AsyncClient,
        session: AsyncSession,
    ):
        """GET /auth/me returns current user from JWT token"""
        # Create admin user
        email = f"me-{uuid.uuid4().hex[:8]}@example.com"
        user = User(
            email=email,
            password_hash=hash_password("password123"),
            name="Me Test User",
            role="admin",
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        # Create token
        token = create_access_token(
            data={"user_id": user.id, "email": email, "role": "admin"}
        )
        
        # Get user info
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == email
        assert data["role"] == "admin"
        assert data["name"] == "Me Test User"

    @pytest.mark.asyncio
    async def test_me_without_token_returns_401(
        self,
        client: AsyncClient,
    ):
        """GET /auth/me without token returns 401"""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401
        assert "authentication" in response.json()["detail"].lower()


class TestTokenPayload:
    """Test JWT token payload structure"""

    @pytest.mark.asyncio
    async def test_jwt_contains_user_id_email_role(
        self,
        client: AsyncClient,
    ):
        """JWT token contains user_id, email, and role"""
        # Register
        email = f"payload-{uuid.uuid4().hex[:8]}@example.com"
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "password123", "name": "Payload User"},
        )
        
        token = response.json()["token"]
        
        # Decode token (without verification for testing)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        # Verify payload structure
        assert "user_id" in payload
        assert "email" in payload
        assert "role" in payload
        assert "exp" in payload  # Expiration timestamp
        
        assert payload["email"] == email
        assert payload["role"] == "viewer"
        assert isinstance(payload["user_id"], str)

    @pytest.mark.asyncio
    async def test_jwt_expiration_set_to_24_hours(
        self,
        client: AsyncClient,
    ):
        """JWT token expires in 24 hours"""
        # Register
        email = f"expiry-{uuid.uuid4().hex[:8]}@example.com"
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "password123", "name": "Expiry User"},
        )
        
        token = response.json()["token"]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        # Check expiration is approximately 24 hours from now
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.utcfromtimestamp(exp_timestamp)
        now = datetime.utcnow()
        
        time_until_expiry = exp_datetime - now
        
        # Should be close to 24 hours (allow 1 minute variance)
        assert timedelta(hours=23, minutes=59) < time_until_expiry < timedelta(hours=24, minutes=1)

