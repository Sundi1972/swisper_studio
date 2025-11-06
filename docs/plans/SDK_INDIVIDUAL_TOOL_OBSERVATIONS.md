# Implementation Plan: Individual Tool Observations

**Date:** 2025-11-06  
**Version:** SDK v0.5.0  
**Estimated Time:** 2 hours  
**Approach:** Option B - SDK creates real observations for each tool

---

## 🎯 Objective

Create individual TOOL observations for each tool call, not just aggregate in tool_execution.

### **Current State:**

```
tool_execution (SPAN)
  output.tool_results: {
    "batch_xyz": {
      "results": {
        "office365_search_emails": {...},
        "analyze_emails": {...}
      }
    }
  }
```

### **Desired State:**

```
tool_execution (SPAN)
  ├─ 🔧 office365_search_emails (TOOL) ✅ Success
  │   └─ Click to see: parameters, response, status
  ├─ 🔧 analyze_emails (TOOL) ✅ Success
  │   └─ Click to see: parameters, response, status
  └─ 🔧 send_email (TOOL) ❌ Failed
      └─ Click to see: parameters, error message
```

---

## 🏗️ Architecture Design

### **SDK Responsibilities:**

**1. Wrap Swisper's Tool Execution:**
- Intercept tool calls in productivity_agent and research_agent
- Create one observation per tool call
- Set type="TOOL"
- Set parent_observation_id = tool_execution obs
- Capture: tool name, parameters, result, status

**2. Data Structure:**

```python
# For each tool call:
await publish_event(
    event_type="observation_start",
    trace_id=trace_id,
    observation_id=tool_obs_id,
    data={
        "name": "office365_search_emails",  # Tool name
        "type": "TOOL",
        "parent_observation_id": tool_execution_obs_id,
        "input": {
            "tool_name": "office365_search_emails",
            "parameters": {
                "folder": "inbox",
                "filter": "receivedDateTime ge 2025-11-06...",
                "max_results": 50
            }
        },
        "start_time": "2025-11-06T..."
    }
)

# After tool completes:
await publish_event(
    event_type="observation_end",
    trace_id=trace_id,
    observation_id=tool_obs_id,
    data={
        "output": {
            "status": "success",  # or "failure"
            "result": {...},  # Tool response payload
            "error": None  # or error message
        },
        "level": "DEFAULT",  # or "ERROR" if failed
        "end_time": "2025-11-06T..."
    }
)
```

---

## 🔍 Where to Implement

### **Challenge:**

Swisper's tools are executed INSIDE agent nodes (productivity_agent, research_agent).
We need to intercept at the right level.

### **Options:**

**Option 1: Wrap in tool_execution node** (Swisper-side)
- Modify Swisper's ToolExecutionNode
- Add SDK wrapper around each tool call
- **Downside:** Requires Swisper code changes

**Option 2: Post-process tool_results** (SDK-side)
- After tool_execution completes
- Parse tool_results from output
- Create observations retroactively
- **Downside:** Not real-time, but simpler

**Option 3: Monkey-patch tool execution** (SDK-side)
- Wrap Swisper's tool caller at runtime
- Intercept tool calls automatically
- **Downside:** Complex, fragile

---

## 📋 Recommended Approach: Post-Processing

### **Why:**
- ✅ No Swisper code changes needed
- ✅ Works with existing tool_results structure
- ✅ Handles batch tool execution
- ✅ SDK-only implementation
- ✅ Can iterate without breaking Swisper

### **How:**

**In decorator.py, after function execution:**

```python
# After getting output_data
if obs_name == "tool_execution" and output_data:
    # Check if we have tool_results
    if 'tool_results' in output_data:
        # Create child observations for each tool
        await _create_tool_observations(
            trace_id=trace_id,
            parent_obs_id=obs_id,
            tool_results=output_data['tool_results']
        )
```

---

## 🔧 Implementation Steps

### **Step 1: Add Tool Observation Creator** (30 mins)

**File:** `sdk/swisper_studio_sdk/tracing/tool_observer.py` (NEW)

