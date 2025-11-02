# Phase 3: Graph Visualization - Analysis

**Date:** November 2, 2025  
**Status:** Analysis Complete  
**Phase:** Phase 3 - Graph Visualization

---

## Executive Summary

Phase 3 delivers **two distinct visualization features**:

1. **System Architecture View** (Swisper Builder - NEW main navigation)
   - Static visualization of Swisper's LangGraph agent definitions
   - Parse Python agent files to extract graph structure
   - Future foundation for agent building/integration platform

2. **Single Trace Graph View** (Tracing submenu)
   - Dynamic visualization of actual trace execution
   - Convert observation tree → graph for single user request
   - Show which agents/nodes/tools were invoked

**Visualization Library:** vis-network v9.1.9 (standalone) - same as Langfuse

---

## 1. Visualization Library Research

### Langfuse Implementation (Production Reference)

**Library:** `vis-network` v9.1.9 (standalone version)

**Location in reference:** `reference/langfuse/web/src/features/trace-graph-view/`

**Key files analyzed:**
- `TraceGraphCanvas.tsx` - React component wrapping vis-network
- `buildGraphCanvasData.ts` - Converts observation tree → graph structure
- `types.ts` - Graph data types

**Why Langfuse chose vis-network:**
1. ✅ Hierarchical layout built-in (top-to-bottom flow perfect for execution traces)
2. ✅ Easy node styling (color-coded by observation type)
3. ✅ Interactive controls out-of-the-box (zoom, pan, node selection)
4. ✅ Performance-optimized for complex graphs
5. ✅ Minimal dependencies (standalone version available)

**Implementation highlights from Langfuse:**
```typescript
// Hierarchical layout configuration
layout: {
  hierarchical: {
    enabled: true,
    direction: "UD",  // Up-Down (top to bottom)
    levelSeparation: 60,
    nodeSpacing: 175,
    sortMethod: "hubsize"
  }
}

// Color-coded nodes by type
const getNodeStyle = (nodeType: string) => {
  switch (nodeType) {
    case "AGENT": return { border: "#c4b5fd", background: "#f3f4f6" };
    case "TOOL": return { border: "#fed7aa", background: "#f3f4f6" };
    case "GENERATION": return { border: "#f0abfc", background: "#f3f4f6" };
    case "SPAN": return { border: "#93c5fd", background: "#f3f4f6" };
    // ... more types
  }
}

// Interactive controls
- Zoom in/out buttons
- Reset view button
- Click nodes to select
- Drag to pan
```

**Data structure:**
```typescript
type GraphCanvasData = {
  nodes: GraphNodeData[];  // { id, label, type }
  edges: { from: string; to: string }[];
};
```

### Alternatives Considered

| Library | Pros | Cons | Verdict |
|---------|------|------|---------|
| **vis-network** | ✅ Proven by Langfuse<br>✅ Hierarchical layout<br>✅ Mature (v9)<br>✅ Interactive | Older API style | ✅ **RECOMMENDED** |
| React Flow | Modern React API<br>Good docs | More custom layout code<br>Larger bundle | Good alternative |
| D3.js | Maximum flexibility | Steep learning curve<br>More work | Overkill for MVP |
| Cytoscape.js | Scientific graphs | Complex API | Not needed |

**Decision:** Use **vis-network** (same as Langfuse)

**Reasons:**
1. Proven solution for trace visualization
2. Reference implementation available
3. Faster implementation (less custom code)
4. Perfect hierarchical layout for our use case
5. Smaller learning curve

---

## 2. Swisper Agent Architecture

### Agent Locations

**Path:** `reference/swisper/backend/app/api/services/agents/`

**Discovered agents:**
```
agents/
├── global_supervisor/        # Main orchestrator (routes to domain agents)
│   ├── global_supervisor.py
│   ├── nodes/
│   │   ├── user_interface_node.py
│   │   ├── global_planner_node.py
│   │   ├── agent_execution_node.py
│   │   ├── memory_node.py
│   │   ├── intent_classification_node.py
│   │   └── indexing_node.py
│   └── global_supervisor_state.py
│
├── productivity_agent/       # Email, calendar, tasks
│   ├── productivity_agent.py
│   ├── nodes/
│   │   ├── provider_selection_node.py
│   │   ├── productivity_planner_node.py
│   │   ├── productivity_write_node.py
│   │   └── productivity_tool_execution_node.py
│   └── productivity_agent_state.py
│
├── research_agent/           # Web search, real-time info
│   ├── research_agent.py
│   ├── agent_state.py
│   └── nodes/
│
├── wealth_agent/             # Financial data
│   ├── wealth_agent.py
│   ├── agent_state.py
│   └── nodes/
│
└── doc_agent/                # Document search (RAG)
    ├── doc_agent.py
    └── nodes/
```

