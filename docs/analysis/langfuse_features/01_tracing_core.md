# Feature Analysis: Tracing Core

**Priority:** P0 (Must-Have)
**Version:** v1.0
**Date:** 2025-11-01
**Status:** Complete Analysis

---

## 1. What It Does

**Purpose:** Track execution flow of LLM applications with hierarchical spans

**Core Capabilities:**
- ✅ Create traces (execution sessions)
- ✅ Add observations (spans, generations, events)
- ✅ Track LLM calls with input/output
- ✅ Track tool usage
- ✅ Nest observations (parent-child hierarchy)
- ✅ Add metadata, tags, user IDs
- ✅ Track costs (tokens → $)
- ✅ Track latency (start/end times)
- ✅ Group by sessions
- ✅ Search and filter
- ✅ Visualize as tree/graph

**User Experience:**
1. SDK sends trace data via REST API
2. Data stored in PostgreSQL
3. Worker syncs to ClickHouse
4. UI shows traces in table view
5. Click trace → see detailed tree view
6. Filter by user, tag, date, cost, etc.

---

## 2. How It Works (Architecture)

### Data Model

#### **Trace** (`LegacyPrismaTrace`)
```prisma
model LegacyPrismaTrace {
  id         String   @id
  externalId String?  # User-provided ID
  timestamp  DateTime
  name       String?
  userId     String?
  metadata   Json?
  release    String?  # App version
  version    String?  # Trace version
  projectId  String
  public     Boolean
  bookmarked Boolean
  tags       String[]
  input      Json?    # Initial input
  output     Json?    # Final output
  sessionId  String?  # Group related traces
  createdAt  DateTime
  updatedAt  DateTime
}
```

**Key Fields:**
- `id` - Unique trace identifier
- `sessionId` - Groups multiple traces (e.g., chat session)
- `userId` - End user identifier
- `tags` - Filterable labels
- `metadata` - Arbitrary JSON context
- `input/output` - Trace-level I/O

---

#### **Observation** (`LegacyPrismaObservation`)
```prisma
model LegacyPrismaObservation {
  id                  String   @id
  traceId             String?  # Parent trace
  projectId           String
  type                ObservationType  # SPAN, GENERATION, EVENT, etc.
  startTime           DateTime
  endTime             DateTime?
  name                String?
  metadata            Json?
  parentObservationId String?  # For nesting
  level               ObservationLevel  # DEBUG, DEFAULT, WARNING, ERROR
  statusMessage       String?
  version             String?

  # LLM-specific
  model               String?
  modelParameters     Json?
  input               Json?
  output              Json?
  promptTokens        Int
  completionTokens    Int
  totalTokens         Int

  # Cost tracking
  inputCost           Decimal?  # User-provided
  outputCost          Decimal?
  totalCost           Decimal?
  calculatedInputCost Decimal?  # Calculated from model prices
  calculatedOutputCost Decimal?
  calculatedTotalCost  Decimal?

  # Prompt versioning
  promptId            String?  # Link to Prompt

  completionStartTime DateTime?  # Time to first token
}

enum ObservationType {
  SPAN        # Generic span
  EVENT       # Point-in-time event
  GENERATION  # LLM generation
  AGENT       # Agent execution
  TOOL        # Tool call
  CHAIN       # Chain of operations
  RETRIEVER   # RAG retrieval
  EVALUATOR   # Evaluation step
  EMBEDDING   # Embedding generation
  GUARDRAIL   # Safety check
}
```

**Key Fields:**
- `type` - Observation category
- `parentObservationId` - Builds tree structure
- `startTime/endTime` - Duration tracking
- `promptTokens/completionTokens` - LLM usage
- `input/output` - Step-level I/O
- `promptId` - Links to prompt version

---

### API Endpoints

#### **Ingestion API** (`/api/public/...`)
```typescript
POST /api/public/traces
POST /api/public/generations
POST /api/public/spans
POST /api/public/events
POST /api/public/scores
```

**Example: Create Trace**
```json
POST /api/public/traces
{
  "id": "trace-123",
  "name": "chat_session",
  "userId": "user-456",
  "metadata": {
    "environment": "production"
  },
  "tags": ["chat", "v1.0"]
}
```

