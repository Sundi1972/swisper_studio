# Fix Plan: Nested Agent Traces & Tool Data Display

**Date:** 2025-11-06  
**Version:** SDK v0.4.1 (hotfix for v0.4.0)  
**Estimated Time:** 4-6 hours  
**Priority:** P0 - Critical for production use

---

## 🎯 Objectives

**Issue #1:** Fix nested agent traces (global_supervisor → productivity_agent should be ONE trace)  
**Issue #2:** Fix tool data display in frontend (tool_execution observation showing blank)

---

## 📋 Issue #1: Nested Agent Trace Context

### **Problem Statement**

**Current behavior:**
```
Trace 1: global_supervisor (ID: abc123)
  └─ agent_execution → calls productivity_agent

Trace 2: productivity_agent (ID: def456) ← SEPARATE!
  └─ productivity_planner
```

**Expected behavior:**
```
Trace 1: global_supervisor (ID: abc123) ← SINGLE E2E TRACE
  ├─ agent_execution
  │   └─ productivity_agent ← NESTED (same trace ID!)
  │       ├─ productivity_planner (parent: productivity_agent obs)
  │       └─ tool_execution
  └─ user_interface
```

---

### **Root Cause Analysis**

**File:** `sdk/swisper_studio_sdk/tracing/graph_wrapper.py`

**Problem code (line 89-115):**
```python
async def traced_ainvoke(input_state, config=None, **invoke_kwargs):
    redis_client = get_redis_client()
    if not redis_client:
        return await original_ainvoke(input_state, config, **invoke_kwargs)
    
    # PROBLEM: Always creates new trace
    trace_id = str(uuid.uuid4())  ← NEW trace every time!
    
    await publish_event(
        event_type="trace_start",
        trace_id=trace_id,  ← Separate trace for nested agent!
        ...
    )
```

**Why this is wrong:**
- `ProductivityAgent` calls `create_traced_graph()` which wraps `ainvoke()`
- When `global_supervisor` calls `productivity_agent.execute()`, it calls `ainvoke()`
- SDK creates NEW trace instead of checking for existing trace context
- Result: Separate traces, lost parent-child relationship

---

### **Solution Design**

**Approach:** Context-aware trace creation

```python
async def traced_ainvoke(input_state, config=None, **invoke_kwargs):
    """Create trace OR reuse existing if nested"""
    redis_client = get_redis_client()
    if not redis_client:
        return await original_ainvoke(input_state, config, **invoke_kwargs)
    
    # Check for existing trace context
    existing_trace_id = get_current_trace()
    existing_parent_obs = get_current_observation()
    
    if existing_trace_id:
        # NESTED AGENT: We're inside another traced graph
        # Don't create new trace - create observation under existing trace
        logger.debug(f"Nested agent detected, using trace: {existing_trace_id}")
        
        parent_obs_id = str(uuid.uuid4())
        
        # Create observation for this graph (AGENT type)
        await publish_event(
            event_type="observation_start",
            trace_id=existing_trace_id,  ← REUSE existing trace!
            observation_id=parent_obs_id,
            data={
                "name": trace_name,
                "type": "AGENT",
                "parent_observation_id": existing_parent_obs,  ← Link to caller!
                "input": copy.deepcopy(input_state),
                "start_time": datetime.utcnow().isoformat(),
            }
        )
        
        # Set as current observation (child observations will nest under this)
        parent_token = set_current_observation(parent_obs_id)
        
        try:
            result = await original_ainvoke(input_state, config, **invoke_kwargs)
            
            await publish_event(
                event_type="observation_end",
                trace_id=existing_trace_id,
                observation_id=parent_obs_id,
                data={
                    "output": copy.deepcopy(result),
                    "level": "DEFAULT",
                    "end_time": datetime.utcnow().isoformat(),
                }
            )
            
            return result
        finally:
            # Restore parent observation context (don't clear trace!)
            set_current_observation(existing_parent_obs, parent_token)
            # Don't clear trace - still in parent graph!
    
    else:
        # TOP-LEVEL AGENT: Create new trace
        # ... existing logic ...
```

---

### **Implementation Steps**

