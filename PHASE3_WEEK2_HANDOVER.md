# 🚀 Phase 3 Week 2 Handover - Frontend Implementation

**Date:** November 2, 2025  
**Current Status:** Week 1 Backend COMPLETE ✅  
**Next:** Week 2 Frontend (Graph Visualization UI)  
**Branch:** `feature/week-1-backend-foundation` (committed)  
**Reference Plan:** `docs/plans/phase3_detailed_subplan.md`

---

## ✅ What's Complete (Week 1: Backend)

**Completed:** November 2, 2025  
**Duration:** 1 day (planned 7 days - ahead of schedule!)  
**Test Results:** 57/57 tests passing ✅

### Backend Components Built

**1. Graph Data Models** (`backend/app/models/graph.py`)
- `GraphNode` - Represents a node in the graph (id, label, type)
- `GraphEdge` - Represents an edge between nodes (from_node, to_node)
- `GraphData` - Complete graph structure (nodes + edges)
- `AgentGraphDefinition` - Static agent graph definition
- `SystemArchitectureData` - Collection of all agent graphs

**2. Graph Builder Service** (`backend/app/api/services/graph_builder_service.py`)
- `build_trace_graph(observations)` - Converts observation tree → graph
  - Algorithm: Creates nodes from observations, edges from parent-child relationships
  - Adds START and END system nodes
  - Connects orphan nodes appropriately
- `get_system_architecture()` - Loads static agent graphs from JSON
  - Returns all 5 agent definitions
  - Cached for performance

**3. Static Agent Graphs** (`backend/app/data/agent_graphs.json`)
- 5 Swisper agents defined:
  - `global_supervisor` - Main orchestrator (6 nodes, 5 edges)
  - `productivity_agent` - Email/calendar (4 nodes, 3 edges)
  - `research_agent` - Web search (3 nodes, 2 edges)
  - `wealth_agent` - Financial data (2 nodes, 1 edge)
  - `doc_agent` - Document RAG (3 nodes, 2 edges)

**4. API Endpoints**
- `GET /api/v1/traces/{trace_id}/graph` - Get graph for single trace
  - Returns: GraphData (nodes + edges)
  - Use case: Trace Graph View in UI
- `GET /api/v1/system-architecture` - Get all agent graphs
  - Returns: SystemArchitectureData (5 agents)
  - Use case: Swisper Builder UI

**5. Tests** (11 new tests, all passing)
- Service tests: 6 tests (`test_graph_builder_service.py`)
- API tests: 5 tests (`test_system_architecture.py` + `test_traces.py`)
- TDD workflow followed: Red → Green → Refactor

---

## 🎯 What's Next (Week 2: Frontend)

**Goal:** Build visualization UI using vis-network library

**Reference:** `docs/plans/phase3_detailed_subplan.md` (Week 2 section)

### Feature 1: System Architecture View (Swisper Builder)

**Location:** NEW main navigation entry "Swisper Builder"

**What to Build:**
- `frontend/src/components/graph/GraphCanvas.tsx` - Reusable vis-network wrapper
- `frontend/src/features/swisper-builder/SystemArchitectureView.tsx` - Main view
- `frontend/src/features/swisper-builder/hooks/useSystemArchitecture.ts` - Data fetching

**UI Structure:**
```
┌─────────────────────────────────────────┐
│ Swisper Builder                          │
├─────────────────────────────────────────┤
│ Sidebar      │ Main Graph View           │
│              │                           │
│ Agents:      │  [Graph Canvas]          │
│ • global_... │                           │
│ • product... │  Nodes: colored by type  │
│ • research...│  Edges: execution flow   │
│ • wealth_... │  Controls: Zoom/Pan/Reset│
│ • doc_agent  │                           │
└─────────────────────────────────────────┘
```

**Data Flow:**
1. Component mounts → Call `useSystemArchitecture()` hook
2. Hook calls `GET /api/v1/system-architecture`
3. Receive 5 agent graphs
4. Render in sidebar (agent list) + canvas (graph)
5. Click agent → Update canvas with that agent's graph

---

### Feature 2: Trace Graph View (Tracing Enhancement)

