# Phase 2 Detailed Sub-Plan: Rich Tracing

**Date:** November 2, 2025  
**Phase:** Phase 2 - Rich Tracing  
**Duration:** 3 weeks (Backend: 2 weeks, Frontend: 2 weeks, SDK: 1 week - overlapping)  
**Branch:** `feature/week-1-backend-foundation` (continuing)  
**Status:** Backend COMPLETE ✅ | Frontend IN PROGRESS 🔄 | SDK PENDING ⏸️

## Progress Summary

**Backend (Steps 1-5): ✅ COMPLETE**
- Database schema extended
- Cost calculation working
- Observation tree service working
- Enhanced filtering implemented
- 46/46 tests passing
- Async event loop infrastructure fixed permanently

**Frontend (Steps 6-7): ✅ COMPLETE**
- Project navigation with sidebar
- Project overview page
- Configuration page (read-only)
- Routing updated to nested structure

**Frontend (Steps 8-9): ✅ COMPLETE**
- Trace detail page with tabs (Tree/Timeline/JSON)
- Observation tree component with MUI TreeView
- useTraceDetail hook for data fetching
- Navigation from trace list to detail working

**Frontend (Steps 10-14): ⏸️ DEFERRED (Optional for MVP)**
- State viewer, LLM details, tool viewer components
- Can be added as needed for richer detail view
- MVP shows key info in tree nodes

**SDK (Steps 15-18): ⏸️ DEFERRED**
- Will implement after frontend complete

---

## 📋 PHASE IMPLEMENTATION PLAN

From: `docs/plans/swisper_studio_implementation_plan.md - Phase 2: Rich Tracing`

**Business Value:** Developers can debug with complete execution context - full state, LLM details, cost tracking

---

## Detailed Sub-Plan

### **Backend (Week 1-2)**

#### **Step 1: Database Schema - Observations & Model Pricing**

**Files to Modify:**
1. `backend/app/models.py`
   - **Extend Observation model:**
     - Add timing fields: `completion_start_time`
     - Add token fields: `prompt_tokens`, `completion_tokens`, `total_tokens`
     - Add cost fields: `calculated_input_cost`, `calculated_output_cost`, `calculated_total_cost`
     - Add LLM fields: `model`, `model_parameters` (JSON)
     - Add content fields: enhance `input`/`output` to store full state snapshots
     - Add status fields: `level` (DEFAULT/DEBUG/WARNING/ERROR), `status_message`
   
   - **Add ModelPricing model:**
     ```python
     class ModelPricing(SQLModel, table=True):
         id: UUID
         project_id: UUID  # FK to projects
         hosting_provider: str  # "openai", "anthropic", "azure", etc.
         model_name: str  # "gpt-4-turbo", "claude-3-opus", etc.
         input_price_per_million: Decimal  # USD per 1M tokens
         output_price_per_million: Decimal  # USD per 1M tokens
         created_at: datetime
         updated_at: datetime
     ```
     - Unique constraint on (project_id, hosting_provider, model_name)
     - Index on (project_id, hosting_provider, model_name) for fast lookups

2. `backend/alembic/versions/YYYYMMDD_phase2_observations_and_pricing.py`
   - Extend observations table (new columns)
   - Create model_pricing table
   - Add indexes on observations: `model`, `level`, `calculated_total_cost`
   - Add indexes on model_pricing: composite (project_id, hosting_provider, model_name)
   - Seed default pricing for common models (OpenAI, Anthropic, Azure)
   - Ensure nullable for backward compatibility

**Seed Data (in migration):**
```python
# Common model pricing (as of Nov 2024)
default_pricing = [
    ("openai", "gpt-4-turbo", 10.00, 30.00),
    ("openai", "gpt-4", 30.00, 60.00),
    ("openai", "gpt-3.5-turbo", 0.50, 1.50),
    ("anthropic", "claude-3-opus", 15.00, 75.00),
    ("anthropic", "claude-3-sonnet", 3.00, 15.00),
    ("anthropic", "claude-3-haiku", 0.25, 1.25),
]
```

