"""Tests for Phase 2 model extensions (Observation + ModelPricing)."""
import pytest
from decimal import Decimal
from datetime import datetime
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models import Observation, Trace, Project, ModelPricing


class TestObservationPhase2Fields:
    """Test Phase 2 extensions to Observation model."""
    
    @pytest.mark.asyncio
    async def test_create_observation_with_llm_telemetry(self, session: AsyncSession):
        """Test creating observation with LLM telemetry fields."""
        # Create project and trace first
        project = Project(
            name="Test Project",
            swisper_url="http://localhost:8000",
            swisper_api_key="test-key"
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
        
        # Create observation with Phase 2 fields
        observation = Observation(
            id=str(uuid4()),
            trace_id=trace.id,
            name="llm_call",
            type="GENERATION",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            completion_start_time=datetime.utcnow(),
            # Token fields
            prompt_tokens=150,
            completion_tokens=50,
            total_tokens=200,
            # Cost fields
            calculated_input_cost=Decimal("0.0015"),
            calculated_output_cost=Decimal("0.0015"),
            calculated_total_cost=Decimal("0.0030"),
            # LLM fields
            model="gpt-4-turbo",
            model_parameters={"temperature": 0.7, "max_tokens": 2000},
            # Content fields
            input={"messages": [{"role": "user", "content": "Hello"}]},
            output={"content": "Hi there!"},
            # Status fields
            level="DEFAULT",
            status_message=None
        )
        
        session.add(observation)
        await session.commit()
        await session.refresh(observation)
        
        # Verify all fields saved correctly
        assert observation.prompt_tokens == 150
        assert observation.completion_tokens == 50
        assert observation.total_tokens == 200
        assert observation.calculated_input_cost == Decimal("0.0015")
        assert observation.calculated_output_cost == Decimal("0.0015")
        assert observation.calculated_total_cost == Decimal("0.0030")
        assert observation.model == "gpt-4-turbo"
        assert observation.model_parameters["temperature"] == 0.7
        assert observation.input["messages"][0]["content"] == "Hello"
        assert observation.output["content"] == "Hi there!"
        assert observation.level == "DEFAULT"
    
    @pytest.mark.asyncio    
    async def test_create_observation_minimal_fields(self, session: AsyncSession):
        """Test backward compatibility - observation with only required fields."""
        # Create project and trace
        project = Project(
            name="Test Project 2",
            swisper_url="http://localhost:8000",
            swisper_api_key="test-key-2"
        )
        session.add(project)
        await session.commit()
        await session.refresh(project)
        
        trace = Trace(
            id=str(uuid4()),
            name="test_trace_2",
            project_id=project.id,
            timestamp=datetime.utcnow()
        )
        session.add(trace)
        await session.commit()
        await session.refresh(trace)
        
        observation = Observation(
            id=str(uuid4()),
            trace_id=trace.id,
            name="simple_span",
            type="SPAN",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow()
        )
        
        session.add(observation)
        await session.commit()
        await session.refresh(observation)
        
        # Verify optional Phase 2 fields are None
        assert observation.prompt_tokens is None
        assert observation.completion_tokens is None
        assert observation.calculated_total_cost is None
        assert observation.model is None
        assert observation.level == "DEFAULT"  # Default value
    
    @pytest.mark.asyncio
    async def test_create_observation_with_error_status(self, session: AsyncSession):
        """Test observation with ERROR level and status message."""
        # Create project and trace
        project = Project(
            name="Test Project 3",
            swisper_url="http://localhost:8000",
            swisper_api_key="test-key-3"
        )
        session.add(project)
        await session.commit()
        await session.refresh(project)
        
        trace = Trace(
            id=str(uuid4()),
            name="test_trace_3",
            project_id=project.id,
            timestamp=datetime.utcnow()
        )
        session.add(trace)
        await session.commit()
        await session.refresh(trace)
        
        observation = Observation(
            id=str(uuid4()),
            trace_id=trace.id,
            name="failed_call",
            type="GENERATION",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            level="ERROR",
            status_message="API rate limit exceeded"
        )
        
        session.add(observation)
        await session.commit()
        await session.refresh(observation)
        
        assert observation.level == "ERROR"
        assert observation.status_message == "API rate limit exceeded"


class TestModelPricing:
    """Test ModelPricing model."""
    
    @pytest.mark.asyncio
    async def test_create_project_specific_pricing(self, session: AsyncSession):
        """Test creating project-specific model pricing."""
        # Create test project
        project = Project(
            name="Pricing Test Project",
            swisper_url="http://localhost:8000",
            swisper_api_key="pricing-test-key"
        )
        session.add(project)
        await session.commit()
        await session.refresh(project)
        
        pricing = ModelPricing(
            id=str(uuid4()),
            project_id=project.id,
            hosting_provider="openai",
            model_name="gpt-4-turbo",
            input_price_per_million=Decimal("10.00"),
            output_price_per_million=Decimal("30.00")
        )
        
        session.add(pricing)
        await session.commit()
        await session.refresh(pricing)
        
        assert pricing.project_id == project.id
        assert pricing.hosting_provider == "openai"
        assert pricing.model_name == "gpt-4-turbo"
        assert pricing.input_price_per_million == Decimal("10.00")
        assert pricing.output_price_per_million == Decimal("30.00")
        assert pricing.created_at is not None
        assert pricing.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_create_default_pricing(self, session: AsyncSession):
        """Test creating default pricing (no project_id)."""
        pricing = ModelPricing(
            id=str(uuid4()),
            project_id=None,  # Default pricing
            hosting_provider="anthropic",
            model_name="claude-3-opus",
            input_price_per_million=Decimal("15.00"),
            output_price_per_million=Decimal("75.00")
        )
        
        session.add(pricing)
        await session.commit()
        await session.refresh(pricing)
        
        assert pricing.project_id is None
        assert pricing.hosting_provider == "anthropic"
        assert pricing.model_name == "claude-3-opus"
    
    @pytest.mark.asyncio
    async def test_unique_constraint_project_provider_model(self, session: AsyncSession):
        """Test unique constraint on (project_id, hosting_provider, model_name)."""
        # Create test project
        project = Project(
            name="Unique Test Project",
            swisper_url="http://localhost:8000",
            swisper_api_key="unique-test-key"
        )
        session.add(project)
        await session.commit()
        await session.refresh(project)
        
        pricing1 = ModelPricing(
            id=str(uuid4()),
            project_id=project.id,
            hosting_provider="openai",
            model_name="gpt-4",
            input_price_per_million=Decimal("30.00"),
            output_price_per_million=Decimal("60.00")
        )
        session.add(pricing1)
        await session.commit()
        
        # Try to create duplicate
        pricing2 = ModelPricing(
            id=str(uuid4()),
            project_id=project.id,
            hosting_provider="openai",
            model_name="gpt-4",
            input_price_per_million=Decimal("35.00"),  # Different price
            output_price_per_million=Decimal("65.00")
        )
        session.add(pricing2)
        
        # Should raise IntegrityError due to unique constraint
        with pytest.raises(Exception):  # SQLAlchemy IntegrityError
            await session.commit()
        
        # Rollback to clean state after expected error
        await session.rollback()
    
    @pytest.mark.asyncio
    async def test_same_model_different_providers(self, session: AsyncSession):
        """Test same model name can exist for different providers."""
        # Create test project
        project = Project(
            name="Multi-Provider Project",
            swisper_url="http://localhost:8000",
            swisper_api_key="multi-provider-key"
        )
        session.add(project)
        await session.commit()
        await session.refresh(project)
        
        openai_pricing = ModelPricing(
            id=str(uuid4()),
            project_id=project.id,
            hosting_provider="openai",
            model_name="gpt-4-turbo",
            input_price_per_million=Decimal("10.00"),
            output_price_per_million=Decimal("30.00")
        )
        
        azure_pricing = ModelPricing(
            id=str(uuid4()),
            project_id=project.id,
            hosting_provider="azure",
            model_name="gpt-4-turbo",  # Same model, different provider
            input_price_per_million=Decimal("12.00"),  # Different pricing
            output_price_per_million=Decimal("35.00")
        )
        
        session.add(openai_pricing)
        session.add(azure_pricing)
        await session.commit()
        
        # Query both
        statement = select(ModelPricing).where(
            ModelPricing.project_id == project.id,
            ModelPricing.model_name == "gpt-4-turbo"
        )
        result = await session.execute(statement)
        results = result.scalars().all()
        
        assert len(results) == 2
        providers = [r.hosting_provider for r in results]
        assert "openai" in providers
        assert "azure" in providers
    
    @pytest.mark.asyncio
    async def test_query_pricing_for_project(self, session: AsyncSession):
        """Test querying all pricing for a specific project."""
        # Create test project
        project = Project(
            name="Query Test Project",
            swisper_url="http://localhost:8000",
            swisper_api_key="query-test-key"
        )
        session.add(project)
        await session.commit()
        await session.refresh(project)
        
        # Add multiple pricing entries
        models = [
            ("openai", "gpt-4-turbo", "10.00", "30.00"),
            ("openai", "gpt-3.5-turbo", "0.50", "1.50"),
            ("anthropic", "claude-3-sonnet", "3.00", "15.00"),
        ]
        
        for provider, model, input_price, output_price in models:
            pricing = ModelPricing(
                id=str(uuid4()),
                project_id=project.id,
                hosting_provider=provider,
                model_name=model,
                input_price_per_million=Decimal(input_price),
                output_price_per_million=Decimal(output_price)
            )
            session.add(pricing)
        
        await session.commit()
        
        # Query all pricing for project
        statement = select(ModelPricing).where(ModelPricing.project_id == project.id)
        result = await session.execute(statement)
        results = result.scalars().all()
        
        assert len(results) == 3
        model_names = [r.model_name for r in results]
        assert "gpt-4-turbo" in model_names
        assert "gpt-3.5-turbo" in model_names
        assert "claude-3-sonnet" in model_names