**Step 1:** Update `graph_wrapper.py` (30 mins)
- Add existing trace check
- Implement nested agent logic
- Preserve parent observation context
- Add logging for debugging

**Step 2:** Test with global_supervisor (15 mins)
- Send message that triggers productivity_agent
- Verify single trace created
- Verify observations nested correctly

**Step 3:** Verify database structure (15 mins)
- Check all observations have same trace_id
- Check parent_observation_id linkage
- Verify tree structure in database

**Step 4:** Verify UI rendering (15 mins)
- Check frontend shows nested structure
- Verify tree indentation correct
- Verify no duplicate traces

**Total Time:** ~75 minutes (1.25 hours)

---

### **Edge Cases to Handle**

**1. Triple Nesting:**
```
global_supervisor
  └─ agent_execution
      └─ productivity_agent
          └─ sub_agent (hypothetical)
```
**Solution:** Use stack-based context (already supported by context vars)

**2. Parallel Agents:**
```
global_supervisor
  ├─ productivity_agent (thread 1)
  └─ research_agent (thread 2)
```
**Solution:** Each thread has own context (context vars are thread-safe)

**3. Agent Re-Entry:**
```
global_supervisor
  ├─ productivity_agent (first call)
  └─ productivity_agent (second call, same trace)
```
**Solution:** Works automatically (creates new observation each time)

---

### **Testing Checklist**

- [ ] Single agent (global_supervisor only) → Creates trace
- [ ] Nested agent (global_supervisor → productivity_agent) → ONE trace
- [ ] Triple nesting (if applicable) → ONE trace
- [ ] Parallel agents (if applicable) → ONE trace
- [ ] Multiple calls to same agent → Separate observations, same trace

---

## 📋 Issue #2: Tool Data Display

### **Problem Statement**

User reports: "Last node has no entries, seems truncated, no tool calls showing"

**But database shows:**
```
tool_execution observation:
  ✅ Has input: True
  ✅ Has output: True
  ✅ Has tool_results data
```

**Hypothesis:** Frontend rendering issue, not data issue.

---

### **Investigation Plan**

**Step 1:** Check what frontend expects (15 mins)
- Read `ToolResponseViewer.tsx` code
- Check what keys it looks for
- Verify data structure expectations

**Step 2:** Check what Swisper provides (15 mins)
- Inspect actual `tool_execution` output structure
- Compare to what frontend expects
- Identify mismatch

**Step 3:** Determine fix approach (15 mins)
- Option A: Update frontend to handle Swisper's format
- Option B: Transform data in SDK before sending
- Option C: Update Swisper's tool node to match expected format

---

### **Likely Causes**

**Cause 1: Key name mismatch**
```typescript
// Frontend expects:
output.tool_calls = [...]

// Swisper provides:
output.tool_operations = [...]
output.tool_results = {...}
```

**Cause 2: Data structure mismatch**
```typescript
// Frontend expects:
tool_calls: [{name: "...", arguments: {...}}]

// Swisper provides:
tool_results: {"batch_id": {current_plan: "...", ...}}
```

**Cause 3: Output too large**
- Output might be 10MB+
- React crashes trying to render
- Need pagination/truncation

**Cause 4: Component error**
- ToolResponseViewer crashes on unexpected data
- No error boundary catches it
- Shows blank

---

### **Solution Design**

**Approach 1: Make ToolResponseViewer Robust (Recommended)**

```typescript
// In ToolResponseViewer.tsx
export function ToolResponseViewer({ output }: ToolResponseViewerProps) {
  if (!output) {
    return <Box>No tool data</Box>;
  }
  
  // Try multiple keys (handle different formats)
  const toolData = (
    output.tool_results ||     // Swisper format
    output.tool_calls ||       // LangChain format
    output.tool_operations ||  // Alternative format
    null
  );
  
  if (!toolData) {
    return <Box>No tool execution data</Box>;
  }
  
  // Handle different data types
  if (Array.isArray(toolData)) {
    return <ArrayToolDisplay data={toolData} />;
  }
  
  if (typeof toolData === 'object') {
    return <ObjectToolDisplay data={toolData} />;
  }
  
  return <StringToolDisplay data={String(toolData)} />;
}
```

