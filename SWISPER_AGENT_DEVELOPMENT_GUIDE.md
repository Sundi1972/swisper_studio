# Swisper Domain Agent Development Guide

**Version:** 2.0  
**Date:** 2025-11-07  
**Status:** Active  
**Supersedes:** agent_creation_guide.md v1.x  
**Last Updated:** 2025-11-07 11:20 UTC

---

## 📋 **Document Versioning**

| Version | Date | Changes | Deprecated |
|---------|------|---------|------------|
| 2.0 | 2025-11-07 | SwisperStudio integration standards, tool format specification | - |
| 1.x | 2024-11-xx | Original agent creation guide | ⚠️ Use v2.0 |

**Breaking Changes from v1.x:**
- Added `_tools_executed` requirement for tool tracking
- Added `_tools_executed_by` for anti-duplication
- Updated state TypedDict requirements

---

## 🎯 **Purpose**

This guide defines the **standard interface** for building Swisper domain agents with SwisperStudio observability integration.

**Use this guide when:**
- Creating new domain agents
- Refactoring existing agents
- Ensuring SwisperStudio compatibility
- Understanding agent architecture patterns

---

## ✅ **Required vs. Optional**

### **REQUIRED (Must Have for SwisperStudio):**
- ✅ TypedDict state definition
- ✅ `_tools_executed: List[Dict[str, Any]]` field (if agent uses tools)
- ✅ `_tools_executed_by: Optional[str]` field (if agent uses tools)
- ✅ Populate `_tools_executed` after tool execution
- ✅ Set `_tools_executed_by` when creating tools

### **OPTIONAL (Recommended):**
- 📚 Separate tool_execution node (cleaner architecture)
- 📚 Error handling for tools
- 📚 Duration tracking (`duration_ms`)
- 📚 Batch keys for grouping

---

## 📐 **Agent Architecture Patterns**

### **Pattern 1: Separate Tool Node** (Recommended for Complex Agents)

**Example:** Productivity Agent, Wealth Agent

```
Agent Graph:
├─ Planner (decides what to do)
├─ tool_execution (executes tools) ← Sets _tools_executed here
└─ Response Formatter
```

**Pros:**
- ✅ Clean separation of concerns
- ✅ Easy to test tool execution
- ✅ Clear ownership model

**Cons:**
- More nodes in graph

---

### **Pattern 2: Integrated Tools** (Recommended for Simple Agents)

**Example:** Research Agent (current implementation)

```
Agent Graph:
├─ Planner (decides + executes tools) ← Sets _tools_executed here
└─ Evaluator
```

**Pros:**
- ✅ Simpler graph structure
- ✅ Fewer nodes
- ✅ Works well for single-purpose agents

**Cons:**
- Less separation
- Harder to test tool execution in isolation

---

## 🏗️ **Step-by-Step: Creating a New Agent**

### **Step 1: Define Agent State (CRITICAL)**

```python
from typing import TypedDict, List, Dict, Any, Optional

class MyAgentState(TypedDict):
    # REQUIRED CORE FIELDS:
    chat_id: str
    correlation_id: str
    global_plan: str
    
    # REQUIRED IF USING TOOLS (SwisperStudio Integration):
    _tools_executed: List[Dict[str, Any]]
    """
    Standard format for tool tracking (v2.0 requirement):
    [
      {
        "tool_name": str,      # Required
        "parameters": dict,    # Required (can be {})
        "result": Any,         # Required
        "error": None | dict,  # Required
        "status": "success" | "failure",  # Required
        "batch_key": str,      # Optional
        "duration_ms": int     # Optional
      }
    ]
    """
    
    _tools_executed_by: Optional[str]
    """
    OWNERSHIP MARKER (v2.0 anti-duplication):
    Set to node name that creates _tools_executed.
    Example: "tool_execution", "my_agent_node"
    Prevents duplicate extraction when state propagates to child nodes.
    """
    
    # YOUR AGENT-SPECIFIC FIELDS:
    my_agent_result: Optional[str]
    iteration_count: int
    # ... other fields as needed ...
```

**Why _tools_executed_by is needed:**
- LangGraph passes state through nodes
- `_tools_executed` gets copied to all child nodes
- Without ownership marker, SDK extracts same tools multiple times
- Ownership marker tells SDK which node created the tools

---

### **Step 2: Create Tool Execution Node**

**If using Pattern 1 (Separate Node):**

