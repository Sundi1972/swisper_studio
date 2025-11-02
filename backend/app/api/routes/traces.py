"""Trace ingestion API endpoints"""

import math
from datetime import datetime
from typing import Any
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select, func

from app.api.deps import APIKey, DBSession
from app.models import Trace, Project


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
    session: DBSession = None,
    api_key: APIKey = None,
) -> dict[str, Any]:
    """
    List traces for a project with pagination.
    
    Following Langfuse pagination pattern.
    """
    # Build query
    base_stmt = select(Trace).where(Trace.project_id == project_id)
    
    # Count total
    count_stmt = select(func.count()).select_from(Trace).where(
        Trace.project_id == project_id
    )
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
