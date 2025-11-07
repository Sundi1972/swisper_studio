# Agent Tool Format Standardization - Critical Issue

**Date:** 2025-11-06  
**Priority:** HIGH  
**Impact:** Research agent tools not appearing in SwisperStudio  
**Root Cause:** Inconsistent tool result serialization

---

## 🐛 **Current Problem**

### **Symptom:**
- ✅ Productivity_agent tools appear in SwisperStudio (individual TOOL observations)
- ❌ Research_agent tools DO NOT appear (no TOOL observations)

### **Root Cause:**

**Research_agent stores tool results as Python object strings:**
```python
# What gets stored in database:
"results={'search_web_...': ToolResultEntry(tool_name='search_web', tool_args={...}, result='...')}"
```

**This is a STRING, not JSON!** The SDK can't parse it.

**Productivity_agent stores tool results as proper JSON:**
```json
{
  "tool_results": {
    "batch_key": {
      "results": {
        "tool_name": "analyze_emails",
        "parameters": {...},
        "result": "..."
      }
    }
  }
}
```

This **IS JSON** and parses correctly.

---

## 🔍 **Technical Analysis**

### **Where the Problem Occurs:**

**In Swisper Agent Code (research_agent):**
```python
# research_agent/nodes/tool_execution.py (example)
from your_models import ToolResultEntry  # Pydantic model

def execute_tools(state):
    results = {}
    for tool in tools_to_execute:
        # Creates ToolResultEntry OBJECT
        results[tool_key] = ToolResultEntry(
            tool_name=tool.name,
            tool_args=args,
            result=result
        )
    
    # State contains Pydantic objects, not dicts!
    state["tool_execution_results_history"].append({
        "results": results  # ← This is a dict of OBJECTS
    })
    return state
```

**What happens:**
1. State contains `ToolResultEntry` Pydantic objects
2. SDK copies state with `copy.deepcopy()`
3. Pydantic objects get serialized as `repr()` strings
4. Database stores: `"ToolResultEntry(...)"`  ← Not parseable!

---

## ✅ **Solution Options**

### **Option 1: Fix in Swisper (Recommended) - 30 mins**

**Change research_agent to use plain dicts:**

```python
# Before (BROKEN):
results[tool_key] = ToolResultEntry(
    tool_name=tool.name,
    tool_args=args,
    result=result
)

# After (FIXED):
results[tool_key] = {
    "tool_name": tool.name,
    "tool_args": args,  # or "parameters"
    "result": result,
    "error": None,
    "status": "success"
}
```

**Benefits:**
- ✅ Consistent with productivity_agent
- ✅ JSON-serializable
- ✅ Works with SDK tool extraction
- ✅ No SDK changes needed

**Files to modify in Swisper:**
- `backend/app/domain/research/nodes/tool_execution.py` (or similar)
- Anywhere `ToolResultEntry` is created

---

### **Option 2: Add Serialization Hook in SDK - 1 hour**

**Make SDK convert Pydantic models to dicts before storing:**

```python
# In decorator.py, before copy.deepcopy():
def serialize_for_json(obj):
    """Convert Pydantic models to dicts"""
    if hasattr(obj, 'model_dump'):
        return obj.model_dump()
    elif isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_for_json(item) for item in obj]
    return obj

output_data = serialize_for_json(result)
```

**Benefits:**
- ✅ Works with any Pydantic model
- ✅ No Swisper code changes

**Drawbacks:**
- ❌ Adds complexity to SDK
- ❌ May break if models have circular references
- ❌ Doesn't fix root cause (agents using objects instead of dicts)

---

### **Option 3: Standardize Agent State Format - 2 hours**

**Create a unified tool result format for ALL agents:**

```python
# Proposed standard format (add to LangGraph state):
class StandardState(TypedDict):
    # Existing fields...
    
    # NEW: Standardized tool tracking
    _tools_executed: List[Dict[str, Any]]  # Always a list of dicts!
    """
    Standard format:
    [
      {
        "tool_name": "search_web",
        "parameters": {"query": "...", "type": "news"},
        "result": "...",
        "error": None,
        "status": "success",
        "timestamp": "2025-11-06...",
        "batch_key": "research_batch_1"
      }
    ]
    """
```

**Benefits:**
- ✅ Future-proof
- ✅ Consistent across all agents
- ✅ Easy for SDK to parse
- ✅ Extensible (can add fields later)

**Drawbacks:**
- ❌ Requires updating ALL agents
- ❌ Migration for existing code

---

## 🎯 **My Recommendation**

**Short-term (30 mins):** **Option 1** - Fix research_agent to use dicts
- Quickest fix
- Aligns with productivity_agent
- Unblocks tool observations immediately

**Long-term (2 hours):** **Option 3** - Standardize all agents
- Create `_tools_executed` standard
- Migrate all agents gradually
- Future agents follow standard

---

## 📊 **Current State Analysis**

### **Productivity Agent:**
```json
{
  "tool_results": {
    "batch_read_...": {
      "results": {
        "analyze_emails_...": {
          "tool_name": "analyze_emails",
          "parameters": {...},
          "result": "..."
        }
      }
    }
  }
}
```
**Format:** Dict → Dict → Dict (3 levels)  
**Serialization:** ✅ JSON  
**Tool Extraction:** ✅ Works

### **Research Agent:**
```python
{
  "tool_execution_results_history": [
    "results={'search_web_...': ToolResultEntry(...)}"  # STRING!
  ]
}
```
**Format:** List of strings (Python repr)  
**Serialization:** ❌ String repr  
**Tool Extraction:** ❌ Broken

---

## 🚀 **Action Items**

### **For Swisper Team:**

**Immediate (30 mins):**
1. Find where `ToolResultEntry` is created in research_agent
2. Replace with plain dict (see Option 1 above)
3. Test that tools appear in SwisperStudio

**Files to check:**
```bash
cd /root/projects/helvetiq
grep -r "ToolResultEntry" backend/app/domain/
grep -r "tool_execution_results_history" backend/app/domain/
```

### **For SwisperStudio Team (Us):**

**Optional Enhancement:**
- Add better error handling for unparseable tool formats
- Log warning when tool extraction fails
- Add debugging endpoint to show raw tool data

---

## 💡 **Would You Like Me To:**

**Option A:** Create a plan document for Swisper team to standardize agents?

**Option B:** Add SDK workaround to parse Python repr strings? (hacky but quick)

**Option C:** Create a migration guide for moving to `_tools_executed` standard?

**Option D:** Just document this for now and let Swisper team handle it?

---

**This is an important architectural decision - what's your preference?** 🤔