**Testing Approach:**
- Test model creation with all new fields
- Test model creation with only required fields (backward compat)
- Test migration up/down

---

#### **Step 2: Cost Calculation Service (DB-based)**

**Files to Create:**
1. `backend/app/api/services/cost_calculation_service.py`
   - Function: `calculate_llm_cost(project_id: UUID, hosting_provider: str, model: str, prompt_tokens: int, completion_tokens: int) -> CostResult`
   - **Lookup pricing from database:**
     - Query `ModelPricing` by (project_id, hosting_provider, model_name)
     - If not found for project, try default pricing (project_id = NULL)
     - If still not found, log warning and return None (or use fallback estimate)
   - **Calculate costs:**
     - `input_cost = (prompt_tokens / 1_000_000) * input_price_per_million`
     - `output_cost = (completion_tokens / 1_000_000) * output_price_per_million`
     - `total_cost = input_cost + output_cost`
   - Return `CostResult(input_cost, output_cost, total_cost)`
   
   **Important:** Swisper allows per-node model configuration, so each observation can have a different model. We look up pricing per observation, not per trace.

**Files to Create (Tests):**
1. `backend/tests/api/services/test_cost_calculation_service.py`
   - Test known models
   - Test unknown models
   - Test edge cases (zero tokens, negative)

**Testing Approach:**
- TDD: Write tests first
- Test all common models
- Test rounding and precision (Decimal)

---

####**Step 3: Enhanced Trace Ingestion**

**Files to Modify:**
1. `backend/app/api/routes/traces.py`
   - Update `POST /api/v1/observations` to accept new fields
   - Calculate costs on ingestion (call cost_calculation_service)
   - Store full state snapshots in `input`/`output`

2. `backend/app/api/routes/observations.py` (if exists, else create)
   - `PATCH /api/v1/observations/{id}` - Update observation (e.g., add end_time, output)
   - Recalculate costs on update if tokens/model change

**Files to Create (Schemas):**
1. `backend/app/api/schemas/observation_schemas.py`
   - `ObservationCreate` - Extended with new fields
   - `ObservationUpdate` - For PATCH endpoint
   - `ObservationResponse` - Include calculated fields

**Testing Approach:**
- Test observation creation with LLM telemetry
- Test cost calculation on ingestion
- Test observation update

---

#### **Step 4: Observation Tree API**

**Files to Create:**
1. `backend/app/api/services/observation_tree_service.py`
   - Function: `build_observation_tree(trace_id: UUID) -> ObservationTree`
   - Fetch all observations for trace
   - Build nested structure (parent-child relationships)
   - Calculate aggregated metrics (total cost, total duration)
   - Return tree structure with nested children

**Files to Modify:**
1. `backend/app/api/routes/traces.py`
   - Add `GET /api/v1/traces/{id}/tree` endpoint
   - Call observation_tree_service
   - Return nested JSON structure

**Files to Create (Tests):**
1. `backend/tests/api/services/test_observation_tree_service.py`
   - Test tree building with multiple levels
   - Test cost aggregation
   - Test empty tree (no observations)

**Testing Approach:**
- Create test data with nested observations
- Verify tree structure
- Verify aggregated metrics

---

#### **Step 5: Search and Filter API**

**Files to Modify:**
1. `backend/app/api/routes/traces.py`
   - Enhance `GET /api/v1/traces` with filters:
     - `user_id` (existing)
     - `session_id` (new)
     - `start_date`, `end_date` (date range)
     - `min_cost`, `max_cost` (cost range)
     - `model` (filter by LLM model)
     - `level` (filter by observation level)
   - Add pagination (existing)
   - Add sorting (by date, cost, duration)

**Files to Modify (Tests):**
1. `backend/tests/api/test_traces.py`
   - Test filtering by each parameter
   - Test combined filters
   - Test sorting
   - Test pagination with filters

