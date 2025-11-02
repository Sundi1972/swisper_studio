# Phase 2 Analysis: Rich Tracing - Langfuse & Swisper Patterns

**Date:** November 2, 2025  
**Analyst:** AI Assistant  
**Purpose:** Understand observation processing, cost calculation, LLM telemetry, state tracking patterns before implementing Phase 2

---

## Executive Summary

**Key Findings:**
- ✅ Langfuse has comprehensive observation model with cost tracking
- ✅ Langfuse tracks tokens, costs, and model parameters systematically
- ✅ Swisper uses TypedDict for complex state management
- ✅ State tracking requires before/after snapshots at each node
- ✅ MUI components (not Tailwind) for frontend

**Recommendation:** Adopt Langfuse's observation column structure and cost calculation patterns, but simplify for MVP (PostgreSQL only, no ClickHouse yet).

---

## 1. Langfuse Observation Model Analysis

### 1.1 Core Observation Fields

From `observationsTable.ts`, Langfuse tracks:

**Identity & Metadata:**
- `id`, `name`, `type` (SPAN, GENERATION, EVENT, TOOL, AGENT)
- `traceId`, `traceName`
- `userId`, `environment`
- `version`, `metadata`

**Timing Metrics:**
- `startTime`, `endTime`
- `completionStartTime` (for TTFT calculation)
- Calculated: `latency` (end - start)
- Calculated: `timeToFirstToken` (completionStartTime - startTime)

**Token & Cost Tracking:**
- `prompt_tokens` (inputTokens)
- `completion_tokens` (outputTokens)
- `total_tokens`
- **Calculated fields:**
  - `calculated_input_cost` ($)
  - `calculated_output_cost` ($)
  - `calculated_total_cost` ($)
- Calculated: `tokensPerSecond` (completion_tokens / latency)

**LLM Details:**
- `model` - Model name (e.g., "gpt-4-turbo")
- `modelId` - Internal model identifier
- `modelParameters` - Temperature, maxTokens, etc.

**Content:**
- `input` (JSON) - Prompt/input data
- `output` (JSON) - Completion/output data

**Status:**
- `level` - DEBUG, DEFAULT, WARNING, ERROR
- `statusMessage` - Error or status details

**Prompt Tracking:**
- `promptName`, `promptVersion` - Links to prompt versioning

### 1.2 Usage Schema

From `types.ts`:

```typescript
Usage = {
  input: number | null,          // Input tokens
  output: number | null,         // Output tokens  
  total: number | null,          // Total tokens
  unit: "TOKENS" | "CHARACTERS" | "IMAGES" | etc,
  inputCost: number | null,      // Calculated input cost
  outputCost: number | null,     // Calculated output cost
  totalCost: number | null       // Calculated total cost
}
```

**Cost Details:**
```typescript
CostDetails = Record<string, number>  // Breakdown by model/tier
```

**Usage Details (Advanced Token Tracking):**
- Supports OpenAI's token breakdown
- `input_cached_tokens`, `output_reasoning_tokens`, etc.
- Flexible key-value structure for future token types

### 1.3 Observation Types

**Supported Types:**
- `SPAN` - Generic execution span
- `GENERATION` - LLM generation (has prompt, completion, usage)
- `EVENT` - Single event (no duration)
- `TOOL` - Tool call execution
- `AGENT` - Agent execution
- `CHAIN` - Chain of operations
- `RETRIEVER` - RAG retrieval
- `EVALUATOR` - Evaluation execution
- `EMBEDDING` - Embedding generation
- `GUARDRAIL` - Guardrail check

**For MVP, focus on:**
- `SPAN` - General nodes
- `GENERATION` - LLM calls
- `TOOL` - Tool executions

---

## 2. Langfuse Cost Calculation Patterns

### 2.1 Cost Calculation Logic

**Pattern observed:**
1. **Capture usage** during ingestion:
   - Extract `promptTokens`, `completionTokens` from LLM response
   - Store in `usage` field
   
2. **Model matching:**
   - Match `model` string to internal `modelId`
   - Look up pricing tier/configuration
   
3. **Calculate costs:**
   - `inputCost = promptTokens * inputPricePerToken`
   - `outputCost = completionTokens * outputPricePerToken`
   - `totalCost = inputCost + outputCost`
   
