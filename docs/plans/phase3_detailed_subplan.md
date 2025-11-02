# Phase 3: Graph Visualization - Detailed Sub-Plan

**Date:** November 2, 2025  
**Duration:** 2 weeks  
**Status:** Week 1 Backend COMPLETE ✅ | Week 2 Frontend IN PROGRESS  
**Analysis:** `docs/analysis/phase3_visualization_analysis.md`

---

## ✅ Week 1 Backend - COMPLETED (November 2, 2025)

**Status:** All backend implementation complete and tested

**Files Created:**
- ✅ `backend/app/models/graph.py` - Graph data models (GraphNode, GraphEdge, GraphData, AgentGraphDefinition, SystemArchitectureData)
- ✅ `backend/app/data/agent_graphs.json` - Static agent definitions (5 agents: global_supervisor, productivity_agent, research_agent, wealth_agent, doc_agent)
- ✅ `backend/app/api/services/graph_builder_service.py` - Graph conversion logic (observation tree → graph, system architecture loader)
- ✅ `backend/app/api/routes/system_architecture.py` - System architecture API endpoint
- ✅ `backend/tests/api/services/test_graph_builder_service.py` - Service tests (6 tests)
- ✅ `backend/tests/api/test_system_architecture.py` - API endpoint tests (3 tests)

**Files Modified:**
- ✅ `backend/app/api/routes/traces.py` - Added `GET /traces/{id}/graph` endpoint
- ✅ `backend/app/main.py` - Registered system architecture router
- ✅ `backend/tests/api/test_traces.py` - Added graph endpoint tests (2 tests)

**API Endpoints:**
- ✅ `GET /api/v1/traces/{trace_id}/graph` - Returns graph structure for single trace visualization
- ✅ `GET /api/v1/system-architecture` - Returns all 5 agent graph definitions

**Test Results:**
- ✅ **57/57 tests passing** (46 existing + 11 new)
- ✅ All tests executed in Docker containers with verbose mode (-vv)
- ✅ TDD workflow followed: Red → Green → Refactor
- ✅ No regressions in existing functionality

**Next:** Week 2 Frontend Implementation (see handover: `PHASE3_WEEK2_HANDOVER.md`)

---

## Executive Summary

Phase 3 delivers TWO visualization features using **vis-network** library:

1. **System Architecture View** (Swisper Builder - NEW main navigation)
   - Show all Swisper agent graphs (static from Python definitions)
   - 5 agents: global_supervisor, productivity_agent, research_agent, wealth_agent, doc_agent

2. **Single Trace Graph View** (Tracing submenu - new tab)
   - Show execution flow for one user request
   - Convert observation tree → interactive graph

**Visualization Library:** vis-network v9.1.9 (same as Langfuse - proven solution)

---

## Week 1: Backend Implementation

### Day 1-2: Graph Builder Service

**Files to Create:**

**1. `backend/app/api/services/graph_builder_service.py`**
```python
# Service to convert observation tree → graph structure
# AND provide static agent graph definitions

class GraphBuilderService:
    def build_trace_graph(self, observations: List[Observation]) -> GraphData:
        """Convert observation tree to graph structure for vis-network"""
        # Similar to Langfuse's buildGraphCanvasData.ts
        # Group by parent_id to build tree
        # Create nodes from observations
        # Create edges from parent-child relationships
        # Add START/END system nodes
        
    def get_system_architecture(self) -> SystemArchitectureData:
        """Return static agent graph definitions"""
        # Return pre-defined JSON structure
        # 5 agents with their nodes and edges
```

