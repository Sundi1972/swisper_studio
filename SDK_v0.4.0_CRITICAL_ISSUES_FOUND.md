# SDK v0.4.0 - Critical Issues Found During Testing

**Date:** 2025-11-06  
**Discovered By:** User testing  
**Severity:** HIGH - Affects observability experience  
**Status:** 🔴 Requires fixes before production

---

## 🐛 Issue #1: Separate Traces for Nested Agents

### **Problem:**

When `global_supervisor` delegates to `productivity_agent`, TWO separate traces are created:

```
Trace 1: global_supervisor (e75a6256...)
  ├─ user_in_the_loop_handler
  ├─ classify_intent
  ├─ memory_node
  ├─ global_planner
  ├─ agent_execution  ← Delegates to productivity_agent
  └─ user_interface

Trace 2: productivity_agent (330c9c19...) ← SEPARATE TRACE!
  ├─ provider_selection
  ├─ productivity_planner
  ├─ tool_execution
  └─ productivity_planner
```

**Expected behavior:**
```
Trace 1: global_supervisor (SINGLE E2E TRACE)
  ├─ user_in_the_loop_handler
  ├─ classify_intent
  ├─ memory_node
  ├─ global_planner
  ├─ agent_execution
  │   └─ productivity_agent ← NESTED as child!
  │       ├─ provider_selection
  │       ├─ productivity_planner
  │       ├─ tool_execution
  │       └─ productivity_planner
  └─ user_interface
```

---

### **Root Cause:**

**In `productivity_agent.py` line 143-147:**

```python
# ProductivityAgent creates its OWN traced graph
from swisper_studio_sdk import create_traced_graph
workflow = create_traced_graph(
    ProductivityAgentState,
    trace_name="productivity_agent"  ← Creates NEW trace!
)
```

**Problem:**
- `create_traced_graph()` ALWAYS creates a new trace on `ainvoke()`
- When productivity_agent is invoked from global_supervisor's agent_execution node
- It creates a separate trace (different trace ID)
- Lost the parent-child relationship!

---

### **Solution: Check for Existing Trace Context**

**SDK needs to be smarter:**

```python
# In graph_wrapper.py
async def traced_ainvoke(input_state, config=None, **invoke_kwargs):
    """Create trace before running graph (Redis Streams version)"""
    redis_client = get_redis_client()
    
    if not redis_client:
        return await original_ainvoke(input_state, config, **invoke_kwargs)
    
    # NEW: Check if we're already in a trace context
    existing_trace_id = get_current_trace()
    
    if existing_trace_id:
        # We're inside another traced graph (nested agent)
        # Don't create a new trace - use existing one
        logger.debug(f"Using existing trace context: {existing_trace_id}")
        
        # Just create parent observation (no new trace)
        parent_obs_id = str(uuid.uuid4())
        await publish_event(
            event_type="observation_start",
            trace_id=existing_trace_id,  ← Use existing trace!
            observation_id=parent_obs_id,
            data={
                "name": trace_name,
                "type": "AGENT",
                "parent_observation_id": get_current_observation(),  ← Link to parent!
                ...
            }
        )
        
        # Set as current observation
        parent_token = set_current_observation(parent_obs_id)
        
        try:
            result = await original_ainvoke(input_state, config, **invoke_kwargs)
            # End observation
            await publish_event("observation_end", ...)
            return result
        finally:
            set_current_observation(None, parent_token)
            # Don't clear trace context - still in parent trace!
    
    else:
        # No existing trace - create new one (top-level graph)
        trace_id = str(uuid.uuid4())
        await publish_event("trace_start", ...)
        # ... existing logic ...
```

**Result:**
- ✅ Top-level graph (global_supervisor) creates trace
- ✅ Nested graphs (productivity_agent) reuse trace
- ✅ All agents in ONE trace
- ✅ Full E2E visibility

---

### **Impact:**