**Testing Approach:**
- Create varied test data
- Test each filter independently
- Test filter combinations

---

### **Frontend (Week 2-3)**

#### **Step 6: Project Navigation Structure**

**Files to Create:**
1. `frontend/src/features/projects/ProjectLayout.tsx`
   - Layout wrapper for all project pages
   - Contains: Header (project name, environment badge) + Sidebar + Content area
   - Props: `projectId`, `children`
   - Fetches project details for header

2. `frontend/src/features/projects/ProjectSidebar.tsx`
   - Navigation sidebar (reuse Swisper agent sidebar styling)
   - Menu items:
     - 📊 Overview (`/projects/:projectId`)
     - 🔍 Tracing (`/projects/:projectId/tracing`)
     - 📈 Analytics (`/projects/:projectId/analytics`) - grayed out for MVP
     - 🌐 Graphs (`/projects/:projectId/graphs`) - grayed out for MVP
     - ⚙️ Configuration (`/projects/:projectId/config`)
   - Highlight active route
   - Collapsible on mobile

3. `frontend/src/features/projects/ProjectOverview.tsx`
   - Simple landing page when clicking project card
   - Shows: Project name, environment, description
   - **MVP version:** Basic layout with "View Traces" button
   - **Post-MVP:** Key metrics (total traces, total cost, error rate, recent traces)
   - Quick actions card with links to main features

**Files to Modify:**
1. `frontend/src/App.tsx`
   - Update routing structure to nested routes:
   ```typescript
   <Route path="/projects/:projectId" element={<ProjectLayout />}>
     <Route index element={<ProjectOverview />} />
     <Route path="tracing" element={<TracingPage />} />
     <Route path="tracing/:traceId" element={<TraceDetailPage />} />
     <Route path="analytics" element={<AnalyticsPage />} />
     <Route path="graphs" element={<GraphsPage />} />
     <Route path="config" element={<ConfigPage />} />
   </Route>
   ```

2. `frontend/src/features/projects/ProjectsPage.tsx`
   - Update project card click to navigate to `/projects/:projectId` (overview)
   - Instead of directly to tracing

**Testing Approach:**
- Manual UAT
- Verify sidebar navigation works
- Verify project context persists across pages
- Verify active route highlighting
- Test on mobile (sidebar collapse)

---

#### **Step 7: Configuration Page (Read-only)**

**Files to Create:**
1. `frontend/src/features/config/ConfigPage.tsx`
   - Simple read-only display for MVP
   - Tabs: General | Model Pricing | API Keys (coming soon)
   - **General tab:** Project name, environment, created date
   - **Model Pricing tab:** Table showing current pricing
     - Columns: Provider, Model, Input ($/1M), Output ($/1M)
     - Data fetched from `GET /api/v1/projects/:projectId/model-pricing`
   - Message: "Full configuration UI coming in Phase 4"

2. `frontend/src/features/config/api/useModelPricing.ts`
   - React Query hook: `useModelPricing(projectId)`
   - Fetch pricing data

**Files to Create (Backend API):**
1. `backend/app/api/routes/model_pricing.py`
   - `GET /api/v1/projects/:projectId/model-pricing` - List all pricing for project
   - Returns: Array of ModelPricing objects

**Testing Approach:**
- Manual UAT
- Verify pricing displays correctly
- Verify different providers group properly

---

#### **Step 8: Trace Detail Page**

**Files to Create:**
1. `frontend/src/features/traces/TraceDetailPage.tsx`
   - Route: `/traces/:traceId`
   - Fetch trace + observations tree
   - Layout: Header (trace info) + Tabs (Tree/Timeline/JSON)
   - Display trace metadata (name, user, timestamps, total cost)

**Files to Create:**
1. `frontend/src/features/traces/api/useTraceDetail.ts`
   - React Query hook: `useTraceDetail(traceId)`
   - Fetch `GET /api/v1/traces/{id}/tree`

