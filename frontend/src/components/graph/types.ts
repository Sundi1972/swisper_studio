// Graph visualization types
// Based on backend models: backend/app/models/graph.py

export interface GraphNode {
  id: string;
  label: string;
  type: string;
}

export interface GraphEdge {
  from: string; // Backend serializes as "from" (Pydantic alias)
  to: string; // Backend serializes as "to" (Pydantic alias)
  conditional?: boolean; // True if conditional edge (if/else routing)
  label?: string; // Label for conditional edges (e.g., "if simple_chat")
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface AgentGraphDefinition {
  name: string;
  description: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface SystemArchitectureData {
  agents: AgentGraphDefinition[];
}