```python
async def tool_execution_node(state: MyAgentState) -> MyAgentState:
    """
    Execute tools and track them for SwisperStudio.
    
    REQUIRED: Set both _tools_executed AND _tools_executed_by
    """
    # Get tools to execute
    tool_operations = state.get("tool_operations", [])
    
    # Initialize tracking
    tools_executed = []
    
    # Execute each tool
    for operation in tool_operations:
        try:
            result = await execute_tool(operation.tool_name, operation.parameters)
            
            # REQUIRED: Add to _tools_executed (SwisperStudio format)
            tools_executed.append({
                "tool_name": operation.tool_name,
                "parameters": operation.parameters,
                "result": result,
                "error": None,
                "status": "success",
                # Optional:
                "batch_key": "batch_1",
                "duration_ms": execution_time
            })
            
        except Exception as e:
            # REQUIRED: Track errors too
            tools_executed.append({
                "tool_name": operation.tool_name,
                "parameters": operation.parameters,
                "result": f"ERROR: {str(e)}",
                "error": {"message": str(e), "type": type(e).__name__},
                "status": "failure"
            })
    
    # Get existing tools (for accumulation)
    existing_tools = state.get("_tools_executed", [])
    
    # REQUIRED: Return with ownership marker
    return {
        **state,
        "_tools_executed": existing_tools + tools_executed,
        "_tools_executed_by": "tool_execution"  # CRITICAL: Set ownership!
    }
```

---

### **Step 3: Register with SwisperStudio Tracing**

```python
from swisper_studio_sdk import create_traced_graph

class MyAgent:
    def _build_graph(self):
        # Use create_traced_graph for automatic tracing
        workflow = create_traced_graph(
            MyAgentState,
            trace_name="my_agent"
        )
        
        # Add nodes
        workflow.add_node("planner", planner_node)
        workflow.add_node("tool_execution", tool_execution_node)
        workflow.add_node("response", response_node)
        
        # Define flow
        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "tool_execution")
        workflow.add_edge("tool_execution", "response")
        workflow.add_edge("response", END)
        
        return workflow.compile()
```

---

## ⚠️ **Common Pitfalls & Solutions**

### **Pitfall 1: Forgetting _tools_executed_by**

**Symptom:** Duplicate tools in SwisperStudio (3 tools → 6-9 observations)

**Cause:**
```python
# ❌ WRONG - Missing ownership marker
return {
    **state,
    "_tools_executed": tools  # State propagates to child nodes
}
```

**Fix:**
```python
# ✅ CORRECT - Set ownership
return {
    **state,
    "_tools_executed": tools,
    "_tools_executed_by": "tool_execution"  # Prevents duplication!
}
```

---

### **Pitfall 2: Not Adding to TypedDict**

**Symptom:** Ownership marker disappears after first node

**Cause:**
```python
# ❌ WRONG - Field not in TypedDict
class MyAgentState(TypedDict):
    my_field: str
    _tools_executed: List[Dict[str, Any]]
    # Missing: _tools_executed_by
```

**Fix:**
```python
# ✅ CORRECT - Include in TypedDict
class MyAgentState(TypedDict):
    my_field: str
    _tools_executed: List[Dict[str, Any]]
    _tools_executed_by: Optional[str]  # LangGraph preserves this
```

---

### **Pitfall 3: Using Pydantic Objects**

**Symptom:** Research agent tools don't appear (before v2.0 fix)

**Cause:**
```python
# ❌ WRONG - Pydantic object gets stringified
result = ToolResultEntry(tool_name="search", ...)
state["_tools_executed"].append(result)  # Becomes "ToolResultEntry(...)" string
```

**Fix:**
```python
# ✅ CORRECT - Convert to dict
result = ToolResultEntry(tool_name="search", ...)
state["_tools_executed"].append(result.model_dump())  # JSON dict
```

---

## 📊 **Integration Checklist**

When creating a new agent:

### **Phase 1: Agent Structure**
- [ ] State TypedDict defined
- [ ] If using tools: Add `_tools_executed: List[Dict[str, Any]]`
- [ ] If using tools: Add `_tools_executed_by: Optional[str]`
- [ ] Agent class implements DomainAgentInterface
- [ ] Graph uses `create_traced_graph()`