**Example: Create Generation (LLM Call)**
```json
POST /api/public/generations
{
  "traceId": "trace-123",
  "name": "openai_chat",
  "startTime": "2025-11-01T10:00:00Z",
  "endTime": "2025-11-01T10:00:02Z",
  "model": "gpt-4",
  "modelParameters": {
    "temperature": 0.7,
    "max_tokens": 150
  },
  "input": {
    "messages": [{"role": "user", "content": "Hello"}]
  },
  "output": {
    "choices": [{"message": {"role": "assistant", "content": "Hi!"}}]
  },
  "usage": {
    "promptTokens": 10,
    "completionTokens": 5,
    "totalTokens": 15
  }
}
```

---

### Storage Architecture

```
┌─────────────┐
│  SDK Call   │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  POST /api/public   │ (Next.js API Route)
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   PostgreSQL        │ (Primary storage)
│  - traces           │
│  - observations     │
│  - scores           │
└──────┬──────────────┘
       │
       ▼ (async via BullMQ)
┌─────────────────────┐
│   Worker Process    │ (Background sync)
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   ClickHouse        │ (Analytics DB)
│  - Fast aggregations│
│  - Dashboard metrics│
└─────────────────────┘
```

**Why Two Databases?**
- **PostgreSQL** - ACID transactions, relations, fast writes
- **ClickHouse** - Columnar storage, fast analytics, aggregations

---

### Query Layer

#### **tRPC Router** (`traces.ts`)
```typescript
export const traceRouter = createTRPCRouter({
  // Get traces list with filters
  all: protectedProjectProcedure
    .input(TraceFilterOptions)
    .query(async ({ input }) => {
      return await getTracesTable(input);
    }),

  // Get single trace with observations
  byId: protectedGetTraceProcedure
    .input(z.object({ traceId: z.string() }))
    .query(async ({ input }) => {
      const trace = await getTraceById(input.traceId);
      const observations = await getObservationsForTrace(input.traceId);
      return { trace, observations };
    }),

  // Get trace graph data (for visualization)
  graph: protectedGetTraceProcedure
    .input(z.object({ traceId: z.string() }))
    .query(async ({ input }) => {
      return await getAgentGraphData(input.traceId);
    }),
});
```

**Query Features:**
- Filtering by: user, tag, date range, metadata
- Search: full-text across names, IDs, metadata
- Pagination: server-side
- Sorting: by timestamp, cost, duration

---

### UI Components

#### **Trace Table View**
**Location:** `web/src/features/dashboard/` or traces page

**Features:**
- Paginated table
- Sortable columns
- Filterable (advanced filters)
- Search
- Bulk actions (export, delete)

**Columns:**
- Timestamp
- Name
- User ID
- Latency
- Token count
- Cost
- Tags
- Status

---

#### **Trace Detail View**
**Location:** Trace detail page

**Features:**
- Trace metadata (user, tags, timestamps)
- Tree view of observations
- Timeline visualization
- Input/output display (JSON viewer)
- Cost breakdown
- Token usage
- Linked prompt versions

**Example Tree:**
```
Trace: chat_session
├── SPAN: global_supervisor
│   ├── GENERATION: intent_classification (gpt-4-turbo)
│   ├── SPAN: memory_node
│   │   └── GENERATION: fact_extraction (gpt-4)
│   ├── TOOL: search_documents
│   │   └── RETRIEVER: vector_search
│   └── GENERATION: response_generation (gpt-4)
└── EVENT: session_complete
```

---

#### **Graph Visualization**
**Location:** `web/src/features/trace-graph-view/`

**Features:**
- Interactive node graph
- Zoom/pan
- Node details on hover
- Color-coded by type
- Shows token usage per node
- Shows latency per node

---

## 3. Relevance to Swisper SDK

### Priority: **P0 (Must-Have)**

**Why Essential:**
1. ✅ **LangGraph Tracing** - Your supervisor/agents create complex graphs
2. ✅ **Tool Tracking** - Track all tool calls (search, calendar, email)
3. ✅ **LLM Call Visibility** - See every prompt/response
4. ✅ **Performance Debug** - Find slow nodes
5. ✅ **Cost Tracking** - Per-user, per-session costs
6. ✅ **Error Debugging** - See where failures occur

---

### Swisper-Specific Considerations

#### **LangGraph Integration:**
Langfuse has native LangGraph support:
```python
from langfuse.callback import CallbackHandler

handler = CallbackHandler(...)
graph.invoke(input, config={"callbacks": [handler]})
```

**What It Captures:**
- Each node as a SPAN
- Conditional edges
- State updates (input/output of each node)
- Sub-graphs (nested)

