# Phase 5.1: SDK Fixes - Post-Integration Issues

**Date:** November 5, 2025  
**Status:** Ready for Implementation  
**Trigger:** Swisper team integration testing feedback  
**Priority:** 🔥 CRITICAL - Blocking production use  
**Estimated Duration:** 1 day (6-8 hours)

---

## Executive Summary

Swisper team successfully integrated SDK and found critical issues preventing production use:
1. Missing parent observation (flat structure)
2. No LLM prompts captured (expected - Phase 5.2)
3. State not changing (shallow copy bug)
4. Frontend crashes on some nodes (error handling)
5. Performance issues (blocking HTTP)
6. Overall data quality issues

**Goal:** Fix all critical issues to make SDK production-ready.

---

## Issue Breakdown & Fixes

### **Issue 1: Missing Global Supervisor Parent** 🔥 CRITICAL

**Priority:** P0 - Fix First  
**Effort:** 30 minutes  
**Impact:** UX - Proper hierarchy in tree view

**Problem:**
```
Expected:
global_supervisor (AGENT)
├─ classify_intent
├─ memory_node
└─ user_interface

Actual:
classify_intent (flat)
memory_node (flat)
user_interface (flat)
```

**Root Cause:**
`graph_wrapper.py` creates trace but no parent observation for the graph itself.

**Fix:**
```python
# In sdk/swisper_studio_sdk/tracing/graph_wrapper.py
# After creating trace (line ~90), ADD:

# Create parent observation for the graph
parent_obs_id = await client.create_observation(
    trace_id=trace_id,
    name=trace_name,  # "global_supervisor"
    type="AGENT",
    input=input_state,
)

# Set as current observation so child nodes nest under it
token = set_current_observation(parent_obs_id)

try:
    # Execute original graph
    result = await original_ainvoke(input_state, config=config)
    
    # End parent observation
    await client.end_observation(
        observation_id=parent_obs_id,
        output=result,
        level="DEFAULT"
    )
    
    return result
finally:
    # Clear context
    set_current_observation(None, token)
```

**Files to Modify:**
- `sdk/swisper_studio_sdk/tracing/graph_wrapper.py` (main fix)
- `sdk/tests/test_graph_wrapper.py` (new tests)

**Tests:**
- [ ] Graph creates parent observation
- [ ] Child observations nest under parent
- [ ] Parent observation has start/end times
- [ ] Parent observation type = AGENT

---

### **Issue 2: No Prompts/LLM Output** ⏸️ DEFERRED

**Priority:** P3 - Defer to Phase 5.2  
**Effort:** 2-3 hours  
**Impact:** Debugging - Can't see LLM interactions

**Status:** **Expected behavior - Phase 5.2 was deferred**

**Why deferred:**
- Requires access to Swisper's llm_adapter code
- Need to test monkey patching against real Swisper
- Infrastructure ready, implementation needs Swisper collaboration

**To implement (future):**
1. Review Swisper's `llm_adapter.get_structured_output()` signature
2. Implement wrapper in `sdk/swisper_studio_sdk/wrappers/llm_wrapper.py`
3. Call wrapper in `initialize_tracing()`
4. Test with real Swisper LLM calls

**Decision:** **Skip for now, revisit after core SDK stable**

---

### **Issue 3: State Not Changing (Shallow Copy)** 🔥 CRITICAL

**Priority:** P0 - Fix First  
**Effort:** 15 minutes  
**Impact:** Observability - State diffs don't work!

**Problem:**
```python
input_state = {intent: None}
# SDK captures: input_data = dict(input_state)  # Shallow copy!
# Node executes: input_state['intent'] = 'complex_chat'
# SDK captures output: output_data = dict(input_state)

# Result: input_data and output_data point to SAME object!
# Both show: {intent: 'complex_chat'}
```

**Root Cause:**
`dict(state)` creates shallow copy - nested objects still reference same memory.