**2. `backend/app/models/graph.py`** (New models)
```python
class GraphNode(BaseModel):
    id: str
    label: str
    type: str  # SPAN, GENERATION, TOOL, AGENT

class GraphEdge(BaseModel):
    from_node: str  # "from" is reserved keyword in Python
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

**3. `backend/app/data/agent_graphs.json`** (Static data)
```json
{
  "agents": [
    {
      "name": "global_supervisor",
      "description": "Main orchestrator that routes to domain agents",
      "nodes": [
        {"id": "intent_classification", "label": "Intent Classification", "type": "SPAN"},
        {"id": "memory", "label": "Memory", "type": "SPAN"},
        {"id": "planner", "label": "Global Planner", "type": "SPAN"},
        {"id": "agent_execution", "label": "Agent Execution", "type": "AGENT"},
        {"id": "ui_node", "label": "User Interface", "type": "GENERATION"}
      ],
      "edges": [
        {"from_node": "intent_classification", "to_node": "memory"},
        {"from_node": "memory", "to_node": "planner"},
        {"from_node": "planner", "to_node": "agent_execution"},
        {"from_node": "agent_execution", "to_node": "ui_node"}
      ]
    },
    {
      "name": "productivity_agent",
      "description": "Email, calendar, and task management",
      "nodes": [
        {"id": "provider_selection", "label": "Provider Selection", "type": "SPAN"},
        {"id": "planner", "label": "Productivity Planner", "type": "SPAN"},
        {"id": "write", "label": "Productivity Write", "type": "GENERATION"},
        {"id": "tool_execution", "label": "Tool Execution", "type": "TOOL"}
      ],
      "edges": [
        {"from_node": "provider_selection", "to_node": "planner"},
        {"from_node": "planner", "to_node": "write"},
        {"from_node": "write", "to_node": "tool_execution"}
      ]
    },
    {
      "name": "research_agent",
      "description": "Web search and real-time information",
      "nodes": [
        {"id": "research_planner", "label": "Research Planner", "type": "SPAN"},
        {"id": "search", "label": "Search", "type": "TOOL"},
        {"id": "evaluator", "label": "Evaluator", "type": "SPAN"}
      ],
      "edges": [
        {"from_node": "research_planner", "to_node": "search"},
        {"from_node": "search", "to_node": "evaluator"}
      ]
    },
    {
      "name": "wealth_agent",
      "description": "Financial data retrieval",
      "nodes": [
        {"id": "wealth_planner", "label": "Wealth Planner", "type": "SPAN"},
        {"id": "data_fetch", "label": "Data Fetch", "type": "TOOL"}
      ],
      "edges": [
        {"from_node": "wealth_planner", "to_node": "data_fetch"}
      ]
    },
    {
      "name": "doc_agent",
      "description": "Document search (RAG)",
      "nodes": [
        {"id": "query_processor", "label": "Query Processor", "type": "SPAN"},
        {"id": "retrieval", "label": "Retrieval", "type": "RETRIEVER"},
        {"id": "response_generator", "label": "Response Generator", "type": "GENERATION"}
      ],
      "edges": [
        {"from_node": "query_processor", "to_node": "retrieval"},
        {"from_node": "retrieval", "to_node": "response_generator"}
      ]
    }
  ]
}
```

**Implementation Details:**
- Graph builder converts observation parent_id → edges
- Observation type maps to node color
- START/END nodes added automatically
- Edge direction: parent → child

---

### Day 3: API Endpoints

**Files to Modify:**

**1. `backend/app/api/routes/traces.py`** (Add graph endpoint)
```python
@router.get("/traces/{trace_id}/graph", response_model=GraphData)
async def get_trace_graph(
    trace_id: uuid.UUID,
    session: Session = Depends(get_session)
) -> GraphData:
    """Get graph structure for single trace visualization"""
    # Fetch all observations for this trace
    observations = await fetch_observations_for_trace(session, trace_id)
    
    if not observations:
        raise HTTPException(status_code=404, detail="Trace not found")
    
    # Build graph using service
    graph = graph_builder_service.build_trace_graph(observations)
    return graph
```

**Files to Create:**

**2. `backend/app/api/routes/system_architecture.py`** (New route file)
```python
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.api.services.graph_builder_service import graph_builder_service
from app.models.graph import SystemArchitectureData

router = APIRouter(prefix="/system-architecture", tags=["system-architecture"])

@router.get("", response_model=SystemArchitectureData)
async def get_system_architecture() -> SystemArchitectureData:
    """Get all Swisper agent graphs (static definitions)"""
    return graph_builder_service.get_system_architecture()
