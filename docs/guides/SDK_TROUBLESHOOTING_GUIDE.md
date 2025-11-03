# SDK Troubleshooting Guide

**Last Updated:** November 3, 2025  
**Version:** v1.0  
**For:** SwisperStudio SDK Basic Integration

---

## 🔍 Common Issues

### **Issue 1: SDK Import Fails**

**Error:**
```python
ImportError: No module named 'swisper_studio_sdk'
```

**Cause:** SDK not installed

**Solution:**
```bash
cd /path/to/swisper
uv pip install -e /root/projects/swisper_studio/sdk

# Verify:
python -c "from swisper_studio_sdk import create_traced_graph; print('OK')"
```

---

### **Issue 2: No Traces Appearing in SwisperStudio**

**Symptoms:**
- Swisper runs without errors
- But no traces in SwisperStudio

**Debugging steps:**

**A) Check SwisperStudio backend is running:**
```bash
docker compose ps
# backend should be "Up"

curl http://localhost:8001/api/v1/health
# Should return: {"status": "healthy"}
```

**B) Check initialization:**
```python
# Add logging to Swisper after initialize_tracing():
from swisper_studio_sdk.tracing.client import get_studio_client
client = get_studio_client()
print(f"SDK Client: {client}")  # Should NOT be None
print(f"API URL: {client.api_url if client else 'None'}")
```

**C) Check network connectivity:**
```bash
# From Swisper container, can you reach SwisperStudio?
curl http://localhost:8001/api/v1/traces \
  -H "X-API-Key: dev-api-key-change-in-production"

# Should return 405 (method not allowed) or 422, not connection error
```

**D) Check API key:**
```python
# In SwisperStudio backend, get the correct key:
docker compose exec backend python -c "
from app.core.config import settings
print(settings.API_KEY)
"

# Use that in initialize_tracing()
```

**E) Check project ID:**
```
# Get from SwisperStudio UI:
http://localhost:3000/projects

# Project ID is in the URL when you click a project
```

---

### **Issue 3: Swisper Crashes on Startup**

**Error:**
```
AttributeError: 'StateGraph' object has no attribute 'add_node'
```

**Cause:** `create_traced_graph()` returns wrong type

**Solution:**
```python
# The SDK monkey-patches add_node, might conflict with custom implementations
# Verify you're using standard LangGraph:

from langgraph.graph import StateGraph  # Must be this import
graph = StateGraph(...)  # Standard usage

# If using custom StateGraph, SDK might not work
```

---

### **Issue 4: Observations Created but Empty**

**Symptoms:**
- Trace appears
- Observations appear
- But `input` and `output` are null

**Cause:** State not serializable

**Debugging:**
```python
# In a Swisper node, check if state is serializable:
import json

async def my_node(state):
    try:
        serialized = json.dumps(dict(state))
        print(f"✅ State is serializable: {len(serialized)} bytes")
    except Exception as e:
        print(f"❌ State not serializable: {e}")
    
    return state
```

**Solution:**
```python
# GlobalSupervisorState is TypedDict - should work automatically
# If using Pydantic models, convert:

from pydantic import BaseModel

class MyState(BaseModel):
    field: str

# In node:
async def my_node(state: MyState) -> MyState:
    # State.dict() or state.model_dump() if needed
    return state
```

---

### **Issue 5: Performance Degradation**

**Symptoms:**
- Swisper is slower after adding SDK
- Requests taking >1s longer

**Measure:**
```bash
# Before SDK:
time curl -X POST http://localhost:8000/api/chat ...

# After SDK:
time curl -X POST http://localhost:8000/api/chat ...

# Compare times
```

**Expected overhead:** <100ms

**If >200ms:**

**A) Check SwisperStudio backend latency:**
```bash
curl -w "@-" -H "X-API-Key: dev-api-key-change-in-production" \
  http://localhost:8001/api/v1/traces \
  <<'EOF'
    time_namelookup:  %{time_namelookup}\n
    time_connect:  %{time_connect}\n
    time_total:  %{time_total}\n
EOF
```