**Location:** Tracing → Trace Detail → NEW "Graph" tab

**What to Build:**
- `frontend/src/features/traces/components/TraceGraphView.tsx` - Graph tab content
- `frontend/src/features/traces/hooks/useTraceGraph.ts` - Data fetching
- Modify `frontend/src/features/traces/components/TraceDetail.tsx` - Add graph tab

**UI Structure:**
```
┌─────────────────────────────────────────┐
│ Trace Detail                             │
├─────────────────────────────────────────┤
│ [Tree] [Graph] [Timeline] [JSON]        │
│                                          │
│  Graph View:                             │
│                                          │
│       [START]                            │
│          ↓                               │
│  [intent_classification]                 │
│          ↓                               │
│     [memory_node]                        │
│          ↓                               │
│       [planner]                          │
│          ↓                               │
│     [ui_node]                            │
│          ↓                               │
│        [END]                             │
│                                          │
│  Controls: [Zoom+] [Zoom-] [Reset]      │
└─────────────────────────────────────────┘
```

**Data Flow:**
1. User clicks "Graph" tab
2. Component calls `useTraceGraph(traceId)` hook
3. Hook calls `GET /api/v1/traces/{traceId}/graph`
4. Receive GraphData (nodes from observations, edges from parent-child)
5. Render in GraphCanvas with vis-network

---

## 📚 Implementation Guide

### Step 1: Install vis-network

```bash
cd /root/projects/swisper_studio/frontend
npm install vis-network@^9.1.9
```

### Step 2: Create Shared Graph Component

**File:** `frontend/src/components/graph/GraphCanvas.tsx`

**Key Implementation Points:**
- Use `vis-network/standalone` import
- Adapt from Langfuse's `TraceGraphCanvas.tsx` (reference: `reference/langfuse/web/src/features/trace-graph-view/components/TraceGraphCanvas.tsx`)
- Hierarchical layout: top-to-bottom (`direction: "UD"`)
- Node colors from Langfuse (see analysis doc for color scheme)
- Interactive controls: Zoom In, Zoom Out, Reset View
- Click handler: `onNodeClick(nodeId)` callback

**Color Scheme:**
```typescript
const NODE_COLORS = {
  AGENT: { border: "#c4b5fd", background: "#f3f4f6" },      // purple
  TOOL: { border: "#fed7aa", background: "#f3f4f6" },       // orange
  GENERATION: { border: "#f0abfc", background: "#f3f4f6" }, // fuchsia
  SPAN: { border: "#93c5fd", background: "#f3f4f6" },       // blue
  RETRIEVER: { border: "#5eead4", background: "#f3f4f6" },  // teal
  EVENT: { border: "#6ee7b7", background: "#f3f4f6" },      // green
  SYSTEM: { border: "#d1d5db", background: "#f3f4f6" }      // gray
};
```

### Step 3: Build Swisper Builder Section

**Navigation Update:**
- Add "Swisper Builder" to main navigation (between Projects and other sections)
- Route: `/swisper-builder`

**Component Structure:**
```typescript
// SystemArchitectureView.tsx
- Sidebar: List of 5 agents (clickable)
- Main area: GraphCanvas showing selected agent's graph
- State: selectedAgent (string | null)
- Hook: useSystemArchitecture() to fetch data
```

### Step 4: Add Trace Graph Tab

**Modify TraceDetail.tsx:**
- Add "Graph" tab to existing tabs (Tree, Timeline, JSON)
- Conditionally render `<TraceGraphView traceId={traceId} />` when tab active

**TraceGraphView.tsx:**
- Fetch graph data with `useTraceGraph(traceId)` hook
- Render GraphCanvas with fetched data
- Show loading spinner while fetching
- Show "No data" message if graph empty

---

## 🔧 Technical Details

### vis-network Configuration

**From Langfuse reference:**
```typescript
const options = {
  layout: {
    hierarchical: {
      enabled: true,
      direction: "UD",        // Top to bottom
      levelSeparation: 60,    // Vertical spacing
      nodeSpacing: 175,       // Horizontal spacing
      sortMethod: "hubsize"
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
};
```

