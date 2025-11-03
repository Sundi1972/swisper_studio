"""Tests for ProjectEnvironment and Config versioning models"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from app.models.project import Project
from app.models.project_environment import ProjectEnvironment
from app.models.config_version import ConfigVersion, ConfigDeployment


@pytest.mark.asyncio
async def test_create_environment(session: AsyncSession):
    """Test creating an environment"""
    project = Project(name="Test Project")
    session.add(project)
    await session.commit()
    await session.refresh(project)
    
    env = ProjectEnvironment(
        project_id=project.id,
        env_type="dev",
        swisper_url="http://dev.test.com",
        api_key="test_key"
    )
    session.add(env)
    await session.commit()
    await session.refresh(env)
    
    assert env.id is not None
    assert env.env_type == "dev"
    assert env.swisper_url == "http://dev.test.com"


@pytest.mark.asyncio
async def test_create_three_environments(session: AsyncSession):
    """Test creating all three environment types"""
    project = Project(name="Test Project")
    session.add(project)
    await session.commit()
    await session.refresh(project)
    
    # Create dev, staging, production
    for env_type in ["dev", "staging", "production"]:
        env = ProjectEnvironment(
            project_id=project.id,
            env_type=env_type,
            swisper_url=f"http://{env_type}.test.com",
            api_key=f"{env_type}_key"
        )
        session.add(env)
    
    await session.commit()
    
    # Verify all created
    statement = select(ProjectEnvironment).where(
        ProjectEnvironment.project_id == project.id
    )
    result = await session.execute(statement)
    environments = result.scalars().all()
    assert len(environments) == 3
    
    env_types = [e.env_type for e in environments]
    assert "dev" in env_types
    assert "staging" in env_types
    assert "production" in env_types


@pytest.mark.asyncio
async def test_unique_env_type_constraint(session: AsyncSession):
    """Test can't create duplicate env_type for same project"""
    project = Project(name="Test Project")
    session.add(project)
    await session.commit()
    await session.refresh(project)
    
    # Create first dev environment
    env1 = ProjectEnvironment(
        project_id=project.id,
        env_type="dev",
        swisper_url="http://dev1.com",
        api_key="key1"
    )
    session.add(env1)
    await session.commit()
    
    # Try to create second dev environment (should fail)
    env2 = ProjectEnvironment(
        project_id=project.id,
        env_type="dev",  # Duplicate!
        swisper_url="http://dev2.com",
        api_key="key2"
    )
    session.add(env2)
    
    with pytest.raises(IntegrityError):
        await session.commit()
    
    # Rollback to clean up session
    await session.rollback()


@pytest.mark.asyncio
async def test_config_version_creation(session: AsyncSession):
    """Test creating a config version"""
    project = Project(name="Test Project")
    session.add(project)
    await session.commit()
    await session.refresh(project)
    
    version = ConfigVersion(
        project_id=project.id,
        table_name="llm_node_config",
        record_id="global_planner",
        version_number=1,
        config_data={"temperature": 0.7, "model": "gpt-4"},
        created_by="test@example.com"
    )
    session.add(version)
    await session.commit()
    await session.refresh(version)
    
    assert version.id is not None
    assert version.config_data["temperature"] == 0.7
    assert version.version_number == 1


@pytest.mark.asyncio
async def test_config_version_with_parent(session: AsyncSession):
    """Test config version lineage tracking"""
    project = Project(name="Test Project")
    session.add(project)
    await session.commit()
    await session.refresh(project)
    
    # Create parent version
    v1 = ConfigVersion(
        project_id=project.id,
        table_name="llm_node_config",
        record_id="global_planner",
        version_number=1,
        config_data={"temperature": 0.7},
        created_by="test@example.com"
    )
    session.add(v1)
    await session.commit()
    await session.refresh(v1)
    
    # Create child version
    v2 = ConfigVersion(
        project_id=project.id,
        table_name="llm_node_config",
        record_id="global_planner",
        version_number=2,
        config_data={"temperature": 0.5},
        created_by="test@example.com",
        parent_version_id=v1.id
    )
    session.add(v2)
    await session.commit()
    await session.refresh(v2)
    
    assert v2.parent_version_id == v1.id


@pytest.mark.asyncio
async def test_config_deployment_tracking(session: AsyncSession):
    """Test deployment tracking"""
    project = Project(name="Test Project")
    session.add(project)
    await session.commit()
    await session.refresh(project)
    
    # Create environment
    env = ProjectEnvironment(
        project_id=project.id,
        env_type="dev",
        swisper_url="http://dev.test.com",
        api_key="test_key"
    )
    session.add(env)
    await session.commit()
    await session.refresh(env)
    
    # Create version
    version = ConfigVersion(
        project_id=project.id,
        table_name="llm_node_config",
        record_id="global_planner",
        version_number=1,
        config_data={"temperature": 0.7},
        created_by="test@example.com"
    )
    session.add(version)
    await session.commit()
    await session.refresh(version)
    
    # Create deployment
    deployment = ConfigDeployment(
        version_id=version.id,
        environment_id=env.id,
        status="deployed",
        deployed_by="test@example.com"
    )
    session.add(deployment)
    await session.commit()
    await session.refresh(deployment)
    
    assert deployment.id is not None
    assert deployment.status == "deployed"
    assert deployment.version_id == version.id
    assert deployment.environment_id == env.id


@pytest.mark.ci_critical
@pytest.mark.asyncio
async def test_environment_and_versioning_integration(session: AsyncSession):
    """CI: Test complete integration - project, environments, versions, deployments"""
    # Create project
    project = Project(name="Integration Test Project")
    session.add(project)
    await session.commit()
    await session.refresh(project)
    
    # Create 3 environments
    envs = []
    for env_type in ["dev", "staging", "production"]:
        env = ProjectEnvironment(
            project_id=project.id,
            env_type=env_type,
            swisper_url=f"http://{env_type}.test.com",
            api_key=f"{env_type}_key"
        )
        session.add(env)
        await session.commit()
        await session.refresh(env)
        envs.append(env)
    
    # Create version
    version = ConfigVersion(
        project_id=project.id,
        table_name="llm_node_config",
        record_id="global_planner",
        version_number=1,
        config_data={"temperature": 0.7, "model": "gpt-4"},
        created_by="test@example.com"
    )
    session.add(version)
    await session.commit()
    await session.refresh(version)
    
    # Deploy to dev
    deployment = ConfigDeployment(
        version_id=version.id,
        environment_id=envs[0].id,
        status="deployed",
        deployed_by="test@example.com"
    )
    session.add(deployment)
    await session.commit()
    
    # Verify
    assert len(envs) == 3
    assert version.id is not None
    assert deployment.id is not None

