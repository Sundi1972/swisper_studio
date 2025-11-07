# SwisperStudio Implementation Plan v3.0

**Version:** 3.0  
**Date:** November 7, 2025  
**Last Updated:** 2025-11-07 11:30 UTC  
**Status:** In Progress - Week 1 Complete  
**Approach:** Vertical phases delivering end-to-end business value  
**Supersedes:** v2.0 (2025-11-01)

---

## 📊 **Current Status (Week 1 Complete)**

**Completed Phases:**
- ✅ Phase 0: Infrastructure Foundation
- ✅ Phase 1: "Hello World" End-to-End Proof
- ✅ Phase 2: "Rich Tracing" Full Context
- ✅ Phase 2.5: State Visualization
- ✅ Phase 3: Visualization (Graphs)
- ✅ Phase 4: Configuration Management
- ✅ Phase 5.1: SDK Integration & Enhancements (v0.5.0)

**Pending Phases:**
- ⏸️ Phase 5.2: Model Pricing Management GUI (2-3 days)
- ⏸️ Phase 5.4: SDK Deployment & Publishing (1 day) - **RECOMMENDED NEXT**
- 🔥 Phase 5.3: User Authentication (1-2 weeks) - **HIGH PRIORITY**

**Outstanding - Swisper Team:**
- ⏸️ SPA (Swisper Admin Protocol) Implementation (3-4 days)

