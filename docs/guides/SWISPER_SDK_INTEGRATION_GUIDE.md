# Swisper SDK Integration Guide - Basic Tracing

**Date:** November 3, 2025  
**Version:** v1.0 - Basic Integration  
**Goal:** Get state-level tracing from Swisper to SwisperStudio  
**Duration:** 2-3 hours

---

## 🎯 What You'll Get

**After this integration:**
- ✅ Every Swisper request creates a trace in SwisperStudio
- ✅ All nodes (intent_classification, memory_node, planner, agents, ui_node) visible
- ✅ State before/after each node captured
- ✅ State diff showing what changed (green/red highlighting)
- ✅ Execution duration for each node
- ✅ Error tracking if nodes fail
- ✅ Parent-child nesting (agents → nodes)

**What's NOT included yet (Phase 5.2 enhancements):**
- ⚠️ LLM prompts (will show in state but not extracted)
- ⚠️ Token counts (no cost calculation yet)
- ⚠️ Model parameters (temperature, etc.)
- ⚠️ Observation type = SPAN for all (not GENERATION/TOOL)

**This is sufficient for MVP validation!**

---

## 📋 Prerequisites

**Swisper Requirements:**
- ✅ Python 3.11+
- ✅ LangGraph installed
- ✅ Using `StateGraph(GlobalSupervisorState)`

**SwisperStudio Requirements:**
- ✅ SwisperStudio backend running (`docker compose up -d`)
- ✅ Project created in SwisperStudio
- ✅ API key: `dev-api-key-change-in-production`
- ✅ Project ID: Get from SwisperStudio UI

---

## 🚀 Step-by-Step Integration

### **Step 1: Install SDK in Swisper** (5 mins)

**Navigate to Swisper project:**
```bash
cd /path/to/swisper  # Your Swisper backend project
```

**Install SDK (editable mode for development):**
```bash
# Option A: Using uv (recommended)
uv pip install -e /root/projects/swisper_studio/sdk

# Option B: Using pip
pip install -e /root/projects/swisper_studio/sdk

# Option C: Add to pyproject.toml dependencies
# Add this line to [project.dependencies]:
swisper-studio-sdk = { path = "/root/projects/swisper_studio/sdk", editable = true }
```

**Verify installation:**
```bash
python -c "from swisper_studio_sdk import create_traced_graph, initialize_tracing; print('✅ SDK installed')"
```

**Expected output:**
```
✅ SDK installed
```

---

### **Step 2: Initialize Tracing at Startup** (10 mins)

**Location:** `backend/app/main.py` (FastAPI startup)

**Find the startup event or app creation:**
```python
# Around line 20-30 in main.py
from fastapi import FastAPI

app = FastAPI(title="Swisper Internal API")

# ADD THIS AFTER APP CREATION:
from swisper_studio_sdk import initialize_tracing

# Initialize SwisperStudio tracing
initialize_tracing(
    api_url="http://localhost:8001",  # SwisperStudio backend
    api_key="dev-api-key-change-in-production",  # From SwisperStudio
    project_id="YOUR_PROJECT_ID_HERE",  # Get from SwisperStudio UI
    enabled=True  # Set to False to disable tracing
)

print("✅ SwisperStudio tracing initialized")
```

**Get your Project ID:**
1. Open `http://localhost:3000/projects`
2. Click on your project
3. Copy the ID from the URL: `/projects/{THIS_IS_YOUR_PROJECT_ID}/...`

**Alternative (environment variable):**
```python
import os

initialize_tracing(
    api_url=os.getenv("SWISPER_STUDIO_URL", "http://localhost:8001"),
    api_key=os.getenv("SWISPER_STUDIO_API_KEY", "dev-api-key-change-in-production"),
    project_id=os.getenv("SWISPER_STUDIO_PROJECT_ID"),
    enabled=os.getenv("SWISPER_STUDIO_ENABLED", "true").lower() == "true"
)
```

---

### **Step 3: Wrap Global Supervisor Graph** (5 mins)

**Location:** `backend/app/api/services/agents/global_supervisor/global_supervisor.py`

**Find the graph creation (around line 50-100):**
```python
# BEFORE (current code):
from langgraph.graph import StateGraph
from ..global_supervisor_state import GlobalSupervisorState

def build_graph():
    graph = StateGraph(GlobalSupervisorState)
    
    # Add nodes...
    graph.add_node("intent_classification", intent_classification_node)
    graph.add_node("memory_node", memory_node)
    # ... more nodes
    
    return graph.compile()
```