**Fix:**
```python
# In sdk/swisper_studio_sdk/tracing/decorator.py
import copy  # Add to imports

# Line 64-76, change ALL to deep copy:
if isinstance(state, dict):
    input_data = copy.deepcopy(state)  # DEEP copy!
elif hasattr(state, 'model_dump'):
    input_data = state.model_dump()  # Pydantic already creates new dict
elif hasattr(state, 'dict'):
    input_data = state.dict()
else:
    input_data = copy.deepcopy(vars(state)) if hasattr(state, '__dict__') else None

# Same for output (line 112-122)
if isinstance(result, dict):
    output_data = copy.deepcopy(result)  # DEEP copy!
# ... etc
```

**Files to Modify:**
- `sdk/swisper_studio_sdk/tracing/decorator.py` (change dict() to copy.deepcopy())
- `sdk/swisper_studio_sdk/tracing/graph_wrapper.py` (same fix)

**Tests:**
- [ ] Mutating state after capture doesn't affect input_data
- [ ] State diffs show actual changes
- [ ] Nested dict changes captured correctly

---

### **Issue 4: Frontend Crashes on Some Nodes** 🔧 MEDIUM

**Priority:** P1 - Fix After Critical  
**Effort:** 1 hour  
**Impact:** UX - Can't view all observations

**Problem:**
Clicking `memory_node` or `user_interface` → nothing/crash

**Likely Causes:**
1. Circular references in state
2. Non-serializable data (functions, classes)
3. Undefined/null in nested structure
4. Very large state objects

**Fix Part 1 - SDK (sanitize data):**
```python
# In sdk/swisper_studio_sdk/tracing/decorator.py
def _sanitize_for_json(obj, max_depth=10, current_depth=0):
    """Remove non-serializable data before sending to SwisperStudio"""
    if current_depth > max_depth:
        return "<max depth reached>"
    
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    
    if callable(obj):
        return f"<function: {obj.__name__}>"
    
    if isinstance(obj, (bytes, bytearray)):
        return f"<bytes: {len(obj)} bytes>" if len(obj) > 100 else obj.decode('utf-8', errors='ignore')
    
    if isinstance(obj, dict):
        return {
            k: _sanitize_for_json(v, max_depth, current_depth + 1)
            for k, v in list(obj.items())[:100]  # Limit dict size
        }
    
    if isinstance(obj, (list, tuple)):
        return [
            _sanitize_for_json(item, max_depth, current_depth + 1)
            for item in list(obj)[:50]  # Limit list size
        ]
    
    # Try to serialize object
    try:
        return str(obj)
    except:
        return f"<{type(obj).__name__}>"

# Apply before sending:
input_data = _sanitize_for_json(copy.deepcopy(state))
```

**Fix Part 2 - Frontend (error boundaries):**
```typescript
// In frontend/src/features/traces/components/state-viewer.tsx
try {
  <JsonView value={state} />
} catch (error) {
  <Alert severity="warning">
    Unable to display state. Data may contain circular references.
  </Alert>
}
```

**Files to Modify:**
- `sdk/swisper_studio_sdk/tracing/decorator.py` (add sanitization)
- `frontend/src/features/traces/components/state-viewer.tsx` (error handling)
- `frontend/src/features/traces/components/observation-details-panel.tsx` (error boundary)

**Tests:**
- [ ] Large state objects handled gracefully
- [ ] Circular references don't crash
- [ ] Functions/classes sanitized
- [ ] Frontend shows error message instead of crashing

---

### **Issue 5: Performance (Blocking HTTP)** ⚠️ HIGH (for prod)

**Priority:** P1 - Fix Before Production  
**Effort:** 2-3 hours  
**Impact:** Performance - 400-600ms latency added

**Problem:**
```python
# Current (BLOCKING):
obs_id = await client.create_observation(...)  # Waits for response
result = await func(*args)  # User waits for HTTP
await client.end_observation(...)  # Waits again
return result  # Finally!
```