```

**3. Modify `backend/app/main.py`** (Register new route)
```python
from app.api.routes import system_architecture

app.include_router(system_architecture.router, prefix="/api/v1")
```

---

### Day 4-5: Testing

**Files to Create:**

**1. `backend/tests/api/services/test_graph_builder_service.py`**
```python
@pytest.mark.asyncio
async def test_build_trace_graph_single_observation(session):
    """Test: Single observation creates single-node graph"""
    # Create test trace with 1 observation
    # Build graph
    # Assert: 1 node + START + END = 3 nodes
    # Assert: 2 edges (START→obs, obs→END)

@pytest.mark.asyncio
async def test_build_trace_graph_nested_observations(session):
    """Test: Nested observations create tree structure"""
    # Create trace with parent-child observations
    # Build graph
    # Assert: Correct number of nodes
    # Assert: Edges follow parent-child relationships

@pytest.mark.asyncio
async def test_build_trace_graph_observation_types(session):
    """Test: Different observation types preserved"""
    # Create observations with different types (SPAN, GENERATION, TOOL)
    # Build graph
    # Assert: Node types match observation types

@pytest.mark.asyncio
async def test_get_system_architecture():
    """Test: Returns all 5 agent definitions"""
    # Call service
    # Assert: 5 agents returned
    # Assert: Each has nodes and edges
```

**2. `backend/tests/api/test_system_architecture.py`**
```python
@pytest.mark.asyncio
async def test_get_system_architecture_endpoint(client):
    """Test: GET /api/v1/system-architecture returns agent graphs"""
    # Call endpoint
    # Assert: 200 status
    # Assert: Returns SystemArchitectureData schema
    # Assert: Contains 5 agents

@pytest.mark.asyncio
async def test_get_system_architecture_structure(client):
    """Test: Agent graphs have correct structure"""
    # Call endpoint
    # Get global_supervisor agent
    # Assert: Has expected nodes (intent, memory, planner, etc.)
    # Assert: Has expected edges
```

**3. Modify `backend/tests/api/test_traces.py`** (Add graph tests)
```python
@pytest.mark.asyncio
async def test_get_trace_graph_success(client, test_trace):
    """Test: GET /api/v1/traces/{id}/graph returns graph"""
    # Call graph endpoint
    # Assert: 200 status
    # Assert: Returns GraphData schema
    # Assert: Has nodes and edges

@pytest.mark.asyncio
async def test_get_trace_graph_not_found(client):
    """Test: GET /api/v1/traces/{invalid_id}/graph returns 404"""
    # Call with non-existent trace_id
    # Assert: 404 status
```

**Test Execution (Docker containers with verbose mode):**
```bash
# Update container with latest code
docker compose cp backend/app/. backend:/code/app/
docker compose cp backend/tests/. backend:/code/tests/

# Run tests in container (verbose mode)
docker compose exec backend pytest tests/api/services/test_graph_builder_service.py -vv
docker compose exec backend pytest tests/api/test_system_architecture.py -vv
docker compose exec backend pytest tests/api/test_traces.py::test_get_trace_graph_success -vv
```

**Expected test count:** ~8 new tests

---

## Week 2: Frontend Implementation

### Day 1-2: Setup & Shared Components

**Installation:**
```bash
cd frontend
npm install vis-network@^9.1.9
```

**Files to Create:**

**1. `frontend/src/components/graph/GraphCanvas.tsx`**
```tsx
// Reusable vis-network wrapper (adapted from Langfuse)
import React, { useEffect, useRef } from "react";
import { Network, DataSet } from "vis-network/standalone";
import { Button } from "@mui/material";
import { ZoomIn, ZoomOut, RestartAlt } from "@mui/icons-material";

interface GraphCanvasProps {
  graph: GraphData;
  onNodeClick?: (nodeId: string) => void;
}