**AFTER (ONE LINE CHANGE):**
```python
# Import the SDK wrapper
from swisper_studio_sdk import create_traced_graph
from ..global_supervisor_state import GlobalSupervisorState

def build_graph():
    # Change this line ↓
    graph = create_traced_graph(
        GlobalSupervisorState,
        trace_name="global_supervisor"
    )
    
    # Add nodes (UNCHANGED - no changes needed here)
    graph.add_node("intent_classification", intent_classification_node)
    graph.add_node("memory_node", memory_node)
    # ... more nodes
    
    return graph.compile()
```

**That's it!** All nodes are now automatically traced.

---

### **Step 4: Restart Swisper** (1 min)

```bash
# If using Docker:
docker compose restart backend

# If running locally:
# Ctrl+C and restart your dev server
uvicorn app.main:app --reload
```

---

### **Step 5: Send Test Request** (2 mins)

**Option A: Use Swisper UI**
1. Open Swisper frontend
2. Send a message: "What's my next meeting?"
3. Wait for response

**Option B: Use API**
```bash
curl -X POST http://localhost:8000/api/v1/chat/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "user_message": "What is my next meeting?",
    "chat_id": "test_chat_sdk_integration",
    "user_id": "test_user",
    "avatar_id": "your_avatar_id",
    "workspace_id": "your_workspace_id"
  }'
```

---

### **Step 6: View Trace in SwisperStudio** (1 min)

**Navigate to:**
```
http://localhost:3000/projects/{YOUR_PROJECT_ID}/tracing
```

**You should see:**
- ✅ New trace: "global_supervisor"
- ✅ Timestamp: Just now
- ✅ User: test_user
- ✅ Session: test_chat_sdk_integration

**Click the trace!**

---

### **Step 7: Verify Observations** (5 mins)

**In the trace detail view, you should see:**

**Tree structure:**
```
☑ SPAN: global_supervisor  [STATE CHANGED]
  ├─ SPAN: intent_classification  [STATE CHANGED]
  ├─ SPAN: memory_node  [STATE CHANGED]
  ├─ SPAN: global_planner  [STATE CHANGED]
  ├─ SPAN: productivity_agent  [STATE CHANGED]
  └─ SPAN: ui_node  [STATE CHANGED]
```

**Note:** All will be type=SPAN (expected with basic SDK)

**Click on any observation:**
- ✅ State Before shows (user_message, chat_id, model, etc.)
- ✅ State After shows (with additions)
- ✅ State Diff works (green backgrounds for additions!)

---

### **Step 8: Test State Transitions** (10 mins)

**Click on each observation and verify state accumulation:**

**intent_classification:**
- ✅ State Before: Basic fields (user_message, model, chat_id)
- ✅ State After: ADDS `intent_classification` field
- ✅ Diff shows: `+ intent_classification: { route, is_temporal_query, entities, ... }`

**memory_node:**
- ✅ State Before: Has intent_classification from previous
- ✅ State After: ADDS `memory_domain`, `avatar_name`, `presentation_rules`
- ✅ Diff shows: `+ memory_domain: { conversation_context, facts: {...} }`

**productivity_agent:**
- ✅ State Before: Has memory_domain
- ✅ State After: ADDS `agent_responses`
- ✅ Diff shows: `+ agent_responses: { responses: [...] }`

**ui_node:**
- ✅ State Before: Has agent_responses
- ✅ State After: ADDS `user_interface_response`
- ✅ Diff shows: `+ user_interface_response: "Your next meeting is..."`

**Success!** You can trace data flow through the graph! 🎉

---

## ✅ **What Works**

**With basic SDK integration:**

1. ✅ **State Transitions** - See how state accumulates through workflow
   - Example: See when `intent_classification` field is added
   - Example: See when `memory_domain` is loaded
   - Example: See when `agent_responses` are populated

2. ✅ **Execution Flow** - Understand node execution order
   - See which nodes run
   - See parent-child relationships
   - See duration of each node

3. ✅ **Debugging** - Trace issues in production
   - See state at point of failure
   - See which node errored
   - See error message

4. ✅ **Data Flow** - Track how data moves
   - See when fields are added
   - See when fields change
   - See full state at any point

**This is 50% of full observability - and the MOST important 50%!**

---

## ⚠️ **What's Missing (Expected)**

**Known limitations with basic SDK:**

