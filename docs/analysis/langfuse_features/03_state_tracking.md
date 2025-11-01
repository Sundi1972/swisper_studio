# Feature Analysis: State Tracking

**Priority:** P0 (Must-Have)
**Version:** v1.0
**Date:** 2025-11-01
**Status:** Complete Analysis

---

## 1. What It Does

**Purpose:** Track state object changes across LangGraph node executions

**Core Capabilities:**
- ✅ Capture state snapshots before/after each node
- ✅ Track which fields changed
- ✅ Visualize state evolution timeline
- ✅ Compare state between nodes
- ✅ See state diffs
- ✅ Debug state-related issues
- ✅ Understand data flow through graph

**User Experience:**
1. LangGraph executes, SDK captures state after each node
2. State snapshots stored with trace
3. UI shows state timeline
4. Click node → see state at that point
5. Compare states between nodes (diff view)
6. Track specific field changes over time

---

## 2. How It Works (Architecture)

### ⚠️ **Current Langfuse Status:**

**Langfuse DOES Track:**
- ✅ Node executions (observations)
- ✅ Input to each node
- ✅ Output from each node
- ✅ Metadata (JSON)

**Langfuse DOES NOT Track:**
- ❌ State object snapshots
- ❌ State diffs between nodes
- ❌ State field-level changes
- ❌ State evolution timeline

**Why Missing:**
Langfuse is designed for general LLM observability, not specifically for LangGraph state management.

---

### Proposed Data Model

#### **StateSnapshot** Table
```prisma
model StateSnapshot {
  id            String   @id @default(cuid())
  createdAt     DateTime @default(now())
  updatedAt     DateTime @default(now()) @updatedAt

  # Links
  traceId       String   # Parent trace
  observationId String?  # Which node created this snapshot
  projectId     String

  # State Info
  stateName     String   # e.g., "GlobalSupervisorState"
  stateVersion  Int      # Version of state schema
  stateData     Json     # Full state object

  # Change Tracking
  changedFields String[] # Which fields changed from previous
  previousId    String?  # Link to previous snapshot

  # Metadata
  checkpoint    String?  # LangGraph checkpoint ID (if using checkpointing)
  nodeSequence  Int      # Order in execution (0, 1, 2...)

  @@index([traceId, nodeSequence])
  @@index([observationId])
  @@index([stateName])
  @@map("state_snapshots")
}
```

**Key Fields:**
- `traceId` - Links to trace
- `observationId` - Links to specific node execution
- `stateData` - Full JSON of state object
- `changedFields` - Array of field names that changed
- `nodeSequence` - Order of execution (0, 1, 2...)
- `previousId` - Links to previous snapshot for diff

---

### Example State Data

#### **GlobalSupervisorState Snapshot:**
```json
{
  "id": "snapshot_abc123",
  "traceId": "trace_xyz789",
  "observationId": "obs_memory_node",
  "stateName": "GlobalSupervisorState",
  "nodeSequence": 2,
  "stateData": {
    "current_intent": "search_documents",
    "conversation_history": [
      {"role": "user", "content": "Find contracts"},
      {"role": "assistant", "content": "Searching..."}
    ],
    "facts": [
      {"id": "fact_1", "content": "User wants contracts", "priority": 8}
    ],
    "active_agent": "doc_agent",
    "metadata": {
      "session_id": "sess_123",
      "user_id": "user_456"
    }
  },
  "changedFields": ["current_intent", "active_agent"],
  "previousId": "snapshot_abc122"
}
```

---

### API Endpoints

#### **Ingestion API**

**Create State Snapshot:**
```typescript
POST /api/public/state-snapshots
{
  "traceId": "trace-123",
  "observationId": "obs-456",  // Current node
  "stateName": "GlobalSupervisorState",
  "stateVersion": 1,
  "stateData": {
    "current_intent": "search",
    "facts": [...]
  },
  "changedFields": ["current_intent"],
  "nodeSequence": 2,
  "checkpoint": "checkpoint_abc123"  // Optional
}
```