### LangGraph Structure Pattern

**All agents follow this pattern:**

```python
from langgraph.graph import StateGraph, END

class AgentName:
    def __init__(self, ...):
        self._graph_cache = None
    
    async def build_graph(self):
        if self._graph_cache is not None:
            return self._graph_cache
        
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("node_name", node_function)
        graph.add_node("another_node", another_function)
        
        # Add edges
        graph.add_edge("node_name", "another_node")
        graph.add_conditional_edges("another_node", routing_function)
        
        # Set entry/finish
        graph.set_entry_point("node_name")
        graph.set_finish_point(END)
        
        self._graph_cache = graph.compile()
        return self._graph_cache
```

**Graph definition locations:**
- `global_supervisor/global_supervisor.py` - `build_graph()` method
- `productivity_agent/productivity_agent.py` - `build_graph()` method
- `research_agent/research_agent.py` - `build_graph()` method
- `wealth_agent/wealth_agent.py` - `build_graph()` method
- `doc_agent/doc_agent.py` - `build_graph()` method

---

## 3. Feature Specifications

### Feature 1: System Architecture View (Swisper Builder)

**Purpose:** Show all Swisper agent graphs (static definitions from code)

**Location:** NEW main navigation entry "Swisper Builder"

**Data source:** Parse Python agent files from Swisper reference code

**What to display:**
- List of all agents (global_supervisor, productivity_agent, research_agent, wealth_agent, doc_agent)
- For each agent: graph with nodes and edges
- Node types: Different colors/shapes per node type
- Future: Click agent to select/edit/build

**Implementation approach:**

**Option A: Static extraction (Phase 3 MVP)**
- Manually document graph structure from each agent's `build_graph()` method
- Store as JSON in SwisperStudio backend
- API endpoint returns pre-defined graph structure
- Frontend renders with vis-network

**Option B: Dynamic parsing (Future - Phase 4+)**
- Parse Python AST to extract StateGraph definitions
- Auto-detect nodes, edges, conditional routing
- More complex but automatically stays in sync

**Decision for Phase 3:** Option A (Static) - simpler, faster, MVP-appropriate

**Expected structure:**
```json
{
  "agents": [
    {
      "name": "global_supervisor",
      "description": "Main orchestrator",
      "nodes": [
        {"id": "intent_classification", "label": "Intent Classification", "type": "SPAN"},
        {"id": "memory", "label": "Memory", "type": "SPAN"},
        {"id": "planner", "label": "Global Planner", "type": "SPAN"},
        {"id": "agent_execution", "label": "Agent Execution", "type": "AGENT"},
        {"id": "ui_node", "label": "User Interface", "type": "GENERATION"}
      ],
      "edges": [
        {"from": "intent_classification", "to": "memory"},
        {"from": "memory", "to": "planner"},
        {"from": "planner", "to": "agent_execution"},
        {"from": "agent_execution", "to": "ui_node"}
      ]
    },
    {
      "name": "productivity_agent",
      "description": "Email, calendar, tasks",
      "nodes": [...],
      "edges": [...]
    }
    // ... more agents
  ]
}
```

---

### Feature 2: Single Trace Graph View (Tracing)

**Purpose:** Show how one user request flowed through system

**Location:** Tracing section → Trace detail page (new tab/view)

**Data source:** Observation tree from database

**What to display:**
- Nodes: Each observation (SPAN, GENERATION, TOOL, AGENT)
- Edges: Parent-child relationships from observation tree
- Start/End nodes: Special system nodes
- Node details: Click to see observation metadata

**Implementation approach:**
1. Backend: Convert observation tree → graph structure
2. Similar to Langfuse's `buildGraphCanvasData.ts` pattern
3. API endpoint: `GET /api/v1/traces/{trace_id}/graph`
4. Frontend: Render with vis-network using Langfuse patterns

**Graph building algorithm (from Langfuse):**
```typescript
// Group observations by step (or use parent_id for tree structure)
// Create nodes from unique observation names/types
// Create edges from parent-child relationships
// Add START and END system nodes
```

---

## 4. Technical Implementation Plan

### Backend Components