1. ⚠️ **No Prompts** - Can't see LLM prompts (yet)
   - Workaround: Prompts might be in state if you store them
   - Enhancement: Phase 5.2 will add automatic prompt capture

2. ⚠️ **No Token Counts** - Can't calculate costs (yet)
   - Workaround: None
   - Enhancement: Phase 5.2 will add automatic token counting

3. ⚠️ **No Tool Call Details** - Can't see tool arguments (yet)
   - Workaround: Tool args might be in state
   - Enhancement: Phase 5.2 will add tool call tracking

4. ⚠️ **All SPAN Type** - Everything shows as SPAN (not GENERATION/TOOL)
   - Workaround: None
   - Enhancement: Phase 5.2 will auto-detect types

**These are acceptable for MVP!**

---

## 🐛 **Troubleshooting**

### **Problem 1: No Traces Appearing**

**Check SwisperStudio backend:**
```bash
docker compose ps
# backend should be "Up"
```

**Check API key:**
```bash
# In Swisper, print during startup:
print(f"SwisperStudio API: {api_url}")
print(f"SwisperStudio Project: {project_id}")
```

**Check network:**
```bash
# From Swisper, can you reach SwisperStudio?
curl http://localhost:8001/api/v1/health
# Should return: {"status": "healthy"}
```

---

### **Problem 2: Observations Missing**

**Check if nodes are being traced:**
```python
# Add debug logging to Swisper
import logging
logging.basicConfig(level=logging.DEBUG)

# Should see: "Creating observation: intent_classification"
```

**Check SDK context:**
```python
# In Swisper, add to a node:
from swisper_studio_sdk.tracing.context import get_current_trace
print(f"Current trace: {get_current_trace()}")
# Should print a UUID
```

---

### **Problem 3: State Not Captured**

**Issue:** `input` and `output` are null

**Cause:** State isn't serializable

**Solution:** Ensure state is a dict:
```python
# GlobalSupervisorState is TypedDict - already a dict!
# Should work automatically

# If using Pydantic:
state.model_dump()  # Use this instead of state
```

---

### **Problem 4: Performance Impact**

**Measure latency:**
```bash
# Before adding tracing:
time curl -X POST ... # Note the time

# After adding tracing:
time curl -X POST ... # Compare

# Should be <100ms difference
```

**If too slow:**
- Check SwisperStudio backend latency
- Check network between Swisper and SwisperStudio
- Consider async sending (SDK already does this)

---

## 📊 **Testing Checklist**

**After integration, test these scenarios:**

- [ ] Simple message: "Hello"
  - ✅ Creates trace
  - ✅ Shows global_supervisor + nodes
  - ✅ State captured

- [ ] Complex message: "What's my next meeting?"
  - ✅ Creates trace
  - ✅ Routes to productivity_agent
  - ✅ All nodes visible

- [ ] Error case: Invalid input
  - ✅ Creates trace
  - ✅ Error observation with level=ERROR
  - ✅ Status message visible

- [ ] Multiple requests
  - ✅ Each creates separate trace
  - ✅ All visible in trace list
  - ✅ No mixing of data

---

## 🎓 **Understanding What You're Seeing**

### **Trace List:**
```
Traces for Project: AAA Swisper Production Test
┌──────────────────────────────────────────────────────────┐
│ global_supervisor                                        │
│ user_alice | session_xyz | 3 minutes ago                 │
└──────────────────────────────────────────────────────────┘
```

### **Trace Detail (Tree View):**
```
☑ SPAN: global_supervisor  [STATE CHANGED]  5000ms
  ├─ SPAN: intent_classification  [STATE CHANGED]  800ms
  ├─ SPAN: memory_node  [STATE CHANGED]  300ms
  ├─ SPAN: global_planner  [STATE CHANGED]  250ms
  ├─ SPAN: productivity_agent  [STATE CHANGED]  850ms
  └─ SPAN: ui_node  [STATE CHANGED]  500ms
```

### **Details Panel (when you click a node):**
```
State Transition

+ intent_classification:    (GREEN BACKGROUND)
  {
    "route": "complex_chat",
    "is_temporal_query": true,
    "entities": [...]
  }

- (fields removed from input)  (RED BACKGROUND)

(unchanged fields)            (GRAY)
```

---

## 🔍 **What to Look For**

### **Successful Integration:**

1. **Trace appears in list** ✅
   - Name: "global_supervisor"
   - User ID: From your request
   - Timestamp: Now

2. **Observation tree shows nodes** ✅
   - See all graph nodes
   - See nesting (productivity_agent might have children)
   - See durations