### **Phase 2: Tool Integration (If Applicable)**
- [ ] Tool execution populates `_tools_executed`
- [ ] Tool execution sets `_tools_executed_by` to node name
- [ ] All 5 required fields present (tool_name, parameters, result, error, status)
- [ ] Error handling tracks failed tools
- [ ] Accumulates (doesn't overwrite) existing tools

### **Phase 3: Testing**
- [ ] Send test message through Swisper
- [ ] Verify trace appears in SwisperStudio
- [ ] Check tools appear as TOOL observations
- [ ] Verify no duplicates (count matches _tools_executed length)
- [ ] Check logs for skip messages (owned by: XXX)

### **Phase 4: Documentation**
- [ ] Add agent to domain_agent_registry
- [ ] Document tool operations
- [ ] Add test examples
- [ ] Update this guide if new patterns emerge

---

## 🔧 **Minimal Required Code**

**For agents WITHOUT tools:**
```python
class SimpleAgentState(TypedDict):
    chat_id: str
    global_plan: str
    result: Optional[str]
    # No _tools_executed needed
```

**For agents WITH tools:**
```python
class ToolAgentState(TypedDict):
    chat_id: str
    global_plan: str
    _tools_executed: List[Dict[str, Any]]  # REQUIRED
    _tools_executed_by: Optional[str]      # REQUIRED
    result: Optional[str]

# In tool execution node:
return {
    **state,
    "_tools_executed": existing + new_tools,
    "_tools_executed_by": "my_node_name"  # REQUIRED
}
```

---

## 📚 **Reference Examples**

### **Example 1: Research Agent** (Integrated Pattern)
```
Location: backend/app/api/services/agents/research_agent/
Pattern: Tools in agent workflow
Complexity: Medium
Tools: search_web, weather_lookup
```

**Key Files:**
- `agent_state.py` - Has _tools_executed + _tools_executed_by
- `nodes/tool_execution_node.py` - Sets ownership marker

### **Example 2: Productivity Agent** (Separate Node Pattern)
```
Location: backend/app/api/services/agents/productivity_agent/
Pattern: Separate tool_execution node
Complexity: High
Tools: Email, Calendar operations
```

**Key Files:**
- `productivity_agent_state.py` - Has _tools_executed + _tools_executed_by
- `nodes/productivity_tool_execution_node.py` - Sets ownership

### **Example 3: Wealth Agent** (Simple Pattern)
```
Location: backend/app/api/services/agents/wealth_agent/
Pattern: Simple tool execution
Complexity: Low
Tools: WealthOS API calls
```

---

## 🚨 **Migration Guide (v1.x → v2.0)**

If you have existing agents:

### **Step 1: Update State TypedDict**
```python
# Add these two fields:
_tools_executed: List[Dict[str, Any]]
_tools_executed_by: Optional[str]
```

### **Step 2: Update Tool Execution**
```python
# Where you execute tools, add:
state["_tools_executed_by"] = "your_node_name"
```

### **Step 3: Test**
```
# Send test message
# Verify no duplicates (tool count matches _tools_executed length)
```

**Time Required:** 15-30 minutes per agent

---

## 🎓 **Best Practices**

### **1. Always Set Ownership When Creating Tools**
```python
✅ DO:    state["_tools_executed_by"] = "tool_execution"
❌ DON'T: Leave it unset (causes duplicates)
```

### **2. Use TypedDict (Not Pydantic) for State**
```python
✅ DO:    class MyState(TypedDict): ...
❌ DON'T: class MyState(BaseModel): ...
```

### **3. Accumulate Tools, Don't Overwrite**
```python
✅ DO:    existing + new_tools
❌ DON'T: state["_tools_executed"] = new_tools  # Loses previous tools
```

### **4. Always Track Errors**
```python
✅ DO:    {"error": {"message": str(e), "type": type(e).__name__}, "status": "failure"}
❌ DON'T: Skip error tools (breaks observability)
```

---

## 📊 **Tool Format Specification (v2.0)**

### **Required Fields:**

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `tool_name` | str | `"search_web"` | Tool identifier |
| `parameters` | dict | `{"query": "AI"}` | Input params (use `{}` if none) |
| `result` | Any | `"Found 5 results"` | Tool output (any JSON type) |
| `error` | None \| dict | `None` or `{"message": "..."}` | Error info or None |
| `status` | str | `"success"` \| `"failure"` | Execution status |

### **Optional Fields:**

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `batch_key` | str | `"batch_read_001"` | Group related tools |
| `duration_ms` | int | `1234` | Execution time in ms |
| `timestamp` | str | `"2025-11-07T..."` | ISO 8601 format |
| `metadata` | dict | `{"retries": 2}` | Extensible |

---

## 🔍 **Testing Your Agent**

### **Test 1: Basic Functionality**
```bash
# Send test message through Swisper
# Verify response is correct
# Check logs for errors
```

### **Test 2: SwisperStudio Integration**
```bash
# Go to http://localhost:3000
# Navigate to Projects → Your Project → Traces
# Click on latest trace
# Verify:
  - ✅ Agent appears as AGENT observation
  - ✅ Tools appear as TOOL observations (if applicable)
  - ✅ Tool count matches _tools_executed length (no duplicates)
  - ✅ Click tool → See parameters and results
```

### **Test 3: Deduplication**
```bash
# In SwisperStudio database, run:
SELECT COUNT(*) FROM observations 
WHERE trace_id = 'YOUR_TRACE_ID' 
AND type = 'TOOL'

# Should match the length of _tools_executed array
```

---

## 📖 **Related Documentation**

### **For Agent Development:**
- `agent_creation_guide.md` - Original guide (v1.x - deprecated)
- `testing_guide.md` - Testing best practices
- `prompt_writing_guide.md` - Prompt engineering

### **For SwisperStudio Integration:**
- `docs/swisper_studio_integration_tasks/FUTURE_AGENT_TOOL_INTEGRATION_GUIDE.md` - Tool integration
- `docs/swisper_studio_integration_tasks/TOOL_FORMAT_STANDARDIZATION_PLAN.md` - Format details

---

## 🚀 **Quick Start Template**

```python
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from swisper_studio_sdk import create_traced_graph

# Step 1: Define State
class MyAgentState(TypedDict):
    chat_id: str
    global_plan: str
    _tools_executed: List[Dict[str, Any]]  # Required if using tools
    _tools_executed_by: Optional[str]      # Required if using tools
    result: Optional[str]

# Step 2: Create Nodes
async def planner_node(state: MyAgentState) -> MyAgentState:
    # Your planning logic
    return {...state, "plan": "..."}

async def tool_execution_node(state: MyAgentState) -> MyAgentState:
    # Execute tools
    tools_executed = []
    
    # Execute your tools...
    tools_executed.append({
        "tool_name": "my_tool",
        "parameters": {...},
        "result": result,
        "error": None,
        "status": "success"
    })
    
    # CRITICAL: Set ownership!
    return {
        **state,
        "_tools_executed": state.get("_tools_executed", []) + tools_executed,
        "_tools_executed_by": "tool_execution"  # Prevents duplicates
    }

# Step 3: Build Graph
class MyAgent:
    def _build_graph(self):
        # Use create_traced_graph for SwisperStudio integration
        workflow = create_traced_graph(MyAgentState, trace_name="my_agent")
        
        workflow.add_node("planner", planner_node)
        workflow.add_node("tool_execution", tool_execution_node)
        
        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "tool_execution")
        workflow.add_edge("tool_execution", END)
        
        return workflow.compile()
```

---

## ⚠️ **Version 2.0 Requirements Summary**

**If your agent uses tools, you MUST:**

1. ✅ Add `_tools_executed: List[Dict[str, Any]]` to state TypedDict
2. ✅ Add `_tools_executed_by: Optional[str]` to state TypedDict
3. ✅ Populate `_tools_executed` after tool execution (all 5 required fields)
4. ✅ Set `_tools_executed_by` to node name when creating tools
5. ✅ Accumulate (don't overwrite) existing tools
6. ✅ Use `create_traced_graph()` for automatic tracing

**If your agent does NOT use tools:**
- No special requirements beyond basic LangGraph patterns

---

## 🆘 **Troubleshooting**

### **Issue: Duplicate tools in SwisperStudio**
```
Symptom: 3 tools in _tools_executed but 6 TOOL observations
Solution: Add _tools_executed_by field to TypedDict and set it when creating tools
```

### **Issue: Tools don't appear at all**
```
Symptom: _tools_executed has data but no TOOL observations
Solution: Verify _tools_executed format has all 5 required fields
```

### **Issue: Ownership marker lost**
```
Symptom: _tools_executed_by present in first node but not in child nodes
Solution: Add _tools_executed_by to TypedDict state definition
```

---

## 📞 **Support**

**For questions:**
- Check example agents (research, productivity, wealth, doc)
- See `FUTURE_AGENT_TOOL_INTEGRATION_GUIDE.md`
- Check SwisperStudio integration docs

**For bugs:**
- Check logs for error messages
- Verify state TypedDict includes all required fields
- Test with simple single-tool example first

---

## 🎯 **Summary**

**Building Swisper agents in v2.0:**
1. Define state with `_tools_executed` + `_tools_executed_by` (if using tools)
2. Populate `_tools_executed` with standard format (5 required fields)
3. Set `_tools_executed_by` when creating tools
4. Use `create_traced_graph()` for tracing
5. Test in SwisperStudio for duplicates

**The two ownership fields are CRITICAL for proper observability!**

---

**Document Version:** 2.0  
**Last Updated:** 2025-11-07 11:20 UTC  
**Status:** Active  
**Next Review:** When v3.0 requirements emerge

---

**End of Guide**