**Approach 2: Add Error Boundary (Safety)**

```typescript
class ToolViewerErrorBoundary extends React.Component {
  state = { hasError: false, error: null };
  
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  
  render() {
    if (this.state.hasError) {
      return (
        <Alert severity="error">
          Failed to render tool data: {this.state.error.message}
          <Button onClick={() => this.setState({ hasError: false })}>
            Retry
          </Button>
        </Alert>
      );
    }
    return this.props.children;
  }
}
```

---

### **Implementation Steps**

**Step 1:** Inspect actual tool_execution output (15 mins)
- Query database for full output
- Save to file for analysis
- Identify structure

**Step 2:** Read ToolResponseViewer code (15 mins)
- Understand current implementation
- Identify what it expects
- Find mismatch

**Step 3:** Update ToolResponseViewer (30 mins)
- Add multi-format support
- Add error handling
- Add truncation for large outputs
- Add "Show More" button

**Step 4:** Test rendering (15 mins)
- Reload frontend
- Click on tool_execution
- Verify data displays
- Check no crashes

**Total Time:** ~75 minutes (1.25 hours)

---

### **Testing Checklist**

- [ ] tool_execution observation loads without crash
- [ ] Tool results display correctly
- [ ] Large outputs don't freeze UI
- [ ] Error messages helpful if data malformed
- [ ] Copy button works
- [ ] Formatting readable

---

## 📊 Implementation Timeline

### **Phase 1: Issue #1 (Nested Traces)** - 1.5 hours

**Tasks:**
1. Update `graph_wrapper.py` - Check existing trace context
2. Add nested agent logic
3. Test with global_supervisor → productivity_agent
4. Verify single trace in database
5. Verify UI shows nested structure

---

### **Phase 2: Issue #2 (Tool Display)** - 1.5 hours

**Tasks:**
1. Inspect tool_execution output structure
2. Read ToolResponseViewer code
3. Update to handle Swisper's format
4. Add error boundary
5. Test rendering

---

### **Phase 3: Integration Testing** - 1 hour

**Tasks:**
1. Clean database (fresh start)
2. Send test message (triggers both issues)
3. Verify single E2E trace
4. Verify tool data displays
5. Check for regressions

---

### **Phase 4: Documentation** - 1 hour

**Tasks:**
1. Update SDK_v0.4.0 docs with fixes
2. Create SDK v0.4.1 release notes
3. Update migration guide
4. Document nested agent behavior

---

**Total Estimated Time:** 4-6 hours

---

## 🔧 Implementation Order

**Recommended sequence:**

1. ✅ **Issue #2 first** (Tool Display)
   - Easier to fix
   - Quick win
   - Independent of Issue #1
   - Can verify immediately

2. ✅ **Issue #1 second** (Nested Traces)
   - More complex
   - Requires careful testing
   - Depends on clean data

**Rationale:**
- Fix easy issue first for momentum
- Tool display is independent
- Nested traces needs thorough testing
- Can test both together after both fixed

---

## 📝 Success Criteria

### **Issue #1: Nested Traces**

**Must have:**
- [ ] global_supervisor → productivity_agent creates ONE trace
- [ ] productivity_agent observation nested under agent_execution
- [ ] All child observations have correct parent_observation_id
- [ ] UI shows tree structure correctly
- [ ] No separate traces

**Nice to have:**
- [ ] Works for triple nesting
- [ ] Works for parallel agents
- [ ] Clear logging for debugging

---

### **Issue #2: Tool Display**

**Must have:**
- [ ] tool_execution observation displays without crash
- [ ] Tool results visible
- [ ] Data formatted readably
- [ ] No blank screens

**Nice to have:**
- [ ] Pretty formatting
- [ ] Syntax highlighting
- [ ] Copy button
- [ ] Expandable sections for large outputs

---

## 🚨 Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Breaks existing single-agent traces | Medium | High | Test single agent first |
| Context not preserved across agents | Medium | High | Use context vars correctly |
| Performance regression | Low | Medium | Benchmark before/after |
| Tool viewer crashes on edge cases | Medium | Medium | Add error boundaries |
| Large tool outputs freeze UI | Medium | Medium | Add pagination/truncation |