**Get State Timeline:**
```typescript
GET /api/trpc/stateSnapshots.getTimeline
?traceId=trace-123
```

**Response:**
```json
{
  "snapshots": [
    {
      "nodeSequence": 0,
      "nodeName": "intent_classification",
      "stateData": {...},
      "changedFields": []
    },
    {
      "nodeSequence": 1,
      "nodeName": "memory_node",
      "stateData": {...},
      "changedFields": ["facts", "conversation_history"]
    },
    {
      "nodeSequence": 2,
      "nodeName": "doc_agent",
      "stateData": {...},
      "changedFields": ["active_agent", "search_results"]
    }
  ]
}
```

**Get State Diff:**
```typescript
GET /api/trpc/stateSnapshots.getDiff
?snapshotId1=snapshot_1
&snapshotId2=snapshot_2
```

---

### Storage Architecture

```
┌─────────────────────┐
│  LangGraph Node     │
│  Execution          │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  SDK: Capture State │
│  After Each Node    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  POST /api/public/  │
│  state-snapshots    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  PostgreSQL         │
│  - state_snapshots  │
└──────┬──────────────┘
       │
       ▼ (async)
┌─────────────────────┐
│  ClickHouse         │
│  - State analytics  │
│  - Field usage      │
└─────────────────────┘
```

---

### UI Components

#### **1. State Timeline View**
**Location:** Trace detail page (new tab)

**Features:**
- Horizontal timeline showing state evolution
- Node markers
- State changes highlighted
- Zoom/pan
- Click node → see state at that point

**Example:**
```
Timeline (left-to-right):
─────────────────────────────────────────────────────
START → intent_class → memory → doc_agent → ui_node → END
  │         │             │          │          │
  └─ {}     └─ intent↑    └─ facts↑  └─ agent↑  └─ response↑
```

**Legend:**
- `{}` - Empty state
- `field↑` - Field added/changed
- `field↓` - Field removed

---

#### **2. State Inspector**
**Location:** Right panel in trace detail

**Features:**
- JSON tree view of current state
- Collapsible sections
- Search within state
- Copy state as JSON
- Highlight changed fields

**Example:**
```
State at: memory_node (step 2/5)
─────────────────────────────────────
{
  "current_intent": "search",        ← Changed
  "conversation_history": [...],     ← Changed
  "facts": [                         ← Changed
    {"id": "fact_1", ...}
  ],
  "active_agent": null,
  "metadata": {
    "session_id": "sess_123",
    "user_id": "user_456"
  }
}

Changed in this step: current_intent, conversation_history, facts
```

---

#### **3. State Diff View**
**Location:** Compare modal

**Features:**
- Side-by-side comparison
- Highlight additions (green)
- Highlight deletions (red)
- Highlight modifications (yellow)
- JSON diff format

**Example:**
```
Before (Step 1)            │  After (Step 2)
─────────────────────────────────────────────────────
{                          │  {
  "current_intent": null,  │    "current_intent": "search", ← Changed
  "facts": [],             │    "facts": [                  ← Added
                           │      {"id": "fact_1", ...}
                           │    ],
  "active_agent": null     │    "active_agent": null
}                          │  }
```

---

#### **4. Field Change History**
**Location:** Field detail view

**Features:**
- Track single field across all nodes
- Value changes over time
- Line chart (for numeric fields)
- List view (for complex fields)

**Example:**
```
Field: current_intent

Step 0: null
Step 1: null
Step 2: "search_documents"  ← Set here
Step 3: "search_documents"
Step 4: "format_response"   ← Changed here
Step 5: null                ← Cleared here
```

---

#### **5. State Graph Visualization**
**Location:** Graph view with state overlays

**Features:**
- Show state changes on graph edges
- Color-code by change magnitude
- Hover node → see state
- Animate state flow

