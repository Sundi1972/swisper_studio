"""
Authentication endpoints - User registration, login, logout

Endpoints:
- POST /auth/register - Create new user account
- POST /auth/login - Login with email + password
- GET /auth/me - Get current user info
- POST /auth/logout - Logout (frontend clears token)
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token, hash_password, verify_password
from app.core.database import get_session
from app.core.security import CurrentUser
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Request/Response Models


class RegisterRequest(BaseModel):
    """User registration request"""

    email: EmailStr = Field(..., description="User email (must be unique)")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    name: str = Field(..., min_length=1, max_length=255, description="User full name")


class LoginRequest(BaseModel):
    """User login request"""

    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    """User info response (NEVER includes password_hash!)"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    name: str
    role: str  # admin, developer, qa, or viewer
    is_active: bool
    created_at: datetime
    last_login: datetime | None


class AuthResponse(BaseModel):
    """Authentication response with user info and JWT token"""

    user: UserResponse
    token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    """Generic message response"""

    message: str


# Endpoints


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email, password, and name. Returns JWT token.",
)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_session),
) -> AuthResponse:
    """
    Register a new user account.

    - **email**: Must be unique
    - **password**: Minimum 8 characters (hashed with bcrypt)
    - **name**: User's full name
    - **role**: Defaults to VIEWER (upgrade via admin)

    Returns JWT token for immediate login.
    """
    # Check if email already exists
    result = await session.execute(select(User).where(User.email == request.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        name=request.name,
        role="viewer",  # Default role
        is_active=True,
        last_login=datetime.utcnow(),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Create JWT token
    token = create_access_token(
        data={
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
        }
    )

    return AuthResponse(
        user=UserResponse.model_validate(user),
        token=token,
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login user",
    description="Login with email and password. Returns JWT token.",
)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> AuthResponse:
    """
    Login with email and password.

    - **email**: User email
    - **password**: User password

    Returns JWT token for authentication.
    """
    # Find user by email
    result = await session.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Update last_login timestamp
    user.last_login = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(user)

    # Create JWT token
    token = create_access_token(
        data={
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
        }
    )

    return AuthResponse(
        user=UserResponse.model_validate(user),
        token=token,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get authenticated user info from JWT token.",
)
async def get_me(
    current_user: CurrentUser,
) -> UserResponse:
    """
    Get current authenticated user.

    Requires valid JWT token in Authorization header.
    """
    return UserResponse.model_validate(current_user)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout user",
    description="Logout user (client should clear JWT token).",
)
async def logout(
    current_user: CurrentUser,
) -> MessageResponse:
    """
    Logout user.

    JWT tokens are stateless, so logout is handled client-side by clearing the token.
    This endpoint validates the token is still valid before logout.

    Future enhancement: Implement token blacklist for immediate revocation.
    """
    return MessageResponse(message="Logged out successfully")