---

## 🔍 Detailed Implementation Plan

### **Task 1: Fix Nested Agent Traces**

**File:** `sdk/swisper_studio_sdk/tracing/graph_wrapper.py`

**Changes:**

```python
# BEFORE (line 89-165):
async def traced_ainvoke(input_state, config=None, **invoke_kwargs):
    # Always creates new trace
    trace_id = str(uuid.uuid4())
    await publish_event("trace_start", trace_id, ...)

# AFTER:
async def traced_ainvoke(input_state, config=None, **invoke_kwargs):
    # Check if already in trace context
    existing_trace_id = get_current_trace()
    existing_parent_obs = get_current_observation()
    
    if existing_trace_id:
        # Nested agent - create observation only
        return await _traced_ainvoke_nested(...)
    else:
        # Top-level agent - create new trace
        return await _traced_ainvoke_toplevel(...)

async def _traced_ainvoke_nested(input_state, trace_name, ...):
    """Handle nested agent invocation (reuse trace)"""
    parent_obs_id = str(uuid.uuid4())
    
    await publish_event(
        event_type="observation_start",
        trace_id=existing_trace_id,  ← Reuse!
        observation_id=parent_obs_id,
        data={
            "name": trace_name,
            "type": "AGENT",
            "parent_observation_id": existing_parent_obs,  ← Link!
            ...
        }
    )
    
    parent_token = set_current_observation(parent_obs_id)
    
    try:
        result = await original_ainvoke(...)
        await publish_event("observation_end", ...)
        return result
    finally:
        set_current_observation(existing_parent_obs, parent_token)
        # Don't clear trace - still in parent graph!

async def _traced_ainvoke_toplevel(input_state, trace_name, ...):
    """Handle top-level graph invocation (create trace)"""
    # Existing logic (create trace + parent observation)
    ...
```

---

### **Task 2: Fix Tool Data Display**

**Step 2.1: Investigate current tool_execution output** (15 mins)

Query database for full output:
```python
# Get full tool_execution output
obs = session.query(Observation).filter(name='tool_execution').first()
print(json.dumps(obs.output, indent=2))

# Check size
output_size = len(json.dumps(obs.output))
print(f"Output size: {output_size} bytes")
```

**Step 2.2: Read ToolResponseViewer code** (15 mins)

```bash
cat frontend/src/features/traces/components/tool-response-viewer.tsx
```

Check:
- What keys does it look for?
- What data structure does it expect?
- Any error handling?

**Step 2.3: Update ToolResponseViewer** (30 mins)

Add robust handling:
```typescript
function extractToolData(output: any): any {
  if (!output) return null;
  
  // Try multiple keys (different formats)
  return (
    output.tool_results ||      // Swisper format
    output.tool_calls ||        // LangChain format
    output.tool_operations ||   // Alternative
    output.tools ||             // Generic
    null
  );
}

export function ToolResponseViewer({ output }: Props) {
  const toolData = extractToolData(output);
  
  if (!toolData) {
    return <NoToolDataMessage />;
  }
  
  // Truncate if too large
  const dataString = JSON.stringify(toolData, null, 2);
  if (dataString.length > 50000) {  // 50KB limit
    return <TruncatedToolDisplay data={dataString} />;
  }
  
  // Render based on type
  if (Array.isArray(toolData)) {
    return <ArrayToolDisplay data={toolData} />;
  }
  
  if (typeof toolData === 'object') {
    return <ObjectToolDisplay data={toolData} />;
  }
  
  return <RawToolDisplay data={dataString} />;
}
```

---

## 🧪 Testing Strategy

### **Test Suite 1: Nested Traces**

**Test 1.1: Single Agent (Regression Test)**
```bash
# Send message that doesn't trigger agents
curl -X POST /chat -d '{"message": "Hello"}'

# Expected:
# - ONE trace: global_supervisor
# - No productivity_agent trace
# - All observations under global_supervisor trace
```

