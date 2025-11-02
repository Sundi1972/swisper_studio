"""
Tests for cost calculation service.

Tests cover:
- Cost calculation for known models
- Project-specific vs default pricing
- Provider extraction from model names
- Edge cases (zero tokens, unknown models)
"""

import pytest
from decimal import Decimal
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.services.cost_calculation_service import (
    calculate_llm_cost,
    extract_provider_from_model,
    CostResult
)
from app.models import Project, ModelPricing


@pytest.mark.ci_critical
@pytest.mark.asyncio
async def test_calculate_cost_with_default_pricing(session: AsyncSession) -> None:
    """
    CI: Golden path - Calculate cost using default pricing.
    
    Business case: Project doesn't have custom pricing, use defaults from migration.
    Expected: Cost calculated using default pricing for gpt-4-turbo.
    """
    # Create a test project (but no custom pricing)
    project = Project(
        name="Test Project",
        swisper_url="http://localhost:8000",
        swisper_api_key="test-key"
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)
    
    # Calculate cost (should use default pricing seeded in migration)
    # Default: gpt-4-turbo = $10/1M input, $30/1M output
    cost = await calculate_llm_cost(
        session=session,
        project_id=project.id,
        model="gpt-4-turbo",
        prompt_tokens=150,
        completion_tokens=50
    )
    
    assert cost is not None
    assert cost.pricing_source == "default"
    
    # Verify calculations:
    # input_cost = (150 / 1,000,000) * 10 = 0.0015
    # output_cost = (50 / 1,000,000) * 30 = 0.0015
    # total = 0.0030
    assert cost.input_cost == Decimal("0.001500")
    assert cost.output_cost == Decimal("0.001500")
    assert cost.total_cost == Decimal("0.003000")


@pytest.mark.asyncio
async def test_calculate_cost_with_project_specific_pricing(session: AsyncSession) -> None:
    """
    Business case: Project has custom pricing (enterprise agreement).
    Expected: Use project-specific pricing, not defaults.
    """
    # Create project
    project = Project(
        name="Enterprise Project",
        swisper_url="http://localhost:8000",
        swisper_api_key="enterprise-key"
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)
    
    # Add custom pricing for this project
    custom_pricing = ModelPricing(
        id=str(uuid4()),
        project_id=project.id,
        hosting_provider="openai",
        model_name="gpt-4-turbo",
        input_price_per_million=Decimal("8.00"),  # Custom price (cheaper than default $10)
        output_price_per_million=Decimal("25.00")  # Custom price (cheaper than default $30)
    )
    session.add(custom_pricing)
    await session.commit()
    
    # Calculate cost
    cost = await calculate_llm_cost(
        session=session,
        project_id=project.id,
        model="gpt-4-turbo",
        prompt_tokens=1000,
        completion_tokens=500
    )
    
    assert cost is not None
    assert cost.pricing_source == "project"
    
    # Verify uses custom pricing:
    # input_cost = (1000 / 1,000,000) * 8 = 0.008
    # output_cost = (500 / 1,000,000) * 25 = 0.0125
    # total = 0.0205
    assert cost.input_cost == Decimal("0.008000")
    assert cost.output_cost == Decimal("0.012500")
    assert cost.total_cost == Decimal("0.020500")


@pytest.mark.asyncio
async def test_calculate_cost_unknown_model(session: AsyncSession) -> None:
    """
    Edge case: Model not in pricing table.
    Expected: Return None, log warning.
    """
    # Create project
    project = Project(
        name="Test Project Unknown",
        swisper_url="http://localhost:8000",
        swisper_api_key="test-unknown"
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)
    
    # Try to calculate cost for unknown model
    cost = await calculate_llm_cost(
        session=session,
        project_id=project.id,
        model="custom-fine-tuned-model",
        prompt_tokens=100,
        completion_tokens=50
    )
    
    # Should return None (no pricing available)
    assert cost is None