**B) Check network:**
- Are Swisper and SwisperStudio on same host?
- Using localhost or docker network?

**C) Temporary solution - disable tracing:**
```python
initialize_tracing(
    ...,
    enabled=False  # Disable until performance issue resolved
)
```

---

### **Issue 6: SDK Doesn't Capture State Changes**

**Symptoms:**
- State Before and After are identical
- No changes shown in diff

**Cause:** Node doesn't return modified state

**Check:**
```python
async def my_node(state):
    # ❌ WRONG - doesn't modify state
    return state

# ✅ CORRECT - returns new state
async def my_node(state):
    return {
        **state,
        "new_field": "new_value"  # Adds field
    }
```

**Verify in Swisper:**
- Nodes MUST return modified state (TypedDict or dict)
- Use spread operator: `{**state, new_field: value}`

---

### **Issue 7: Nested Observations Not Appearing**

**Symptoms:**
- Only root observation visible
- Child nodes missing

**Cause:** Context not properly set

**SDK handles this automatically, but check:**
```python
# The SDK uses contextvars for observation nesting
# Ensure you're using async functions (not sync)

# ✅ WORKS:
async def my_node(state):
    await some_async_call()
    return state

# ⚠️ MIGHT NOT WORK:
def my_node_sync(state):  # Sync function
    return state
```

**Solution:** Use async nodes (LangGraph requirement anyway)

---

## 🧪 **Testing Checklist**

**Before declaring SDK working, verify:**

- [ ] SDK imports successfully
- [ ] `initialize_tracing()` runs without errors
- [ ] `create_traced_graph()` returns a StateGraph
- [ ] Graph compiles and runs
- [ ] Trace appears in SwisperStudio
- [ ] Observations appear in trace
- [ ] State is captured (input/output not null)
- [ ] State diff shows changes
- [ ] Nesting works (parent-child relationships)
- [ ] Errors are tracked (try a failing node)
- [ ] Performance overhead <100ms

---

## 📞 **Getting Help**

**If stuck:**

1. **Check SwisperStudio backend logs:**
   ```bash
   docker compose logs backend -f
   # Look for errors when trace is sent
   ```

2. **Check Swisper logs:**
   ```bash
   # Look for SDK HTTP requests and errors
   # Should see: "Creating observation: ..."
   ```

3. **Test SDK independently:**
   ```bash
   python sdk/test_sdk_locally.py
   # Isolates SDK issues from Swisper integration
   ```

4. **Verify API manually:**
   ```bash
   # Create a trace manually:
   curl -X POST http://localhost:8001/api/v1/traces \
     -H "X-API-Key: dev-api-key-change-in-production" \
     -H "Content-Type: application/json" \
     -d '{
       "id": "test-trace-001",
       "name": "Manual Test",
       "project_id": "YOUR_PROJECT_ID",
       "user_id": "test",
       "timestamp": "2025-11-03T10:00:00Z"
     }'
   
   # Should return 201 Created
   ```

---

## 🎯 **Quick Diagnosis**

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Import error | SDK not installed | `pip install -e /path/to/sdk` |
| No traces | SwisperStudio down | `docker compose up -d` |
| No traces | Wrong API key | Check with `settings.API_KEY` |
| No traces | Wrong project ID | Get from UI URL |
| Empty observations | State not serializable | Check state is dict/TypedDict |
| No nesting | Sync functions | Use async |
| Slow performance | Network latency | Check localhost vs docker network |

---

## ✅ **Success Indicators**

**When everything works:**
- ✅ `python sdk/test_sdk_locally.py` passes
- ✅ Trace appears in SwisperStudio within 1 second
- ✅ All observations visible
- ✅ State diff shows green backgrounds for additions
- ✅ Can click through observations
- ✅ Duration metrics make sense

**You're ready for real Swisper integration!** 🎉

---

**Last Updated:** November 3, 2025  
**Status:** Ready for Use  
**Related:** `docs/guides/SWISPER_SDK_INTEGRATION_GUIDE.md`

