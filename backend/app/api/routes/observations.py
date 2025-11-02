"""Observation ingestion API endpoints"""

from datetime import datetime
from decimal import Decimal
from typing import Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.api.deps import APIKey, DBSession
from app.models import Observation, ObservationType


router = APIRouter()


class ObservationCreate(BaseModel):
    """Request model for creating an observation"""
    
    id: str = Field(..., description="Unique observation identifier (UUID)")
    trace_id: str = Field(..., description="Parent trace ID")
    parent_observation_id: str | None = Field(None, description="Parent observation ID")
    type: ObservationType = Field(..., description="Observation type")
    name: str | None = Field(None, description="Human-readable observation name")
    start_time: datetime = Field(default_factory=datetime.utcnow, description="Start time")
    input: dict[str, Any] | None = Field(None, description="Input data")
    meta: dict[str, Any] | None = Field(None, description="Additional metadata")
    model: str | None = Field(None, description="LLM model name (if applicable)")


class ObservationUpdate(BaseModel):
    """Request model for updating an observation"""
    
    end_time: datetime | None = Field(None, description="End time")
    output: dict[str, Any] | None = Field(None, description="Output data")
    level: str | None = Field(None, description="Log level")
    status_message: str | None = Field(None, description="Status or error message")
    prompt_tokens: int | None = Field(None, description="Number of prompt tokens")
    completion_tokens: int | None = Field(None, description="Number of completion tokens")
    total_cost: Decimal | None = Field(None, description="Total cost in USD")


class ObservationResponse(BaseModel):
    """Response model for observation"""
    
    id: str
    trace_id: str
    parent_observation_id: str | None
    type: ObservationType
    name: str | None
    start_time: datetime
    end_time: datetime | None
    level: str
    
    model_config = {"from_attributes": True}


@router.post("/observations", response_model=ObservationResponse, status_code=status.HTTP_201_CREATED)
async def create_observation(
    observation_data: ObservationCreate,
    session: DBSession,
    api_key: APIKey,
) -> Observation:
    """
    Create a new observation.
    
    Accepts observation data from the Swisper SDK and stores it in the database.
    """
    # Check if observation already exists (idempotency)
    stmt = select(Observation).where(Observation.id == observation_data.id)
    result = await session.execute(stmt)
    existing_observation = result.scalar_one_or_none()
    
    if existing_observation:
        return existing_observation
    
    # Create new observation
    observation = Observation(**observation_data.model_dump())
    
    session.add(observation)
    await session.commit()
    await session.refresh(observation)
    
    return observation


@router.patch("/observations/{observation_id}", response_model=ObservationResponse)
async def update_observation(
    observation_id: str,
    update_data: ObservationUpdate,
    session: DBSession,
    api_key: APIKey,
) -> Observation:
    """
    Update an observation (typically to close it with end_time and output).
    
    Used by the SDK when an observation completes.
    """
    stmt = select(Observation).where(Observation.id == observation_id)
    result = await session.execute(stmt)
    observation = result.scalar_one_or_none()
    
    if not observation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Observation {observation_id} not found"
        )
    
    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(observation, field, value)
    
    await session.commit()
    await session.refresh(observation)
    
    return observation


@router.get("/observations/{observation_id}", response_model=ObservationResponse)
async def get_observation(
    observation_id: str,
    session: DBSession,
    api_key: APIKey,
) -> Observation:
    """Get an observation by ID"""
    stmt = select(Observation).where(Observation.id == observation_id)
    result = await session.execute(stmt)
    observation = result.scalar_one_or_none()
    
    if not observation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Observation {observation_id} not found"
        )
    
    return observation
