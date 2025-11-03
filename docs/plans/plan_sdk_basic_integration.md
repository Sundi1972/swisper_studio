# Plan: Basic SDK Integration with Real Swisper

**Date:** November 3, 2025  
**Status:** Ready for Implementation  
**Approach:** Ship basic SDK, get state transitions working, enhance later  
**Duration:** 1-2 days  
**Phase:** 5 - Option 1 (Basic SDK Integration)

---

## 🎯 Goal

**Get real Swisper traces flowing to SwisperStudio with basic state capture.**

**What we'll get:**
- ✅ State before/after each node
- ✅ Observation tree structure (nesting)
- ✅ Execution duration
- ✅ Error tracking
- ✅ State diff viewer working

**What we won't get (yet):**
- ❌ LLM prompts (will enhance later)
- ❌ Token counts (will enhance later)
- ❌ Tool call details (will enhance later)
- ⚠️ All observations will be SPAN type (not GENERATION/TOOL)

**This is acceptable for MVP validation!**

---

## 📋 Implementation Steps

### **Step 1: Prepare SDK for Installation** (30 mins)

**Tasks:**
- [x] Verify SDK package structure
- [ ] Build SDK package
- [ ] Test SDK locally (create simple test)
- [ ] Create installation guide

**Files to check:**
- `sdk/pyproject.toml` - Package configuration
- `sdk/swisper_studio_sdk/__init__.py` - Exports
- `sdk/swisper_studio_sdk/tracing/` - Core functionality

**Acceptance:**
- SDK can be installed via pip/uv
- `from swisper_studio_sdk import create_traced_graph` works

---

### **Step 2: Create Swisper Integration Guide** (30 mins)

**Document:**
- Where to add initialization code
- Which graph to wrap first (global_supervisor recommended)
- How to test integration
- Troubleshooting common issues

**Files to create:**
- `docs/guides/swisper_integration_guide.md`

---

### **Step 3: Install SDK in Swisper** (1 hour)

**In Swisper backend:**

```bash
# Option A: Install from local path
cd /path/to/swisper
uv pip install /path/to/swisper_studio/sdk

# Option B: Install editable (for development)
uv pip install -e /path/to/swisper_studio/sdk
```

**Verify:**
```python
from swisper_studio_sdk import create_traced_graph, initialize_tracing
print("✅ SDK imported successfully")
```

---

### **Step 4: Initialize Tracing in Swisper** (30 mins)

**Location:** Swisper's `backend/app/main.py` or startup handler

```python
# Add to Swisper's startup
from swisper_studio_sdk import initialize_tracing

# In startup event or main()
initialize_tracing(
    api_url="http://localhost:8001",  # SwisperStudio backend
    api_key="dev-api-key-change-in-production",
    project_id="0d7aa606-cb29-4a31-8a59-50fa61151a32",
    enabled=True  # Can disable in production
)
```

**Acceptance:**
- No errors on Swisper startup
- SDK initialized successfully

---

### **Step 5: Wrap Global Supervisor Graph** (15 mins)

**Location:** Swisper's `backend/app/api/services/agents/global_supervisor/global_supervisor.py`

**Find this code:**
```python
# Current code (line ~50):
graph = StateGraph(GlobalSupervisorState)
```

**Replace with:**
```python
# New code (ONE LINE CHANGE):
from swisper_studio_sdk import create_traced_graph

graph = create_traced_graph(
    GlobalSupervisorState,
    trace_name="global_supervisor"
)
```

**Acceptance:**
- Swisper still runs
- No errors during graph creation

---

### **Step 6: Create Test Trace** (15 mins)

**Send a test request to Swisper:**
```bash
# Via Swisper's API or UI
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "What is my next meeting?",
    "chat_id": "test_chat_001",
    "user_id": "test_user"
  }'
```

**Or use Swisper's frontend**

---

### **Step 7: Verify in SwisperStudio** (15 mins)

**Check:**
1. Navigate to: `http://localhost:3000/projects/{PROJECT_ID}/tracing`
2. Look for new trace: "global_supervisor"
3. Click trace → See observations
4. Verify:
   - ✅ global_supervisor (root)
   - ✅ intent_classification (child)
   - ✅ memory_node (child)
   - ✅ global_planner (child)
   - ✅ productivity_agent (child)
   - ✅ ui_node (child)

