"""Trace model - Top-level execution trace"""

from datetime import datetime
from typing import Any
from sqlalchemy import Column, JSON, Index, ForeignKey
from sqlmodel import Field, SQLModel


class Trace(SQLModel, table=True):
    """
    Main trace record representing a complete execution flow.
    
    A trace is the top-level container for all observations (spans, generations, events).
    Typically represents a single user request or agent execution.
    """
    
    __tablename__ = "traces"
    
    # Primary key
    id: str = Field(primary_key=True, description="Unique trace identifier (UUID)")
    
    # Project relationship
    project_id: str = Field(
        sa_column=Column(ForeignKey("projects.id", ondelete="CASCADE"), index=True),
        description="Project this trace belongs to"
    )
    
    # Trace metadata
    name: str | None = Field(default=None, description="Human-readable trace name")
    user_id: str | None = Field(default=None, index=True, description="User who initiated the trace")
    session_id: str | None = Field(default=None, index=True, description="Session identifier")
    
    # Input/Output
    input: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="Input data for the trace"
    )
    output: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="Output data from the trace"
    )
    
    # Metadata (using 'meta' to avoid SQLAlchemy reserved keyword)
    meta: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="Additional metadata"
    )
    tags: list[str] = Field(
        default=[],
        sa_column=Column(JSON),
        description="Tags for categorization"
    )
    
    # Timestamps
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="When the trace was created"
    )
    
    __table_args__ = (
        Index("ix_traces_project_timestamp", "project_id", "timestamp"),
        Index("ix_traces_user_timestamp", "user_id", "timestamp"),
        Index("ix_traces_session_timestamp", "session_id", "timestamp"),
    )