**Example:**
```
   [intent_class]
         │
         │ +current_intent
         ▼
   [memory_node]
         │
         │ +facts, +history
         ▼
   [doc_agent]
         │
         │ +results, +active_agent
         ▼
   [ui_node]
```

---

## 3. Relevance to Swisper SDK

### Priority: **P0 (Must-Have)**

**Why Essential:**
1. ✅ **State Debugging** - See what state looks like at any point
2. ✅ **Data Flow Understanding** - How data moves through graph
3. ✅ **Bug Reproduction** - Replay exact state sequence
4. ✅ **Performance Analysis** - Which nodes bloat state
5. ✅ **Testing** - Verify state transitions
6. ✅ **Documentation** - Show how state evolves

---

### Swisper-Specific Use Cases

#### **Use Case 1: Debug Fact Extraction**
```
Problem: Facts not being stored correctly

Investigation:
1. View trace
2. Check state timeline
3. See memory_node output:
   Before: {"facts": []}
   After: {"facts": [{"id": "fact_1", "content": "...", "priority": null}]}

Issue Found: priority field is null (should be 8)
Root Cause: extract_facts() not setting priority
```

**Benefit:** Fast debugging with state visibility

---

#### **Use Case 2: Track Intent Changes**
```
Trace: user_request_complex

State Evolution:
Step 0: {"current_intent": null}
Step 1: {"current_intent": "search"}           ← intent_classification
Step 2: {"current_intent": "search"}           ← memory (unchanged)
Step 3: {"current_intent": "multi_step"}       ← planner (changed)
Step 4: {"current_intent": "multi_step"}       ← agent execution
Step 5: {"current_intent": null}               ← cleanup
```

**Benefit:** Understand intent routing logic

---

#### **Use Case 3: Verify State Cleanup**
```
Expected: State should be cleared after request
Actual: conversation_history persists across requests

State Check:
- Step 0 (new request): {"conversation_history": [...]}  ← Should be []
- Issue: Previous state not cleaned up
```

**Benefit:** Catch state leaks

---

#### **Use Case 4: Monitor State Size**
```
State Size Growth:
Step 0: 0.5 KB
Step 1: 1.2 KB
Step 2: 3.8 KB
Step 3: 12.5 KB   ← Large jump
Step 4: 45.2 KB   ← Memory issue!

Investigation:
- Step 3: Added 200 facts (too many)
- Root Cause: Fact filtering not working
```

**Benefit:** Catch performance issues

---

## 4. Complexity Assessment

### Build Effort

**Data Model:**
- Schema design: 2 days
- Migrations: 1 day
- **Subtotal:** 3 days

**Ingestion API:**
- Endpoint creation: 2 days
- Diff calculation: 2 days
- Validation: 1 day
- **Subtotal:** 5 days (1 week)

**Query Layer:**
- Timeline API: 2 days
- Diff API: 2 days
- Field history API: 1 day
- **Subtotal:** 5 days (1 week)

**UI Components:**
- Timeline view: 3 days
- State inspector: 2 days
- Diff view: 3 days
- Field history: 2 days
- Graph overlays: 3 days
- **Subtotal:** 13 days (2.5 weeks)

**SDK Integration:**
- Auto-capture middleware: 2 days
- LangGraph checkpointing: 2 days
- State serialization: 1 day
- **Subtotal:** 5 days (1 week)

**Testing:**
- Unit tests: 3 days
- Integration tests: 2 days
- Bug fixes: 3 days
- **Subtotal:** 8 days (1.5 weeks)

**ClickHouse Sync (Optional):**
- Schema: 2 days
- Worker: 2 days
- Analytics: 2 days
- **Subtotal:** 6 days (1 week)

**TOTAL BUILD EFFORT (without ClickHouse):** **6-7 weeks**
**TOTAL BUILD EFFORT (with ClickHouse):** **7-8 weeks**

---