export const GraphCanvas: React.FC<GraphCanvasProps> = ({ graph, onNodeClick }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const networkRef = useRef<Network | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const nodesDataSet = new DataSet(graph.nodes.map(node => ({
      id: node.id,
      label: node.label,
      color: getNodeColor(node.type)
    })));

    const network = new Network(
      containerRef.current,
      { nodes: nodesDataSet, edges: graph.edges },
      {
        layout: {
          hierarchical: {
            enabled: true,
            direction: "UD",  // top to bottom
            levelSeparation: 60,
            nodeSpacing: 175
          }
        },
        nodes: {
          shape: "box",
          margin: 10,
          font: { size: 14, color: "#000000" },
          borderWidth: 2
        },
        edges: {
          arrows: { to: { enabled: true } },
          color: { color: "#64748b" }
        }
      }
    );

    if (onNodeClick) {
      network.on("click", (params) => {
        if (params.nodes.length > 0) {
          onNodeClick(params.nodes[0]);
        }
      });
    }

    networkRef.current = network;

    return () => {
      network.destroy();
    };
  }, [graph, onNodeClick]);

  const handleZoomIn = () => {
    if (networkRef.current) {
      const scale = networkRef.current.getScale();
      networkRef.current.moveTo({ scale: scale * 1.2 });
    }
  };

  const handleZoomOut = () => {
    if (networkRef.current) {
      const scale = networkRef.current.getScale();
      networkRef.current.moveTo({ scale: scale / 1.2 });
    }
  };

  const handleReset = () => {
    if (networkRef.current) {
      networkRef.current.fit();
    }
  };

  return (
    <div className="relative h-full w-full">
      <div className="absolute top-2 right-2 z-10 flex gap-1">
        <Button size="small" onClick={handleZoomIn}><ZoomIn /></Button>
        <Button size="small" onClick={handleZoomOut}><ZoomOut /></Button>
        <Button size="small" onClick={handleReset}><RestartAlt /></Button>
      </div>
      <div ref={containerRef} className="h-full w-full" />
    </div>
  );
};

// Color scheme from Langfuse (adapted for our types)
function getNodeColor(type: string) {
  const colors = {
    AGENT: { border: "#c4b5fd", background: "#f3f4f6" },
    TOOL: { border: "#fed7aa", background: "#f3f4f6" },
    GENERATION: { border: "#f0abfc", background: "#f3f4f6" },
    SPAN: { border: "#93c5fd", background: "#f3f4f6" },
    RETRIEVER: { border: "#5eead4", background: "#f3f4f6" },
    EVENT: { border: "#6ee7b7", background: "#f3f4f6" },
    SYSTEM: { border: "#d1d5db", background: "#f3f4f6" }
  };
  return colors[type] || colors.SPAN;
}
```

**2. `frontend/src/components/graph/types.ts`**
```typescript
export interface GraphNode {
  id: string;
  label: string;
  type: string;
}

