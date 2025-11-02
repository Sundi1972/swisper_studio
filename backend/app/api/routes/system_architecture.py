"""System Architecture API endpoints"""

from fastapi import APIRouter
from app.models.graph import SystemArchitectureData
from app.api.services.graph_builder_service import graph_builder_service


router = APIRouter()


@router.get("/system-architecture", response_model=SystemArchitectureData)
async def get_system_architecture() -> SystemArchitectureData:
    """
    Get all Swisper agent graph definitions.
    
    Returns static graph structures for all agents:
    - global_supervisor
    - productivity_agent
    - research_agent
    - wealth_agent
    - doc_agent
    
    This data is used by the Swisper Builder UI to visualize
    the system architecture.
    
    Returns:
        SystemArchitectureData with all agent graphs
    """
    return graph_builder_service.get_system_architecture()