**Test 1.2: Nested Agent**
```bash
# Send message that triggers productivity_agent
curl -X POST /chat -d '{"message": "Check my emails"}'

# Expected:
# - ONE trace: global_supervisor
# - productivity_agent as nested observation
# - All productivity nodes nested under productivity_agent obs
```

**Test 1.3: Database Verification**
```sql
-- All observations should have same trace_id
SELECT trace_id, COUNT(*) 
FROM observations 
GROUP BY trace_id;

-- Should show ONE trace with ALL observations
```

**Test 1.4: UI Verification**
```
Open SwisperStudio UI → Tracing page

Should see:
global_supervisor (AGENT)
  ├─ user_in_the_loop_handler
  ├─ classify_intent
  ├─ memory_node
  ├─ global_planner
  ├─ agent_execution
  │   └─ productivity_agent (AGENT) ← NESTED!
  │       ├─ provider_selection
  │       ├─ productivity_planner
  │       ├─ tool_execution
  │       └─ productivity_planner
  └─ user_interface
```

---

### **Test Suite 2: Tool Display**

**Test 2.1: View tool_execution**
```
1. Open trace with tool_execution
2. Click on tool_execution observation
3. Verify data displays (not blank)
4. Check browser console (no errors)
```

**Test 2.2: Large Tool Output**
```
1. Send request that produces large tool output
2. Verify UI doesn't freeze
3. Check truncation works
4. Verify "Show More" button
```

**Test 2.3: Different Tool Formats**
```
1. Test with productivity_agent tools
2. Test with research_agent tools (if available)
3. Verify all formats display
```

---

## 📦 Deliverables

**SDK Changes:**
- `sdk/swisper_studio_sdk/tracing/graph_wrapper.py` (updated)
- Version bump to 0.4.1

**Frontend Changes:**
- `frontend/src/features/traces/components/tool-response-viewer.tsx` (updated)
- Possibly add error boundary

**Documentation:**
- SDK v0.4.1 release notes
- Update testing guide
- Add nested agent examples

**Tests:**
- Nested agent test suite
- Tool display test suite

---

## 🎯 Acceptance Criteria

**Must Pass:**
- [ ] Single E2E trace for nested agents
- [ ] Tool data displays correctly
- [ ] No blank screens
- [ ] No JavaScript errors
- [ ] Performance unchanged
- [ ] No regressions

**Should Pass:**
- [ ] UI shows clear nesting
- [ ] Tool data formatted nicely
- [ ] Large outputs handled gracefully
- [ ] Copy buttons work

---

## 🚀 Implementation Sequence

**Hour 1-1.5:** Issue #2 (Tool Display)
1. Investigate output structure (15 mins)
2. Read ToolResponseViewer code (15 mins)
3. Implement fix (30 mins)
4. Test (15 mins)

**Hour 1.5-3:** Issue #1 (Nested Traces)
1. Update graph_wrapper.py (30 mins)
2. Add context checking logic (30 mins)
3. Test single agent (15 mins)
4. Test nested agent (15 mins)
5. Verify database (15 mins)

**Hour 3-4:** Integration Testing
1. Clean database
2. Send various test messages
3. Verify all scenarios
4. Check UI rendering
5. Performance check

**Hour 4-5:** Documentation & Polish
1. Update docs
2. Create release notes
3. Update migration guide
4. Clean up debug logs

**Hour 5-6:** Final Validation
1. Full regression test
2. Load test
3. UX review
4. Sign-off

---

## 📝 Open Questions

1. **Should we preserve trace context across async boundaries?**
   - Currently: Yes (using contextvars)
   - Works for async/await chains
   - Should work for nested agents

2. **Should tool_execution be typed as TOOL instead of SPAN?**
   - Would make it clearer in UI
   - Could auto-detect based on tool_results presence
   - Add to type detection logic

3. **Should we add observation metadata for nested depth?**
   - E.g., `depth: 2` for productivity_agent
   - Could help with UI indentation
   - Optional enhancement

---

**Author:** AI Assistant  
**Status:** READY FOR IMPLEMENTATION  
**Approval:** Awaiting user confirmation to proceed

**Ready to implement? Say the word!** 🚀

