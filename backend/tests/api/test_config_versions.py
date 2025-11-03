"""Tests for Config Version API endpoints"""
import pytest
from httpx import AsyncClient


@pytest.mark.ci_critical
@pytest.mark.asyncio
async def test_create_first_version(
    client: AsyncClient,
    api_headers: dict[str, str],
    test_project_payload: dict
):
    """CI: Create first config version (version_number=1)"""
    # Create project
    project_response = await client.post(
        "/api/v1/projects",
        json=test_project_payload,
        headers=api_headers
    )
    project_id = project_response.json()["id"]
    
    # Create first version
    response = await client.post(
        f"/api/v1/projects/{project_id}/config/versions",
        json={
            "table_name": "llm_node_config",
            "record_id": "global_planner",
            "config_data": {
                "default_model": "gpt-4-turbo",
                "default_temperature": 0.7,
                "default_max_tokens": 4000
            },
            "description": "Initial config",
            "created_by": "test@example.com"
        },
        headers=api_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify version number
    assert data["version_number"] == 1
    assert data["table_name"] == "llm_node_config"
    assert data["record_id"] == "global_planner"
    assert data["config_data"]["default_temperature"] == 0.7
    assert data["parent_version_id"] is None  # First version has no parent


@pytest.mark.asyncio
async def test_create_second_version_increments(
    client: AsyncClient,
    api_headers: dict[str, str],
    test_project_payload: dict
):
    """Test creating second version auto-increments to version_number=2"""
    # Create project
    project_response = await client.post(
        "/api/v1/projects",
        json=test_project_payload,
        headers=api_headers
    )
    project_id = project_response.json()["id"]
    
    # Create version 1
    v1_response = await client.post(
        f"/api/v1/projects/{project_id}/config/versions",
        json={
            "table_name": "llm_node_config",
            "record_id": "global_planner",
            "config_data": {"default_temperature": 0.7},
            "created_by": "test@example.com"
        },
        headers=api_headers
    )
    v1_id = v1_response.json()["id"]
    
    # Create version 2
    v2_response = await client.post(
        f"/api/v1/projects/{project_id}/config/versions",
        json={
            "table_name": "llm_node_config",
            "record_id": "global_planner",
            "config_data": {"default_temperature": 0.5},
            "description": "Lower temperature for deterministic planning",
            "created_by": "test@example.com"
        },
        headers=api_headers
    )
    
    assert v2_response.status_code == 201
    v2_data = v2_response.json()
    
    assert v2_data["version_number"] == 2
    assert v2_data["parent_version_id"] == v1_id  # Tracks parent


@pytest.mark.asyncio
async def test_list_versions_empty(
    client: AsyncClient,
    api_headers: dict[str, str],
    test_project_payload: dict
):
    """Edge case: List versions for project with no versions"""
    # Create project
    project_response = await client.post(
        "/api/v1/projects",
        json=test_project_payload,
        headers=api_headers
    )
    project_id = project_response.json()["id"]
    
    # List versions (should be empty)
    response = await client.get(
        f"/api/v1/projects/{project_id}/config/versions",
        headers=api_headers
    )
    
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_versions_for_record(
    client: AsyncClient,
    api_headers: dict[str, str],
    test_project_payload: dict
):
    """Test listing versions with filter by record_id"""
    # Create project
    project_response = await client.post(
        "/api/v1/projects",
        json=test_project_payload,
        headers=api_headers
    )
    project_id = project_response.json()["id"]
    
    # Create 2 versions for global_planner
    for i in range(2):
        await client.post(
            f"/api/v1/projects/{project_id}/config/versions",
            json={
                "table_name": "llm_node_config",
                "record_id": "global_planner",
                "config_data": {"default_temperature": 0.7 - (i * 0.1)},
                "created_by": "test@example.com"
            },
            headers=api_headers
        )
    
    # Create 1 version for intent_classification
    await client.post(
        f"/api/v1/projects/{project_id}/config/versions",
        json={
            "table_name": "llm_node_config",
            "record_id": "intent_classification",
            "config_data": {"default_temperature": 0.8},
            "created_by": "test@example.com"
        },
        headers=api_headers
    )
    
    # List versions for global_planner only
    response = await client.get(
        f"/api/v1/projects/{project_id}/config/versions",
        params={"record_id": "global_planner"},
        headers=api_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # Only global_planner versions
    assert all(v["record_id"] == "global_planner" for v in data)


@pytest.mark.ci_critical
@pytest.mark.asyncio
async def test_deploy_version_to_dev(
    client: AsyncClient,
    api_headers: dict[str, str],
    test_project_payload: dict
):
    """CI: Deploy config version to dev environment"""
    # Create project
    project_response = await client.post(
        "/api/v1/projects",
        json=test_project_payload,
        headers=api_headers
    )
    project_id = project_response.json()["id"]
    
    # Get dev environment
    envs_response = await client.get(
        f"/api/v1/projects/{project_id}/environments",
        headers=api_headers
    )
    dev_env = [e for e in envs_response.json() if e["env_type"] == "dev"][0]
    
    # Create version
    version_response = await client.post(
        f"/api/v1/projects/{project_id}/config/versions",
        json={
            "table_name": "llm_node_config",
            "record_id": "global_planner",
            "config_data": {
                "default_model": "gpt-4-turbo",
                "default_temperature": 0.6
            },
            "description": "Test deployment",
            "created_by": "test@example.com"
        },
        headers=api_headers
    )
    version_id = version_response.json()["id"]
    
    # Deploy to dev
    response = await client.post(
        f"/api/v1/projects/{project_id}/environments/{dev_env['id']}/deploy",
        json={
            "version_id": version_id,
            "deployed_by": "test@example.com"
        },
        headers=api_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert "version" in data
    assert "deployment" in data
    assert data["deployment"]["status"] == "deployed"


@pytest.mark.asyncio
async def test_deploy_version_to_staging(
    client: AsyncClient,
    api_headers: dict[str, str],
    test_project_payload: dict
):
    """Test deploying same version to staging environment"""
    # Create project
    project_response = await client.post(
        "/api/v1/projects",
        json=test_project_payload,
        headers=api_headers
    )
    project_id = project_response.json()["id"]
    
    # Get staging environment
    envs_response = await client.get(
        f"/api/v1/projects/{project_id}/environments",
        headers=api_headers
    )
    staging_env = [e for e in envs_response.json() if e["env_type"] == "staging"][0]
    
    # Create version
    version_response = await client.post(
        f"/api/v1/projects/{project_id}/config/versions",
        json={
            "table_name": "llm_node_config",
            "record_id": "global_planner",
            "config_data": {"default_temperature": 0.5},
            "created_by": "test@example.com"
        },
        headers=api_headers
    )
    version_id = version_response.json()["id"]
    
    # Deploy to staging
    response = await client.post(
        f"/api/v1/projects/{project_id}/environments/{staging_env['id']}/deploy",
        json={
            "version_id": version_id,
            "deployed_by": "test@example.com"
        },
        headers=api_headers
    )
    
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_deploy_invalid_version_id(
    client: AsyncClient,
    api_headers: dict[str, str],
    test_project_payload: dict
):
    """Error case: Deploy non-existent version returns 404"""
    # Create project
    project_response = await client.post(
        "/api/v1/projects",
        json=test_project_payload,
        headers=api_headers
    )
    project_id = project_response.json()["id"]
    
    # Get dev environment
    envs_response = await client.get(
        f"/api/v1/projects/{project_id}/environments",
        headers=api_headers
    )
    dev_env = [e for e in envs_response.json() if e["env_type"] == "dev"][0]
    
    # Try to deploy non-existent version
    response = await client.post(
        f"/api/v1/projects/{project_id}/environments/{dev_env['id']}/deploy",
        json={
            "version_id": "nonexistent-version-id",
            "deployed_by": "test@example.com"
        },
        headers=api_headers
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_deploy_invalid_environment_id(
    client: AsyncClient,
    api_headers: dict[str, str],
    test_project_payload: dict
):
    """Error case: Deploy to non-existent environment returns 404"""
    # Create project
    project_response = await client.post(
        "/api/v1/projects",
        json=test_project_payload,
        headers=api_headers
    )
    project_id = project_response.json()["id"]
    
    # Create version
    version_response = await client.post(
        f"/api/v1/projects/{project_id}/config/versions",
        json={
            "table_name": "llm_node_config",
            "record_id": "global_planner",
            "config_data": {"default_temperature": 0.6},
            "created_by": "test@example.com"
        },
        headers=api_headers
    )
    version_id = version_response.json()["id"]
    
    # Try to deploy to non-existent environment
    response = await client.post(
        f"/api/v1/projects/{project_id}/environments/nonexistent-env-id/deploy",
        json={
            "version_id": version_id,
            "deployed_by": "test@example.com"
        },
        headers=api_headers
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_current_deployed_version(
    client: AsyncClient,
    api_headers: dict[str, str],
    test_project_payload: dict
):
    """Test getting currently deployed version for an environment"""
    # Create project
    project_response = await client.post(
        "/api/v1/projects",
        json=test_project_payload,
        headers=api_headers
    )
    project_id = project_response.json()["id"]
    
    # Get dev environment
    envs_response = await client.get(
        f"/api/v1/projects/{project_id}/environments",
        headers=api_headers
    )
    dev_env = [e for e in envs_response.json() if e["env_type"] == "dev"][0]
    
    # Create and deploy version
    version_response = await client.post(
        f"/api/v1/projects/{project_id}/config/versions",
        json={
            "table_name": "llm_node_config",
            "record_id": "global_planner",
            "config_data": {"default_temperature": 0.6},
            "created_by": "test@example.com"
        },
        headers=api_headers
    )
    version_id = version_response.json()["id"]
    
    await client.post(
        f"/api/v1/projects/{project_id}/environments/{dev_env['id']}/deploy",
        json={
            "version_id": version_id,
            "deployed_by": "test@example.com"
        },
        headers=api_headers
    )
    
    # Get current deployed version
    response = await client.get(
        f"/api/v1/projects/{project_id}/environments/{dev_env['id']}/current-config",
        params={
            "table_name": "llm_node_config",
            "record_id": "global_planner"
        },
        headers=api_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["version"]["id"] == version_id
    assert data["version"]["version_number"] == 1
    assert data["deployment"]["status"] == "deployed"


@pytest.mark.asyncio
async def test_list_versions_with_table_filter(
    client: AsyncClient,
    api_headers: dict[str, str],
    test_project_payload: dict
):
    """Test listing versions filtered by table_name"""
    # Create project
    project_response = await client.post(
        "/api/v1/projects",
        json=test_project_payload,
        headers=api_headers
    )
    project_id = project_response.json()["id"]
    
    # Create versions for different tables
    await client.post(
        f"/api/v1/projects/{project_id}/config/versions",
        json={
            "table_name": "llm_node_config",
            "record_id": "global_planner",
            "config_data": {"temperature": 0.7},
            "created_by": "test@example.com"
        },
        headers=api_headers
    )
    
    await client.post(
        f"/api/v1/projects/{project_id}/config/versions",
        json={
            "table_name": "feature_flags",
            "record_id": "research_enabled",
            "config_data": {"enabled": True},
            "created_by": "test@example.com"
        },
        headers=api_headers
    )
    
    # List versions for llm_node_config only
    response = await client.get(
        f"/api/v1/projects/{project_id}/config/versions",
        params={"table_name": "llm_node_config"},
        headers=api_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["table_name"] == "llm_node_config"


@pytest.mark.asyncio
async def test_version_parent_tracking(
    client: AsyncClient,
    api_headers: dict[str, str],
    test_project_payload: dict
):
    """Test version lineage tracking via parent_version_id"""
    # Create project
    project_response = await client.post(
        "/api/v1/projects",
        json=test_project_payload,
        headers=api_headers
    )
    project_id = project_response.json()["id"]
    
    # Create version chain: v1 → v2 → v3
    v1_response = await client.post(
        f"/api/v1/projects/{project_id}/config/versions",
        json={
            "table_name": "llm_node_config",
            "record_id": "global_planner",
            "config_data": {"temperature": 0.7},
            "created_by": "test@example.com"
        },
        headers=api_headers
    )
    v1_id = v1_response.json()["id"]
    
    v2_response = await client.post(
        f"/api/v1/projects/{project_id}/config/versions",
        json={
            "table_name": "llm_node_config",
            "record_id": "global_planner",
            "config_data": {"temperature": 0.6},
            "created_by": "test@example.com"
        },
        headers=api_headers
    )
    v2_id = v2_response.json()["id"]
    
    v3_response = await client.post(
        f"/api/v1/projects/{project_id}/config/versions",
        json={
            "table_name": "llm_node_config",
            "record_id": "global_planner",
            "config_data": {"temperature": 0.5},
            "created_by": "test@example.com"
        },
        headers=api_headers
    )
    
    # Verify lineage
    assert v1_response.json()["parent_version_id"] is None
    assert v2_response.json()["parent_version_id"] == v1_id
    assert v3_response.json()["parent_version_id"] == v2_id