### API Client Calls

**System Architecture:**
```typescript
// useSystemArchitecture.ts
const response = await apiClient.get<SystemArchitectureData>(
  "/system-architecture"
);
```

**Trace Graph:**
```typescript
// useTraceGraph.ts
const response = await apiClient.get<GraphData>(
  `/traces/${traceId}/graph`
);
```

### TypeScript Types

**File:** `frontend/src/components/graph/types.ts`

```typescript
export interface GraphNode {
  id: string;
  label: string;
  type: string;
}

export interface GraphEdge {
  from_node: string;  // Note: Backend uses alias "from"
  to_node: string;    // Note: Backend uses alias "to"
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

## 📂 Files to Create (Week 2)

**Shared Components:**
1. `frontend/src/components/graph/GraphCanvas.tsx` - Reusable vis-network wrapper (~150 lines)
2. `frontend/src/components/graph/types.ts` - TypeScript interfaces (~30 lines)

**Swisper Builder:**
3. `frontend/src/features/swisper-builder/SystemArchitectureView.tsx` (~100 lines)
4. `frontend/src/features/swisper-builder/hooks/useSystemArchitecture.ts` (~20 lines)
5. `frontend/src/features/swisper-builder/index.tsx` (~5 lines)

**Trace Graph:**
6. `frontend/src/features/traces/components/TraceGraphView.tsx` (~60 lines)
7. `frontend/src/features/traces/hooks/useTraceGraph.ts` (~20 lines)

**Navigation:**
8. Update `frontend/src/app.tsx` - Add `/swisper-builder` route
9. Update navigation component - Add "Swisper Builder" entry
10. Modify `frontend/src/features/traces/components/TraceDetail.tsx` - Add Graph tab

**Total:** ~10 files (7 new, 3 modified)

---

## 🧪 Testing Strategy (Week 2)

### Manual Testing Checklist

**System Architecture View:**
- [ ] Navigate to Swisper Builder
- [ ] See list of 5 agents in sidebar
- [ ] Default agent (global_supervisor) displays graph
- [ ] Click different agents → Graph updates
- [ ] Zoom in/out controls work
- [ ] Reset view button works
- [ ] Nodes color-coded correctly
- [ ] Edges show correct flow
- [ ] Graph loads in <1 second

**Trace Graph View:**
- [ ] Navigate to existing trace detail page
- [ ] Click "Graph" tab
- [ ] Graph renders with START and END nodes
- [ ] Observation nodes visible
- [ ] Edges connect parent → child correctly
- [ ] Node colors match observation types
- [ ] Zoom/pan/reset controls work
- [ ] Graph loads in <2 seconds

**Browser Compatibility:**
- [ ] Chrome/Edge (primary)
- [ ] Firefox (secondary)
- [ ] No console errors

---

## 📖 Reference Documents

**Analysis:**
- `docs/analysis/phase3_visualization_analysis.md` - Langfuse reference, color schemes, vis-network evaluation

**Implementation Plan:**
- `docs/plans/phase3_detailed_subplan.md` - Day-by-day breakdown, exact code snippets

**Langfuse Reference:**
- `reference/langfuse/web/src/features/trace-graph-view/components/TraceGraphCanvas.tsx` - vis-network wrapper example
- `reference/langfuse/web/src/features/trace-graph-view/buildGraphCanvasData.ts` - Graph building patterns
- `reference/langfuse/web/package.json` - vis-network version (9.1.9)

**Swisper Reference:**
- `reference/swisper/backend/app/api/services/agents/` - Agent definitions (to understand graph structures)

---

## 🎯 Success Criteria (Week 2)

**When complete, we should have:**

**System Architecture View:**
- [ ] Shows all 5 Swisper agents
- [ ] Each agent displays correct nodes and edges
- [ ] Nodes color-coded by type
- [ ] Zoom/pan/reset controls working
- [ ] Loads in <1 second
- [ ] Can switch between agents smoothly

**Trace Graph View:**
- [ ] Displays observation tree as graph
- [ ] Nodes show correct observation types
- [ ] Edges show parent-child flow
- [ ] START/END nodes visible
- [ ] Zoom/pan/reset controls working
- [ ] Loads in <2 seconds
- [ ] Accessible from trace detail page

**Code Quality:**
- [ ] Frontend builds without errors (`npm run build`)
- [ ] TypeScript compiles (`tsc --noEmit`)
- [ ] Linting passes (`npm run lint`)
- [ ] No console errors in browser
- [ ] Following MUI design patterns

---

## 🚀 Quick Start (Next Session)

```bash
# 1. Navigate to frontend
cd /root/projects/swisper_studio/frontend

