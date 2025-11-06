# Scalable Tool Tracing Design - Developer-Friendly Approach

**Date:** 2025-11-06  
**Problem:** Current approach requires decorator changes for each agent format  
**Goal:** Universal tool detection that works for ANY agent, ANY format

---

## 🎯 Design Principles

1. **Zero Swisper Code Changes** - SDK handles everything
2. **Works for All Agents** - productivity, research, future agents
3. **Developer Friendly** - No manual wrapping per tool
4. **Node-Level Detection** - Automatic based on patterns
5. **Scalable** - New agents "just work"

---

## 💡 Proposed Solution: Universal Tool Extractor

### **Concept: Pattern-Based Detection**

Instead of hardcoding agent formats, detect tools by PATTERN:

```python
def extract_tools_from_output(output: dict) -> list[ToolCall]:
    """
    Universal tool extractor - works for ANY agent format.
    
    Detects tools by looking for common patterns:
    - Any key containing 'tool' + 'result'
    - Any list of dicts with tool-like structure
    - Any nested structure with tool execution metadata
    """
    tools = []
    
    # Pattern 1: tool_results (productivity_agent)
    if 'tool_results' in output:
        tools.extend(_extract_from_tool_results(output['tool_results']))
    
    # Pattern 2: tool_execution_results_history (research_agent)
    if 'tool_execution_results_history' in output:
        tools.extend(_extract_from_execution_history(output['tool_execution_results_history']))
    
    # Pattern 3: Direct tool calls (generic)
    if '_tools_executed' in output:  # Future standard
        tools.extend(_extract_from_tools_executed(output['_tools_executed']))
    
    # Pattern 4: Scan for tool-like structures (fallback)
    for key, value in output.items():
        if 'tool' in key.lower() and isinstance(value, (list, dict)):
            tools.extend(_extract_from_generic_structure(value))
    
    return tools
```

**This works for:**
- ✅ productivity_agent (today)
- ✅ research_agent (today)
- ✅ future_agent (tomorrow) - auto-detects!

---

## 🏗️ Implementation: Three Layers

### **Layer 1: Node-Level Detection (SDK)**

**In decorator.py:**

```python
# After function execution
if obs_name == "tool_execution" and final_output:
    # Universal tool extraction (works for all agents!)
    tools = extract_tools_from_output(final_output)
    
    if tools:
        await create_tool_observations(trace_id, obs_id, tools)
```

**No agent-specific logic!** ✅

---

### **Layer 2: Pattern Extractors (SDK)**

**In tool_observer.py:**

```python
def _extract_from_tool_results(tool_results: dict) -> list[ToolCall]:
    """Extract from productivity_agent format"""
    tools = []
    for batch_key, batch_data in tool_results.items():
        if 'results' in batch_data:
            for tool_key, tool_data in batch_data['results'].items():
                tools.append(ToolCall(
                    name=tool_data.get('tool_name', 'unknown'),
                    parameters=_parse_parameters(tool_key, tool_data),
                    result=tool_data.get('result'),
                    error=tool_data.get('error'),
                    status='success' if not tool_data.get('error') else 'failure'
                ))
    return tools

def _extract_from_execution_history(history: list) -> list[ToolCall]:
    """Extract from research_agent format"""
    tools = []
    for execution in history:
        if isinstance(execution, dict) and 'results' in execution:
            for result in execution['results']:
                tools.append(ToolCall(
                    name=result.get('tool_name', 'unknown'),
                    parameters=result.get('parameters', {}),
                    result=result.get('result'),
                    error=result.get('error'),
                    status=result.get('status', 'success')
                ))
    return tools

def _extract_from_generic_structure(data: any) -> list[ToolCall]:
    """Fallback: Extract from any tool-like structure"""
    # Duck typing: if it looks like tool results, extract it!
    tools = []
    
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and ('tool_name' in item or 'name' in item):
                tools.append(ToolCall.from_dict(item))
    
    elif isinstance(data, dict):
        # Could be nested batches or results
        for value in data.values():
            tools.extend(_extract_from_generic_structure(value))
    
    return tools
```

---

### **Layer 3: Developer API (Future)**

**For Swisper developers who want explicit control:**

```python
# In their tool execution node (optional, not required!)
from swisper_studio_sdk import trace_tool

@trace_tool("office365_search_emails")
async def search_emails(folder, filter, max_results):
    # SDK automatically creates TOOL observation
    result = await office365_api.search(...)
    return result
    # SDK automatically ends TOOL observation

# Or context manager style:
async with trace_tool("send_email", parameters=params):
    result = await send_email_api(...)
    return result
```

**But this is OPTIONAL!** The pattern detection works without any Swisper changes.

---

## ✅ **Answer to Q1:**

**Problem:** Current approach requires adding conditions for each agent format

**Solution:** **Universal pattern-based detection**
- ✅ No decorator changes for new agents
- ✅ Works by detecting patterns in output
- ✅ Scalable to infinite agent types
- ✅ Falls back to generic detection
- ✅ Optional explicit API for developers who want control

**Should I implement this universal extractor?** (30 mins)

---

## 🔄 **Q2: Tracing Toggle Design**

### **Architecture: Per-Request Dynamic Check**

```
┌─────────────────────────────────────────────┐
│ SWISPERSTUDIO UI                            │
│                                             │
│  Project Settings:                          │
│    Tracing: [ON] [OFF]  ← Toggle            │
│                                             │
│  POST /api/v1/projects/{id}/settings        │
│    {"tracing_enabled": true}                │
│                                             │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ SWISPERSTUDIO BACKEND                        │
│                                             │
│  Updates: projects.tracing_enabled = true   │
│                                             │
│  Writes to Redis cache (fast lookup):       │
│    SET tracing:project:{id}:enabled true    │
│    EXPIRE 60  # 60 second cache             │
│                                             │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ SWISPER SDK (Per-Request Check)             │
│                                             │
│  Before creating trace:                     │
│                                             │
│  enabled = redis.get(                       │
│      f"tracing:project:{project_id}:enabled"│
│  )                                          │
│                                             │
│  if enabled != "true":                      │
│      return  # Skip tracing (1-2ms check)   │
│                                             │
│  # Proceed with tracing...                  │
│                                             │
└─────────────────────────────────────────────┘
```

---

### **Performance:**

- Redis GET: ~1ms
- Cached for 60 seconds
- Minimal overhead
- Can disable instantly (within 60s)

---

### **Per-User Level (Future):**

```python
# Check hierarchy:
if not global_enabled:
    return  # Global kill switch

if not project_enabled:
    return  # Project disabled

if not user_enabled:
    return  # User opted out

if not should_sample(user_id, 10%):
    return  # Sample only 10% of users

# Proceed with tracing
```

---

## 🎯 **What I'll Implement:**

**Q1: Universal Tool Extractor**
- Pattern-based detection
- No decorator changes for new agents
- ~30 minutes

**Q2: Project-Level Toggle**
- Database column: projects.tracing_enabled
- Redis cache for fast checks
- UI toggle in project settings
- Per-request check in SDK
- ~1 hour

**Total: ~1.5 hours**

---

**Should I implement both now?** 🚀

Or do you want to review the design first?