4. **Store calculated values:**
   - `calculated_input_cost`
   - `calculated_output_cost`
   - `calculated_total_cost`

### 2.2 Pricing Model

**Assumed structure (needs confirmation in Phase 2 implementation):**
- Pricing stored per model
- Separate prices for input/output tokens
- Unit: USD per 1K tokens (typical)
- Example:
  ```
  gpt-4-turbo:
    input: $0.01 / 1K tokens
    output: $0.03 / 1K tokens
  ```

**For MVP:**
- Hardcode common model prices in backend
- Provide override mechanism in database
- Calculate on ingestion (not on-the-fly)

---

## 3. Swisper State Management Patterns

### 3.1 Global Supervisor State

From `global_supervisor_state.py`:

**State is a TypedDict with:**
- **Core conversation:** `user_message`, `chat_id`, `user_id`, `workspace_id`
- **Agent coordination:** `global_planner_decision`, `agent_responses`
- **Memory:** `memory_domain` (conversation_context, facts)
- **User interaction:** `user_in_the_loop` (clarifications, confirmations)
- **Intent:** `intent_classification` (route, needs_external_tools, preferences)
- **Output:** `user_interface_response`

**Key Insight:** State is comprehensive and tracks:
- What the user said
- What the agent plans to do
- What has been executed
- What needs confirmation
- Conversation history

### 3.2 Productivity Agent State

From `productivity_agent_state.py`:

**Agent-specific state includes:**
- `tool_results` - Results from tool executions
- `global_plan`, `current_plan` - Multi-step planning
- `tool_operations` - Batch operations to execute
- `workflow_type` - Current workflow stage
- `stored_data` - Data collected across interrupts
- `resource_type` - EMAIL/CALENDAR (domain-specific)

**Key Insight:** Each agent can extend base state with domain-specific fields.

### 3.3 State Tracking Requirements

**For SwisperStudio, we need to capture:**
1. **Input state** - State at node entry
2. **Output state** - State at node exit
3. **Diff** - What changed (calculated or stored)

**Implementation approach:**
- Serialize full state as JSON at entry/exit
- Store in `observation.input` and `observation.output`
- Calculate diff in backend or display dynamically in UI

---

## 4. Langfuse UI Patterns (for Phase 2 Frontend)

### 4.1 Trace Detail Components

**From exploration:**
- `IOPreview.tsx` - Displays input/output with multiple views:
  - Pretty view (ChatML messages, formatted)
  - JSON view (raw data)
  - Markdown rendering
  - Media support (images, audio)
  
- `TraceTree.tsx` - Tree visualization:
  - Nested observation structure
  - Cost calculation (aggregated)
  - Latency display
  - Expandable/collapsible nodes
  - Color-coded metrics

### 4.2 Key UI Patterns

**Dual view toggle:**
- Users can switch between "Pretty" (formatted) and "JSON" (raw)
- Preference saved in localStorage

**Cost aggregation:**
- Calculate total cost from all child observations
- Display at trace level
- Breakdown per observation

**Timeline vs Tree:**
- Timeline: Chronological sequence
- Tree: Hierarchical structure with nesting
- Both views useful for different debugging

---

## 5. Frontend Technology Stack

### 5.1 Phase 1 Decisions