# 2. Install vis-network
npm install vis-network@^9.1.9

# 3. Verify backend is running
curl http://localhost:8001/api/v1/system-architecture \
  -H "X-API-Key: dev-api-key-change-in-production"

# Expected: JSON with 5 agents

# 4. Start frontend dev server
npm run dev

# 5. Open browser: http://localhost:3000
```

---

## 🛠️ Current System Status

**Running Services:**
```bash
# Backend
docker compose up -d
# Running on: http://localhost:8001
# API Docs: http://localhost:8001/api/v1/docs

# Frontend
cd frontend && npm run dev
# Running on: http://localhost:3000
```

**API Endpoints Available:**
- ✅ `GET /api/v1/system-architecture` - Returns 5 agent graphs
- ✅ `GET /api/v1/traces/{id}/graph` - Returns graph for trace
- ✅ All existing Phase 1-2 endpoints

**Database:**
- Test trace available: "AAA Swisper Production Test"
- 7 observations with nested structure (perfect for graph testing)

**Test Data:**
```bash
# Get test trace ID
curl http://localhost:8001/api/v1/traces \
  -H "X-API-Key: dev-api-key-change-in-production" | jq '.items[0].id'

# Get graph for test trace
curl http://localhost:8001/api/v1/traces/{TRACE_ID}/graph \
  -H "X-API-Key: dev-api-key-change-in-production"
```

---

## 📝 Notes for Next Session

**Key Implementation Tips:**
1. **vis-network import:** Use `/standalone` version to avoid peer dependency issues
2. **Color scheme:** Copy from Langfuse (documented in analysis)
3. **Layout:** Hierarchical with `direction: "UD"` works best
4. **Edge alias:** Backend returns `from`/`to`, but Pydantic allows `from_node`/`to_node` too
5. **MUI consistency:** Use existing MUI components (Button, Tabs, Box, etc.)
6. **Test with real data:** Use "AAA Swisper Production Test" trace

**Common Pitfalls to Avoid:**
- Don't use React Flow (we chose vis-network for good reasons - see analysis)
- Don't recreate vis-network on every render (use refs properly)
- Don't forget to dispose network on component unmount (memory leak)
- Don't skip error states (loading, empty data, API errors)

**Time Estimate:**
- Day 1-2: Shared components + Swisper Builder
- Day 3: Trace Graph View
- Day 4: Testing + polish

**Total:** 4 days (buffer: 3 days in 7-day plan)

---

## ✨ What We've Accomplished So Far

**Phase 3 Progress:**
- ✅ Week 1 Backend: 100% complete (1 day, ahead of schedule)
- ⏳ Week 2 Frontend: Ready to start

**Overall MVP Progress:**
- ✅ Phase 0: Infrastructure ✅
- ✅ Phase 1: Hello World ✅
- ✅ Phase 2: Rich Tracing ✅
- ⏳ Phase 3: Visualization - 50% complete
- ⏸️ Phase 4: Configuration (backlog)

**Test Results:**
- 57/57 backend tests passing ✅
- No regressions ✅
- TDD workflow followed ✅

---

**Last Updated:** November 2, 2025  
**Phase 3 Week 1 Commit:** (about to commit)  
**Ready for:** Phase 3 Week 2 - Frontend Implementation

**Questions?** Check:
- `docs/plans/phase3_detailed_subplan.md` - Implementation plan
- `docs/analysis/phase3_visualization_analysis.md` - Technical analysis
- `reference/langfuse/web/src/features/trace-graph-view/` - Reference code

---

**🎯 Next Step:** Install vis-network and create GraphCanvas component!

