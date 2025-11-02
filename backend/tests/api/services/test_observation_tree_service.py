"""
Tests for observation tree building service.
"""

import pytest
from decimal import Decimal
from uuid import uuid4
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.services.observation_tree_service import build_observation_tree
from app.models import Project, Trace, Observation, ObservationType


@pytest.mark.ci_critical
@pytest.mark.asyncio
async def test_build_tree_with_nested_observations(session: AsyncSession) -> None:
    """
    CI: Golden path - Build tree from nested observations.
    
    Business case: Agent with nested LLM calls and tool calls.
    Expected: Tree structure with correct parent-child relationships.
    """
    # Create project and trace
    project = Project(
        name="Tree Test Project",
        swisper_url="http://localhost:8000",
        swisper_api_key="tree-key"
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)
    
    trace = Trace(
        id=str(uuid4()),
        name="test_trace",
        project_id=project.id,
        timestamp=datetime.utcnow()
    )
    session.add(trace)
    await session.commit()
    await session.refresh(trace)
    
    # Create nested observations
    # Root: agent
    #   ├─ Child 1: llm_call
    #   └─ Child 2: tool_call
    
    start = datetime.utcnow()
    
    root_obs = Observation(
        id=str(uuid4()),
        trace_id=trace.id,
        type=ObservationType.AGENT,
        name="agent",
        start_time=start,
        end_time=start + timedelta(seconds=5)
    )
    session.add(root_obs)
    await session.commit()
    await session.refresh(root_obs)
    
    child1_obs = Observation(
        id=str(uuid4()),
        trace_id=trace.id,
        parent_observation_id=root_obs.id,
        type=ObservationType.GENERATION,
        name="llm_call",
        start_time=start + timedelta(seconds=1),
        end_time=start + timedelta(seconds=3),
        model="gpt-4",
        prompt_tokens=100,
        completion_tokens=50,
        calculated_total_cost=Decimal("0.0050")
    )
    session.add(child1_obs)
    
    child2_obs = Observation(
        id=str(uuid4()),
        trace_id=trace.id,
        parent_observation_id=root_obs.id,
        type=ObservationType.TOOL,
        name="tool_call",
        start_time=start + timedelta(seconds=3),
        end_time=start + timedelta(seconds=4)
    )
    session.add(child2_obs)
    
    await session.commit()
    
    # Build tree
    tree = await build_observation_tree(session, trace.id)
    
    # Verify structure
    assert len(tree) == 1  # One root node
    
    root = tree[0]
    assert root.id == root_obs.id
    assert root.name == "agent"
    assert len(root.children) == 2
    
    # Verify children
    child_names = {child.name for child in root.children}
    assert "llm_call" in child_names
    assert "tool_call" in child_names
    
    # Verify aggregated cost (only child1 has cost)
    assert root.total_cost == Decimal("0.0050")


@pytest.mark.asyncio
async def test_build_tree_empty_trace(session: AsyncSession) -> None:
    """
    Edge case: Trace with no observations.
    Expected: Empty tree (empty list).
    """
    # Create project and trace
    project = Project(
        name="Empty Tree Project",
        swisper_url="http://localhost:8000",
        swisper_api_key="empty-tree-key"
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)
    
    trace = Trace(
        id=str(uuid4()),
        name="empty_trace",
        project_id=project.id,
        timestamp=datetime.utcnow()
    )
    session.add(trace)
    await session.commit()
    await session.refresh(trace)
    
    # Build tree
    tree = await build_observation_tree(session, trace.id)
    
    # Verify empty
    assert tree == []


@pytest.mark.asyncio
async def test_build_tree_multiple_roots(session: AsyncSession) -> None:
    """
    Business case: Trace with multiple root observations (parallel execution).
    Expected: Multiple root nodes in tree.
    """
    # Create project and trace
    project = Project(
        name="Multi Root Project",
        swisper_url="http://localhost:8000",
        swisper_api_key="multi-root-key"
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)
    
    trace = Trace(
        id=str(uuid4()),
        name="multi_root_trace",
        project_id=project.id,
        timestamp=datetime.utcnow()
    )
    session.add(trace)
    await session.commit()
    await session.refresh(trace)
    
    # Create two root observations (no parent)
    obs1 = Observation(
        id=str(uuid4()),
        trace_id=trace.id,
        type=ObservationType.SPAN,
        name="root_1",
        start_time=datetime.utcnow()
    )
    
    obs2 = Observation(
        id=str(uuid4()),
        trace_id=trace.id,
        type=ObservationType.SPAN,
        name="root_2",
        start_time=datetime.utcnow()
    )
    
    session.add(obs1)
    session.add(obs2)
    await session.commit()
    
    # Build tree
    tree = await build_observation_tree(session, trace.id)
    
    # Verify two roots
    assert len(tree) == 2
    names = {node.name for node in tree}
    assert "root_1" in names
    assert "root_2" in names


@pytest.mark.asyncio
async def test_build_tree_calculates_latency(session: AsyncSession) -> None:
    """
    Business case: Calculate latency for each observation.
    Expected: latency_ms = (end_time - start_time) in milliseconds.
    """
    # Create project and trace
    project = Project(
        name="Latency Test Project",
        swisper_url="http://localhost:8000",
        swisper_api_key="latency-key"
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)
    
    trace = Trace(
        id=str(uuid4()),
        name="latency_trace",
        project_id=project.id,
        timestamp=datetime.utcnow()
    )
    session.add(trace)
    await session.commit()
    await session.refresh(trace)
    
    # Create observation with known duration
    start = datetime.utcnow()
    end = start + timedelta(seconds=2.5)  # 2.5 seconds = 2500 ms
    
    obs = Observation(
        id=str(uuid4()),
        trace_id=trace.id,
        type=ObservationType.SPAN,
        name="timed_span",
        start_time=start,
        end_time=end
    )
    session.add(obs)
    await session.commit()
    
    # Build tree
    tree = await build_observation_tree(session, trace.id)
    
    # Verify latency calculated
    assert len(tree) == 1
    node = tree[0]
    assert node.latency_ms is not None
    assert node.latency_ms == pytest.approx(2500, abs=10)  # 2.5 seconds ± 10ms

