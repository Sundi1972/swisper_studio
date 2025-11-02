"""Observation model - Individual execution steps within a trace"""

from datetime import datetime
from decimal import Decimal
from typing import Any
from sqlalchemy import Column, JSON, Index, ForeignKey
from sqlmodel import Field, SQLModel

from app.models.enums import ObservationType


class Observation(SQLModel, table=True):
    """
    Observation record representing a single step in a trace.
    
    Observations can be:
    - SPAN: Generic execution span (e.g., function call, node execution)
    - GENERATION: LLM generation with token counts and costs
    - EVENT: Point-in-time event (e.g., state change, error)
    - TOOL: Tool/function call
    - AGENT: Agent execution
    
    Observations can be nested (parent-child relationships).
    """
    
    __tablename__ = "observations"
    
    # Primary key
    id: str = Field(primary_key=True, description="Unique observation identifier (UUID)")
    
    # Relationships
    trace_id: str = Field(
        sa_column=Column(ForeignKey("traces.id", ondelete="CASCADE"), index=True),
        description="Parent trace ID"
    )
    parent_observation_id: str | None = Field(
        default=None,
        description="Parent observation ID for nested observations"
    )
    
    # Observation type and metadata
    type: ObservationType = Field(description="Type of observation")
    name: str | None = Field(default=None, description="Human-readable observation name")
    
    # Timing
    start_time: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the observation started"
    )
    end_time: datetime | None = Field(
        default=None,
        description="When the observation ended"
    )
    
    # Input/Output
    input: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="Input data for this observation"
    )
    output: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="Output data from this observation"
    )
    
    # Metadata (using 'meta' to avoid SQLAlchemy reserved keyword)
    meta: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="Additional metadata"
    )
    
    # LLM-specific fields (for GENERATION type)
    model: str | None = Field(default=None, description="LLM model name (if applicable)")
    prompt_tokens: int | None = Field(default=None, description="Number of prompt tokens")
    completion_tokens: int | None = Field(default=None, description="Number of completion tokens")
    total_cost: Decimal | None = Field(default=None, description="Total cost in USD")
    
    # Status
    level: str = Field(default="DEFAULT", description="Log level: DEFAULT, WARNING, ERROR")
    status_message: str | None = Field(default=None, description="Status or error message")
    
    __table_args__ = (
        Index("ix_observations_trace_start_time", "trace_id", "start_time"),
        Index("ix_observations_type_start_time", "type", "start_time"),
        Index("ix_observations_parent_id", "parent_observation_id"),
    )