@pytest.mark.asyncio
async def test_calculate_cost_zero_tokens(session: AsyncSession) -> None:
    """
    Edge case: Zero tokens.
    Expected: Cost is $0.00.
    """
    # Create project
    project = Project(
        name="Zero Tokens Project",
        swisper_url="http://localhost:8000",
        swisper_api_key="zero-tokens-key"
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)
    
    # Calculate cost with zero tokens
    cost = await calculate_llm_cost(
        session=session,
        project_id=project.id,
        model="gpt-4-turbo",
        prompt_tokens=0,
        completion_tokens=0
    )
    
    assert cost is not None
    assert cost.input_cost == Decimal("0.000000")
    assert cost.output_cost == Decimal("0.000000")
    assert cost.total_cost == Decimal("0.000000")


@pytest.mark.asyncio
async def test_calculate_cost_negative_tokens_raises_error(session: AsyncSession) -> None:
    """
    Error case: Negative token counts should raise ValueError.
    Expected: ValueError raised.
    """
    # Create project
    project = Project(
        name="Negative Test Project",
        swisper_url="http://localhost:8000",
        swisper_api_key="negative-key"
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)
    
    # Try negative tokens
    with pytest.raises(ValueError, match="Token counts must be non-negative"):
        await calculate_llm_cost(
            session=session,
            project_id=project.id,
            model="gpt-4",
            prompt_tokens=-100,
            completion_tokens=50
        )


@pytest.mark.asyncio
async def test_calculate_cost_claude_model(session: AsyncSession) -> None:
    """
    Business case: Calculate cost for Anthropic Claude model.
    Expected: Correct provider extraction and cost calculation.
    """
    # Create project
    project = Project(
        name="Claude Project",
        swisper_url="http://localhost:8000",
        swisper_api_key="claude-key"
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)
    
    # Calculate cost for Claude (should use default pricing from migration)
    # Default: claude-3-sonnet = $3/1M input, $15/1M output
    cost = await calculate_llm_cost(
        session=session,
        project_id=project.id,
        model="claude-3-sonnet-20240229",
        prompt_tokens=1000,
        completion_tokens=200
    )
    
    assert cost is not None
    assert cost.pricing_source == "default"
    
    # Verify calculations:
    # input_cost = (1000 / 1,000,000) * 3 = 0.003
    # output_cost = (200 / 1,000,000) * 15 = 0.003
    # total = 0.006
    assert cost.input_cost == Decimal("0.003000")
    assert cost.output_cost == Decimal("0.003000")
    assert cost.total_cost == Decimal("0.006000")


class TestProviderExtraction:
    """Test provider extraction from model names."""
    
    def test_extract_openai_models(self):
        """Test OpenAI model name patterns."""
        assert extract_provider_from_model("gpt-4-turbo") == "openai"
        assert extract_provider_from_model("gpt-4") == "openai"
        assert extract_provider_from_model("gpt-3.5-turbo") == "openai"
        assert extract_provider_from_model("gpt-4o") == "openai"
        assert extract_provider_from_model("text-davinci-003") == "openai"
        
    def test_extract_anthropic_models(self):
        """Test Anthropic model name patterns."""
        assert extract_provider_from_model("claude-3-opus-20240229") == "anthropic"
        assert extract_provider_from_model("claude-3-sonnet-20240229") == "anthropic"
        assert extract_provider_from_model("claude-3-haiku-20240307") == "anthropic"
        assert extract_provider_from_model("claude-3-5-sonnet-20241022") == "anthropic"
        
    def test_extract_azure_models(self):
        """Test Azure OpenAI model name patterns."""
        assert extract_provider_from_model("azure-gpt-4-turbo") == "azure"
        assert extract_provider_from_model("gpt-4-azure") == "azure"
        
    def test_extract_unknown_model(self):
        """Test unknown model returns 'unknown'."""
        assert extract_provider_from_model("my-custom-model") == "unknown"
        assert extract_provider_from_model("llama-3-70b") == "unknown"

