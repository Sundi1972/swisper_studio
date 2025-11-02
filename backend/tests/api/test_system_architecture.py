"""
Tests for system architecture API endpoints.
"""

import pytest
from httpx import AsyncClient


class TestSystemArchitectureAPI:
    """Tests for /api/v1/system-architecture endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_system_architecture_success(self, client: AsyncClient):
        """Test: GET /api/v1/system-architecture returns agent graphs"""
        response = await client.get("/api/v1/system-architecture")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have agents list
        assert "agents" in data
        assert isinstance(data["agents"], list)
        assert len(data["agents"]) == 5
    
    @pytest.mark.asyncio
    async def test_get_system_architecture_structure(self, client: AsyncClient):
        """Test: Agent graphs have correct structure"""
        response = await client.get("/api/v1/system-architecture")
        
        assert response.status_code == 200
        data = response.json()
        
        # Get global_supervisor agent
        supervisor = next(
            (agent for agent in data["agents"] if agent["name"] == "global_supervisor"),
            None
        )
        assert supervisor is not None
        
        # Should have description
        assert "description" in supervisor
        assert supervisor["description"] != ""
        
        # Should have nodes
        assert "nodes" in supervisor
        assert len(supervisor["nodes"]) > 0
        
        # Should have edges
        assert "edges" in supervisor
        assert len(supervisor["edges"]) > 0
        
        # Node structure
        first_node = supervisor["nodes"][0]
        assert "id" in first_node
        assert "label" in first_node
        assert "type" in first_node
        
        # Edge structure  
        first_edge = supervisor["edges"][0]
        # Check for either 'from' or 'from_node' (alias support)
        assert "from" in first_edge or "from_node" in first_edge
        assert "to" in first_edge or "to_node" in first_edge
    
    @pytest.mark.asyncio
    async def test_get_system_architecture_all_agents(self, client: AsyncClient):
        """Test: All 5 agents are present"""
        response = await client.get("/api/v1/system-architecture")
        
        assert response.status_code == 200
        data = response.json()
        
        agent_names = [agent["name"] for agent in data["agents"]]
        
        # Should have all 5 agents
        assert "global_supervisor" in agent_names
        assert "productivity_agent" in agent_names
        assert "research_agent" in agent_names
        assert "wealth_agent" in agent_names
        assert "doc_agent" in agent_names