**Testing Approach:**
- Manual UAT (no frontend tests in MVP per ADR-007)
- Verify page loads
- Verify trace info displays

---

#### **Step 9: Observation Tree Component**

**Files to Create:**
1. `frontend/src/features/traces/components/ObservationTree.tsx`
   - MUI TreeView component
   - Display nested observations
   - Show: name, type, duration, cost (per observation)
   - Color-code by type (SPAN, GENERATION, TOOL)
   - Click to select observation → show details

2. `frontend/src/features/traces/components/ObservationTreeItem.tsx`
   - Individual tree node
   - Display icon by type
   - Display metrics (duration, tokens, cost)
   - Highlight selected observation

**Testing Approach:**
- Manual UAT
- Verify tree structure displays
- Verify selection works
- Verify metrics display correctly

---

#### **Step 10: State Viewer Component**

**Files to Create:**
1. `frontend/src/features/traces/components/StateViewer.tsx`
   - Tabs: Input | Output | Diff
   - Display JSON with syntax highlighting
   - Expandable/collapsible sections
   - Copy to clipboard button

2. `frontend/src/features/traces/components/JsonViewer.tsx`
   - Reusable JSON display component
   - Use `react-json-view` or similar library
   - Syntax highlighting
   - Collapse/expand controls

3. `frontend/src/features/traces/components/StateDiff.tsx`
   - Display diff between input and output
   - Use `react-diff-viewer` or similar
   - Highlight added/removed/changed fields
   - Handle nested objects

**Testing Approach:**
- Manual UAT
- Test with various state structures
- Verify diff calculation
- Test collapse/expand

---

#### **Step 11: LLM Details Component**

**Files to Create:**
1. `frontend/src/features/traces/components/LLMDetails.tsx`
   - Card layout
   - Display: Model, Parameters (temp, max_tokens, etc.)
   - Display: Tokens (input, output, total)
   - Display: Costs (input, output, total)
   - Display: Timing (start, end, latency, TTFT)

**Testing Approach:**
- Manual UAT
- Verify all fields display
- Verify cost formatting
- Verify timing calculations

---

#### **Step 12: Tool Call Viewer Component**

**Files to Create:**
1. `frontend/src/features/traces/components/ToolCallViewer.tsx`
   - Display tool name
   - Display arguments (JSON)
   - Display results (JSON)
   - Display duration

**Testing Approach:**
- Manual UAT
- Test with various tool calls
- Verify JSON formatting

---

#### **Step 13: Search and Filter UI**

**Files to Modify:**
1. `frontend/src/features/traces/TracesPage.tsx`
   - Add filter controls:
     - Date range picker
     - Model selector (dropdown)
     - Cost range (min/max inputs)
     - Level selector (checkboxes)
   - Add search input (trace name)
   - Apply filters to API call

2. `frontend/src/features/traces/api/useTraces.ts`
   - Update to accept filter parameters
   - Pass to API query

**Testing Approach:**
- Manual UAT
- Test each filter
- Test combined filters
- Verify results update

---

#### **Step 14: Cost Tracking Display**

**Files to Create:**
1. `frontend/src/features/traces/components/CostSummary.tsx`
   - Display on trace detail page
   - Show total cost for trace
   - Show cost breakdown by observation
   - Show cost by model (aggregated)

**Files to Modify:**
1. `frontend/src/features/traces/TracesPage.tsx`
   - Add cost column to traces table
   - Format as currency ($X.XXXX)

**Testing Approach:**
- Manual UAT
- Verify cost aggregation
- Verify currency formatting

---

### **SDK Enhancement (Week 3)**

#### **Step 15: Auto-Capture State**

**Files to Create:**
1. `sdk/swisper_studio_sdk/tracing/state_capture.py`
   - Function: `capture_state_snapshot(state: Dict) -> Dict`
   - Serialize state to JSON
   - Handle special types (datetime, UUID, etc.)
   - Return JSON-serializable dict