**Fix - Fire and Forget:**
```python
# Generate ID locally
obs_id = str(uuid.uuid4())

# Fire in background (don't wait)
asyncio.create_task(client.create_observation_async(obs_id, ...))

# Execute immediately
result = await func(*args)  # No waiting!

# Update in background
asyncio.create_task(client.end_observation_async(obs_id, ...))

return result  # Instant!
```

**Files to Modify:**
- `sdk/swisper_studio_sdk/tracing/decorator.py` (fire-and-forget)
- `sdk/swisper_studio_sdk/tracing/graph_wrapper.py` (fire-and-forget)
- `sdk/swisper_studio_sdk/tracing/client.py` (add async methods)

**Tests:**
- [ ] Zero latency added (< 10ms overhead)
- [ ] Observations still created (eventually)
- [ ] No data loss under load
- [ ] Silent failures don't crash app

---

### **Issue 6: Overall Data Quality** 🔧 MEDIUM

**Priority:** P2 - Polish  
**Effort:** 1 hour  
**Impact:** Debugging - Better data visibility

**Improvements:**
- Add observation metadata (duration, timestamps)
- Better error messages
- Validate data before sending
- Add retry logic for failed HTTP

---

## Implementation Plan

### Sprint 1: Critical Fixes (Morning - 3 hours)

**Issue #3: State Deep Copy** (15 mins)
- Change `dict()` to `copy.deepcopy()`
- Test state mutations
- Verify diffs work

**Issue #1: Parent Observation** (30 mins)
- Add parent observation creation
- Set context for nesting
- Test hierarchy

**Issue #4: Data Sanitization** (1 hour)
- Add `_sanitize_for_json()` function
- Remove circular refs, functions
- Test with complex state

**Testing & Validation** (1 hour)
- Test with Swisper
- Verify all fixes working
- Document results

---

### Sprint 2: Performance Fix (Afternoon - 3 hours)

**Issue #5: Fire-and-Forget** (2-3 hours)
- Implement async background tasks
- Generate IDs locally
- Test performance
- Verify no data loss

---

### Sprint 3: Polish (Optional)

**Issue #2: LLM Prompts** (Future - Phase 5.2)
**Issue #6: Data Quality** (1 hour - if time permits)

---

## Success Criteria

**After Sprint 1 (Critical Fixes):**
- ✅ global_supervisor appears as parent in tree
- ✅ Child observations properly nested
- ✅ State diffs show actual changes (green/red)
- ✅ All nodes clickable without crashes
- ✅ Can see what changed at each step

**After Sprint 2 (Performance):**
- ✅ Zero user-facing latency (< 10ms)
- ✅ Swisper runs at full speed
- ✅ Observations created in background
- ✅ Production-ready performance

---

## File Changes Summary

**SDK Files:**
- `sdk/swisper_studio_sdk/tracing/decorator.py` - Deep copy + sanitization + fire-and-forget
- `sdk/swisper_studio_sdk/tracing/graph_wrapper.py` - Parent observation + fire-and-forget
- `sdk/swisper_studio_sdk/tracing/client.py` - Async methods
- `sdk/tests/test_decorator.py` - New tests
- `sdk/tests/test_graph_wrapper.py` - New tests

**Frontend Files (if needed):**
- `frontend/src/features/traces/components/state-viewer.tsx` - Error handling
- `frontend/src/features/traces/components/observation-details-panel.tsx` - Error boundary

---

## Testing Strategy

**Unit Tests:**
- Deep copy mutations
- Parent-child nesting
- Data sanitization
- Async task completion

**Integration Tests:**
- End-to-end with Swisper
- Performance benchmarks
- Error scenarios
- Data quality validation

---

## Timeline

**Today:**
- Sprint 1 (morning): Critical fixes - 3 hours
- Sprint 2 (afternoon): Performance - 3 hours
- **Total: 6 hours**

**Ready for production after:** End of day

---

**Status:** Ready to begin implementation following strict TDD workflow.

**Approve to proceed?** 🚦

