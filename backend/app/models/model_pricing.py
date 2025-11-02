"""
ModelPricing model - Stores LLM pricing configuration per project

Pricing is configured at project level with hosting provider and model granularity.
This allows different projects to have different pricing (enterprise agreements, regions, etc.)
and handles the fact that Swisper configures models per-node (each observation can use a different model).

Reference: ADR-008 - Phase 2 Architecture
"""

import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, ForeignKey, UniqueConstraint, Index
from sqlmodel import Field, SQLModel


class ModelPricing(SQLModel, table=True):
    """
    LLM model pricing configuration.
    
    Stores pricing per (project, hosting_provider, model_name) combination.
    
    Examples:
    - (project_id=123, provider="openai", model="gpt-4-turbo", input=$10/1M, output=$30/1M)
    - (project_id=123, provider="azure", model="gpt-4-turbo", input=$12/1M, output=$35/1M)
    - (project_id=NULL, provider="openai", model="gpt-4", input=$30/1M, output=$60/1M) # Default
    
    Pricing lookup priority:
    1. Project-specific pricing (project_id matches)
    2. Default pricing (project_id is NULL)
    3. If not found, log warning and skip cost calculation
    
    Note: Swisper allows per-node model configuration, so each observation in a trace
    can use a different model. Cost calculation happens per observation.
    """
    
    __tablename__ = "model_pricing"
    
    # Primary key
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique pricing entry identifier (UUID)"
    )
    
    # Project relationship (nullable for default pricing)
    project_id: str | None = Field(
        default=None,
        sa_column=Column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=True),
        description="Project ID (NULL for default pricing applicable to all projects)"
    )
    
    # Model identification
    hosting_provider: str = Field(
        ...,
        max_length=100,
        description="Hosting provider (e.g., 'openai', 'anthropic', 'azure', 'together')"
    )
    
    model_name: str = Field(
        ...,
        max_length=200,
        description="Model name (e.g., 'gpt-4-turbo', 'claude-3-opus')"
    )
    
    # Pricing (USD per 1 million tokens)
    input_price_per_million: Decimal = Field(
        ...,
        ge=Decimal("0"),  # Non-negative validation
        description="Price per 1 million input/prompt tokens (USD)"
    )
    
    output_price_per_million: Decimal = Field(
        ...,
        ge=Decimal("0"),  # Non-negative validation
        description="Price per 1 million output/completion tokens (USD)"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this pricing was created"
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this pricing was last updated"
    )
    
    __table_args__ = (
        # Unique constraint: one pricing entry per (project, provider, model) combo
        UniqueConstraint(
            "project_id", 
            "hosting_provider", 
            "model_name",
            name="uq_model_pricing_project_provider_model"
        ),
        # Index for fast lookups during cost calculation
        Index(
            "ix_model_pricing_lookup",
            "project_id",
            "hosting_provider",
            "model_name"
        ),
        # Index for querying all pricing for a project
        Index("ix_model_pricing_project_id", "project_id"),
    )

