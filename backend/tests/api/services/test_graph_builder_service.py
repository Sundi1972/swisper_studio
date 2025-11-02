"""
Tests for graph builder service.

Tests cover:
- Building trace graphs from observations
- Loading system architecture data
- Edge cases (empty data, single node, nested trees)
"""

import pytest
import uuid
from datetime import datetime, timezone
from app.api.services.graph_builder_service import GraphBuilderService
from app.models.observation import Observation, ObservationType
from app.models.graph import GraphData, SystemArchitectureData


class TestGraphBuilderService:
    """Tests for GraphBuilderService"""
    
    @pytest.fixture
    def service(self):
        """Create graph builder service instance"""
        return GraphBuilderService()
    
    @pytest.mark.asyncio
    async def test_build_trace_graph_empty_observations(self, service):
        """Test: Empty observations list returns empty graph with just START and END"""
        observations = []
        
        graph = service.build_trace_graph(observations)
        
        # Should have START and END nodes only
        assert len(graph.nodes) == 2
        assert any(node.id == "__start__" for node in graph.nodes)
        assert any(node.id == "__end__" for node in graph.nodes)
        
        # Should have one edge: START → END
        assert len(graph.edges) == 1
        assert graph.edges[0].from_node == "__start__"
        assert graph.edges[0].to_node == "__end__"
    
    @pytest.mark.asyncio
    async def test_build_trace_graph_single_observation(self, service):
        """Test: Single observation creates 3-node graph (START → obs → END)"""
        obs = Observation(
            id=uuid.uuid4(),
            trace_id=uuid.uuid4(),
            project_id=uuid.uuid4(),
            type=ObservationType.SPAN,
            name="test_observation",
            start_time=datetime.now(timezone.utc),
            parent_observation_id=None
        )
        observations = [obs]
        
        graph = service.build_trace_graph(observations)
        
        # Should have 3 nodes: START, observation, END
        assert len(graph.nodes) == 3
        node_ids = [node.id for node in graph.nodes]
        assert "__start__" in node_ids
        assert str(obs.id) in node_ids
        assert "__end__" in node_ids
        
        # Observation node should have correct type
        obs_node = next(node for node in graph.nodes if node.id == str(obs.id))
        assert obs_node.label == "test_observation"
        assert obs_node.type == "SPAN"
        
        # Should have 2 edges: START → obs, obs → END
        assert len(graph.edges) == 2
    
    @pytest.mark.asyncio
    async def test_build_trace_graph_nested_observations(self, service):
        """Test: Parent-child observations create proper tree structure"""
        parent_id = uuid.uuid4()
        child_id = uuid.uuid4()
        trace_id = uuid.uuid4()
        project_id = uuid.uuid4()
        
        parent = Observation(
            id=parent_id,
            trace_id=trace_id,
            project_id=project_id,
            type=ObservationType.SPAN,
            name="parent",
            start_time=datetime.now(timezone.utc),
            parent_observation_id=None
        )
        
        child = Observation(
            id=child_id,
            trace_id=trace_id,
            project_id=project_id,
            type=ObservationType.GENERATION,
            name="child",
            start_time=datetime.now(timezone.utc),
            parent_observation_id=parent_id
        )
        
        observations = [parent, child]
        
        graph = service.build_trace_graph(observations)
        
        # Should have 4 nodes: START, parent, child, END
        assert len(graph.nodes) == 4
        
        # Should have edge from parent to child
        parent_to_child = next(
            (edge for edge in graph.edges 
             if edge.from_node == str(parent_id) and edge.to_node == str(child_id)),
            None
        )
        assert parent_to_child is not None
    
    @pytest.mark.asyncio
    async def test_build_trace_graph_observation_types(self, service):
        """Test: Different observation types are preserved in nodes"""
        trace_id = uuid.uuid4()
        project_id = uuid.uuid4()
        
        observations = [
            Observation(
                id=uuid.uuid4(),
                trace_id=trace_id,
                project_id=project_id,
                type=ObservationType.SPAN,
                name="span_obs",
                start_time=datetime.now(timezone.utc)
            ),
            Observation(
                id=uuid.uuid4(),
                trace_id=trace_id,
                project_id=project_id,
                type=ObservationType.GENERATION,
                name="gen_obs",
                start_time=datetime.now(timezone.utc)
            ),
            Observation(
                id=uuid.uuid4(),
                trace_id=trace_id,
                project_id=project_id,
                type=ObservationType.TOOL,
                name="tool_obs",
                start_time=datetime.now(timezone.utc)
            )
        ]
        
        graph = service.build_trace_graph(observations)
        
        # Find nodes (excluding START/END)
        span_node = next((n for n in graph.nodes if n.label == "span_obs"), None)
        gen_node = next((n for n in graph.nodes if n.label == "gen_obs"), None)
        tool_node = next((n for n in graph.nodes if n.label == "tool_obs"), None)
        
        assert span_node is not None and span_node.type == "SPAN"
        assert gen_node is not None and gen_node.type == "GENERATION"
        assert tool_node is not None and tool_node.type == "TOOL"
    
    @pytest.mark.asyncio
    async def test_get_system_architecture(self, service):
        """Test: Returns all 5 agent definitions"""
        architecture = service.get_system_architecture()
        
        assert isinstance(architecture, SystemArchitectureData)
        assert len(architecture.agents) == 5
        
        # Check agent names
        agent_names = [agent.name for agent in architecture.agents]
        assert "global_supervisor" in agent_names
        assert "productivity_agent" in agent_names
        assert "research_agent" in agent_names
        assert "wealth_agent" in agent_names
        assert "doc_agent" in agent_names
    
    @pytest.mark.asyncio
    async def test_get_system_architecture_structure(self, service):
        """Test: Agent graphs have correct structure"""
        architecture = service.get_system_architecture()
        
        # Get global_supervisor agent
        supervisor = next(
            (a for a in architecture.agents if a.name == "global_supervisor"),
            None
        )
        assert supervisor is not None
        assert supervisor.description != ""
        
        # Should have nodes
        assert len(supervisor.nodes) > 0
        
        # Should have edges
        assert len(supervisor.edges) > 0
        
        # Nodes should have required fields
        for node in supervisor.nodes:
            assert node.id != ""
            assert node.label != ""
            assert node.type != ""
        
        # Edges should reference existing nodes
        node_ids = {node.id for node in supervisor.nodes}
        for edge in supervisor.edges:
            assert edge.from_node in node_ids
            assert edge.to_node in node_ids

