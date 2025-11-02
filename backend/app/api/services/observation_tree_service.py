"""
Observation tree building service.

Converts flat observations into a nested tree structure for display.
Calculates aggregated metrics (total cost, total duration) for the tree.

Reference: Langfuse ObservationTree patterns
"""

import logging
from typing import Any
from decimal import Decimal
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Observation, Trace

logger = logging.getLogger(__name__)


class ObservationTreeNode(BaseModel):
    """
    A node in the observation tree.
    
    Represents one observation with its nested children.
    """
    
    # Observation data
    id: str
    trace_id: str
    parent_observation_id: str | None
    type: str
    name: str | None
    
    # Timing
    start_time: str  # ISO format
    end_time: str | None
    completion_start_time: str | None
    latency_ms: float | None  # Calculated: (end_time - start_time) in milliseconds
    
    # LLM Details
    model: str | None
    model_parameters: dict[str, Any] | None
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    
    # Costs
    calculated_input_cost: Decimal | None
    calculated_output_cost: Decimal | None
    calculated_total_cost: Decimal | None
    
    # Content
    input: dict[str, Any] | None
    output: dict[str, Any] | None
    meta: dict[str, Any] | None
    
    # Status
    level: str
    status_message: str | None
    
    # Tree structure
    children: list["ObservationTreeNode"] = []
    
    # Aggregated metrics (calculated from this node + all children)
    total_cost: Decimal | None = None  # Sum of all costs in subtree
    total_duration_ms: float | None = None  # Sum of all durations in subtree
    
    model_config = {"from_attributes": True}


async def build_observation_tree(
    session: AsyncSession,
    trace_id: str
) -> list[ObservationTreeNode]:
    """
    Build observation tree for a trace.
    
    Fetches all observations for the trace and organizes them into a nested tree structure.
    Root observations (parent_observation_id = NULL) are returned as top-level nodes.
    
    Args:
        session: Database session
        trace_id: Trace identifier
    
    Returns:
        List of root observation nodes with nested children
        
    Example:
        >>> tree = await build_observation_tree(session, "trace-123")
        >>> # tree = [
        >>> #   ObservationTreeNode(
        >>> #     id="obs-1",
        >>> #     name="agent",
        >>> #     children=[
        >>> #       ObservationTreeNode(id="obs-2", name="llm_call", children=[]),
        >>> #       ObservationTreeNode(id="obs-3", name="tool_call", children=[])
        >>> #     ]
        >>> #   )
        >>> # ]
    """
    # Fetch all observations for this trace
    stmt = select(Observation).where(
        Observation.trace_id == trace_id
    ).order_by(Observation.start_time)
    
    result = await session.execute(stmt)
    observations = result.scalars().all()
    
    # Build lookup maps
    obs_by_id: dict[str, Observation] = {obs.id: obs for obs in observations}
    children_by_parent: dict[str | None, list[Observation]] = {}
    
    for obs in observations:
        parent_id = obs.parent_observation_id
        if parent_id not in children_by_parent:
            children_by_parent[parent_id] = []
        children_by_parent[parent_id].append(obs)
    
    # Build tree recursively
    def build_node(obs: Observation) -> ObservationTreeNode:
        """Build tree node with all children."""
        
        # Calculate latency
        latency_ms = None
        if obs.end_time and obs.start_time:
            latency_seconds = (obs.end_time - obs.start_time).total_seconds()
            latency_ms = latency_seconds * 1000
        
        # Build node
        node = ObservationTreeNode(
            id=obs.id,
            trace_id=obs.trace_id,
            parent_observation_id=obs.parent_observation_id,
            type=obs.type.value,
            name=obs.name,
            start_time=obs.start_time.isoformat(),
            end_time=obs.end_time.isoformat() if obs.end_time else None,
            completion_start_time=obs.completion_start_time.isoformat() if obs.completion_start_time else None,
            latency_ms=latency_ms,
            model=obs.model,
            model_parameters=obs.model_parameters,
            prompt_tokens=obs.prompt_tokens,
            completion_tokens=obs.completion_tokens,
            total_tokens=obs.total_tokens,
            calculated_input_cost=obs.calculated_input_cost,
            calculated_output_cost=obs.calculated_output_cost,
            calculated_total_cost=obs.calculated_total_cost,
            input=obs.input,
            output=obs.output,
            meta=obs.meta,
            level=obs.level,
            status_message=obs.status_message,
            children=[]
        )
        
        # Add children recursively
        if obs.id in children_by_parent:
            for child_obs in children_by_parent[obs.id]:
                child_node = build_node(child_obs)
                node.children.append(child_node)
        
        # Calculate aggregated metrics
        node.total_cost = calculate_total_cost(node)
        node.total_duration_ms = calculate_total_duration(node)
        
        return node
    
    # Build root nodes (observations with no parent)
    root_observations = children_by_parent.get(None, [])
    tree = [build_node(obs) for obs in root_observations]
    
    return tree


def calculate_total_cost(node: ObservationTreeNode) -> Decimal | None:
    """
    Calculate total cost for a node and all its children.
    
    Args:
        node: Tree node to calculate for
    
    Returns:
        Total cost (sum of this node + all descendants), or None if no costs
    """
    total = Decimal("0")
    has_cost = False
    
    # Add this node's cost
    if node.calculated_total_cost is not None:
        total += node.calculated_total_cost
        has_cost = True
    
    # Add children's costs
    for child in node.children:
        child_cost = calculate_total_cost(child)
        if child_cost is not None:
            total += child_cost
            has_cost = True
    
    return total if has_cost else None


def calculate_total_duration(node: ObservationTreeNode) -> float | None:
    """
    Calculate total duration for a node and all its children.
    
    Note: This is sum of durations, not end-to-end duration.
    For end-to-end, use root node's latency_ms.
    
    Args:
        node: Tree node to calculate for
    
    Returns:
        Total duration in milliseconds, or None if no durations
    """
    total = 0.0
    has_duration = False
    
    # Add this node's duration
    if node.latency_ms is not None:
        total += node.latency_ms
        has_duration = True
    
    # Add children's durations
    for child in node.children:
        child_duration = calculate_total_duration(child)
        if child_duration is not None:
            total += child_duration
            has_duration = True
    
    return total if has_duration else None