3. **State diff works** ✅
   - Click intent_classification
   - See `+ intent_classification` field added (green background)
   - See white text on colored backgrounds

4. **State accumulates** ✅
   - Early nodes: Simple state (user_message, model)
   - Later nodes: Rich state (intent, memory, responses)
   - Final node: Complete state with UI response

---

## 🎉 **Success Criteria**

**Integration is successful when:**
- ✅ At least 1 real Swisper trace visible in SwisperStudio
- ✅ All nodes from global_supervisor visible
- ✅ State before/after captured for each node
- ✅ State diff shows changes with green/red backgrounds
- ✅ Can trace execution flow through the graph
- ✅ Can debug state mutations
- ✅ <100ms tracing overhead

---

## 📝 **Example: What You'll See**

### **User Request:** "What's my next meeting with Sarah?"

**Trace:** global_supervisor

**Observations:**

**1. intent_classification**
- State Before: `{user_message, model, chat_id}`
- State After: ADDS `intent_classification: {route: "complex_chat", entities: [{text: "Sarah"}]}`
- **You can see:** The agent classified this as complex_chat and extracted "Sarah"!

**2. memory_node**
- State Before: Has intent_classification
- State After: ADDS `memory_domain: {facts: {sarah_email: "sarah@...", sarah_role: "colleague"}}`
- **You can see:** The system loaded facts about Sarah based on entity extraction!

**3. productivity_agent**
- State Before: Has memory_domain with Sarah's facts
- State After: ADDS `agent_responses: {meeting_title: "Product Review", ...}`
- **You can see:** The agent found the meeting!

**4. ui_node**
- State Before: Has agent_responses
- State After: ADDS `user_interface_response: "Your next meeting with Sarah is..."`
- **You can see:** The final formatted response!

**This is incredibly powerful for debugging!** Even without prompts, you can trace the entire data flow.

---

## 🔧 **Advanced Configuration**

### **Disable Tracing for Specific Environments:**

```python
import os

# Only enable in development
initialize_tracing(
    api_url=os.getenv("SWISPER_STUDIO_URL"),
    api_key=os.getenv("SWISPER_STUDIO_API_KEY"),
    project_id=os.getenv("SWISPER_STUDIO_PROJECT_ID"),
    enabled=os.getenv("ENVIRONMENT") == "development"  # Off in production
)
```

### **Trace Naming:**

```python
# Use different names for different graphs
graph = create_traced_graph(
    GlobalSupervisorState,
    trace_name="global_supervisor"  # Appears in trace list
)

# Or dynamic naming based on request:
graph = create_traced_graph(
    state_class=GlobalSupervisorState,
    trace_name=f"supervisor_{user_id}"  # Per-user traces
)
```

---

## 📚 **Next Steps After Basic Integration**

**Once basic tracing works:**

1. **Gather feedback** (1 week)
   - Use SwisperStudio for debugging
   - See what's valuable
   - Identify gaps

2. **Plan SDK enhancements** (based on feedback)
   - If prompts critical → Add LLM wrapper
   - If costs matter → Add token counting
   - If tool debugging needed → Add tool wrapper

3. **Implement enhancements** (4-5 days)
   - Phase 5.2: Complete SDK
   - Full observability
   - Production-ready

---

## 🎯 **Expected Results**

**Immediate (Day 1):**
- ✅ First real Swisper trace in SwisperStudio
- ✅ Can see state transitions
- ✅ Can trace execution flow
- ✅ Can debug state mutations

**After 1 week of usage:**
- ✅ Identified real debugging value
- ✅ Know what enhancements are critical
- ✅ Ready to complete SDK (if needed)

---

## 📞 **Support**

**If you encounter issues:**
1. Check `docs/guides/SDK_TROUBLESHOOTING_GUIDE.md` (creating next)
2. Review `sdk/README.md` for SDK usage
3. Check SwisperStudio backend logs: `docker compose logs backend`
4. Check Swisper logs for SDK HTTP requests

---

## ✨ **Summary**

**3 code changes to make:**
1. ✅ Install SDK: `uv pip install -e /path/to/sdk`
2. ✅ Initialize: `initialize_tracing(...)` in main.py
3. ✅ Wrap graph: `create_traced_graph(...)` instead of `StateGraph(...)`

**Total time:** 20-30 minutes
**Result:** Real traces flowing to SwisperStudio! 🎉

---

**Ready to integrate!** Follow the steps above and you'll have tracing in <30 minutes.


