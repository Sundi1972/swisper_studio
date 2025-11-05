# Swisper Integration - Issues Analysis & Fixes

**Date:** November 5, 2025  
**Test Status:** ✅ Trace appearing, but with issues  
**Severity:** Medium (functional but not perfect)

---

## ✅ What's Working:

1. ✅ **Trace creation successful** - FK constraint fix worked!
2. ✅ **4 observations created** (user_in_the_loop_handler, classify_intent, memory_node, user_interface)
3. ✅ **Network connectivity** - SDK → SwisperStudio communication working
4. ✅ **State capture** - Input and output data being sent
5. ✅ **UI loading** - Trace list and tree view rendering

**This is great progress!** Basic integration is functional.

---

## 🐛 Issues Found (with priorities):

### **Issue 1: Missing Global Supervisor Parent** 🔥 High Priority

**Problem:**
- Expected: `global_supervisor` (AGENT) as parent → with child observations
- Actual: 4 flat observations, no parent

**Root Cause:**
The SDK's `create_traced_graph()` creates observations for each node but NOT for the graph itself.

**In SDK `graph_wrapper.py`:**
```python
# It wraps nodes but doesn't create parent observation
# So you get flat structure instead of:
# global_supervisor (AGENT)
# ├─ classify_intent
# ├─ memory_node
# └─ user_interface
```

**Fix:**
```python
# In graph_wrapper.py, after creating trace, ADD:
parent_obs_id = await client.create_observation(
    trace_id=trace_id,
    name=trace_name,  # "global_supervisor"
    type="AGENT",
    input=input_state,
)
set_current_observation(parent_obs_id)

# Then all node observations will nest under this parent
```

**Effort:** 30 minutes  
**Priority:** High - Better UX, shows execution hierarchy

---

### **Issue 2: No Prompts/LLM Output** ⏸️ Deferred (Phase 5.2)

**Problem:**
- No LLM prompts visible
- No LLM responses visible
- Can't see what was sent to GPT-4

**Root Cause:**
This is **Phase 5.2** (SDK Enhancements) which we deferred because:
- Needs access to Swisper's `llm_adapter` code to intercept LLM calls
- Requires monkey-patching or decorator changes in Swisper
- We created the infrastructure but deferred implementation

**Current Status:**
- ✅ Type detection infrastructure ready
- ✅ Wrapper skeletons created (`llm_wrapper.py`, `tool_wrapper.py`)
- ⏸️ Actual LLM interception deferred

**To Implement (when needed):**
See: `sdk/swisper_studio_sdk/wrappers/llm_wrapper.py` - Has TODO with implementation guide

**Effort:** 2-3 hours  
**Priority:** Medium - Nice to have, not blocking  
**When:** After Phase 5.1 fully validated

---

### **Issue 3: State Not Changing** 🔥 High Priority

**Problem:**
All observations show IDENTICAL state:
```
Input: {user_message, filename, file_content, model, chat_id, ...}
Output: {user_message, filename, file_content, model, chat_id, ...} ← SAME!
```

**Root Cause:**
SDK is likely capturing state **by reference** instead of creating a copy.

**In `decorator.py` line 64-76:**
```python
if isinstance(state, dict):
    input_data = dict(state)  # ← This creates SHALLOW copy!
```

**Problem with shallow copy:**
- LangGraph mutates the same dict object
- By the time SDK serializes output, input has also changed
- Both point to same object in memory

**Fix:**
```python
import copy

if isinstance(state, dict):
    input_data = copy.deepcopy(state)  # ← DEEP copy!
```

**Effort:** 15 minutes  
**Priority:** 🔥 **CRITICAL** - Without this, state diffs don't work!

---

### **Issue 4 & 5: Memory/UI Nodes Crash Frontend** 🔧 Medium Priority

**Problem:**
- Clicking `memory_node` → crash/nothing
- Clicking `user_interface` → crash/nothing

**Likely Causes:**
1. **Null/undefined in nested data** - Frontend can't handle
2. **Circular references** - State object has circular refs
3. **Non-serializable data** - Functions, class instances in state
4. **Large data** - State too big for JSON viewer

**Diagnostic:**
Let me check what's in those observations' input/output

**Fix (Backend - Add validation):**
```python
# In decorator.py, before sending:
def sanitize_state(state):
    """Remove non-serializable and problematic data"""
    if not isinstance(state, dict):
        return state
    
    cleaned = {}
    for key, value in state.items():
        # Skip callables
        if callable(value):
            continue
        # Skip large objects
        if isinstance(value, (bytes, bytearray)) and len(value) > 10000:
            cleaned[key] = f"<bytes: {len(value)} bytes>"
            continue
        # Recursively clean nested dicts
        if isinstance(value, dict):
            cleaned[key] = sanitize_state(value)
        else:
            cleaned[key] = value
    
    return cleaned
```

**Fix (Frontend - Better error handling):**
```typescript
// In observation-details-panel.tsx
try {
  renderStateView(observation.input)
} catch (error) {
  return <Alert severity="error">Unable to display state data</Alert>
}
```

**Effort:** 1 hour  
**Priority:** Medium - Affects specific nodes

---

### **Issue 6: Performance (Blocking HTTP)** ⚠️ Medium (for prod)

**From:** `PERFORMANCE_ISSUE_BLOCKING_SDK.md`

**Problem:**
- SDK uses `await` for HTTP calls (blocking)
- Adds 400-600ms latency per request
- User perceives slower responses

**Fix:**
- Change to fire-and-forget pattern (asyncio.create_task)
- Generate observation IDs locally
- Send HTTP in background

**Effort:** 2-3 hours  
**Priority:**
- Low for dev/testing (acceptable)
- High for production (must fix)

---

## 🎯 Recommended Fix Priority:

### **CRITICAL (Fix Now - 1 hour):**

**1. Deep Copy State** (15 mins)
```python
# sdk/swisper_studio_sdk/tracing/decorator.py
import copy

# Line 64-76, change to:
if isinstance(state, dict):
    input_data = copy.deepcopy(state)  # Deep copy!
```

**2. Add Parent Observation** (30 mins)
```python
# sdk/swisper_studio_sdk/tracing/graph_wrapper.py
# After creating trace, create parent observation for graph
parent_obs = await client.create_observation(
    trace_id=trace_id,
    name=trace_name,
    type="AGENT",
)
set_current_observation(parent_obs)
```

**3. Test** (15 mins)
- Send request
- Verify state diffs show changes
- Verify parent-child nesting

---

### **HIGH (Fix This Week - 3 hours):**

**4. Fire-and-Forget HTTP** (2-3 hours)
- Remove blocking await
- Use asyncio.create_task
- Zero latency impact

---

### **MEDIUM (Can defer):**

**5. LLM Prompt Capture** (Phase 5.2)
- Intercept llm_adapter calls
- Extract prompts and responses
- Show in UI

**6. Frontend Error Handling** (1 hour)
- Better null/undefined handling
- Graceful degradation for bad data

---

## 📋 Action Plan:

**Immediate (30-60 mins):**
1. Fix deep copy issue in SDK
2. Add parent observation
3. Re-test with Swisper
4. Verify state diffs working

**This Week:**
5. Implement fire-and-forget pattern
6. Performance test
7. Deploy updated SDK

**Future:**
8. LLM prompt capture (Phase 5.2)
9. Enhanced error handling

---

## 🔧 Quick Fixes I Can Apply Now:

Want me to:
1. ✅ Fix the deep copy issue (15 mins)
2. ✅ Add parent observation (30 mins)
3. ✅ Test and verify

This will address issues #1 and #3 immediately!

**Should I proceed with these fixes?** 🚦