**What It DOESN'T Capture:**
- ❌ Full state object snapshots
- ❌ State diffs between nodes
- ❌ State field-level changes

**For Your Requirement:** "Track state changes of all state objects"
→ **Need to add custom instrumentation**

---

#### **Swisper Agent Hierarchy:**
```
Trace: user_request
├── AGENT: global_supervisor
│   ├── SPAN: intent_classification_node
│   │   └── GENERATION: classify_intent (gpt-4)
│   ├── SPAN: memory_node
│   │   ├── GENERATION: extract_facts (gpt-4)
│   │   └── TOOL: store_facts (redis)
│   ├── AGENT: productivity_agent
│   │   ├── SPAN: calendar_node
│   │   │   └── TOOL: google_calendar_api
│   │   └── GENERATION: format_response (gpt-4)
│   └── SPAN: ui_node
│       └── GENERATION: format_ui (gpt-4)
└── EVENT: request_complete
```

**Langfuse Can Track:** ✅ All of the above structure

**Langfuse CANNOT Track:**
- ❌ `GlobalSupervisorState` object changes
- ❌ State fields: `facts`, `conversation_history`, `current_intent`
- ❌ When state fields are added/updated/removed

---

## 4. Complexity Assessment

### Build Effort (From Scratch)

**Core Tracing System:**
- Data model: 1 week
- Ingestion API: 1 week
- PostgreSQL storage: 1 week
- Query API: 1 week
- **Subtotal:** 4 weeks

**UI Components:**
- Table view: 1 week
- Detail view: 1 week
- Tree visualization: 2 weeks
- Search/filtering: 1 week
- **Subtotal:** 5 weeks

**ClickHouse Analytics:**
- Schema design: 1 week
- Sync worker: 1 week
- Query layer: 1 week
- **Subtotal:** 3 weeks

**Testing & Polish:**
- Unit tests: 1 week
- Integration tests: 1 week
- Bug fixes: 1 week
- **Subtotal:** 3 weeks

**TOTAL BUILD EFFORT:** **15-16 weeks** (3.5-4 months)

---

### Fork Effort

**Using Langfuse:**
- Setup infrastructure: ✅ Done (Phase 1)
- SDK integration: 1 day
- Test traces: 1 day
- Customize UI (rebrand): 2 days
- **Subtotal:** 4 days

**Add State Tracking (custom):**
- Design state snapshot model: 1 day
- Add ingestion endpoint: 2 days
- Add UI view: 3 days
- Test with LangGraph: 2 days
- **Subtotal:** 8 days (1.6 weeks)

**TOTAL FORK EFFORT:** **2 weeks**

**Savings:** 13-14 weeks (~3 months)

---

## 5. Build vs Fork Recommendation

### ✅ **FORK** (Strongly Recommended)

**Reasons:**
1. **Mature System** - Battle-tested with 1000s of users
2. **Complete Feature Set** - Covers 95% of your needs
3. **Active Development** - Weekly improvements
4. **Time Savings** - 3 months vs 2 weeks
5. **Lower Risk** - Proven architecture
6. **ClickHouse Included** - Analytics-ready

**What You Get:**
- ✅ Trace/observation model
- ✅ Ingestion API
- ✅ Storage (PostgreSQL + ClickHouse)
- ✅ Query layer
- ✅ UI (table + detail + graph views)
- ✅ Search/filtering
- ✅ Cost tracking
- ✅ LangGraph support

**What You Need to Add:**
- 🏗️ State tracking (new feature)
- 🔧 Swisper-specific customizations

---

### Trade-offs

#### **Fork Advantages:**
- ✅ Fast time-to-market
- ✅ Production-ready
- ✅ Comprehensive feature set
- ✅ Active upstream

#### **Fork Disadvantages:**
- ❌ TypeScript/Next.js stack (vs Python)
- ❌ Some unnecessary features (multi-tenancy, RBAC)
- ❌ Need to maintain fork
- ❌ State tracking not included

#### **Build from Scratch Advantages:**
- ✅ Python backend (single stack)
- ✅ Tailored to exact needs
- ✅ No extra features
- ✅ Full control

#### **Build from Scratch Disadvantages:**
- ❌ 3-4 months development
- ❌ More bugs initially
- ❌ No community support
- ❌ Need to build ClickHouse integration
- ❌ Miss out on upstream improvements

---

## 6. Implementation Plan (If Forking)