**Files to Modify:**
1. `sdk/swisper_studio_sdk/tracing/decorators.py`
   - Update `@traced` decorator
   - Capture state before node execution (input)
   - Capture state after node execution (output)
   - Send both to SwisperStudio API

**Testing Approach:**
- Test state capture with simple dict
- Test with complex types
- Test with Pydantic models
- Verify JSON serialization

---

#### **Step 16: LLM Wrapper**

**Files to Create:**
1. `sdk/swisper_studio_sdk/tracing/llm_wrapper.py`
   - Wrap LangChain LLMs
   - Auto-capture: prompt, response, tokens, model, parameters
   - Create GENERATION observation automatically
   - Handle streaming responses

**Testing Approach:**
- Test with ChatOpenAI
- Test with streaming
- Test with different models
- Verify token capture

---

#### **Step 17: Tool Wrapper**

**Files to Create:**
1. `sdk/swisper_studio_sdk/tracing/tool_wrapper.py`
   - Wrap LangChain tools
   - Auto-capture: tool name, arguments, result, duration
   - Create TOOL observation automatically

**Testing Approach:**
- Test with various tools
- Test tool with complex arguments
- Verify timing capture

---

#### **Step 18: Error Tracking**

**Files to Modify:**
1. `sdk/swisper_studio_sdk/tracing/decorators.py`
   - Catch exceptions during node execution
   - Set observation `level = ERROR`
   - Set `status_message` to error message
   - Include traceback in metadata

**Testing Approach:**
- Test with failing node
- Verify error captured
- Verify traceback included

---

## Testing Strategy

### **Backend Tests:**
**TDD Approach:**
1. Write tests first for each service/endpoint
2. Execute in Docker containers: `docker compose exec backend pytest -vv`
3. Verify FAIL (red)
4. Implement code
5. Verify PASS (green)

**Test Categories:**
- **Business Value:** Cost calculation works, tree building works
- **Edge Cases:** Empty traces, missing fields, unknown models
- **Error Cases:** Invalid input, missing trace, database errors

**CI Tests:** Mark 1-2 critical tests with `@pytest.mark.ci_critical`

### **Frontend Tests:**
**Per ADR-007:** Simplified testing for MVP
- Manual UAT (User Acceptance Testing)
- No extensive unit tests for UI components
- Focus on end-to-end flows

**UAT Scenarios:**
1. View trace with full LLM details
2. View nested observations in tree
3. View state diff
4. Filter traces by date/cost
5. Search traces by name

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| State serialization fails for complex types | Medium | High | Test with real Swisper state, handle special types |
| Cost calculation inaccurate | Low | Medium | Validate against OpenAI/Anthropic docs, add tests |
| Tree depth causes performance issues | Low | Low | Limit depth in initial implementation, optimize later |
| Diff calculation slow for large states | Medium | Medium | Use efficient diff library, consider backend calculation |
| Frontend complexity | Medium | Medium | Use MUI components, keep MVP scope focused |

---

## Dependencies

**Phase 1 Complete:**
- ✅ Backend infrastructure
- ✅ Database models (Trace, Observation)
- ✅ Frontend setup (React, MUI)
- ✅ Basic trace/observation ingestion

**External:**
- None (all internal development)

---

## Deviations from Original Plan

**Technology:**
- **Original plan:** Mentioned TailwindCSS for frontend
- **Phase 1 decision:** Used MUI v7 (matches Swisper)
- **Phase 2:** Continue with MUI for consistency

**Scope adjustments:**
- **Simplified:** No ClickHouse for MVP (PostgreSQL only)
- **Deferred:** Advanced filtering (full-text search) to later phase

---

## File Checklist

**Backend - New Files:**
- [ ] `backend/app/api/services/cost_calculation_service.py`
- [ ] `backend/app/api/services/observation_tree_service.py`
- [ ] `backend/app/api/schemas/observation_schemas.py`
- [ ] `backend/app/api/routes/model_pricing.py`
- [ ] `backend/alembic/versions/YYYYMMDD_phase2_observations_and_pricing.py`
- [ ] `backend/tests/api/services/test_cost_calculation_service.py`
- [ ] `backend/tests/api/services/test_observation_tree_service.py`

