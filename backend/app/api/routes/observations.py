"""Observation ingestion API endpoints"""

from datetime import datetime
from decimal import Decimal
from typing import Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.api.deps import APIKey, DBSession
from app.models import Observation, ObservationType, Trace
from app.api.services.cost_calculation_service import calculate_llm_cost, extract_provider_from_model


router = APIRouter()


class ObservationCreate(BaseModel):
    """Request model for creating an observation (Phase 2 enhanced)"""
    
    id: str = Field(..., description="Unique observation identifier (UUID)")
    trace_id: str = Field(..., description="Parent trace ID")
    parent_observation_id: str | None = Field(None, description="Parent observation ID")
    type: ObservationType = Field(..., description="Observation type")
    name: str | None = Field(None, description="Human-readable observation name")
    
    # Timing
    start_time: datetime = Field(default_factory=datetime.utcnow, description="Start time")
    end_time: datetime | None = Field(None, description="End time")
    completion_start_time: datetime | None = Field(None, description="When LLM started generating (for TTFT)")
    
    # Content
    input: dict[str, Any] | None = Field(None, description="Input data/state snapshot")
    output: dict[str, Any] | None = Field(None, description="Output data/state snapshot")
    meta: dict[str, Any] | None = Field(None, description="Additional metadata")
    
    # LLM Details
    model: str | None = Field(None, description="LLM model name (e.g., 'gpt-4-turbo')")
    model_parameters: dict[str, Any] | None = Field(None, description="LLM parameters (temperature, max_tokens, etc.)")
    
    # Token counts (for cost calculation)
    prompt_tokens: int | None = Field(None, description="Number of input/prompt tokens")
    completion_tokens: int | None = Field(None, description="Number of output/completion tokens")
    total_tokens: int | None = Field(None, description="Total tokens")
    
    # Status
    level: str = Field(default="DEFAULT", description="Log level: DEBUG, DEFAULT, WARNING, ERROR")
    status_message: str | None = Field(None, description="Status or error message")


class ObservationUpdate(BaseModel):
    """Request model for updating an observation (Phase 2 enhanced)"""
    
    # Timing
    end_time: datetime | None = Field(None, description="End time")
    completion_start_time: datetime | None = Field(None, description="When LLM started generating")
    
    # Content
    output: dict[str, Any] | None = Field(None, description="Output data/state snapshot")
    
    # LLM Details
    model: str | None = Field(None, description="LLM model name")
    model_parameters: dict[str, Any] | None = Field(None, description="LLM parameters")
    
    # Token counts
    prompt_tokens: int | None = Field(None, description="Prompt tokens")
    completion_tokens: int | None = Field(None, description="Completion tokens")
    total_tokens: int | None = Field(None, description="Total tokens")
    
    # Status
    level: str | None = Field(None, description="Log level")
    status_message: str | None = Field(None, description="Status or error message")


class ObservationResponse(BaseModel):
    """Response model for observation (Phase 2 enhanced)"""
    
    id: str
    trace_id: str
    parent_observation_id: str | None
    type: ObservationType
    name: str | None
    
    # Timing
    start_time: datetime
    end_time: datetime | None
    completion_start_time: datetime | None
    
    # LLM Details
    model: str | None
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    
    # Calculated costs
    calculated_input_cost: Decimal | None
    calculated_output_cost: Decimal | None
    calculated_total_cost: Decimal | None
    
    # Status
    level: str
    status_message: str | None
    
    model_config = {"from_attributes": True}


@router.post("/observations", response_model=ObservationResponse, status_code=status.HTTP_201_CREATED)
async def create_observation(
    observation_data: ObservationCreate,
    session: DBSession,
    api_key: APIKey,
) -> Observation:
    """
    Create a new observation with automatic cost calculation.
    
    Phase 2 enhancement:
    - Automatically calculates costs if LLM telemetry provided (model + tokens)
    - Uses project-specific pricing or default pricing
    - Stores calculated costs in observation for efficient querying
    """
    # Check if observation already exists (idempotency)
    stmt = select(Observation).where(Observation.id == observation_data.id)
    result = await session.execute(stmt)
    existing_observation = result.scalar_one_or_none()
    
    if existing_observation:
        return existing_observation
    
    # Create new observation
    observation = Observation(**observation_data.model_dump())
    
    # Calculate costs if LLM telemetry provided
    if observation.model and observation.prompt_tokens is not None and observation.completion_tokens is not None:
        # Get project_id from trace (optimized: could join, but keeping simple for clarity)
        trace_stmt = select(Trace.project_id).where(Trace.id == observation.trace_id)
        trace_result = await session.execute(trace_stmt)
        project_id = trace_result.scalar_one_or_none()
        
        if project_id:
            # Calculate cost
            cost_result = await calculate_llm_cost(
                session=session,
                project_id=project_id,
                model=observation.model,
                prompt_tokens=observation.prompt_tokens,
                completion_tokens=observation.completion_tokens
            )
            
            if cost_result:
                observation.calculated_input_cost = cost_result.input_cost
                observation.calculated_output_cost = cost_result.output_cost
                observation.calculated_total_cost = cost_result.total_cost
    
    # Calculate total_tokens if not provided
    if observation.total_tokens is None and observation.prompt_tokens is not None and observation.completion_tokens is not None:
        observation.total_tokens = observation.prompt_tokens + observation.completion_tokens
    
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
    Update an observation with automatic cost recalculation.
    
    Phase 2 enhancement:
    - Recalculates costs if tokens/model change
    - Updates state snapshots (input/output)
    - Used by SDK when observation completes
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
    
    # Recalculate costs if LLM telemetry provided/updated
    if observation.model and observation.prompt_tokens is not None and observation.completion_tokens is not None:
        # Get project_id from trace (optimized: select only project_id)
        trace_stmt = select(Trace.project_id).where(Trace.id == observation.trace_id)
        trace_result = await session.execute(trace_stmt)
        project_id = trace_result.scalar_one_or_none()
        
        if project_id:
            # Recalculate cost
            cost_result = await calculate_llm_cost(
                session=session,
                project_id=project_id,
                model=observation.model,
                prompt_tokens=observation.prompt_tokens,
                completion_tokens=observation.completion_tokens
            )
            
            if cost_result:
                observation.calculated_input_cost = cost_result.input_cost
                observation.calculated_output_cost = cost_result.output_cost
                observation.calculated_total_cost = cost_result.total_cost
    
    # Calculate total_tokens if not provided
    if observation.total_tokens is None and observation.prompt_tokens is not None and observation.completion_tokens is not None:
        observation.total_tokens = observation.prompt_tokens + observation.completion_tokens
    
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