```python
"""
Tool observation creator - extracts individual tools from tool_results
"""

async def create_tool_observations(
    trace_id: str,
    parent_observation_id: str,
    tool_results: dict
) -> None:
    """
    Create individual TOOL observations from tool_results structure.
    
    Parses Swisper's tool_results format:
    {
        "batch_xyz": {
            "results": {
                "tool_key": {
                    "tool_name": "office365_search_emails",
                    "result": {...},
                    "error": None
                }
            }
        }
    }
    """
    from .redis_publisher import publish_event
    import uuid
    from datetime import datetime
    
    for batch_key, batch_data in tool_results.items():
        if not isinstance(batch_data, dict) or 'results' not in batch_data:
            continue
        
        results = batch_data['results']
        
        for tool_key, tool_data in results.items():
            # Generate observation ID
            tool_obs_id = str(uuid.uuid4())
            
            # Extract tool info
            tool_name = tool_data.get('tool_name', tool_key.split('_')[0])
            has_error = bool(tool_data.get('error'))
            
            # Parse parameters from tool_key (if encoded)
            parameters = _parse_tool_parameters(tool_key, tool_data)
            
            # Create tool observation
            await publish_event(
                event_type="observation_start",
                trace_id=trace_id,
                observation_id=tool_obs_id,
                data={
                    "name": tool_name,
                    "type": "TOOL",
                    "parent_observation_id": parent_observation_id,
                    "input": {
                        "tool_name": tool_name,
                        "parameters": parameters,
                        "batch_key": batch_key,
                    },
                    "start_time": datetime.utcnow().isoformat(),
                }
            )
            
            # End tool observation immediately (already executed)
            await publish_event(
                event_type="observation_end",
                trace_id=trace_id,
                observation_id=tool_obs_id,
                data={
                    "output": {
                        "status": "failure" if has_error else "success",
                        "result": tool_data.get('result'),
                        "error": tool_data.get('error'),
                    },
                    "level": "ERROR" if has_error else "DEFAULT",
                    "end_time": datetime.utcnow().isoformat(),
                }
            )


def _parse_tool_parameters(tool_key: str, tool_data: dict) -> dict:
    """Extract parameters from tool key or data"""
    params = {}
    
    # Try explicit parameters first
    if 'parameters' in tool_data:
        params = tool_data['parameters']
    
    # Parse from key (format: toolname_param1_value1_param2_value2)
    # Example: office365_search_emails_folder_inbox_filter_...
    parts = tool_key.split('_')
    
    # Skip tool name, parse key-value pairs
    for i in range(2, len(parts), 2):
        if i + 1 < parts.length:
            params[parts[i]] = parts[i + 1]
    
    return params
```

---

### **Step 2: Integrate into Decorator** (15 mins)

**File:** `sdk/swisper_studio_sdk/tracing/decorator.py`

**After function execution, before ending observation:**

```python
# Check if this is tool_execution node
if obs_name == "tool_execution" and output_data and 'tool_results' in output_data:
    # Create child observations for each tool
    from .tool_observer import create_tool_observations
    
    try:
        await create_tool_observations(
            trace_id=trace_id,
            parent_observation_id=obs_id,
            tool_results=output_data['tool_results']
        )
    except Exception as e:
        logger.debug(f"Failed to create tool observations: {e}")
        # Continue - not critical
```

---

### **Step 3: Update Frontend Tree** (30 mins)

**Already works!** Tree will automatically show TOOL type nodes with wrench icons.

**May need to:**
- Ensure TOOL nodes display correctly
- Add parameters to tree view tooltip
- Show success/failure badge

---

### **Step 4: Create Tool Detail View** (30 mins)

**File:** `frontend/src/features/traces/components/tool-detail-viewer.tsx` (NEW)

```typescript
export function ToolDetailViewer({ observation }) {
  const toolInput = observation.input;
  const toolOutput = observation.output;
  
  const isSuccess = toolOutput?.status === 'success';
  
  return (
    <Box>
      <Typography variant="h6">
        🔧 {observation.name}
      </Typography>
      
      {/* Status Badge */}
      <Chip 
        label={isSuccess ? '✅ Success' : '❌ Failed'}
        color={isSuccess ? 'success' : 'error'}
      />
      
      {/* Parameters */}
      <Typography variant="subtitle1">Parameters:</Typography>
      <JsonView value={toolInput?.parameters} />
      
      {/* Result */}
      <Typography variant="subtitle1">
        {isSuccess ? 'Response:' : 'Error:'}
      </Typography>
      {isSuccess ? (
        <JsonView value={toolOutput?.result} />
      ) : (
        <Alert severity="error">{toolOutput?.error}</Alert>
      )}
    </Box>
  );
}
```

---

### **Step 5: Update Observation Detail Panel** (15 mins)

**Add condition for TOOL type:**

```typescript
{isTool && (
  <ToolDetailViewer observation={observation} />
)}
```

---

## 🧪 Testing Plan

### **Test 1: Verify Tool Observations Created**

```sql
-- Should see individual tool observations
SELECT name, type, parent_observation_id 
FROM observations 
WHERE type = 'TOOL'
ORDER BY start_time;
```

**Expected:**
- office365_search_emails (TOOL) → parent: tool_execution obs
- analyze_emails (TOOL) → parent: tool_execution obs

---

### **Test 2: Verify Tree Display**

```
tool_execution (SPAN)
  ├─ 🔧 office365_search_emails (TOOL) ✅
  └─ 🔧 analyze_emails (TOOL) ✅
```

---

### **Test 3: Verify Detail View**

Click on individual tool → Should show:
- Parameters
- Success status
- Response payload

---

## ⏱️ Timeline

**Hour 1:**
- Create tool_observer.py (30 mins)
- Integrate into decorator.py (15 mins)
- Test with sample tool_results (15 mins)

**Hour 2:**
- Create ToolDetailViewer component (30 mins)
- Update observation-details-panel (15 mins)
- End-to-end testing (15 mins)

**Total: 2 hours**

---

## 🎯 Success Criteria

- [ ] tool_execution has child TOOL observations
- [ ] Each tool shows with 🔧 icon in tree
- [ ] Click on tool shows detail view
- [ ] Parameters visible
- [ ] Success/failure status clear
- [ ] Response payload accessible
- [ ] Works for both productivity_agent and research_agent

---

**Ready to implement! Shall I proceed?** 🚀

