"""Tests for Environment API endpoints"""
import pytest
from httpx import AsyncClient


@pytest.mark.ci_critical
@pytest.mark.asyncio
async def test_list_environments(
    client: AsyncClient,
    api_headers: dict[str, str],
    test_project_payload: dict
):
    """CI: List all environments for a project"""
    # Create project with 3 environments
    project_response = await client.post(
        "/api/v1/projects",
        json=test_project_payload,
        headers=api_headers
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["id"]
    
    # List environments
    response = await client.get(
        f"/api/v1/projects/{project_id}/environments",
        headers=api_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should have 3 environments
    assert len(data) == 3
    
    # Verify all types present
    env_types = [env["env_type"] for env in data]
    assert "dev" in env_types
    assert "staging" in env_types
    assert "production" in env_types
    
    # Verify structure
    for env in data:
        assert "id" in env
        assert "project_id" in env
        assert "env_type" in env
        assert "swisper_url" in env
        # API key should NOT be in response (security)
        assert "api_key" not in env


@pytest.mark.asyncio
async def test_update_environment_url(
    client: AsyncClient,
    api_headers: dict[str, str],
    test_project_payload: dict
):
    """Test updating environment swisper_url"""
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
    
    # Update URL
    response = await client.put(
        f"/api/v1/environments/{dev_env['id']}",
        json={
            "swisper_url": "http://new-dev.example.com",
            "swisper_api_key": "new_dev_key_12345"
        },
        headers=api_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["swisper_url"] == "http://new-dev.example.com"


@pytest.mark.asyncio
async def test_update_environment_api_key(
    client: AsyncClient,
    api_headers: dict[str, str],
    test_project_payload: dict
):
    """Test updating environment API key"""
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
    
    # Update API key
    response = await client.put(
        f"/api/v1/environments/{staging_env['id']}",
        json={
            "swisper_url": staging_env["swisper_url"],
            "swisper_api_key": "updated_staging_key_67890"
        },
        headers=api_headers
    )
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_nonexistent_environment(
    client: AsyncClient,
    api_headers: dict[str, str]
):
    """Error case: Update non-existent environment returns 404"""
    response = await client.put(
        "/api/v1/environments/nonexistent-id",
        json={
            "swisper_url": "http://example.com",
            "swisper_api_key": "test_key"
        },
        headers=api_headers
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_environment_invalid_url(
    client: AsyncClient,
    api_headers: dict[str, str],
    test_project_payload: dict
):
    """Error case: Invalid URL format should be rejected"""
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
    
    # Try to update with invalid URL
    response = await client.put(
        f"/api/v1/environments/{dev_env['id']}",
        json={
            "swisper_url": "not-a-valid-url",
            "swisper_api_key": "test_key"
        },
        headers=api_headers
    )
    
    assert response.status_code == 422