## 5. Build vs Fork Recommendation

### ⚠️ **BUILD** (Must Add to Fork)

**Why:**
Langfuse doesn't have this feature. You MUST build it.

**Options:**

#### **Option 1: Add to Langfuse Fork** ✅ **Recommended**
- Fork Langfuse
- Add StateSnapshot model
- Add API endpoints
- Add UI components
- Integrated with existing tracing

**Pros:**
- ✅ Integrated with trace viewer
- ✅ Reuse Langfuse UI components
- ✅ Single platform
- ✅ Same authentication/projects

**Cons:**
- ❌ Need to maintain fork
- ❌ TypeScript/Next.js stack

**Effort:** 6-8 weeks

---

#### **Option 2: Separate Service**
- Build standalone state tracking service
- Link to Langfuse traces via trace ID
- Separate UI

**Pros:**
- ✅ Python backend (single stack)
- ✅ Independent development
- ✅ Easier to maintain

**Cons:**
- ❌ Two UIs
- ❌ No integration with trace viewer
- ❌ Duplicate auth/projects

**Effort:** 8-10 weeks (more overhead)

---

### Recommendation: **Option 1** (Add to Fork)

**Why:**
- Better UX (single platform)
- Reuse Langfuse components
- Integrated trace viewer
- Worth the fork maintenance

---

## 6. Implementation Plan

### Phase 1: Data Model & API (2 weeks)
1. Add StateSnapshot model to Prisma
2. Create ingestion endpoint
3. Create diff calculation logic
4. Add timeline query endpoint
5. Test with sample data

### Phase 2: SDK Integration (1 week)
1. Add state capture middleware
2. Integrate with LangGraph
3. Auto-capture after each node
4. Test with real traces

### Phase 3: UI - Timeline View (1.5 weeks)
1. Add state timeline tab to trace detail
2. Implement horizontal timeline
3. Node markers with state changes
4. Click node → show state
5. Test with complex traces

### Phase 4: UI - Inspector & Diff (1.5 weeks)
1. State inspector panel (JSON tree)
2. Diff view modal
3. Highlight changed fields
4. Search within state

### Phase 5: Advanced Features (2 weeks)
1. Field change history
2. Graph visualization overlays
3. State size tracking
4. Performance analytics

### Phase 6: ClickHouse Sync (Optional, 1 week)
1. Add state schema to ClickHouse
2. Sync worker
3. Analytics queries

**Total:** 7-9 weeks (depending on scope)

---

## 7. SDK Integration Design

### Automatic Capture (Recommended)

**LangGraph Middleware:**
```python
from langfuse import Langfuse
from langgraph.graph import StateGraph

langfuse = Langfuse()

class StateCaptureMiddleware:
    """Captures state after each node execution"""

    def __init__(self, trace_id: str):
        self.trace_id = trace_id
        self.sequence = 0
        self.previous_state = None

    def capture_state(self, node_name: str, state: dict, observation_id: str):
        """Capture state snapshot"""

        # Calculate changed fields
        changed_fields = []
        if self.previous_state:
            changed_fields = self._get_changed_fields(
                self.previous_state,
                state
            )

        # Send to Langfuse
        langfuse.track_state_snapshot(
            trace_id=self.trace_id,
            observation_id=observation_id,
            state_name=state.__class__.__name__,
            state_data=state,
            changed_fields=changed_fields,
            node_sequence=self.sequence
        )

        self.sequence += 1
        self.previous_state = state

    def _get_changed_fields(self, prev: dict, curr: dict) -> list[str]:
        """Compare states and return changed field names"""
        changed = []

        for key in set(prev.keys()) | set(curr.keys()):
            if prev.get(key) != curr.get(key):
                changed.append(key)

        return changed


# Usage
def create_graph():
    graph = StateGraph(GlobalSupervisorState)

    # Add nodes
    graph.add_node("intent_classification", intent_node)
    graph.add_node("memory", memory_node)
    # ... more nodes

    # Add state capture middleware
    middleware = StateCaptureMiddleware(trace_id=trace_id)

    # Wrap each node to capture state
    for node_name in graph.nodes:
        original_node = graph.nodes[node_name]

        def wrapped_node(state):
            result = original_node(state)
            middleware.capture_state(
                node_name=node_name,
                state=result,
                observation_id=current_observation_id
            )
            return result

        graph.nodes[node_name] = wrapped_node

    return graph.compile()
```