**1. Graph Builder Service**
- Location: `backend/app/api/services/graph_builder_service.py`
- Purpose: Convert observation tree → graph structure
- Methods:
  - `build_trace_graph(observations)` - For single trace view
  - `get_system_architecture()` - For static agent graphs

**2. Layout Algorithm**
- Use vis-network's built-in hierarchical layout
- No custom algorithm needed (vis-network handles it)

**3. Graph API Endpoints**

```python
# routes/traces.py
@router.get("/traces/{trace_id}/graph")
async def get_trace_graph(trace_id: uuid.UUID) -> GraphData:
    """Get graph structure for single trace"""
    observations = await db.get_observations_for_trace(trace_id)
    return graph_builder_service.build_trace_graph(observations)

# New routes/system_architecture.py
@router.get("/system-architecture")
async def get_system_architecture() -> SystemArchitectureData:
    """Get all agent graphs (static definitions)"""
    return graph_builder_service.get_system_architecture()
```

**4. Data Models**

```python
class GraphNode(BaseModel):
    id: str
    label: str
    type: str  # SPAN, GENERATION, TOOL, AGENT

class GraphEdge(BaseModel):
    from_node: str  # "from" is reserved keyword
    to_node: str

class GraphData(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

class AgentGraphDefinition(BaseModel):
    name: str
    description: str
    nodes: List[GraphNode]
    edges: List[GraphEdge]

class SystemArchitectureData(BaseModel):
    agents: List[AgentGraphDefinition]
```

---

### Frontend Components

**1. Swisper Builder Section (NEW)**

**Navigation structure:**
```
Main Navigation:
├── Projects (existing)
├── Swisper Builder (NEW)
│   └── System Architecture (default page)
└── ... other sections
```

**Components:**
```
frontend/src/features/swisper-builder/
├── components/
│   ├── SystemArchitectureView.tsx   # Main view component
│   ├── AgentGraphCanvas.tsx         # vis-network wrapper
│   ├── AgentSelector.tsx            # List of agents
│   └── NodeDetailsPanel.tsx         # Node info sidebar
├── hooks/
│   └── useSystemArchitecture.ts     # Fetch agent graphs
└── index.tsx                        # Route entry
```

**2. Trace Graph View (Enhancement)**

**Location:** Tracing → Trace Detail → New "Graph" tab

**Components:**
```
frontend/src/features/traces/
├── components/
│   ├── TraceDetail.tsx              # MODIFY: Add graph tab
│   ├── TraceGraphView.tsx           # NEW: Graph visualization
│   └── TraceGraphCanvas.tsx         # NEW: vis-network wrapper
└── hooks/
    └── useTraceGraph.ts             # NEW: Fetch graph data
```

**Tab structure (TraceDetail.tsx):**
```tsx
<Tabs value={activeTab}>
  <Tab label="Tree" />           {/* Existing */}
  <Tab label="Graph" />          {/* NEW */}
  <Tab label="Timeline" />       {/* Future */}
  <Tab label="JSON" />           {/* Future */}
</Tabs>
```

**3. Shared Graph Components**

```
frontend/src/components/graph/
├── GraphCanvas.tsx              # Reusable vis-network wrapper
├── GraphControls.tsx            # Zoom/pan/reset buttons
└── types.ts                     # TypeScript types
```

---

### vis-network Integration

**Installation:**
```bash
cd frontend
npm install vis-network@^9.1.9
```

**Basic usage pattern (from Langfuse):**
```tsx
import { Network, DataSet } from "vis-network/standalone";

export const GraphCanvas: React.FC<GraphCanvasProps> = ({ graph }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const networkRef = useRef<Network | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const nodesDataSet = new DataSet(graph.nodes);
    const network = new Network(
      containerRef.current,
      { nodes: nodesDataSet, edges: graph.edges },
      {
        layout: {
          hierarchical: {
            enabled: true,
            direction: "UD",
            levelSeparation: 60,
            nodeSpacing: 175
          }
        },
        nodes: {
          shape: "box",
          margin: 10,
          font: { size: 14 }
        },
        edges: {
          arrows: { to: { enabled: true } }
        }
      }
    );

    networkRef.current = network;

    return () => {
      network.destroy();
    };
  }, [graph]);

  return <div ref={containerRef} className="h-full w-full" />;
};
```

---

## 5. Color Scheme (from Langfuse)

**Node colors by observation type:**

