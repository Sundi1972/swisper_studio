"""
User management endpoints - Admin only

Endpoints for managing users (list, update role, deactivate).
All endpoints require admin role except /users/me.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import CurrentUser, CurrentAdminUser
from app.models.user import User

router = APIRouter(prefix="/users", tags=["User Management"])


# Response Models


class UserResponse(BaseModel):
    """User info response (NEVER includes password_hash!)"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: datetime | None


class ListUsersResponse(BaseModel):
    """List users response with pagination"""

    users: list[UserResponse]
    total: int
    limit: int
    offset: int


class UpdateUserRequest(BaseModel):
    """Update user request"""

    name: str | None = None
    role: str | None = None
    is_active: bool | None = None


# Endpoints


@router.get(
    "",
    response_model=ListUsersResponse,
    summary="List all users (admin only)",
    description="Get list of all users with pagination and filtering. Requires admin role.",
)
async def list_users(
    admin_user: CurrentAdminUser,
    session: AsyncSession = Depends(get_session),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of users to return"),
    offset: int = Query(0, ge=0, description="Number of users to skip"),
    role: str | None = Query(None, description="Filter by role (admin, developer, qa, viewer)"),
    is_active: bool | None = Query(None, description="Filter by active status"),
) -> ListUsersResponse:
    """
    List all users in the system with pagination and filtering.

    **Admin only endpoint.**

    Query parameters:
    - **limit**: Max users to return (default 100, max 1000)
    - **offset**: Number of users to skip (for pagination)
    - **role**: Filter by role (optional)
    - **is_active**: Filter by active status (optional)

    Returns paginated list of users.
    """
    # Build query with filters
    query = select(User)
    
    # Apply role filter
    if role is not None:
        query = query.where(User.role == role)
    
    # Apply active status filter
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    # Get total count (before pagination)
    count_query = select(User.id)
    if role is not None:
        count_query = count_query.where(User.role == role)
    if is_active is not None:
        count_query = count_query.where(User.is_active == is_active)
    
    count_result = await session.execute(count_query)
    total = len(count_result.fetchall())
    
    # Apply ordering and pagination
    query = query.order_by(User.created_at.desc()).limit(limit).offset(offset)
    
    # Fetch users
    result = await session.execute(query)
    users = result.scalars().all()

    return ListUsersResponse(
        users=[UserResponse.model_validate(user) for user in users],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get authenticated user info. Any authenticated user can access.",
)
async def get_current_user_info(
    current_user: CurrentUser,
) -> UserResponse:
    """
    Get current user information.

    **Any authenticated user can access this endpoint.**
    """
    return UserResponse.model_validate(current_user)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user (admin only)",
    description="Update user role, name, or active status. Requires admin role.",
)
async def update_user(
    user_id: str,
    request: UpdateUserRequest,
    admin_user: CurrentAdminUser,
    session: AsyncSession = Depends(get_session),
) -> UserResponse:
    """
    Update a user's information.

    **Admin only endpoint.**

    Can update:
    - User role (admin, developer, qa, viewer)
    - User name
    - Active status (deactivate/reactivate user)
    """
    # Fetch user
    user = await session.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update fields if provided
    if request.name is not None:
        user.name = request.name

    if request.role is not None:
        # Validate role
        valid_roles = ["admin", "developer", "qa", "viewer"]
        if request.role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}",
            )
        user.role = request.role

    if request.is_active is not None:
        user.is_active = request.is_active

    # Update timestamp
    user.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(user)

    return UserResponse.model_validate(user)