**Current (broken):**
- ❌ Separate traces per agent
- ❌ Can't see full E2E flow
- ❌ Can't see delegation relationships
- ❌ Harder to debug multi-agent workflows

**After fix:**
- ✅ Single trace for entire request
- ✅ See full E2E flow
- ✅ See agent delegation clearly
- ✅ Easy debugging

---

## 🐛 Issue #2: Missing Tool Call Data in UI

### **Problem:**

User reports: "Last node has no entries, truncated, no tool calls showing"

**From database check:**
```
tool_execution observation:
  ✅ Has input: True
  ✅ Has output: True
  ✅ Has tool_results: True (batch_read_20251106_071453_747)
```

**Data IS in database**, but maybe:
1. Frontend not rendering tool data?
2. Data structure unexpected?
3. Output too large (truncated in UI)?

---

### **Investigation Needed:**

**Check 1: Data Size**
```python
# Is the output too large?
output_size = len(json.dumps(obs.output))
# If > 100KB, might cause rendering issues
```

**Check 2: Tool Viewer Component**
- Does `ToolResponseViewer` handle the data structure?
- Does it expect different keys?
- Is it looking for `tool_results` vs `tool_operations`?

**Check 3: Frontend Console**
- Any JavaScript errors when rendering tool_execution?
- React errors about data format?

---

### **Solution (Likely):**

**Option A: Frontend not rendering large outputs**
- Add "Show More" button for large outputs
- Truncate at 1000 lines
- Add download option

**Option B: Tool data structure mismatch**
- Check ToolResponseViewer expects certain keys
- Update to handle Swisper's tool_results format
- Add fallback rendering

**Option C: Observation not fully loaded**
- Check if observation_end event was processed
- Verify output is complete in database
- Check if frontend is fetching full data

---

## 🎯 Priority & Impact

### **Issue #1: Separate Traces**

**Severity:** HIGH  
**Impact:** Can't see E2E flow (major UX issue)  
**Effort:** 2-3 hours  
**Priority:** P0 - Must fix before production

**Affects:**
- Multi-agent workflows
- Debugging complex flows
- Understanding delegation
- User experience

---

### **Issue #2: Tool Data Not Showing**

**Severity:** MEDIUM  
**Impact:** Can't see tool execution details  
**Effort:** 1-2 hours  
**Priority:** P1 - Should fix soon

**Affects:**
- Tool call visibility
- Debugging tool issues
- Understanding what tools did

---

## 🔧 Recommended Action Plan

### **Immediate (Today):**

**1. Fix Issue #2 first** (easier, 1-2 hours)
   - Investigate frontend tool rendering
   - Check data structure
   - Fix display issues

**2. Then fix Issue #1** (2-3 hours)
   - Update SDK graph_wrapper to check existing trace
   - Test nested agent flows
   - Verify E2E trace working

### **Timeline:**

- Issue #2 fix: 1-2 hours
- Issue #1 fix: 2-3 hours
- Testing: 1 hour
- **Total:** 4-6 hours

---

## 📝 Next Steps

**Immediate investigation:**

1. Check frontend console for tool_execution rendering errors
2. Verify tool data structure in observation output
3. Check ToolResponseViewer component code
4. Test with simpler tool call

**For Issue #1:**

1. Modify SDK `graph_wrapper.py`
2. Add existing trace context check
3. Test with global_supervisor → productivity_agent
4. Verify single trace created
5. Verify observations nested correctly

---

## 💬 Questions for You

**1. Which issue should I fix first?**
   - A) Issue #2 (tool data not showing) - Easier, 1-2 hours
   - B) Issue #1 (separate traces) - Harder, 2-3 hours
   - C) Both in parallel

**2. For the tool data issue:**
   - Can you refresh the page and try clicking tool_execution again?
   - Can you check browser console for errors when viewing tool_execution?
   - What exactly do you see (blank? truncated? error message)?

**3. Priority:**
   - Should we fix these now or document for later?
   - Are these blocking for your testing?

---

**Let me know which issue to tackle first and I'll implement the fix!** 🔧