---

### Manual Capture (Fallback)

**In Each Node:**
```python
def memory_node(state: GlobalSupervisorState):
    # Track state BEFORE
    langfuse.track_state_snapshot(
        trace_id=trace_id,
        observation_id=observation_id,
        state_name="GlobalSupervisorState",
        state_data=state.dict(),
        node_sequence=current_sequence,
        changed_fields=[]
    )

    # Execute node
    updated_state = extract_facts(state)

    # Track state AFTER
    langfuse.track_state_snapshot(
        trace_id=trace_id,
        observation_id=observation_id,
        state_name="GlobalSupervisorState",
        state_data=updated_state.dict(),
        node_sequence=current_sequence + 1,
        changed_fields=["facts", "conversation_history"]
    )

    return updated_state
```

---

## 8. Alternative: Use LangGraph Checkpointing

**LangGraph Built-in Feature:**
LangGraph has checkpointing (saves state at each step)

**Could Leverage:**
```python
from langgraph.checkpoint.postgres import PostgresSaver

# LangGraph saves state automatically
checkpointer = PostgresSaver.from_conn_string(DATABASE_URL)

graph = StateGraph(state_schema=GlobalSupervisorState)
# ... add nodes ...

compiled = graph.compile(checkpointer=checkpointer)

# State is saved at each step
result = compiled.invoke(initial_state, config={"thread_id": thread_id})

# Retrieve checkpoints
checkpoints = checkpointer.list(thread_id)
for checkpoint in checkpoints:
    print(checkpoint.state)  # State at that point
```

**Integration:**
1. Enable LangGraph checkpointing
2. Read checkpoints from checkpoint DB
3. Display in Langfuse UI
4. Link checkpoints to traces

**Pros:**
- ✅ No manual instrumentation
- ✅ Built-in to LangGraph
- ✅ Efficient storage

**Cons:**
- ❌ Separate database (unless sync to Langfuse)
- ❌ Need to build UI still

---

## 9. Summary

### Current State:
❌ **Langfuse does NOT have state tracking**

### What You Need:
✅ State snapshots after each node
✅ Diff calculation
✅ Timeline visualization
✅ State inspector
✅ Field change history

### Build Effort:
🏗️ **6-8 weeks** (if adding to Langfuse fork)
🏗️ **8-10 weeks** (if standalone service)

### Recommendation:
**Add to Langfuse Fork** - Better UX, integrated platform

### Implementation Priority:
1. Phase 1-2: Data model + SDK (3 weeks) - **Critical**
2. Phase 3-4: Basic UI (3 weeks) - **High Priority**
3. Phase 5-6: Advanced features (3 weeks) - **Nice to Have**

### Alternative Approach:
Consider using **LangGraph Checkpointing** + UI integration (saves development time)

---

## 10. Feature Comparison

| Feature | Langfuse Tracing | State Tracking (New) |
|---------|------------------|----------------------|
| **What** | Node executions | State snapshots |
| **When** | Each node call | After each node |
| **Data** | Input/output | Full state object |
| **UI** | Tree/graph view | Timeline + inspector |
| **Granularity** | Per-node | Per-node |
| **Diff** | No | Yes (state diffs) |
| **History** | Node history | Field history |
| **Size** | Small (I/O only) | Large (full state) |

**Complementary Features:**
- Tracing shows **what happened**
- State tracking shows **how data changed**

---

**Next:** Create build vs fork recommendation document

