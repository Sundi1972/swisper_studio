"""
Tests for trace tree API endpoint.
"""

import pytest
from uuid import uuid4
from datetime import datetime
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_trace_tree_api(client: AsyncClient, api_headers: dict[str, str], test_project_payload: dict) -> None:
    """
    Business case: Fetch observation tree via API.
    Expected: Returns nested tree structure with aggregated metrics.
    """
    # Create project
    payload = {**test_project_payload, "name": f"Tree API Test {uuid4()}"}
    project_response = await client.post(
        "/api/v1/projects",
        json=payload,
        headers=api_headers
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["id"]
    
    # Create trace
    trace_id = str(uuid4())
    trace_response = await client.post(
        "/api/v1/traces",
        json={
            "id": trace_id,
            "project_id": project_id,
            "name": "Test Trace"
        },
        headers=api_headers
    )
    assert trace_response.status_code == 201
    
    # Create root observation
    root_id = str(uuid4())
    root_response = await client.post(
        "/api/v1/observations",
        json={
            "id": root_id,
            "trace_id": trace_id,
            "type": "AGENT",
            "name": "agent",
            "start_time": datetime.utcnow().isoformat()
        },
        headers=api_headers
    )
    assert root_response.status_code == 201
    
    # Create child observation
    child_response = await client.post(
        "/api/v1/observations",
        json={
            "id": str(uuid4()),
            "trace_id": trace_id,
            "parent_observation_id": root_id,
            "type": "GENERATION",
            "name": "llm_call",
            "start_time": datetime.utcnow().isoformat(),
            "model": "gpt-4",
            "prompt_tokens": 100,
            "completion_tokens": 50
        },
        headers=api_headers
    )
    assert child_response.status_code == 201
    
    # Get tree via API
    tree_response = await client.get(
        f"/api/v1/traces/{trace_id}/tree",
        headers=api_headers
    )
    
    assert tree_response.status_code == 200
    tree = tree_response.json()
    
    # Verify tree structure
    assert len(tree) == 1  # One root
    assert tree[0]["id"] == root_id
    assert tree[0]["name"] == "agent"
    assert len(tree[0]["children"]) == 1
    
    # Verify child
    child = tree[0]["children"][0]
    assert child["name"] == "llm_call"
    assert child["model"] == "gpt-4"
    assert child["calculated_total_cost"] is not None


@pytest.mark.asyncio
async def test_get_trace_tree_nonexistent_trace(client: AsyncClient, api_headers: dict[str, str]) -> None:
    """
    Error case: Get tree for non-existent trace.
    Expected: 404 Not Found.
    """
    response = await client.get(
        f"/api/v1/traces/non-existent-trace-id/tree",
        headers=api_headers
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