**Success criteria:**
- ✅ Trace appears
- ✅ Observation tree shows nesting
- ✅ Can see observations

---

### **Step 8: Validate State Capture** (30 mins)

**Click on observations and verify:**
- ✅ State Before shows (user_message, chat_id, etc.)
- ✅ State After shows (with additions)
- ✅ State diff works (green highlighting)
- ✅ Duration metrics accurate

**Known limitations (expected):**
- ⚠️ No prompts in details panel (SDK doesn't capture yet)
- ⚠️ Model/tokens null (SDK doesn't capture yet)
- ⚠️ All observations type=SPAN (SDK doesn't detect type)

**This is OK for basic integration!**

---

### **Step 9: Test Different Scenarios** (1-2 hours)

**Test cases:**
1. Simple chat: "Hello"
2. Complex chat: "What's the weather?"
3. Calendar query: "What's my next meeting?"
4. Error case: Invalid input
5. Long execution: Multi-agent routing

**Verify:**
- ✅ All create traces
- ✅ State captured correctly
- ✅ Nesting works
- ✅ Errors tracked

---

### **Step 10: Document Findings** (30 mins)

**Create report:**
- What works
- What's missing
- Issues encountered
- Recommendations for SDK enhancements

---

## 🐛 **Expected Issues & Solutions**

### **Issue 1: State Serialization**

**Problem:** TypedDict doesn't serialize to JSON easily

**Solution:**
```python
# In SDK decorator.py (already implemented):
def serialize_state(state):
    # TypedDict is just a dict
    return dict(state)  # Works!
```

**Status:** ✅ Already handled in SDK

---

### **Issue 2: Observation Not Appearing**

**Possible causes:**
- Wrong API URL
- Wrong API key
- Network issue
- SwisperStudio backend down

**Debug:**
```python
# Add to Swisper (temporary):
import logging
logging.basicConfig(level=logging.DEBUG)

# Will show SDK HTTP requests
```

---

### **Issue 3: Performance Impact**

**Concern:** Does tracing slow down Swisper?

**Mitigation:**
- SDK uses async HTTP (non-blocking)
- Timeout: 5 seconds
- Graceful degradation (continues if SwisperStudio down)

**Measure:**
- Compare request latency with/without tracing
- Should be <50ms overhead

---

## 📊 **Success Metrics**

**MVP Success (Basic Integration):**
- ✅ At least 1 real Swisper trace in SwisperStudio
- ✅ All nodes visible in tree
- ✅ State transitions captured
- ✅ Can debug execution flow
- ✅ <100ms tracing overhead

**Phase 2.5 Success (State Viz):**
- ✅ State diff shows changes (green/red backgrounds) ✨
- ✅ Can trace data flow through nodes ✨
- ✅ Resizable panels work ✨
- ⚠️ Prompts not visible yet (expected - will enhance SDK)

---

## 🚀 **Timeline**

**Day 1 (Today):**
- [ ] Hour 1: Prepare SDK package
- [ ] Hour 2: Create integration guide
- [ ] Hour 3: Install SDK in Swisper
- [ ] Hour 4: Initialize tracing + wrap graph
- [ ] Hour 5: First test request
- [ ] Hour 6: Debug and iterate

**Day 2 (Tomorrow):**
- [ ] Hour 1-2: Test different scenarios
- [ ] Hour 3-4: Document findings
- [ ] Hour 5-6: Create SDK enhancement plan (for later)

**Deliverable:** Basic tracing working, documented, ready for enhancement

---

## 📝 **Next Immediate Steps**

**Ready to start? Here's what I'll do:**

1. ✅ Build SDK package
2. ✅ Create installation guide for Swisper
3. ✅ Create integration testing script
4. ✅ Prepare troubleshooting guide

**Then you (or we together):**
5. Install SDK in Swisper
6. Add initialization code
7. Wrap graph
8. Send test request
9. View in SwisperStudio
10. Celebrate first real trace! 🎉

---

**Shall I proceed with Steps 1-4 (prepare SDK for integration)?** 🚀

