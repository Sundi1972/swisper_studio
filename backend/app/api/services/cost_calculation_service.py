"""
Cost calculation service for LLM observations.

Calculates costs based on token usage and model pricing configuration.
Supports project-specific pricing with fallback to default pricing.

Reference: ADR-008 - Phase 2 Architecture (Observation-Level Cost Calculation)
"""

import logging
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models import ModelPricing

logger = logging.getLogger(__name__)


class CostResult(BaseModel):
    """Result of cost calculation."""
    
    input_cost: Decimal
    output_cost: Decimal
    total_cost: Decimal
    pricing_source: str  # "project" or "default" or "unknown"


def extract_provider_from_model(model: str) -> str:
    """
    Extract hosting provider from model name.
    
    Common patterns:
    - *azure* → azure (check first - takes precedence)
    - gpt-* → openai
    - claude-* → anthropic
    
    Args:
        model: Model name (e.g., "gpt-4-turbo", "claude-3-opus", "azure-gpt-4")
    
    Returns:
        Provider name (e.g., "openai", "anthropic", "azure", "unknown")
    """
    model_lower = model.lower()
    
    # Check azure first (before checking for gpt- prefix)
    if "azure" in model_lower:
        return "azure"
    elif model_lower.startswith("gpt-") or model_lower.startswith("text-") or model_lower.startswith("davinci"):
        return "openai"
    elif model_lower.startswith("claude-"):
        return "anthropic"
    elif "together" in model_lower:
        return "together"
    else:
        logger.warning(f"Unknown provider for model: {model}")
        return "unknown"


async def calculate_llm_cost(
    session: AsyncSession,
    project_id: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> Optional[CostResult]:
    """
    Calculate LLM costs based on token usage and model pricing.
    
    Pricing lookup priority:
    1. Project-specific pricing (project_id matches)
    2. Default pricing (project_id is NULL)
    3. If not found, return None
    
    Args:
        session: Database session
        project_id: Project identifier
        model: Model name (e.g., "gpt-4-turbo")
        prompt_tokens: Number of input/prompt tokens
        completion_tokens: Number of output/completion tokens
    
    Returns:
        CostResult with calculated costs, or None if pricing not found
        
    Note:
        Costs are in USD. Prices are stored as USD per 1 million tokens.
        
    Example:
        >>> cost = await calculate_llm_cost(
        ...     session,
        ...     project_id="proj-123",
        ...     model="gpt-4-turbo",
        ...     prompt_tokens=150,
        ...     completion_tokens=50
        ... )
        >>> cost.total_cost
        Decimal('0.0030')  # $0.003
    """
    # Validate inputs
    if prompt_tokens < 0 or completion_tokens < 0:
        raise ValueError(f"Token counts must be non-negative: prompt={prompt_tokens}, completion={completion_tokens}")
    
    # Extract provider from model name
    hosting_provider = extract_provider_from_model(model)
    
    # Try project-specific pricing first
    project_pricing_stmt = select(ModelPricing).where(
        ModelPricing.project_id == project_id,
        ModelPricing.hosting_provider == hosting_provider,
        ModelPricing.model_name == model
    )
    result = await session.execute(project_pricing_stmt)
    pricing = result.scalar_one_or_none()
    
    if pricing:
        pricing_source = "project"
    else:
        # Fall back to default pricing (project_id is NULL)
        default_pricing_stmt = select(ModelPricing).where(
            ModelPricing.project_id.is_(None),
            ModelPricing.hosting_provider == hosting_provider,
            ModelPricing.model_name == model
        )
        result = await session.execute(default_pricing_stmt)
        pricing = result.scalar_one_or_none()
        
        if pricing:
            pricing_source = "default"
        else:
            # No pricing found
            logger.warning(
                f"No pricing found for model",
                extra={
                    "project_id": project_id,
                    "hosting_provider": hosting_provider,
                    "model": model
                }
            )
            return None
    
    # Calculate costs
    # Formula: (tokens / 1,000,000) * price_per_million
    input_cost = (Decimal(prompt_tokens) / Decimal("1000000")) * pricing.input_price_per_million
    output_cost = (Decimal(completion_tokens) / Decimal("1000000")) * pricing.output_price_per_million
    total_cost = input_cost + output_cost
    
    return CostResult(
        input_cost=input_cost.quantize(Decimal("0.000001")),  # Round to 6 decimal places
        output_cost=output_cost.quantize(Decimal("0.000001")),
        total_cost=total_cost.quantize(Decimal("0.000001")),
        pricing_source=pricing_source
    )