export interface GraphEdge {
  from_node: string;
  to_node: string;
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
```

---

### Day 3-4: System Architecture View (Swisper Builder)

**Files to Create:**

**1. `frontend/src/features/swisper-builder/SystemArchitectureView.tsx`**
```tsx
import React, { useState } from "react";
import { Box, Typography, List, ListItem, ListItemButton, Paper } from "@mui/material";
import { useSystemArchitecture } from "./hooks/useSystemArchitecture";
import { GraphCanvas } from "../../components/graph/GraphCanvas";

export const SystemArchitectureView: React.FC = () => {
  const { data: architecture, isLoading } = useSystemArchitecture();
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

  if (isLoading) return <Typography>Loading...</Typography>;
  if (!architecture) return <Typography>No data</Typography>;

  const currentAgent = architecture.agents.find(a => a.name === selectedAgent) 
    || architecture.agents[0];

  return (
    <Box sx={{ display: "flex", height: "calc(100vh - 120px)" }}>
      {/* Sidebar: Agent list */}
      <Paper sx={{ width: 280, mr: 2 }}>
        <Typography variant="h6" sx={{ p: 2 }}>Agents</Typography>
        <List>
          {architecture.agents.map((agent) => (
            <ListItemButton
              key={agent.name}
              selected={selectedAgent === agent.name}
              onClick={() => setSelectedAgent(agent.name)}
            >
              <Typography>{agent.name}</Typography>
            </ListItemButton>
          ))}
        </List>
      </Paper>

      {/* Main: Graph visualization */}
      <Paper sx={{ flex: 1, p: 2 }}>
        <Typography variant="h5" gutterBottom>{currentAgent.name}</Typography>
        <Typography variant="body2" color="textSecondary" gutterBottom>
          {currentAgent.description}
        </Typography>
        <Box sx={{ height: "calc(100% - 80px)", mt: 2 }}>
          <GraphCanvas 
            graph={{
              nodes: currentAgent.nodes,
              edges: currentAgent.edges
            }}
          />
        </Box>
      </Paper>
    </Box>
  );
};
```

**2. `frontend/src/features/swisper-builder/hooks/useSystemArchitecture.ts`**
```typescript
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../../lib/api-client";
import { SystemArchitectureData } from "../../../components/graph/types";

export function useSystemArchitecture() {
  return useQuery({
    queryKey: ["system-architecture"],
    queryFn: async () => {
      const response = await apiClient.get<SystemArchitectureData>(
        "/system-architecture"
      );
      return response.data;
    }
  });
}
```

**3. `frontend/src/features/swisper-builder/index.tsx`**
```tsx
export { SystemArchitectureView } from "./SystemArchitectureView";
```

**4. Modify `frontend/src/app.tsx`** (Add navigation route)
```tsx
// Add to routes
<Route path="/swisper-builder" element={<SystemArchitectureView />} />
```

**5. Modify navigation sidebar** (Add Swisper Builder entry)
```tsx
// In ProjectLayout.tsx or AppNavigation.tsx
const navItems = [
  { label: "Projects", path: "/projects" },
  { label: "Swisper Builder", path: "/swisper-builder" },  // NEW
  // ... other items
];
```

---

### Day 5: Trace Graph View

**Files to Create:**

**1. `frontend/src/features/traces/components/TraceGraphView.tsx`**
```tsx
import React from "react";
import { Box, Typography, CircularProgress } from "@mui/material";
import { useTraceGraph } from "../hooks/useTraceGraph";
import { GraphCanvas } from "../../../components/graph/GraphCanvas";

interface TraceGraphViewProps {
  traceId: string;
}

export const TraceGraphView: React.FC<TraceGraphViewProps> = ({ traceId }) => {
  const { data: graph, isLoading } = useTraceGraph(traceId);

  if (isLoading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!graph || graph.nodes.length === 0) {
    return (
      <Typography sx={{ p: 4 }} color="textSecondary">
        No graph data available for this trace
      </Typography>
    );
  }

  return (
    <Box sx={{ height: "600px", p: 2 }}>
      <GraphCanvas graph={graph} />
    </Box>
  );
};
```

**2. `frontend/src/features/traces/hooks/useTraceGraph.ts`**
```typescript
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../../lib/api-client";
import { GraphData } from "../../../components/graph/types";

export function useTraceGraph(traceId: string) {
  return useQuery({
    queryKey: ["trace-graph", traceId],
    queryFn: async () => {
      const response = await apiClient.get<GraphData>(
        `/traces/${traceId}/graph`
      );
      return response.data;
    },
    enabled: !!traceId
  });
}
```

**Files to Modify:**

**3. `frontend/src/features/traces/components/TraceDetail.tsx`**
```tsx
// Add Graph tab
import { TraceGraphView } from "./TraceGraphView";

export const TraceDetail: React.FC<TraceDetailProps> = ({ traceId }) => {
  const [activeTab, setActiveTab] = useState<"tree" | "graph">("tree");

  return (
    <Box>
      <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)}>
        <Tab label="Tree" value="tree" />
        <Tab label="Graph" value="graph" />  {/* NEW */}
      </Tabs>