### Phase 1: Use As-Is (1 week)
1. ✅ Infrastructure setup (done)
2. Integrate Langfuse SDK in Swisper backend
3. Add tracing to key services:
   - `orchestration_service.py`
   - `global_supervisor` graph
   - Domain agents
4. Test trace visibility in UI

### Phase 2: Add State Tracking (1-2 weeks)
1. Design `StateSnapshot` data model
2. Add ingestion endpoint: `POST /api/public/state-snapshots`
3. Create state diff calculator
4. Add UI: State timeline view
5. Integrate with LangGraph checkpointing

### Phase 3: Customize UI (1 week)
1. Rebrand to SwisperStudio
2. Simplify navigation (remove unused features)
3. Add Swisper-specific views
4. Custom dashboard for SDK users

**Total:** 3-4 weeks to fully functional SwisperStudio

---

## 7. State Tracking Design (To Add)

### Proposed Data Model

```prisma
model StateSnapshot {
  id            String   @id @default(cuid())
  traceId       String
  observationId String?  # Which node created this snapshot
  timestamp     DateTime @default(now())
  stateName     String   # e.g., "GlobalSupervisorState"
  stateData     Json     # Full state object
  changedFields String[] # Which fields changed
  projectId     String

  @@index([traceId, timestamp])
  @@index([observationId])
}
```

### Ingestion API

```typescript
POST /api/public/state-snapshots
{
  "traceId": "trace-123",
  "observationId": "obs-456",  // Current node
  "stateName": "GlobalSupervisorState",
  "stateData": {
    "current_intent": "search_documents",
    "facts": [...],
    "conversation_history": [...]
  },
  "changedFields": ["current_intent"]  // Optional
}
```

### SDK Integration

```python
from langfuse import Langfuse

langfuse = Langfuse()

# In your LangGraph node
def memory_node(state: GlobalSupervisorState):
    # Track state BEFORE node execution
    langfuse.track_state_snapshot(
        trace_id=trace_id,
        observation_id=current_observation_id,
        state_name="GlobalSupervisorState",
        state_data=state.dict()
    )

    # Execute node logic
    updated_state = extract_facts(state)

    # Track state AFTER node execution
    langfuse.track_state_snapshot(
        trace_id=trace_id,
        observation_id=current_observation_id,
        state_name="GlobalSupervisorState",
        state_data=updated_state.dict(),
        changed_fields=["facts"]
    )

    return updated_state
```

### UI View

**State Timeline:**
```
Timeline View (left-to-right)
├── Node: intent_classification
│   └── State: {"current_intent": null}  →  {"current_intent": "search"}
├── Node: memory_node
│   └── State: {"facts": []}  →  {"facts": [{...}]}
├── Node: productivity_agent
│   └── State: (unchanged)
└── Node: ui_node
    └── State: {"response": null}  →  {"response": {...}}
```

**Diff View:**
```json
{
  "before": {"current_intent": null, "facts": []},
  "after": {"current_intent": "search", "facts": [{"id": 1, ...}]},
  "changed": ["current_intent", "facts"]
}
```

---

## 8. Key Files in Langfuse

**Data Models:**
- `packages/shared/prisma/schema.prisma` (lines 335-440)

**Ingestion API:**
- `web/src/pages/api/public/ingestion.ts`
- `web/src/pages/api/public/traces.ts`
- `web/src/pages/api/public/generations.ts`

**Query Layer:**
- `web/src/server/api/routers/traces.ts`
- `web/src/server/api/routers/observations.ts`
- `packages/shared/src/server/traces.ts`

**UI Components:**
- `web/src/features/dashboard/` (table view)
- `web/src/features/trace-graph-view/` (graph view)
- `web/src/pages/project/[projectId]/traces/[traceId].tsx` (detail view)

**Worker:**
- `worker/src/` (background sync to ClickHouse)

---

## 9. Summary

### What Langfuse Provides:
✅ Complete tracing infrastructure (15-16 weeks of work)
✅ Native LangGraph support
✅ Cost tracking
✅ Performance metrics
✅ Visual graph viewer
✅ Search/filtering
✅ ClickHouse analytics

### What You Need to Add:
🏗️ State tracking (1-2 weeks)
🔧 Swisper-specific UI customization (1 week)

### Recommendation:
**Fork Langfuse** - Saves 3 months, proven architecture, active development

---

**Next:** Analyze Prompt Versioning feature (your requirement #2)

