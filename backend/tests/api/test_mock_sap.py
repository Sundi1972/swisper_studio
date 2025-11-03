"""Tests for Mock SAP endpoints"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_mock_sap_schema(client: AsyncClient):
    """Test schema endpoint returns valid schema"""
    response = await client.get("/api/v1/mock-swisper/api/admin/config/schema")
    assert response.status_code == 200
    
    schema = response.json()
    assert schema["version"] == "1.0"
    assert len(schema["tables"]) == 1
    assert schema["tables"][0]["name"] == "llm_node_config"
    
    # Verify fields
    fields = schema["tables"][0]["fields"]
    field_names = [f["name"] for f in fields]
    assert "node_name" in field_names
    assert "default_model" in field_names
    assert "default_temperature" in field_names


@pytest.mark.asyncio
async def test_mock_sap_list_configs(client: AsyncClient):
    """Test list all configs"""
    response = await client.get("/api/v1/mock-swisper/api/admin/config/llm_node_config")
    assert response.status_code == 200
    
    data = response.json()
    assert data["count"] == 2
    assert len(data["records"]) == 2
    
    # Verify records
    node_names = [r["node_name"] for r in data["records"]]
    assert "global_planner" in node_names
    assert "intent_classification" in node_names


@pytest.mark.asyncio
async def test_mock_sap_get_config(client: AsyncClient):
    """Test get single config"""
    response = await client.get(
        "/api/v1/mock-swisper/api/admin/config/llm_node_config/global_planner"
    )
    assert response.status_code == 200
    
    config = response.json()
    assert config["node_name"] == "global_planner"
    assert config["default_model"] == "gpt-4-turbo"
    assert config["default_temperature"] == 0.7


@pytest.mark.asyncio
async def test_mock_sap_get_config_not_found(client: AsyncClient):
    """Test get non-existent config returns 404"""
    response = await client.get(
        "/api/v1/mock-swisper/api/admin/config/llm_node_config/nonexistent"
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_mock_sap_update_config(client: AsyncClient):
    """Test update config"""
    response = await client.put(
        "/api/v1/mock-swisper/api/admin/config/llm_node_config/global_planner",
        json={"default_temperature": 0.5}
    )
    assert response.status_code == 200
    
    config = response.json()
    assert config["default_temperature"] == 0.5
    assert config["default_model"] == "gpt-4-turbo"  # Other fields unchanged


@pytest.mark.asyncio
async def test_mock_sap_update_validation_temperature_too_high(client: AsyncClient):
    """Test temperature validation (max 2.0)"""
    response = await client.put(
        "/api/v1/mock-swisper/api/admin/config/llm_node_config/global_planner",
        json={"default_temperature": 3.0}  # Invalid (> 2.0)
    )
    assert response.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
async def test_mock_sap_update_validation_temperature_too_low(client: AsyncClient):
    """Test temperature validation (min 0.0)"""
    response = await client.put(
        "/api/v1/mock-swisper/api/admin/config/llm_node_config/global_planner",
        json={"default_temperature": -0.5}  # Invalid (< 0.0)
    )
    assert response.status_code == 422  # Pydantic validation error


@pytest.mark.ci_critical
@pytest.mark.asyncio
async def test_mock_sap_full_workflow(client: AsyncClient):
    """CI: Test complete workflow - get schema, list configs, update"""
    # Get schema
    schema_response = await client.get("/api/v1/mock-swisper/api/admin/config/schema")
    assert schema_response.status_code == 200
    
    # List configs
    list_response = await client.get("/api/v1/mock-swisper/api/admin/config/llm_node_config")
    assert list_response.status_code == 200
    
    # Update config
    update_response = await client.put(
        "/api/v1/mock-swisper/api/admin/config/llm_node_config/global_planner",
        json={"default_temperature": 0.6}
    )
    assert update_response.status_code == 200
    assert update_response.json()["default_temperature"] == 0.6

