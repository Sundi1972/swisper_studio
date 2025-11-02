"""Trace ingestion API endpoints"""

import math
from datetime import datetime
from typing import Any
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select, func

from app.api.deps import APIKey, DBSession
from app.models import Trace, Project, Observation
from app.api.services.observation_tree_service import build_observation_tree, ObservationTreeNode
from app.api.services.graph_builder_service import graph_builder_service
from app.models.graph import GraphData
import uuid


router = APIRouter()


class TraceCreate(BaseModel):
    """Request model for creating a trace"""
    
    id: str = Field(..., description="Unique trace identifier (UUID)")
    name: str | None = Field(None, description="Human-readable trace name")
    user_id: str | None = Field(None, description="User who initiated the trace")
    session_id: str | None = Field(None, description="Session identifier")
    project_id: str = Field(..., description="Project identifier")
    input: dict[str, Any] | None = Field(None, description="Input data")
    output: dict[str, Any] | None = Field(None, description="Output data")
    meta: dict[str, Any] | None = Field(None, description="Additional metadata")
    tags: list[str] = Field(default_factory=list, description="Tags")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Trace timestamp")


class TraceResponse(BaseModel):
    """Response model for trace"""
    
    id: str
    project_id: str
    name: str | None
    user_id: str | None
    session_id: str | None
    timestamp: datetime
    
    model_config = {"from_attributes": True}


@router.post("/traces", response_model=TraceResponse, status_code=status.HTTP_201_CREATED)
async def create_trace(
    trace_data: TraceCreate,
    session: DBSession,
    api_key: APIKey,
) -> Trace:
    """
    Create a new trace.
    
    Accepts trace data from the Swisper SDK and stores it in the database.
    Validates that the project exists before creating the trace.
    """
    # Validate project exists
    project_stmt = select(Project).where(
        Project.id == trace_data.project_id,
        Project.deleted_at.is_(None)
    )
    project = await session.scalar(project_stmt)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {trace_data.project_id} not found"
        )
    
    # Check if trace already exists (idempotency - Langfuse pattern)
    stmt = select(Trace).where(Trace.id == trace_data.id)
    result = await session.execute(stmt)
    existing_trace = result.scalar_one_or_none()
    
    if existing_trace:
        # Return existing with 200 OK (idempotent)
        return existing_trace
    
    # Create new trace
    trace = Trace(**trace_data.model_dump())
    
    session.add(trace)
    await session.commit()
    await session.refresh(trace)
    
    return trace


@router.get("/traces", response_model=dict[str, Any])
async def list_traces(
    project_id: str = Query(..., description="Project ID to filter traces"),
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=50, ge=1, le=1000, description="Items per page"),
    # Phase 2: Enhanced filters
    user_id: str | None = Query(None, description="Filter by user ID"),
    session_id: str | None = Query(None, description="Filter by session ID"),
    start_date: datetime | None = Query(None, description="Filter traces after this date"),
    end_date: datetime | None = Query(None, description="Filter traces before this date"),
    name: str | None = Query(None, description="Filter by trace name (partial match)"),
    # Filter by tags
    tags: list[str] | None = Query(None, description="Filter by tags (any match)"),
    # Dependencies
    session: DBSession = None,
    api_key: APIKey = None,
) -> dict[str, Any]:
    """
    List traces for a project with pagination and filtering (Phase 2 enhanced).
    
    Filters:
    - user_id: Exact match
    - session_id: Exact match
    - start_date/end_date: Date range (inclusive)
    - name: Partial match (case-insensitive)
    - tags: Any tag matches (OR logic)
    
    Following Langfuse pagination pattern.
    """
    # Build query with filters
    base_stmt = select(Trace).where(Trace.project_id == project_id)
    
    # Apply filters
    if user_id:
        base_stmt = base_stmt.where(Trace.user_id == user_id)
    
    if session_id:
        base_stmt = base_stmt.where(Trace.session_id == session_id)
    
    if start_date:
        base_stmt = base_stmt.where(Trace.timestamp >= start_date)
    
    if end_date:
        base_stmt = base_stmt.where(Trace.timestamp <= end_date)
    
    if name:
        base_stmt = base_stmt.where(Trace.name.ilike(f"%{name}%"))
    
    if tags:
        # Filter for traces that have ANY of the specified tags
        # PostgreSQL: tags @> ANY(ARRAY[...])
        from sqlalchemy import any_, cast, ARRAY, String
        base_stmt = base_stmt.where(Trace.tags.op("&&")(cast(tags, ARRAY(String))))
    
    # Count total with filters applied
    count_stmt = select(func.count()).select_from(base_stmt.subquery())
    total = await session.scalar(count_stmt) or 0
    
    # Paginate and order by newest first
    offset = (page - 1) * limit
    stmt = base_stmt.offset(offset).limit(limit).order_by(Trace.timestamp.desc())
    
    result = await session.execute(stmt)
    traces = result.scalars().all()
    
    return {
        "data": traces,
        "meta": {
            "page": page,
            "limit": limit,
            "total_items": total,
            "total_pages": math.ceil(total / limit) if total > 0 else 0,
        }
    }


@router.get("/traces/{trace_id}", response_model=TraceResponse)
async def get_trace(
    trace_id: str,
    session: DBSession,
    api_key: APIKey,
) -> Trace:
    """Get a trace by ID"""
    stmt = select(Trace).where(Trace.id == trace_id)
    result = await session.execute(stmt)
    trace = result.scalar_one_or_none()
    
    if not trace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trace {trace_id} not found"
        )
    
    return trace


@router.get("/traces/{trace_id}/tree", response_model=list[ObservationTreeNode])
async def get_trace_tree(
    trace_id: str,
    session: DBSession,
    api_key: APIKey,
) -> list[ObservationTreeNode]:
    """
    Get observation tree for a trace.
    
    Phase 2 feature: Returns nested observation structure with aggregated metrics.
    Used by frontend to display trace execution flow with costs and timing.
    
    Returns:
        List of root observation nodes with nested children.
        Each node includes:
        - All observation fields
        - Calculated latency
        - Aggregated cost (this node + all children)
        - Aggregated duration (sum of all durations in subtree)
    """
    # Verify trace exists
    trace_stmt = select(Trace).where(Trace.id == trace_id)
    trace_result = await session.execute(trace_stmt)
    trace = trace_result.scalar_one_or_none()
    
    if not trace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trace {trace_id} not found"
        )
    
    # Build tree
    tree = await build_observation_tree(session, trace_id)
    
    return tree


@router.get("/traces/{trace_id}/graph", response_model=GraphData)
async def get_trace_graph(
    trace_id: str,
    session: DBSession,
    api_key: APIKey
) -> GraphData:
    """
    Get graph structure for trace visualization.
    
    Converts the observation tree into a graph format suitable for
    visualization libraries like vis-network.
    
    Returns:
        GraphData with nodes (observations) and edges (parent-child relationships)
    """
    # Trace.id is VARCHAR, so we use the string directly
    trace_id_str = trace_id
    
    # Verify trace exists
    trace_stmt = select(Trace).where(Trace.id == trace_id_str)
    trace_result = await session.execute(trace_stmt)
    trace = trace_result.scalar_one_or_none()
    
    if not trace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trace {trace_id} not found"
        )
    
    # Fetch all observations for this trace (Observation.trace_id is also VARCHAR)
    obs_stmt = select(Observation).where(Observation.trace_id == trace_id_str)
    obs_result = await session.execute(obs_stmt)
    observations = obs_result.scalars().all()
    
    # Build graph using service
    graph = graph_builder_service.build_trace_graph(list(observations))
    
    return graph