      {activeTab === "tree" && <ObservationTree traceId={traceId} />}
      {activeTab === "graph" && <TraceGraphView traceId={traceId} />}  {/* NEW */}
    </Box>
  );
};
```

---

## Definition of Done

### Documentation
- [x] Analysis document created (`phase3_visualization_analysis.md`)
- [ ] Sub-plan reviewed and approved (this document)
- [ ] OpenAPI spec regenerated (after API changes)
- [ ] README updated with new features

### Backend
- [ ] Graph builder service implemented
- [ ] Static agent graphs defined (JSON)
- [ ] API endpoints created (trace graph + system architecture)
- [ ] 8+ tests passing (all in Docker containers with -vv)
- [ ] Linting passes (`ruff`, `black`, `mypy`)

### Frontend
- [ ] vis-network installed (v9.1.9)
- [ ] GraphCanvas component created
- [ ] System Architecture View implemented
- [ ] Trace Graph View tab added
- [ ] Navigation updated (Swisper Builder entry)
- [ ] TypeScript compiles (`tsc --noEmit`)
- [ ] Linting passes (`eslint`, `prettier`)

### Integration
- [ ] Backend API tested via Postman/curl
- [ ] Frontend can fetch and render graphs
- [ ] System architecture shows all 5 agents
- [ ] Trace graph displays for test trace
- [ ] Zoom/pan/reset controls work
- [ ] Node colors match observation types

### Performance
- [ ] System architecture loads in <1 second
- [ ] Trace graph loads in <2 seconds
- [ ] No console errors
- [ ] No memory leaks on component unmount

---

## Testing Strategy

### Backend Tests (TDD - Red/Green/Refactor)

**Test Execution:**
```bash
# BEFORE running tests: Update container
docker compose cp backend/app/. backend:/code/app/
docker compose cp backend/tests/. backend:/code/tests/

# Run tests in Docker (VERBOSE mode)
docker compose exec backend pytest tests/api/services/test_graph_builder_service.py -vv
docker compose exec backend pytest tests/api/test_system_architecture.py -vv
docker compose exec backend pytest tests/api/test_traces.py -vv

# Watch terminal output to verify red → green
```

**Test categories:**
1. Graph builder service (unit tests)
2. API endpoints (integration tests)
3. Data models (validation tests)

### Frontend Testing

**Manual testing:**
1. Navigate to Swisper Builder
2. Select different agents
3. Verify graph renders correctly
4. Test zoom/pan/reset controls
5. Navigate to trace detail
6. Switch to Graph tab
7. Verify trace graph renders

**Browser testing:**
- Chrome/Edge (primary)
- Firefox (secondary)
- Safari (if available)

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| vis-network bundle size | Low | Low | Use standalone version (164kb) |
| Graph layout issues | Medium | Medium | Use Langfuse's proven config |
| Static agent graphs out of sync | High | Low | Document update process, future: AST parsing |
| Performance with large traces | Medium | Medium | Test with 100+ observations, add node limit if needed |

---

## Estimated Effort

**Backend:** 3 days
- Day 1-2: Graph builder service + models
- Day 3: API endpoints
- Day 4-5: Tests

**Frontend:** 4 days
- Day 1-2: Setup + shared components
- Day 3-4: System Architecture View
- Day 5: Trace Graph View

**Total:** 7 days (within 2-week timeline, buffer included)

---

## Success Criteria Checklist

**System Architecture View:**
- [ ] Shows all 5 Swisper agents
- [ ] Each agent displays correct nodes and edges
- [ ] Nodes color-coded by type
- [ ] Zoom/pan/reset controls work
- [ ] Loads in <1 second
- [ ] Can switch between agents smoothly

**Trace Graph View:**
- [ ] Displays observation tree as graph
- [ ] Nodes show correct observation types
- [ ] Edges show parent-child flow
- [ ] Zoom/pan/reset controls work
- [ ] Loads in <2 seconds
- [ ] Accessible from trace detail page

**Code Quality:**
- [ ] All tests pass (backend: Docker -vv, frontend: manual)
- [ ] Linting passes (backend + frontend)
- [ ] Type checking passes (Python + TypeScript)
- [ ] No console errors
- [ ] Following cursor rules (TDD, implementation discipline)

---

**Ready for Approval:** November 2, 2025  
**Approval Status:** PENDING USER CONFIRMATION

**Next Step:** Get user approval, then proceed to implementation (Step 4: TDD Red)