**From PHASE2_HANDOVER.md:**
- ✅ **MUI v7** (Material-UI) - NOT Tailwind
- ✅ React + Vite
- ✅ Swisper dark theme (#141923)

**Key Components Available:**
- MUI data grid (for tables)
- MUI tree view (for hierarchical display)
- MUI tabs (for view switching)
- MUI cards, dialogs, buttons

### 5.2 Styling Approach

**Swisper theme:**
- Dark background: #141923
- Use MUI theming system
- Consistent with Swisper branding

**Note:** Implementation plan originally mentioned Tailwind, but Phase 1 used MUI. Continue with MUI for consistency.

---

## 6. Recommendations for Phase 2

### 6.1 Backend - Observation Model

**Enhanced fields to add:**
```python
class Observation(SQLModel, table=True):
    # ... existing fields from Phase 1 ...
    
    # Timing
    completion_start_time: Optional[datetime] = None  # For TTFT
    
    # Tokens & Usage
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    
    # Costs (calculated)
    calculated_input_cost: Optional[Decimal] = None
    calculated_output_cost: Optional[Decimal] = None
    calculated_total_cost: Optional[Decimal] = None
    
    # LLM Details
    model: Optional[str] = None
    model_parameters: Optional[Dict] = None  # JSON field
    
    # Content
    input: Optional[Dict] = None   # JSON - full input/state
    output: Optional[Dict] = None  # JSON - full output/state
    
    # Status
    level: str = "DEFAULT"  # DEBUG, DEFAULT, WARNING, ERROR
    status_message: Optional[str] = None
```

### 6.2 Cost Calculation Service

**Create:** `backend/app/api/services/cost_calculation_service.py`

```python
def calculate_observation_cost(
    model: str,
    prompt_tokens: int,
    completion_tokens: int
) -> CostResult:
    """
    Calculate LLM costs based on model and token usage.
    
    Returns: CostResult(input_cost, output_cost, total_cost)
    """
    # Look up pricing for model
    # Calculate costs
    # Return result
```

**Pricing storage:**
- Start with hardcoded dict
- Move to database table later (Phase 4 config)

### 6.3 State Diff Calculation

**Approach 1: Store full snapshots**
- `observation.input` = full state at entry
- `observation.output` = full state at exit
- Calculate diff in UI (client-side)

**Approach 2: Calculate diff in backend**
- Store snapshots AND diff
- `observation.state_diff` = JSON with changes
- Faster UI rendering

**Recommendation:** Start with Approach 1 (simpler), optimize later if needed.

### 6.4 Frontend Components

**Priority components:**
1. **Trace detail page** - View single trace with observations
2. **Observation tree** - Hierarchical view
3. **State viewer** - Display input/output/diff
4. **LLM details card** - Model, params, tokens, cost
5. **Timeline view** - Chronological sequence

**MUI components to use:**
- `TreeView` for observation tree
- `Tabs` for view switching (tree/timeline/JSON)
- `Card` for LLM details
- `Typography` for text
- `Box`, `Stack` for layout

---

## 7. Implementation Sequence

**Week 1-2 (Backend):**
1. Extend Observation model with new fields
2. Create Alembic migration
3. Implement cost calculation service
4. Update trace ingestion to capture LLM telemetry
5. Add observation tree API (nested structure)
6. Add filter/search API

**Week 2-3 (Frontend):**
1. Trace detail page (route + basic layout)
2. Observation tree component
3. State viewer (input/output with JSON view)
4. LLM details display
5. Cost tracking display
6. Search/filter UI

**Week 3 (SDK):**
1. Auto-capture state at node entry/exit
2. LLM wrapper for auto-telemetry
3. Tool wrapper for auto-tracking

---

## 8. Open Questions for Phase 2 Planning

1. **State diffing:**
   - Client-side or server-side calculation?
   - Deep diff algorithm (which library)?

2. **Cost calculation:**
   - Where to store model pricing? (Hardcoded vs DB)
   - How to handle custom models?

3. **Tree vs Timeline:**
   - Default view? (Tree more informative)
   - Persist user preference?

4. **Search/filter:**
   - What fields to filter on? (user, date, trace name, cost range)
   - Full-text search needed?

---

## Appendices

### A. Langfuse Files Examined

- `packages/shared/src/observationsTable.ts` - Table columns definition
- `packages/shared/src/server/ingestion/types.ts` - Ingestion schemas
- `web/src/components/trace/IOPreview.tsx` - Input/output display
- `web/src/components/trace/TraceTree.tsx` - Tree visualization

### B. Swisper Files Examined

- `backend/app/api/services/agents/global_supervisor_state.py` - Main state structure
- `backend/app/api/services/agents/productivity_agent/agent_state.py` - Agent state example

### C. Key Takeaways

1. **Comprehensive tracking:** Langfuse tracks everything - we should too
2. **Calculated fields:** Cost, latency, TTFT are calculated, not captured directly
3. **Flexible JSON:** Use JSON columns for input/output/metadata - enables schema evolution
4. **Multi-view UI:** Users need both pretty (formatted) and raw (JSON) views
5. **State is complex:** Swisper state is rich - capture full snapshots for debugging

---

**Analysis Complete!** Ready to create detailed Phase 2 sub-plan.