**Backend - Modified Files:**
- [ ] `backend/app/models.py` (add ModelPricing model, extend Observation)
- [ ] `backend/app/api/routes/traces.py`
- [ ] `backend/tests/api/test_traces.py`

**Frontend - New Files (Navigation):**
- [ ] `frontend/src/features/projects/ProjectLayout.tsx`
- [ ] `frontend/src/features/projects/ProjectSidebar.tsx`
- [ ] `frontend/src/features/projects/ProjectOverview.tsx`
- [ ] `frontend/src/features/config/ConfigPage.tsx`
- [ ] `frontend/src/features/config/api/useModelPricing.ts`

**Frontend - New Files (Tracing):**
- [ ] `frontend/src/features/traces/TraceDetailPage.tsx`
- [ ] `frontend/src/features/traces/api/useTraceDetail.ts`
- [ ] `frontend/src/features/traces/components/ObservationTree.tsx`
- [ ] `frontend/src/features/traces/components/ObservationTreeItem.tsx`
- [ ] `frontend/src/features/traces/components/StateViewer.tsx`
- [ ] `frontend/src/features/traces/components/JsonViewer.tsx`
- [ ] `frontend/src/features/traces/components/StateDiff.tsx`
- [ ] `frontend/src/features/traces/components/LLMDetails.tsx`
- [ ] `frontend/src/features/traces/components/ToolCallViewer.tsx`
- [ ] `frontend/src/features/traces/components/CostSummary.tsx`

**Frontend - Modified Files:**
- [ ] `frontend/src/features/traces/TracesPage.tsx`
- [ ] `frontend/src/features/traces/api/useTraces.ts`
- [ ] `frontend/src/features/projects/ProjectsPage.tsx` (update navigation)
- [ ] `frontend/src/App.tsx` (add nested routes for project workspace)

**SDK - New Files:**
- [ ] `sdk/swisper_studio_sdk/tracing/state_capture.py`
- [ ] `sdk/swisper_studio_sdk/tracing/llm_wrapper.py`
- [ ] `sdk/swisper_studio_sdk/tracing/tool_wrapper.py`

**SDK - Modified Files:**
- [ ] `sdk/swisper_studio_sdk/tracing/decorators.py`

---

## Success Criteria

**Backend:**
- ✅ Observation model has all Phase 2 fields
- ✅ Cost calculation works for common models
- ✅ Tree API returns nested structure
- ✅ Filter API works for all parameters
- ✅ All backend tests pass

**Frontend:**
- ✅ Trace detail page displays all information
- ✅ Observation tree shows nested structure
- ✅ State viewer shows input/output/diff
- ✅ LLM details card shows all metrics
- ✅ Search/filter works

**SDK:**
- ✅ State auto-captured at nodes
- ✅ LLM calls auto-tracked
- ✅ Tool calls auto-tracked
- ✅ Errors captured with details

**Integration:**
- ✅ End-to-end: Swisper → SDK → Backend → Frontend works
- ✅ Developer can debug production issue using SwisperStudio
- ✅ Full context available (state, prompts, responses, costs)

---

## Estimated Complexity

**Backend:** Medium
- New services: 2 (cost, tree)
- Extended models: 1 (Observation)
- New endpoints: 2 (tree, enhanced filter)
- Migration: 1

**Frontend:** Medium-High
- New page: 1 (Trace Detail)
- New components: 9
- Modified components: 2

**SDK:** Medium
- New modules: 3 (state, llm, tool wrappers)
- Modified modules: 1 (decorators)

**Overall:** Medium - Well-scoped, clear requirements, building on Phase 1 foundation

---

📌 **Ready to proceed with this approach?**  
Please approve or suggest changes.

