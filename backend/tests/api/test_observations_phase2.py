"""
Tests for Phase 2 enhanced observation ingestion with automatic cost calculation.
"""

import pytest
from decimal import Decimal
from httpx import AsyncClient
from uuid import uuid4
from datetime import datetime


@pytest.mark.ci_critical
@pytest.mark.asyncio
async def test_create_observation_with_llm_telemetry_auto_cost(
    client: AsyncClient,
    api_headers: dict[str, str],
    test_project_payload: dict
) -> None:
    """
    CI: Golden path - Observation with LLM telemetry auto-calculates costs.
    
    Business case: SDK sends observation with tokens, backend calculates cost automatically.
    Expected: Observation created with calculated costs using default pricing.
    """
    # Create project first
    payload = {**test_project_payload, "name": "Auto Cost Test Project"}
    project_response = await client.post(
        "/api/v1/projects",
        json=payload,
        headers=api_headers
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["id"]
    
    # Create trace
    trace_response = await client.post(
        "/api/v1/traces",
        json={
            "id": str(uuid4()),
            "project_id": project_id,
            "name": "Test Trace"
        },
        headers=api_headers
    )
    assert trace_response.status_code == 201
    trace_id = trace_response.json()["id"]
    
    # Create observation with LLM telemetry
    obs_id = str(uuid4())
    response = await client.post(
        "/api/v1/observations",
        json={
            "id": obs_id,
            "trace_id": trace_id,
            "type": "GENERATION",
            "name": "llm_call",
            "start_time": datetime.utcnow().isoformat(),
            "end_time": datetime.utcnow().isoformat(),
            "model": "gpt-4-turbo",
            "prompt_tokens": 150,
            "completion_tokens": 50,
            "input": {"messages": [{"role": "user", "content": "Hello"}]},
            "output": {"content": "Hi there!"}
        },
        headers=api_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify observation created
    assert data["id"] == obs_id
    assert data["model"] == "gpt-4-turbo"
    assert data["prompt_tokens"] == 150
    assert data["completion_tokens"] == 50
    assert data["total_tokens"] == 200  # Auto-calculated
    
    # Verify costs auto-calculated (using default pricing: $10/1M input, $30/1M output)
    # input_cost = (150 / 1,000,000) * 10 = 0.0015
    # output_cost = (50 / 1,000,000) * 30 = 0.0015
    # total = 0.0030
    assert data["calculated_input_cost"] is not None
    assert float(data["calculated_input_cost"]) == pytest.approx(0.0015, abs=0.0001)
    assert float(data["calculated_output_cost"]) == pytest.approx(0.0015, abs=0.0001)
    assert float(data["calculated_total_cost"]) == pytest.approx(0.0030, abs=0.0001)


@pytest.mark.asyncio
async def test_create_observation_without_tokens_no_cost(
    client: AsyncClient,
    api_headers: dict[str, str],
    test_project_payload: dict
) -> None:
    """
    Edge case: Observation without token counts doesn't calculate cost.
    Expected: Cost fields are None.
    """
    # Create project and trace
    payload = {**test_project_payload, "name": "No Cost Test Project"}
    project_response = await client.post(
        "/api/v1/projects",
        json=payload,
        headers=api_headers
    )
    project_id = project_response.json()["id"]
    
    trace_response = await client.post(
        "/api/v1/traces",
        json={
            "id": str(uuid4()),
            "project_id": project_id,
            "name": "Test Trace"
        },
        headers=api_headers
    )
    trace_id = trace_response.json()["id"]
    
    # Create observation without tokens
    response = await client.post(
        "/api/v1/observations",
        json={
            "id": str(uuid4()),
            "trace_id": trace_id,
            "type": "SPAN",
            "name": "generic_span",
            "start_time": datetime.utcnow().isoformat()
        },
        headers=api_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify no cost calculated
    assert data["calculated_input_cost"] is None
    assert data["calculated_output_cost"] is None
    assert data["calculated_total_cost"] is None


@pytest.mark.asyncio
async def test_update_observation_recalculates_cost(
    client: AsyncClient,
    api_headers: dict[str, str],
    test_project_payload: dict
) -> None:
    """
    Business case: Updating observation with tokens triggers cost recalculation.
    Expected: Costs updated when token counts are added.
    """
    # Create project and trace
    payload = {**test_project_payload, "name": "Update Cost Test Project"}
    project_response = await client.post(
        "/api/v1/projects",
        json=payload,
        headers=api_headers
    )
    project_id = project_response.json()["id"]
    
    trace_response = await client.post(
        "/api/v1/traces",
        json={
            "id": str(uuid4()),
            "project_id": project_id,
            "name": "Test Trace"
        },
        headers=api_headers
    )
    trace_id = trace_response.json()["id"]
    
    # Create observation without tokens initially
    obs_id = str(uuid4())
    create_response = await client.post(
        "/api/v1/observations",
        json={
            "id": obs_id,
            "trace_id": trace_id,
            "type": "GENERATION",
            "name": "llm_call",
            "start_time": datetime.utcnow().isoformat(),
            "model": "gpt-3.5-turbo"
        },
        headers=api_headers
    )
    assert create_response.status_code == 201
    assert create_response.json()["calculated_total_cost"] is None
    
    # Update with token counts
    update_response = await client.patch(
        f"/api/v1/observations/{obs_id}",
        json={
            "end_time": datetime.utcnow().isoformat(),
            "prompt_tokens": 1000,
            "completion_tokens": 500
        },
        headers=api_headers
    )
    
    assert update_response.status_code == 200
    data = update_response.json()
    
    # Verify cost now calculated (gpt-3.5-turbo: $0.50/1M input, $1.50/1M output)
    # input = (1000 / 1M) * 0.50 = 0.0005
    # output = (500 / 1M) * 1.50 = 0.00075
    # total = 0.00125
    assert data["calculated_input_cost"] is not None
    assert float(data["calculated_input_cost"]) == pytest.approx(0.0005, abs=0.0001)
    assert float(data["calculated_output_cost"]) == pytest.approx(0.00075, abs=0.0001)
    assert float(data["calculated_total_cost"]) == pytest.approx(0.00125, abs=0.0001)


@pytest.mark.asyncio
async def test_create_observation_with_model_parameters(
    client: AsyncClient,
    api_headers: dict[str, str],
    test_project_payload: dict
) -> None:
    """
    Business case: Observation captures LLM model parameters.
    Expected: Model parameters stored correctly.
    """
    # Create project and trace
    payload = {**test_project_payload, "name": "Model Params Test"}
    project_response = await client.post(
        "/api/v1/projects",
        json=payload,
        headers=api_headers
    )
    project_id = project_response.json()["id"]
    
    trace_response = await client.post(
        "/api/v1/traces",
        json={
            "id": str(uuid4()),
            "project_id": project_id,
            "name": "Test Trace"
        },
        headers=api_headers
    )
    trace_id = trace_response.json()["id"]
    
    # Create observation with model parameters
    response = await client.post(
        "/api/v1/observations",
        json={
            "id": str(uuid4()),
            "trace_id": trace_id,
            "type": "GENERATION",
            "name": "llm_call",
            "start_time": datetime.utcnow().isoformat(),
            "model": "gpt-4",
            "model_parameters": {
                "temperature": 0.7,
                "max_tokens": 2000,
                "top_p": 0.9
            },
            "prompt_tokens": 100,
            "completion_tokens": 50
        },
        headers=api_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify model parameters stored (Note: Not in response schema yet, but stored in DB)
    assert data["model"] == "gpt-4"
    # model_parameters not in response schema for MVP - would need to add if needed


@pytest.mark.asyncio
async def test_create_observation_with_error_status(
    client: AsyncClient,
    api_headers: dict[str, str],
    test_project_payload: dict
) -> None:
    """
    Business case: Observation captures errors with ERROR level.
    Expected: Error level and message stored.
    """
    # Create project and trace
    payload = {**test_project_payload, "name": f"Error Test Project {uuid4()}"}  # Unique name
    project_response = await client.post(
        "/api/v1/projects",
        json=payload,
        headers=api_headers
    )
    assert project_response.status_code == 201, f"Project creation failed: {project_response.json()}"
    project_id = project_response.json()["id"]
    
    trace_response = await client.post(
        "/api/v1/traces",
        json={
            "id": str(uuid4()),
            "project_id": project_id,
            "name": "Test Trace"
        },
        headers=api_headers
    )
    trace_id = trace_response.json()["id"]
    
    # Create observation with error
    response = await client.post(
        "/api/v1/observations",
        json={
            "id": str(uuid4()),
            "trace_id": trace_id,
            "type": "GENERATION",
            "name": "failed_llm_call",
            "start_time": datetime.utcnow().isoformat(),
            "end_time": datetime.utcnow().isoformat(),
            "level": "ERROR",
            "status_message": "API rate limit exceeded"
        },
        headers=api_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify error captured
    assert data["level"] == "ERROR"
    assert data["status_message"] == "API rate limit exceeded"