**Overall Progress:** ~85% of MVP complete, 15% remaining

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current Status](#current-status-week-1-complete)
3. [What We've Built (Phase 0)](#phase-0-infrastructure-foundation)
4. [MVP Requirements](#mvp-requirements)
5. [Architecture Decisions](#architecture-decisions)
6. [Phase Breakdown](#phase-breakdown)
7. [ClickHouse Integration Timeline](#clickhouse-integration-timeline)
8. [Success Metrics](#success-metrics)

---

## Executive Summary

**Goal:** Build SwisperStudio as an observability and development platform for Swisper, delivering testable business value in each phase.

**Strategy:**
- Build **vertically** (full stack per feature)
- Each phase delivers **end-to-end working functionality**
- **Reference Langfuse** code for implementation patterns
- **Reuse Swisper frontend** components (icons, styling)
- Create **data-driven UI** that auto-adapts to Swisper deployments

**Timeline:** 10-12 weeks to MVP

---

## Phase 0: Infrastructure Foundation ✅ COMPLETE

**Completed:** November 1-2, 2025  
**Status:** ✅ All tasks complete

**What We Built:**

### Backend Infrastructure
- ✅ FastAPI application with `uv` package manager
- ✅ Docker Compose setup (PostgreSQL on port 5433, Backend on port 8001)
- ✅ SQLModel + Alembic migrations
- ✅ Initial database schema (traces, observations tables)
- ✅ API key authentication
- ✅ Health check endpoint

### Data Models
- ✅ `Trace` model (project, user, session tracking)
- ✅ `Observation` model (nested spans with relationships)
- ✅ `ObservationType` enum (SPAN, GENERATION, EVENT, TOOL, AGENT)
- ✅ Foreign keys and indexes

### API Endpoints (Skeleton)
- ✅ `POST /api/v1/traces` - Create trace
- ✅ `GET /api/v1/traces/{id}` - Get trace
- ✅ `POST /api/v1/observations` - Create observation
- ✅ `PATCH /api/v1/observations/{id}` - Update observation
- ✅ `GET /api/v1/observations/{id}` - Get observation

### What's NOT Done Yet
- ❌ Frontend (empty)
- ❌ User authentication (only API keys)
- ❌ Project management
- ❌ State tracking
- ❌ LLM telemetry
- ❌ Graph visualization
- ❌ Configuration management

---

## MVP Requirements

Based on user requirements discussion:

### 1. Authentication & Projects
- Users can log in to SwisperStudio
- Users can create projects (one project = one Swisper deployment)
- Multi-environment support (production, staging, dev)
- Simple auth for MVP (API key), enhance later

### 2. End-to-End Tracing
Must capture and display:
- **a) State Changes** - Full state at each node (input/output/diff)
- **b) LLM Prompts** - Actual prompts sent to LLMs
- **c) Telemetry** - Tokens, costs, response times, model parameters
- **d) LLM Responses** - Full text responses from LLMs
- **e) Tool Calls** - Which tools called with which arguments
- **f) Tool Responses** - Results from tool executions

### 3. Developer-Friendly Integration
**Goal:** PO-friendly, minimal code changes

**Approach:** Graph-level auto-instrumentation
```python
# ONE LINE CHANGE to add tracing
from swisper_sdk import create_traced_graph
graph = create_traced_graph(GlobalSupervisorState, trace_name="supervisor")
# All nodes automatically traced!
```

**Later:** Visual configurator (no-code trace setup) - Backlog Phase 5

### 4. Graph Visualization
- Visualize single trace as graph (nodes + edges)
- Visualize entire system architecture
- Interactive (click nodes for details)

### 5. Configuration Management
- **Data-driven UI** - Auto-generates forms from Swisper schema
- **Live testing** - Test configs in real-time (no redeploy)
- **Production deployment** - Commit to Git when ready
- **Swisper Admin Protocol (SAP)** - Standard API for config management

---

## Architecture Decisions

### Decision 1: Database Separation ✅
- **SwisperStudio DB** (PostgreSQL on 5433): Traces, observations, projects, audit history
- **Swisper DB** (separate): User data, sessions, config tables
- **Communication:** API-only (no direct DB access)

### Decision 2: Multi-Project Support ✅
- One SwisperStudio instance manages multiple Swisper deployments
- Each project has its own API key
- Compare traces across environments (prod vs staging)

### Decision 3: State Tracking ✅
- Track **entire state** at each node (full capture)
- Calculate diffs automatically (show what changed)
- Add PII filtering in UI later

### Decision 4: Configuration Sync ✅
**Two-Mode System:**
- **Live Testing Mode:** Update via API → Immediate effect (cache + DB)
- **Production Mode:** Commit to Git → Source of truth

```
SwisperStudio UI
 ├─ "Test Live" → Swisper API → Update cache + DB (instant)
 └─ "Deploy to Prod" → Commit to Git → CI/CD → Swisper loads on startup
```

### Decision 5: Data-Driven Admin UI ✅
- Swisper exposes config schema via **SAP (Swisper Admin Protocol)**
- SwisperStudio auto-generates UI from schema
- Add new config table in Swisper → SwisperStudio UI updates automatically
- **SAP specification to be created in Phase 4**

### Decision 6: ClickHouse for Analytics 📊
- **MVP:** PostgreSQL only (simple, fast to implement)
- **Phase 5+:** Add ClickHouse for analytics
  - Time-series queries
  - Cost aggregations
  - Performance metrics
  - Large-scale trace analysis

---

## Phase Breakdown

### **Phase 1: "Hello World" - End-to-End Proof** ✅ COMPLETE

**Completed:** November 2, 2025  
**Duration:** 1 day (planned 2 weeks - ahead of schedule!)  
**Status:** ✅ UAT PASSED - All functionality verified

**Business Value Delivered:** Backend + Frontend + SDK working end-to-end

**UAT Results:**
- ✅ Login works with API key authentication
- ✅ Create project works with validation
- ✅ List projects with pagination
- ✅ Delete project (soft delete)
- ✅ View traces page (empty state)
- ✅ Navigation flows work
- ✅ Swisper dark theme and branding applied
- ✅ Hot reload works (backend + frontend)
- ✅ CORS configured correctly
- ✅ All tests passing (23/23)

#### 📚 Analysis Step (Days 1-2)

**MANDATORY: Analyze reference codebases before implementation**

**Langfuse Analysis (Backend + Frontend UX):**
- [ ] Study project management implementation
  - `packages/shared/src/server/repositories/ProjectRepository.ts`
  - `packages/shared/prisma/schema.prisma` - Project model
  - API endpoints structure
- [ ] Study trace ingestion patterns
  - `packages/shared/src/server/ingestion/` - How traces are processed
  - `packages/shared/src/server/repositories/TraceRepository.ts`
  - Pagination and filtering patterns
- [ ] Study frontend UX patterns
  - `web/src/components/trace/TraceList.tsx` - Table layout, columns
  - `web/src/components/trace/TraceDetail.tsx` - Detail view UX
  - Navigation patterns, routing
  - Data fetching (TanStack Query patterns)

**Swisper Analysis (Frontend UI):**
- [ ] Study component library
  - `packages/components/` - What's available to reuse
  - Button styles, form inputs, cards, layouts
- [ ] Study icon library
  - `packages/icons/` - Icon naming conventions
  - How icons are imported and used
- [ ] Study styling approach
  - CSS patterns, Tailwind configuration
  - Color schemes, spacing system
  - Typography styles
- [ ] Study layout patterns
  - Page layouts, navigation structure
  - Responsive design patterns

**Deliverable:** Document findings in `docs/analysis/phase1_langfuse_swisper_analysis.md`
- Key patterns to copy
- Components to reuse
- Architectural decisions Langfuse made (and why)
- UI components available from Swisper

#### Backend (Week 1)
- [ ] Project CRUD API (create, read, list projects)
- [ ] Project model (name, swisper_url, api_key)
- [ ] Enhanced trace ingestion (validate project_id)
- [ ] Trace listing API (GET /api/v1/traces?project_id=X)
- [ ] Basic pagination and filtering

**Langfuse References:**
- `packages/shared/src/server/repositories/ProjectRepository.ts` - Project management
- `packages/shared/src/server/repositories/TraceRepository.ts` - Trace querying
- `packages/shared/prisma/schema.prisma` - Data model relationships

#### Frontend (Week 2)
- [ ] Setup: React + Vite + TailwindCSS
- [ ] Import Swisper UI components (icons, buttons, layouts)
- [ ] Login page (simple API key auth)
- [ ] Project setup page (create first project)
- [ ] Trace list view (table with basic columns)
- [ ] Single trace view (JSON viewer)

**Swisper Frontend References:**
- `packages/components/` - Reusable UI components
- `packages/icons/` - Icon library
- Styling patterns, layout components

**Langfuse Frontend References:**
- `web/src/components/trace/TraceList.tsx` - Trace table
- `web/src/components/trace/TraceDetail.tsx` - Trace viewer
- `web/src/components/layouts/` - Page layouts

#### SDK Integration (Week 2)
- [ ] Create `swisper-studio-sdk` package
- [ ] Implement `create_traced_graph()` wrapper
- [ ] Implement `@traced` decorator
- [ ] Implement context management (trace/observation tracking)
- [ ] SwisperStudio API client
- [ ] Test in local Swisper instance

**Integration Test:**
```python
# Swisper backend
from swisper_sdk import create_traced_graph

graph = create_traced_graph(GlobalSupervisorState, trace_name="test")
# ... add nodes ...
result = await graph.ainvoke({"messages": [...]})

# Verify: See trace in SwisperStudio UI ✅
```

**Success Criteria:**
- ✅ User logs into SwisperStudio
- ✅ User creates a project
- ✅ Swisper sends a trace
- ✅ Trace appears in SwisperStudio list
- ✅ User can click and see trace details (JSON)

---

### **Phase 2: "Rich Tracing" - Full Context** ✅ COMPLETE (3 weeks)

**Completed:** November 2, 2025  
**Duration:** 1 day (planned 3 weeks - ahead of schedule!)  
**Status:** ✅ UAT PASSED - All functionality verified

**Business Value:** Developers can debug with complete execution context

#### 📚 Analysis Step (Days 1-2) ✅ COMPLETE

**Status:** ✅ Analysis complete - November 2, 2025

**Langfuse Analysis (Backend + Frontend UX):**
- ✅ Study observation processing - Documented comprehensive observation model
- ✅ Study cost calculation - Token counting, model pricing patterns
- ✅ Study LLM telemetry capture - Prompts, responses, parameters
- ✅ Study trace detail UI/UX - IOView, ObservationTree, Timeline patterns

**Swisper Analysis (Backend + Frontend):**
- ✅ Study LangGraph integration patterns - State class structure (TypedDict)
- ✅ Study UI patterns - MUI components, dark theme

**Deliverable:** ✅ `docs/analysis/phase2_rich_tracing_analysis.md`

**Key Findings:**
- Langfuse has comprehensive observation model with cost tracking
- State tracking requires before/after snapshots at each node
- MUI v7 (not Tailwind) for frontend consistency
- Per-node model configuration in Swisper → observation-level pricing lookups

#### Backend (Week 1-2) ✅ COMPLETE
- ✅ Enhanced observation model (tokens, costs, LLM details, state tracking)
- ✅ Model pricing table (project-level, provider + model granularity)
- ✅ Cost calculation service (DB-based pricing lookups)
- ✅ State diff calculation (client-side for MVP)
- ✅ LLM telemetry capture (prompts, responses, parameters)
- ✅ Tool call tracking (arguments, results)
- ✅ Observation tree API (GET /api/v1/traces/{id}/tree)
- ✅ Enhanced search and filter API (user, session, date range, name, tags)
- ✅ Model pricing API (GET /api/v1/projects/{id}/model-pricing)
- ✅ **46/46 backend tests passing**
- ✅ **Async event loop infrastructure fixed permanently**

**Langfuse References:**
- `packages/shared/src/server/ingestion/` - Trace ingestion patterns
- `packages/shared/src/features/observations/` - Observation processing
- Cost calculation logic

#### Frontend (Week 2-3) ✅ MVP COMPLETE
- ✅ Project navigation structure
  - ✅ Project layout with sidebar (Overview, Tracing, Config)
  - ✅ Project overview page (landing with quick actions)
  - ✅ Nested routing (Projects → Project → Features)
  - ✅ Breadcrumb navigation in header
- ✅ Configuration page (read-only placeholder for Phase 4)
- ✅ Trace detail view (MVP - tree view)
  - ✅ Tree view showing nested observations
  - ✅ Observation metadata (type, name, duration, tokens, cost)
  - ✅ Click from trace list to detail page
  - ⏸️ Timeline/JSON views (deferred - tabs present but disabled)
  - ⏸️ Detailed state viewer (deferred - info shown in tree nodes)
  - ⏸️ Separate LLM details panel (deferred - shown in tree)
- ✅ Basic search/filters (backend API ready, UI can be added incrementally)
- ✅ Cost tracking display (shown per observation in tree)
- ✅ Frontend builds successfully

**Langfuse Frontend References:**
- `web/src/components/trace/ObservationTree.tsx` - Tree visualization
- `web/src/components/trace/IOView.tsx` - Input/output display
- `web/src/features/dashboard/` - Dashboard components

#### SDK Enhancement (Week 5)
- [ ] Automatic state capture (before/after each node)
- [ ] LLM wrapper (auto-capture prompts, responses, tokens)
- [ ] Tool wrapper (auto-capture calls and results)
- [ ] Error tracking and reporting
- [ ] Performance instrumentation

**Integration Test:**
```python
# Swisper node
@traced("intent_classification", observation_type="GENERATION")
async def intent_node(state):
    llm = ChatOpenAI(model="gpt-4")  # Auto-wrapped
    response = await llm.ainvoke([...])  # Auto-tracked
    return state

# Verify in SwisperStudio:
# ✅ See input state
# ✅ See output state
# ✅ See state diff
# ✅ See LLM prompt sent
# ✅ See LLM response
# ✅ See tokens (prompt: 150, completion: 50)
# ✅ See cost ($0.0045)
```

**Success Criteria: ALL MET ✅**
- ✅ Project navigation with sidebar (Overview, Tracing, Analytics, Config)
- ✅ Model pricing configurable at project level (provider + model)
- ✅ Cost calculation uses DB pricing (per observation)
- ✅ Full state tracking (input/output stored in observations)
- ✅ LLM prompts and responses visible (in observation.input/output)
- ✅ Token counts and costs calculated accurately
- ✅ Tool calls tracked with arguments/results
- ✅ Search/filter backend ready (user, session, date, name, tags)
- ✅ Developer can debug production issues with complete context

**UAT Results:**
- ✅ All 10 test scenarios passed
- ✅ Observation tree displays correctly (3 levels nested)
- ✅ Cost tracking accurate ($0.005400 calculated correctly)
- ✅ Professional navigation (sidebar, breadcrumbs)
- ✅ Type badges color-coded correctly
- ✅ ERROR observations highlighted
- ✅ 46/46 backend tests passing
- ✅ Frontend builds successfully
- ✅ Test cleanup working (database stays clean)

---

### **Phase 2.5: "State Visualization" - UX Enhancement** ✅ COMPLETE (1 day)

**Completed:** November 3, 2025  
**Duration:** 1 day (planned 2-3 weeks - 14+ days ahead of schedule!)  
**Status:** ✅ Complete and tested  
**Business Value:** Complete observability - developers can see state transitions, prompts, and tool calls

#### Frontend (Completed) ✅
- [x] State diff viewer with green/red background highlighting
  - Side-by-side comparison view
  - Diff view with color-coded changes
  - Toggle between views
  - Expand All button for JSON trees
  - JSON syntax highlighting
- [x] Observation details panel (resizable)
  - Dedicated panel (60% width, resizable)
  - Click observation → panel updates
  - Quick action buttons (jump to sections)
  - Type-specific sections (GENERATION, TOOL, SPAN)
- [x] LLM prompt viewer
  - Markdown rendering (headers, lists, code blocks)
  - System/user message display
  - Copy to clipboard
- [x] LLM response viewer
  - JSON tree viewer (expandable/collapsible)
  - Copy to clipboard
- [x] Tool call viewer
  - Function name + arguments
  - Formatted JSON tree
  - Copy to clipboard
- [x] Tool response viewer
  - Results displayed as JSON tree
  - Copy to clipboard
- [x] Model parameters display
  - Temperature, max_tokens, top_p
  - Key-value table format
- [x] STATE CHANGED indicators
  - Prominent chip on nodes that modify state
  - State aggregation (parent shows if children changed)
  - Icons for prompts (💬), tools (🛠️), errors (⚠️)
- [x] Full viewport layout
  - Removed Container maxWidth constraint
  - Resizable panels (drag divider)
  - Responsive design
- [ ] Timeline view (deferred - tab present but disabled)
- [ ] JSON raw view tab (deferred - tab present but disabled)
- [ ] Search/filter UI controls (backend ready, UI deferred)

#### SDK Basic (Completed) ✅
- [x] Auto-state capture
  - Serialize TypedDict/dict state before/after each node
  - Handle Pydantic models with model_dump()
  - Store in observation.input/output
  - **TESTED AND WORKING**
- [x] Automatic trace creation
  - Wraps graph.compile().ainvoke() to create trace
  - Extracts user_id and session_id from state
  - Sets trace context for observations
  - **TESTED AND WORKING**
- [x] Observation nesting
  - Parent-child relationships with contextvars
  - Supports nested agents
  - **TESTED AND WORKING**
- [x] Error tracking
  - Catches exceptions in @traced decorator
  - Sets level=ERROR, status_message=error
  - Still propagates exception to caller
  - **IMPLEMENTED**
- [x] Test script and documentation
  - test_sdk_locally.py for isolated testing
  - Integration guide for Swisper
  - Troubleshooting guide
  - **COMPLETE**

#### SDK Enhancements (Backlog - Phase 5.2)
- [ ] LLM wrapper
  - Intercept llm_adapter.get_structured_output() calls
  - Extract prompts, messages, model, parameters
  - Count tokens from response
  - Set observation type = GENERATION
  - **Duration:** 2 days
- [ ] Tool wrapper
  - Detect tool executions
  - Extract tool arguments and responses
  - Set observation type = TOOL
  - **Duration:** 1 day
- [ ] Observation type auto-detection
  - Detect GENERATION, TOOL, AGENT types
  - Default to SPAN
  - **Duration:** 1 day

#### Additional Enhancements (Week 3)
- [ ] Cost budget alerts
  - Set budget per project
  - Alert when approaching limit
  - Display budget usage in overview
- [ ] Observation filtering in tree
  - Filter by type (show only GENERATION)
  - Filter by level (show only ERROR)
  - Search by name
- [ ] Export functionality
  - Export trace as JSON
  - Export observations as CSV
  - Share trace via link

**When to Implement:**
- User feedback requests specific features
- After Phase 3 (Graphs) if time permits
- As polish before production launch

---

### **Phase 3: "Visualization" - The Big Picture** ✅ COMPLETE (2 weeks)

**Completed:** November 2, 2025  
**Duration:** 2 days (planned 14 days - 12 days ahead of schedule!)  
**Status:** All features complete and tested ✅  
**Business Value:** Visual understanding of agent execution flow

#### 📚 Analysis Step (Day 1) ✅ COMPLETE

**MANDATORY: Analyze reference codebases before implementation**

**Completed:** November 2, 2025  
**Deliverable:** `docs/analysis/phase3_visualization_analysis.md`

**Langfuse Analysis (Backend + Frontend UX):**
- [x] Study graph visualization implementation
  - `web/src/features/trace-visualization/` - If it exists
  - How observation tree converts to graph
  - Layout algorithms used
  - React Flow integration patterns
- [ ] Study node type rendering
  - Different node types (span, generation, tool)
  - Icon/color schemes per type
  - Node detail popups/panels
- [ ] Study graph interactions
  - Zoom/pan controls
  - Node selection
  - Edge highlighting
  - Filtering nodes

**Swisper Analysis (Frontend UI):**
- [ ] Study any existing visualization
  - LangGraph visualization (if any)
  - How graphs are displayed
- [ ] Study interactive component patterns
  - Drag-and-drop (if any)
  - Canvas-based components
  - SVG usage patterns

**Alternative:** Study LangGraph Studio if no Langfuse graph viz
- [ ] Review LangGraph Studio's graph rendering
- [ ] Node/edge styling
- [ ] State display in graph view

**Deliverable:** Document findings in `docs/analysis/phase3_visualization_analysis.md`

#### Backend (Week 6) ✅ COMPLETE
- [x] Graph builder service (convert observations → graph structure)
- [x] Layout algorithm (vis-network hierarchical layout - built-in)
- [x] Graph API (GET /api/v1/traces/{id}/graph)
- [x] System architecture API (GET /api/v1/system-architecture)
- [x] 11 comprehensive tests (all passing)
- [x] Static agent graph definitions (5 agents in JSON)

**Langfuse References:**
- `web/src/features/trace-visualization/` - Graph generation logic
- Observation tree → graph conversion

#### Frontend (Week 6-7)
- [ ] React Flow integration
- [ ] Single trace graph view
  - Nodes (different types: SPAN, GENERATION, TOOL, AGENT)
  - Edges (execution flow)
  - Node details on click
  - Zoom/pan controls
- [ ] System architecture view
  - All unique nodes discovered
  - Common execution paths
  - Statistics (call counts, avg duration)

**Langfuse Frontend References:**
- Graph visualization components
- Node rendering strategies

**Design:**
```
┌─────────────────────────────────────────┐
│ Trace: User Request "What's my next    │
│ meeting?"                               │
├─────────────────────────────────────────┤
│                                         │
│    [intent] → [memory] → [planner]     │
│                            ↓            │
│                         [ui_node]       │
│                                         │
│ Click node → See state, prompt, etc.   │
└─────────────────────────────────────────┘
```

**Success Criteria: ALL MET ✅**
- ✅ Trace displayed as graph (vis-network hierarchical layout)
- ✅ Nodes show type with color coding (SPAN=blue, GENERATION=pink, TOOL=orange, AGENT=purple, SYSTEM=gray)
- ✅ Click node → logs node ID (future: show full details panel)
- ✅ System view shows all 5 agents with correct node structures
- ✅ PO understands execution flow visually
- ✅ Zoom/pan/reset controls functional
- ✅ Performance targets met (System Architecture <1s, Trace Graph <2s)

**Deliverables:**
- ✅ Swisper Builder (System Architecture View) - NEW main navigation section
- ✅ Trace Graph View - New "Graph" tab in Trace Detail page
- ✅ vis-network v9.1.9 integrated
- ✅ Reusable GraphCanvas component
- ✅ All 5 Swisper agents visualized
- ✅ Browser tested successfully (Chrome)

**Test Results:**
- ✅ Backend: 57/57 tests passing
- ✅ Frontend: TypeScript compiles, builds successfully
- ✅ Browser testing: Both features working perfectly
- ✅ 1 bug found and fixed (UUID type issue in graph endpoint)

---

### **Phase 4: "Configuration" - Power User Tools** ✅ COMPLETE (3 weeks)

**Completed:** November 3, 2025  
**Duration:** 2 days (planned 3 weeks - 19 days ahead of schedule!)  
**Status:** ✅ All features complete and tested  
**Business Value:** PO can change system behavior without code changes

#### 📚 Analysis Step (Days 1-2)

**MANDATORY: Analyze reference codebases before implementation**

**Langfuse Analysis (Backend + Frontend UX):**
- [ ] Study admin/settings UI (if exists)
  - `web/src/features/settings/` or similar
  - How settings are organized
  - Form patterns, validation
  - Save/cancel workflows
- [ ] Study configuration storage
  - Database schema for configs
  - Versioning approach (if any)
  - Default values handling
- [ ] Study dynamic form generation (if exists)
  - How Langfuse handles different field types
  - Validation patterns
  - Error handling

**Swisper Analysis (Backend + Frontend):**
- [ ] Study current config loading
  - How YAML configs are loaded
  - `backend/config/` structure
  - Config tables (llm_node_config, llm_route, fact_preloading_config)
  - How configs are accessed at runtime
- [ ] Study config UI patterns (if any)
  - Forms, inputs, selects
  - Validation feedback
  - Success/error states
- [ ] Study table schemas
  - Exact field types
  - Constraints and defaults
  - Relationships between tables

**Other References:**
- [ ] Django Admin - Dynamic form generation
- [ ] Rails Admin - Schema-based UI
- [ ] Strapi - Content type UI generation

**Deliverable:** 
- Document findings in `docs/analysis/phase4_config_analysis.md`
- Create SAP specification based on Swisper's actual tables

#### Backend (Week 8-9)
- [ ] **Create SAP (Swisper Admin Protocol) specification**
  - Schema definition standard
  - Field type specifications
  - Validation rules
  - API endpoint contracts
- [ ] Config history model (audit trail)
- [ ] Config proxy API (forward to Swisper)
  - GET /api/v1/projects/{id}/config/schema
  - GET /api/v1/projects/{id}/config/{table}
  - POST /api/v1/projects/{id}/config/{table}
  - PUT /api/v1/projects/{id}/config/{table}/{record_id}
- [ ] Git integration service
  - Generate YAML from config
  - Commit to Swisper repository
  - Track deployment status

**SAP Specification Tasks:**
- [ ] Document schema format (field types, validation)
- [ ] Define standard endpoints (CRUD + schema)
- [ ] Create examples (llm_node_config, feature_flags)
- [ ] Version specification (v1.0)
- [ ] Create SAP validator tool

#### Swisper Backend (Week 8-9)
**Implement SAP compliance in Swisper:**
- [ ] GET /api/admin/config/schema - Return config schema
- [ ] GET /api/admin/config/{table} - List config records
- [ ] POST /api/admin/config/{table} - Create config
- [ ] PUT /api/admin/config/{table}/{id} - Update config
- [ ] POST /api/admin/config/{table}/deploy - Deploy to production
- [ ] Config manager (cache + DB + hot-reload)

#### Frontend (Week 9-10)
- [ ] Data-driven config editor
  - Fetch schema from Swisper (SAP)
  - Auto-generate forms based on field types
  - Field components (text, number, select, boolean, etc.)
  - Validation based on schema
- [ ] Config testing UI
  - "Test Live" button (immediate update)
  - "Deploy to Production" button (Git commit)
  - Diff viewer (show changes)
- [ ] YAML preview
- [ ] Config history viewer (audit log)

**Example UI:**
```
┌────────────────────────────────────────────┐
│ Configuration > LLM Node Config            │
├────────────────────────────────────────────┤
│                                            │
│ intent_classification                      │
│ Model: [gpt-4-turbo ▼]                    │
│ Temperature: [━━●━━━━━━] 0.8              │
│ Max Tokens: [2000]                         │
│                                            │
│ [Test Live] [Deploy to Production]         │
│                                            │
│ Changes:                                   │
│ - model: gpt-4 → gpt-4-turbo              │
│ - temperature: 0.7 → 0.8                   │
└────────────────────────────────────────────┘
```

**Success Criteria: ALL MET ✅**
- ✅ SAP specification v1.1 documented (comprehensive)
- ✅ Mock SAP implemented (18 Kvant models, 8 tests passing)
- ✅ SwisperStudio auto-generates config UI from schema
- ✅ Environment-aware architecture (dev/staging/production)
- ✅ Config version management (create, deploy, history)
- ✅ Reusable DataTable component (search + sort)
- ✅ Table view → Edit view → Back navigation
- ✅ 88 backend tests + browser verification passing
- ✅ Deployment to environments working
- ✅ Full version audit trail

**UAT Results:**
- ✅ Environment selector works on all pages
- ✅ Config table overview with search and sort
- ✅ Edit view with back button navigation
- ✅ Auto-generated forms from SAP schema
- ✅ Version creation and deployment
- ✅ Version history display
- ✅ Snackbar notifications (non-blocking)
- ✅ Temperature increment by 0.1 (from schema.step)
- ✅ 88/88 backend tests passing
- ✅ Frontend builds successfully
- ✅ Browser tested - all features working

---

### **Phase 5.1: SDK Integration & Enhancements** ✅ COMPLETE (Week 1)

**Completed:** November 6-7, 2025  
**Duration:** 1 week (planned 1 week - on schedule!)  
**Status:** ✅ SDK v0.5.0 Complete  
**Business Value:** Enterprise-grade observability with tool tracking and cost visibility

#### SDK v0.4.0 - Redis Streams Migration ✅
- [x] Redis Streams architecture (50x faster than HTTP)
- [x] LLM reasoning capture (DeepSeek R1, o1)
- [x] Connection status verification (heartbeat)
- [x] Nested agent traces (single E2E trace)

#### SDK v0.5.0 - Tool Harmonization & Enhancements ✅
- [x] Q2 Tracing Toggle (per-project on/off with immediate effect)
- [x] Tool format harmonization (all 4 agents: research, productivity, wealth, doc)
- [x] Universal tool detection (automatic, no decorators)
- [x] Flexible tool extraction (works with any agent architecture)
- [x] Anti-duplication system (ownership tracking)
- [x] Cost tracking (316 models, CHF for KVANT)
- [x] Individual tool observations (🔧 in UI)
- [x] Meaningful trace names (first sentence of user message)

#### Swisper Integration ✅
- [x] SDK installed in Swisper backend
- [x] Global supervisor graph wrapped
- [x] All 4 agents traced (research, productivity, wealth, doc)
- [x] Tool observations working for all agents
- [x] Cost tracking operational
- [x] Reasoning capture enabled

#### Outstanding - Swisper Side
- [ ] **SPA (Swisper Admin Protocol) Implementation**
  - Status: Design complete, implementation pending
  - Swisper needs to implement SAP endpoints for config management
  - Estimated: 3-4 days
  - Owner: Swisper team
  - Blocker for: Phase 4 config management full deployment

**Duration:** 1 week  
**Success Criteria: ALL MET ✅**
- ✅ Real Swisper requests create traces
- ✅ All nodes visible with proper types
- ✅ Tool observations appear for all 4 agents
- ✅ No duplicates (ownership tracking works)
- ✅ Cost tracking accurate
- ✅ Q2 toggle working (immediate effect)
- ✅ Can debug execution flow completely

---

### **Phase 5.2: Model Pricing Management GUI** (2-3 days) - PENDING

**Status:** Not started  
**Priority:** Medium  
**Business Value:** Self-service model pricing management, no SQL required

**Problem:** Currently model pricing requires direct database access or Alembic migrations

**Solution:** CRUD UI for model pricing management

#### Backend (1-2 days)
- [ ] Model Pricing CRUD endpoints
  - GET /api/v1/projects/{id}/model-pricing (already exists ✅)
  - POST /api/v1/model-pricing (create new pricing)
  - PUT /api/v1/model-pricing/{id} (update pricing)
  - DELETE /api/v1/model-pricing/{id} (remove pricing)
  - POST /api/v1/model-pricing/bulk (bulk import from CSV)
- [ ] Validation
  - Unique constraint (project + provider + model)
  - Positive pricing values
  - Valid provider names
- [ ] Import/Export
  - Export all pricing to CSV
  - Import from CSV (for bulk updates)
  - Template CSV download

#### Frontend (1-2 days)
- [ ] Model Pricing Management Page
  - Data table with search and sort
  - Add new pricing button (modal form)
  - Edit pricing (inline or modal)
  - Delete pricing (with confirmation)
  - Bulk import (CSV upload)
  - Export to CSV button
- [ ] Form Components
  - Provider dropdown (KVANT, OpenAI, Anthropic, etc.)
  - Model name input (autocomplete from existing)
  - Input/output price fields (CHF per million tokens)
  - Project selector (global or project-specific)
- [ ] Validation Feedback
  - Real-time validation
  - Error messages
  - Duplicate detection
  - Success notifications

**UI Concept:**
```
┌────────────────────────────────────────────┐
│ Model Pricing Management                   │
├────────────────────────────────────────────┤
│ [+ Add Pricing] [Import CSV] [Export CSV]  │
│                                            │
│ Provider  Model           Input    Output  │
│ KVANT     qwen3-8b        0.035    0.09   │
│ KVANT     llama4-maverick 0.225    0.09   │
│ OpenAI    gpt-4-turbo     15.00    30.00  │
│                                            │
│ [Edit] [Delete]                            │
└────────────────────────────────────────────┘
```

**Success Criteria:**
- ✅ Can add new model pricing via UI (no SQL)
- ✅ Can edit existing pricing
- ✅ Can delete pricing
- ✅ Can bulk import from CSV
- ✅ Can export to CSV for backup
- ✅ Validation prevents duplicates and invalid values
- ✅ Project-specific pricing supported

**Duration:** 2-3 days  
**Dependencies:** None (backend API partial exists)  
**Priority:** Medium (nice-to-have for MVP, critical for scale)

---

### **Phase 5.4: SDK Deployment & Publishing** (1 day) - PENDING

**Status:** Not started  
**Priority:** High (required for production)  
**Business Value:** Professional SDK distribution, easy updates, no code duplication

**Current Situation:**
- SDK source in SwisperStudio repo only
- Hot-deployed to Swisper container for testing (temporary)
- Swisper repo doesn't have SDK code
- Docker builds won't work without SDK

**Problem:** Production builds need SDK, but copying code to Swisper repo creates duplication

**Solution:** Publish SDK as package to GitHub Packages (private registry)

#### Setup GitHub Packages (2-3 hours)
- [ ] Create publish workflow in SwisperStudio repo
  - `.github/workflows/publish-sdk.yml`
  - Triggers on git tag (`sdk-v*`)
  - Builds package (`python -m build`)
  - Publishes to GitHub Packages
- [ ] Configure GitHub authentication
  - Create Personal Access Token with packages:write
  - Add as repository secret
- [ ] Test publish
  - Tag SDK v0.5.0
  - Verify package appears in GitHub Packages
  - Test installation from registry

#### Update Swisper to Use Package (1-2 hours)
- [ ] Update requirements.txt
  ```python
  # Add:
  swisper-studio-sdk==0.5.0
  ```
- [ ] Update Dockerfile/docker-compose.yml
  ```dockerfile
  # Configure pip to use GitHub Packages
  RUN pip config set global.index-url https://...github.com
  RUN pip install -r requirements.txt
  ```
- [ ] Remove hot-deployed SDK files
  - No longer need /app/swisper_studio_sdk_v050/
  - Installed via pip instead
- [ ] Test Docker build
  - Verify SDK downloads from GitHub Packages
  - Verify all features work

#### Documentation (30 mins)
- [ ] Update SWISPER_TEAM_HANDOVER_MESSAGE.md
  - How to update SDK version (change requirements.txt)
  - How to rebuild with new SDK
- [ ] Create SDK_PUBLISHING_GUIDE.md
  - How to publish new SDK versions
  - Semantic versioning strategy
  - Release checklist

**Benefits:**
- ✅ No SDK code duplication
- ✅ Standard Python workflow (pip install)
- ✅ Version management (pin to specific version)
- ✅ Easy updates (change one line in requirements.txt)
- ✅ Private (GitHub Packages within org)
- ✅ Free (included with GitHub)

**Duration:** 1 day (3-4 hours)  
**Priority:** High - Required before Swisper team can build Docker images independently  
**Owner:** SwisperStudio team

**Success Criteria:**
- ✅ SDK v0.5.0 published to GitHub Packages
- ✅ Swisper can `pip install swisper-studio-sdk==0.5.0`
- ✅ Swisper Docker builds work without manual SDK copying
- ✅ Documentation complete for publishing new versions
- ✅ Swisper team can update SDK by changing version number

---

### **Phase 5.3: User Authentication & Management** (Weeks 2-3) - HIGH PRIORITY 🔥

**Status:** Not started - CRITICAL for production  
**Business Value:** Secure multi-user platform, production-ready

**Problem:** Current system uses single API key - not secure or scalable

**Solution:** Implement proper user authentication with JWT

#### Backend (4-5 days)
- [ ] Create User model
  - email (unique, indexed)
  - password_hash (bcrypt, 12 rounds)
  - name, role (admin/developer/viewer)
  - created_at, updated_at, last_login
- [ ] Authentication endpoints
  - POST /api/v1/auth/register (email, password, name)
  - POST /api/v1/auth/login (email, password) → JWT token
  - POST /api/v1/auth/logout (invalidate token)
  - GET /api/v1/auth/me (current user info)
- [ ] JWT middleware
  - Verify token on all protected routes
  - Extract user_id from token
  - Add to request context
- [ ] RBAC system
  - Role enum: ADMIN, DEVELOPER, QA, VIEWER
  - Permission checks per environment
  - Developers: edit dev/staging, read production
  - QA: edit staging, read dev/production
  - Admin: edit all environments
- [ ] Add user_id to existing models
  - Projects.owner_id (foreign key to User)
  - Traces.user_id (already exists, link to User)
  - ConfigVersion.created_by_user_id
- [ ] Migration
  - Create users table
  - Add user_id foreign keys
  - Create default admin user
  - Backfill existing data (optional)
- [ ] Tests (15-20 tests)
  - Registration, login, logout
  - JWT verification
  - Permission checks
  - RBAC enforcement

#### Frontend (3-4 days)
- [ ] Login page
  - Email + password form
  - Remember me checkbox
  - Error handling
  - Loading states
- [ ] Registration page (optional for MVP)
  - Email, password, name
  - Password strength indicator
  - Email verification (optional)
- [ ] Auth context
  - Store JWT in localStorage
  - Provide user info to components
  - Auto-refresh on token expiry (optional)
- [ ] Protected routes
  - Redirect to login if not authenticated
  - ProtectedRoute wrapper component
  - Public routes: /login, /register
  - Protected routes: everything else
- [ ] User profile dropdown
  - Show user name in header
  - Dropdown: Profile, Settings, Logout
  - User avatar (optional)
- [ ] Logout functionality
  - Clear JWT from localStorage
  - Redirect to login
  - Clear auth context

#### Security
- [ ] Password hashing (bcrypt, cost factor 12)
- [ ] JWT with expiration (24 hours)
- [ ] Refresh tokens (optional)
- [ ] HTTPS enforcement (production)
- [ ] Rate limiting on auth endpoints (prevent brute force)
- [ ] CSRF protection
- [ ] XSS protection (Content-Security-Policy)
- [ ] SQL injection protection (SQLModel handles this)

**Duration:** 7-10 days  
**Complexity:** High (security-critical)  
**Priority:** **CRITICAL** - Blocks production deployment

**Success Criteria:**
- ✅ Users can register and login
- ✅ JWT authentication working
- ✅ Protected routes redirect to login
- ✅ RBAC enforces permissions per environment
- ✅ Logout clears session
- ✅ Secure (password hashing, JWT expiration)

---

### **Phase 5: Dynamic Graph Reading & Advanced Visualization** (Backlog - Future)

**Business Value:** Auto-sync agent graphs, no manual JSON maintenance, advanced graph features

#### Dynamic Agent Graph Reading
**Current:** Static JSON manually synced from Swisper code  
**Future:** Dynamic reading from live Swisper deployment

**Option A: Git Repository Reading**
- [ ] Connect to Swisper project Git repository
- [ ] Python AST parser to extract StateGraph definitions
- [ ] Parse `build_graph()` methods in agent files
- [ ] Auto-detect nodes, edges, conditional routing
- [ ] CLI tool: `sync_agent_graphs.py` to update JSON
- [ ] CI check to detect drift between JSON and actual code

**Option B: Swisper Admin Protocol (SAP) - Recommended**
- [ ] Swisper exposes endpoint: `GET /api/admin/system-architecture`
- [ ] Swisper introspects its own agents at runtime
- [ ] Returns complete graph definitions with conditional edges
- [ ] SwisperStudio fetches dynamically (no JSON to maintain)
- [ ] Part of Phase 4 SAP specification
- [ ] Always accurate, no sync issues

**Option C: Hybrid Approach**
- [ ] SAP endpoint for runtime graphs (live deployments)
- [ ] Git reading for dev/analysis (reading code directly)
- [ ] SwisperStudio supports both modes

**Benefits:**
- ✅ Always accurate (auto-syncs)
- ✅ No manual JSON maintenance
- ✅ Discovers new agents automatically
- ✅ Validates against actual implementation
- ✅ Works with multiple Swisper versions

**Estimated Effort:** 2-3 days (AST parsing) or 1 day (SAP endpoint in Swisper)

---

### **Phase 5b: Visual Trace Configuration** (Backlog - Future)

**Business Value:** PO can enable/disable tracing without touching code

#### Swisper Backend
- [ ] Node introspection API (list all LangGraph nodes)
- [ ] Tracing config API (get/update which nodes are traced)
- [ ] Dynamic trace enablement (without code changes)

#### SwisperStudio Frontend
- [ ] Visual node selector (checkboxes for each node)
- [ ] Trace settings (what to capture per node)
- [ ] One-click enable/disable tracing

**UI Concept:**
```
┌────────────────────────────────────────────┐
│ Tracing Configuration                      │
├────────────────────────────────────────────┤
│                                            │
│ Auto-discovered Nodes:                     │
│ ☑ intent_classification                    │
│ ☑ memory_node                              │
│ ☐ planner  [Enable]                        │
│ ☑ ui_node                                  │
│                                            │
│ Global Settings:                           │
│ ☑ Track full state                         │
│ ☑ Track LLM calls                          │
│ ☐ Track only errors                        │
│                                            │
│ [Apply Configuration]                      │
└────────────────────────────────────────────┘
```

**Status:** Backlog (after Phase 4)

---

## ClickHouse Integration Timeline

### Current: PostgreSQL Only (MVP)
- **Phases 1-4:** Use PostgreSQL for all data
- **Storage:** Traces, observations, projects, config history
- **Queries:** Simple filtering, pagination, single trace lookups

### Future: Add ClickHouse (Post-MVP)
**When:** Phase 5+ or when performance requires it

**Use Cases:**
- Time-series analytics (traces over time)
- Cost aggregation (total spend per day/week/month)
- Performance metrics (avg duration per node)
- Large-scale queries (millions of traces)

**Migration Path:**
1. Keep PostgreSQL for:
   - Projects, users, config
   - Recent traces (last 7 days)
   - Active session data

2. Add ClickHouse for:
   - Historical traces (archive after 7 days)
   - Analytics queries
   - Aggregations and reports

3. Dual-write pattern:
   - Write to both PostgreSQL + ClickHouse
   - Read from PostgreSQL (recent) or ClickHouse (historical/analytics)

**When to Add:**
- **Trigger 1:** >1M traces in PostgreSQL (performance degrades)
- **Trigger 2:** Analytics queries taking >5 seconds
- **Trigger 3:** User requests advanced reporting

---

## Success Metrics

### Phase 1 Success
- [ ] First trace visible in UI within 2 weeks
- [ ] PO can create project and see traces
- [ ] SDK integration takes <30 minutes

### Phase 2 Success
- [ ] Developer debugs production issue using SwisperStudio
- [ ] All trace details captured (state, prompts, tools)
- [ ] Cost tracking accurate to $0.001

### Phase 3 Success
- [ ] PO understands system flow without reading code
- [ ] Graph visualization loads in <2 seconds
- [ ] System architecture view shows all nodes

### Phase 4 Success
- [ ] PO changes LLM config without developer help
- [ ] Config change applied in <5 seconds (test mode)
- [ ] Production deployment via Git tracked
- [ ] SAP specification complete and validated

### Overall MVP Success
- [ ] All 5 MVP requirements delivered
- [ ] 100% of Swisper nodes traced
- [ ] <1 second p95 latency for trace ingestion
- [ ] Zero data loss in trace capture
- [ ] PO productivity: Config changes 10x faster

---

## Development Workflow

### Per Phase
1. **📚 ANALYSIS** - Study Langfuse + Swisper codebases (MANDATORY)
   - Langfuse: Backend patterns + Frontend UX
   - Swisper: Backend integration points + Frontend UI (styling, components, icons)
   - Document findings before proceeding
2. **Plan** - Create detailed sub-plan for this phase
3. **Get Approval** - Present to user, wait for confirmation
4. **TDD** - Write tests first (when applicable)
5. **Implement** - Build backend + frontend (using patterns from analysis)
6. **Test** - End-to-end integration test
7. **Critique** - Review code quality
8. **Refactor** - Apply improvements
9. **Document** - Update docs, OpenAPI
10. **Demo** - Present working feature
11. **Get Approval** - Confirm before next phase

### Reference Analysis Per Phase

**Phase 1 Analysis Focus:**
- **Langfuse:** Project CRUD, trace ingestion, trace list UX, routing patterns
- **Swisper:** Component library, icon system, styling basics, page layouts

**Phase 2 Analysis Focus:**
- **Langfuse:** Observation tree, cost calculation, telemetry capture, trace detail UX
- **Swisper:** LangGraph integration, state classes, JSON viewers, code display

**Phase 3 Analysis Focus:**
- **Langfuse:** Graph visualization (if exists), node rendering, React Flow
- **Swisper:** Any graph components, interactive UI patterns
- **LangGraph Studio:** Reference for graph visualization

**Phase 4 Analysis Focus:**
- **Langfuse:** Settings UI, form patterns, configuration storage
- **Swisper:** Config tables, YAML loading, existing admin features
- **Other:** Django Admin, Rails Admin (dynamic forms)

**Analysis Deliverables:**
Each phase produces `docs/analysis/phase{N}_analysis.md` with:
- Key patterns to copy
- Components to reuse
- Code snippets to reference
- Design decisions and rationale
- Things to avoid (anti-patterns)

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Langfuse reference outdated | Low | Low | Pin to specific commit, update quarterly |
| SDK integration complex | Medium | High | Create graph-level wrapper (one-line change) |
| State capture performance | Low | Medium | Async serialization, sampling in production |
| Config sync conflicts | Low | Medium | Git as source of truth, test mode first |
| ClickHouse complexity | Medium | Low | Delay until needed, PostgreSQL sufficient for MVP |
| SAP adoption resistance | Medium | Medium | Make SAP optional, fallback to manual config |

---

## Next Steps

1. **Get approval on this plan** ✅ (You are here)
2. **Start Phase 1 implementation**
3. **Follow TDD workflow strictly**
4. **Reference Langfuse/Swisper code as planned**
5. **Demo after each phase**

---

**Ready to start Phase 1?** 🚀

**Approved by:** _____________  
**Date:** _____________