```typescript
const NODE_COLORS = {
  AGENT: { border: "#c4b5fd", background: "#f3f4f6" },    // purple
  TOOL: { border: "#fed7aa", background: "#f3f4f6" },     // orange
  GENERATION: { border: "#f0abfc", background: "#f3f4f6" }, // fuchsia
  SPAN: { border: "#93c5fd", background: "#f3f4f6" },     // blue
  CHAIN: { border: "#f9a8d4", background: "#f3f4f6" },    // pink
  RETRIEVER: { border: "#5eead4", background: "#f3f4f6" }, // teal
  EVENT: { border: "#6ee7b7", background: "#f3f4f6" },    // green
  EMBEDDING: { border: "#fbbf24", background: "#f3f4f6" }, // amber
  GUARDRAIL: { border: "#fca5a5", background: "#f3f4f6" }, // red
  SYSTEM: { border: "#d1d5db", background: "#f3f4f6" }    // gray
};
```

---

## 6. Key Learnings from Analysis

### From Langfuse

1. ✅ **vis-network works well** for hierarchical execution traces
2. ✅ **Hierarchical layout** is perfect (top-to-bottom flow)
3. ✅ **Color-coded nodes** make types immediately obvious
4. ✅ **Interactive controls** (zoom/pan/reset) are essential
5. ✅ **System nodes** (START/END) provide clear entry/exit points
6. ✅ **Click to select** nodes for details works well

### From Swisper

1. ✅ **All agents use StateGraph** from LangGraph
2. ✅ **Graph defined in `build_graph()` method** - consistent pattern
3. ✅ **5 main agents** to visualize in system architecture view
4. ✅ **Nodes are Python functions** in `nodes/` directory
5. ✅ **Conditional edges** use routing functions

### Design Decisions

**For System Architecture View:**
- Use **static JSON** definitions for MVP (Option A)
- Manually document each agent's graph structure
- Store in backend (not parsed from Python)
- Future enhancement: AST parsing for auto-sync

**For Trace Graph View:**
- **Backend builds graph** from observation tree
- Similar algorithm to Langfuse's `buildGraphCanvasData`
- Frontend just renders (separation of concerns)

**Shared Patterns:**
- Both views use same `GraphCanvas` component
- Both use same color scheme
- Both use vis-network hierarchical layout
- Different data sources (static vs. dynamic)

---

## 7. Dependencies

**Frontend:**
```json
{
  "dependencies": {
    "vis-network": "^9.1.9"
  }
}
```

**Backend:**
- No new dependencies (use existing SQLModel, FastAPI, Pydantic)

---

## 8. Success Criteria

**System Architecture View:**
- [ ] Can see all 5 Swisper agents
- [ ] Each agent shows nodes and edges
- [ ] Nodes color-coded by type
- [ ] Can zoom/pan/reset view
- [ ] Loads in <1 second (static data)

**Trace Graph View:**
- [ ] Single trace displays as visual graph
- [ ] Nodes show observation types with colors
- [ ] Edges show parent-child flow
- [ ] Click node → see observation details
- [ ] Zoom/pan controls work
- [ ] Graph loads in <2 seconds

---

## 9. Implementation Priority

**Week 1: Backend**
1. Graph builder service
2. Static agent graph definitions (JSON)
3. API endpoints (trace graph + system architecture)
4. Tests

**Week 2: Frontend**
1. Install vis-network
2. Shared GraphCanvas component
3. System Architecture View (Swisper Builder section)
4. Trace Graph View (tab in trace detail)
5. Integration with existing navigation

---

## 10. Future Enhancements (Post-MVP)

**Not in Phase 3:**
- [ ] Dynamic Python AST parsing for agent graphs
- [ ] Agent editing/building UI
- [ ] Agent marketplace integration
- [ ] Custom node styling per agent
- [ ] Graph export (PNG/SVG/JSON)
- [ ] Graph comparison (trace A vs. trace B)
- [ ] Performance metrics overlay on graph
- [ ] Timeline view alongside graph view

---

## References

**Langfuse Implementation:**
- `reference/langfuse/web/src/features/trace-graph-view/`
- `reference/langfuse/web/package.json` (vis-network version)

**Swisper Agents:**
- `reference/swisper/backend/app/api/services/agents/*/`

**vis-network Documentation:**
- Official docs: https://visjs.github.io/vis-network/docs/network/
- Examples: https://visjs.github.io/vis-network/examples/

---

**Analysis Complete:** November 2, 2025  
**Ready for:** Detailed Phase 3 Sub-Plan

