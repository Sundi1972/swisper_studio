"""Tests for database models"""

from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Observation, ObservationType, Trace


@pytest.mark.asyncio
async def test_create_trace(session: AsyncSession) -> None:
    """
    Business case: Create a trace record
    Expected: Trace should be created with all fields
    """
    trace_id = str(uuid4())
    
    trace = Trace(
        id=trace_id,
        name="test_trace",
        user_id="user_123",
        session_id="session_456",
        project_id="project_789",
        metadata={"key": "value"},
        tags=["test", "demo"],
        input={"prompt": "Hello"},
        output={"response": "Hi there"},
        timestamp=datetime.utcnow(),
    )
    
    session.add(trace)
    await session.commit()
    await session.refresh(trace)
    
    assert trace.id == trace_id
    assert trace.name == "test_trace"
    assert trace.user_id == "user_123"
    assert trace.project_id == "project_789"
    assert trace.metadata == {"key": "value"}
    assert trace.tags == ["test", "demo"]


@pytest.mark.asyncio
async def test_create_observation(session: AsyncSession) -> None:
    """
    Business case: Create an observation within a trace
    Expected: Observation should be created with parent trace
    """
    # Create trace first
    trace_id = str(uuid4())
    trace = Trace(
        id=trace_id,
        name="test_trace",
        project_id="project_123",
        timestamp=datetime.utcnow(),
    )
    session.add(trace)
    await session.commit()
    
    # Create observation
    obs_id = str(uuid4())
    observation = Observation(
        id=obs_id,
        trace_id=trace_id,
        type=ObservationType.SPAN,
        name="test_span",
        start_time=datetime.utcnow(),
        input={"data": "input"},
        metadata={"info": "test"},
    )
    
    session.add(observation)
    await session.commit()
    await session.refresh(observation)
    
    assert observation.id == obs_id
    assert observation.trace_id == trace_id
    assert observation.type == ObservationType.SPAN
    assert observation.name == "test_span"


@pytest.mark.asyncio
async def test_nested_observations(session: AsyncSession) -> None:
    """
    Business case: Create nested observations (parent-child hierarchy)
    Expected: Child observation should reference parent observation
    """
    # Create trace
    trace_id = str(uuid4())
    trace = Trace(
        id=trace_id,
        name="nested_trace",
        project_id="project_123",
        timestamp=datetime.utcnow(),
    )
    session.add(trace)
    
    # Create parent observation
    parent_id = str(uuid4())
    parent_obs = Observation(
        id=parent_id,
        trace_id=trace_id,
        type=ObservationType.AGENT,
        name="parent_agent",
        start_time=datetime.utcnow(),
    )
    session.add(parent_obs)
    
    # Create child observation
    child_id = str(uuid4())
    child_obs = Observation(
        id=child_id,
        trace_id=trace_id,
        parent_observation_id=parent_id,
        type=ObservationType.GENERATION,
        name="child_generation",
        start_time=datetime.utcnow(),
        model="gpt-4",
        prompt_tokens=100,
        completion_tokens=50,
    )
    session.add(child_obs)
    
    await session.commit()
    await session.refresh(child_obs)
    
    assert child_obs.parent_observation_id == parent_id
    assert child_obs.type == ObservationType.GENERATION
    assert child_obs.model == "gpt-4"


@pytest.mark.asyncio
async def test_trace_without_optional_fields(session: AsyncSession) -> None:
    """
    Edge case: Create trace with only required fields
    Expected: Trace should be created with None for optional fields
    """
    trace_id = str(uuid4())
    
    trace = Trace(
        id=trace_id,
        project_id="project_123",
        timestamp=datetime.utcnow(),
    )
    
    session.add(trace)
    await session.commit()
    await session.refresh(trace)
    
    assert trace.id == trace_id
    assert trace.name is None
    assert trace.user_id is None
    assert trace.metadata is None

