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
    completion_start_time: datetime | None = Field(
        default=None,
        description="When LLM started generating completion (for TTFT calculation)"
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
    model: str | None = Field(default=None, description="LLM model name (e.g., 'gpt-4-turbo')")
    model_parameters: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="LLM parameters (temperature, max_tokens, etc.)"
    )
    
    # Token tracking
    prompt_tokens: int | None = Field(default=None, description="Number of prompt/input tokens")
    completion_tokens: int | None = Field(default=None, description="Number of completion/output tokens")
    total_tokens: int | None = Field(default=None, description="Total tokens (input + output)")
    
    # Cost tracking (calculated during ingestion)
    calculated_input_cost: Decimal | None = Field(
        default=None,
        description="Calculated cost for input tokens (USD)"
    )
    calculated_output_cost: Decimal | None = Field(
        default=None,
        description="Calculated cost for output tokens (USD)"
    )
    calculated_total_cost: Decimal | None = Field(
        default=None,
        description="Total calculated cost (USD)"
    )
    
    # DEPRECATED: Use calculated_total_cost instead
    total_cost: Decimal | None = Field(default=None, description="DEPRECATED: Use calculated_total_cost")
    
    # Status
    level: str = Field(default="DEFAULT", description="Log level: DEFAULT, WARNING, ERROR")
    status_message: str | None = Field(default=None, description="Status or error message")
    
    __table_args__ = (
        Index("ix_observations_trace_start_time", "trace_id", "start_time"),
        Index("ix_observations_type_start_time", "type", "start_time"),
        Index("ix_observations_parent_id", "parent_observation_id"),
        Index("ix_observations_model", "model"),
        Index("ix_observations_level", "level"),
        Index("ix_observations_total_cost", "calculated_total_cost"),
    )
