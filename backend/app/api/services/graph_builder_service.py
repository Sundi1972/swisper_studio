"""
Graph Builder Service

Converts observation trees into graph structures for visualization
and provides static agent architecture definitions.
"""

import json
from pathlib import Path
from typing import List, Dict
from app.models.observation import Observation
from app.models.graph import (
    GraphNode,
    GraphEdge,
    GraphData,
    AgentGraphDefinition,
    SystemArchitectureData
)


# System node constants
START_NODE_ID = "__start__"
END_NODE_ID = "__end__"


class GraphBuilderService:
    """Service to build graph structures from observations and agent definitions."""
    
    def __init__(self):
        """Initialize service and load static agent graphs."""
        self._system_architecture: SystemArchitectureData | None = None
    
    def build_trace_graph(self, observations: List[Observation]) -> GraphData:
        """
        Convert observation tree to graph structure for visualization.
        
        Algorithm:
        1. Create nodes from observations
        2. Create edges from parent-child relationships
        3. Add START and END system nodes
        4. Connect orphan nodes to START/END
        
        Args:
            observations: List of observations for a trace
            
        Returns:
            GraphData with nodes and edges ready for vis-network
        """
        if not observations:
            # Empty trace: just START → END
            return GraphData(
                nodes=[
                    GraphNode(id=START_NODE_ID, label="Start", type="SYSTEM"),
                    GraphNode(id=END_NODE_ID, label="End", type="SYSTEM")
                ],
                edges=[
                    GraphEdge(from_node=START_NODE_ID, to_node=END_NODE_ID)
                ]
            )
        
        # Build nodes from observations
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        obs_by_id: Dict[str, Observation] = {}
        
        # Create node for each observation
        for obs in observations:
            obs_id_str = str(obs.id)
            obs_by_id[obs_id_str] = obs
            
            nodes.append(GraphNode(
                id=obs_id_str,
                label=obs.name,
                type=obs.type.value  # Convert enum to string
            ))
        
        # Create edges from parent-child relationships
        root_obs_ids: List[str] = []  # Observations with no parent
        
        for obs in observations:
            obs_id_str = str(obs.id)
            
            if obs.parent_observation_id is None:
                # Root observation (no parent)
                root_obs_ids.append(obs_id_str)
            else:
                # Has parent - create edge
                parent_id_str = str(obs.parent_observation_id)
                if parent_id_str in obs_by_id:
                    edges.append(GraphEdge(
                        from_node=parent_id_str,
                        to_node=obs_id_str
                    ))
        
        # Find leaf observations (no children)
        all_obs_ids = set(obs_by_id.keys())
        parent_obs_ids = {str(obs.parent_observation_id) 
                         for obs in observations 
                         if obs.parent_observation_id is not None}
        leaf_obs_ids = [obs_id for obs_id in all_obs_ids 
                       if obs_id not in parent_obs_ids]
        
        # Add START and END nodes
        nodes.insert(0, GraphNode(id=START_NODE_ID, label="Start", type="SYSTEM"))
        nodes.append(GraphNode(id=END_NODE_ID, label="End", type="SYSTEM"))
        
        # Connect START to root observations
        for root_id in root_obs_ids:
            edges.insert(0, GraphEdge(from_node=START_NODE_ID, to_node=root_id))
        
        # Connect leaf observations to END
        for leaf_id in leaf_obs_ids:
            edges.append(GraphEdge(from_node=leaf_id, to_node=END_NODE_ID))
        
        return GraphData(nodes=nodes, edges=edges)
    
    def get_system_architecture(self) -> SystemArchitectureData:
        """
        Get static agent graph definitions from JSON file.
        
        Returns:
            SystemArchitectureData with all agent graphs
        """
        if self._system_architecture is not None:
            return self._system_architecture
        
        # Load from JSON file
        data_dir = Path(__file__).parent.parent.parent / "data"
        agent_graphs_file = data_dir / "agent_graphs.json"
        
        if not agent_graphs_file.exists():
            # Fallback: return empty architecture
            return SystemArchitectureData(agents=[])
        
        with open(agent_graphs_file, "r") as f:
            data = json.load(f)
        
        # Parse JSON into Pydantic models
        self._system_architecture = SystemArchitectureData(**data)
        
        return self._system_architecture


# Singleton instance
graph_builder_service = GraphBuilderService()

