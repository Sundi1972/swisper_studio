"""
Graph visualization data models.

Used for converting observation trees to graph structures
and providing static agent architecture definitions.
"""

from typing import List
from pydantic import BaseModel, Field, ConfigDict


class GraphNode(BaseModel):
    """A node in the graph visualization."""
    
    id: str = Field(..., description="Unique identifier for the node")
    label: str = Field(..., description="Display label for the node")
    type: str = Field(..., description="Node type (SPAN, GENERATION, TOOL, AGENT, etc.)")


class GraphEdge(BaseModel):
    """An edge connecting two nodes in the graph."""
    
    model_config = ConfigDict(populate_by_name=True)  # Allow both 'from_node' and 'from'
    
    from_node: str = Field(..., alias="from", description="Source node ID")
    to_node: str = Field(..., alias="to", description="Target node ID")


class GraphData(BaseModel):
    """Complete graph structure with nodes and edges."""
    
    nodes: List[GraphNode] = Field(default_factory=list, description="List of graph nodes")
    edges: List[GraphEdge] = Field(default_factory=list, description="List of graph edges")


class AgentGraphDefinition(BaseModel):
    """Static definition of a Swisper agent graph."""
    
    name: str = Field(..., description="Agent name (e.g., 'global_supervisor')")
    description: str = Field(..., description="Agent purpose and responsibilities")
    nodes: List[GraphNode] = Field(default_factory=list, description="Agent's graph nodes")
    edges: List[GraphEdge] = Field(default_factory=list, description="Agent's graph edges")


class SystemArchitectureData(BaseModel):
    """Collection of all agent graph definitions."""
    
    agents: List[AgentGraphDefinition] = Field(
        default_factory=list,
        description="List of all Swisper agent graphs"
    )

