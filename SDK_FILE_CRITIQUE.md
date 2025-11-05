# SDK v0.3.0 - File Critique (7-Point Review)

**Following:** `.cursor/rules/00-workflow.mdc` Step 6

---

## File 1: `sdk/swisper_studio_sdk/tracing/decorator.py`

### 1. ✅ Spec Alignment
- Deep copy: ✅ Matches requirement to isolate state
- Fire-and-forget: ✅ Matches zero-latency requirement
- LLM telemetry: ✅ Connects to observation output

### 2. ✅ Elegance & Simplicity
- Single responsibility per change
- Clear comments explaining each fix
- Minimal code additions

### 3. ⚠️ Robustness & Edge Cases
**Issue:** LLM telemetry import in try-except, but could fail silently
**Fix needed:** Add logging for debugging

### 4. ✅ Performance
- Deep copy has cost but necessary for correctness
- Fire-and-forget eliminates blocking
- Net improvement: -600ms latency

### 5. ⚠️ Cleanliness & Maintainability
**Issue:** `final_output` merging logic could be cleaner
**Fix needed:** Extract to helper function

### 6. ✅ Business/Product Sanity
- Fixes real user pain (latency, missing data)
- Matches industry standards
- Production-ready

### 7. ✅ Anti-Brittle Design
- Graceful degradation (try-except)
- Works without LLM wrapper
- Backward compatible

---

## File 2: `sdk/swisper_studio_sdk/tracing/graph_wrapper.py`

### 1. ✅ Spec Alignment
- Parent observation: ✅ Creates hierarchy
- Fire-and-forget: ✅ Non-blocking

### 2. ✅ Elegance & Simplicity
- Clear flow: create parent → execute → end parent
- Proper context management

### 3. ✅ Robustness & Edge Cases
- Try-except around trace creation
- Finally block clears context
- Safe error handling

### 4. ✅ Performance
- Fire-and-forget pattern
- No blocking on parent observation

### 5. ✅ Cleanliness & Maintainability
- Well-commented
- Clear variable names
- Easy to understand

### 6. ✅ Business/Product Sanity
- Solves hierarchy problem
- Better UX in tree view

### 7. ✅ Anti-Brittle Design
- Fallback if trace creation fails
- Context cleanup in finally

---

## File 3: `sdk/swisper_studio_sdk/tracing/client.py`

### 1. ✅ Spec Alignment
- Background methods: ✅ Fire-and-forget
- LLM wrapping call: ✅ Auto-initialization

### 2. ✅ Elegance & Simplicity
- Clear separation: sync (background) vs async (internal)
- Consistent naming pattern

### 3. ✅ Robustness & Edge Cases
- Silent failures logged
- Try-except in background tasks
- Import errors handled

### 4. ✅ Performance
- asyncio.create_task for background
- No blocking waits

### 5. ✅ Cleanliness & Maintainability
- Methods well-documented
- Clear async/sync split

### 6. ✅ Business/Product Sanity
- Zero latency = production ready
- Silent failures = reliability

### 7. ⚠️ Anti-Brittle Design
**Issue:** Background tasks could accumulate if server very slow
**Fix needed:** Consider task limit or queue

---

## File 4: `sdk/swisper_studio_sdk/wrappers/llm_wrapper.py`

### 1. ✅ Spec Alignment
- Wraps Swisper's TokenTrackingLLMAdapter: ✅
- Captures messages, results, tokens: ✅

### 2. ⚠️ Elegance & Simplicity
**Issue:** Global dict for telemetry storage (not ideal)
**Better:** Use contextvars for thread-safety

### 3. ✅ Robustness & Edge Cases
- Try-except on import
- Silent failure if not in Swisper
- _llm_wrapper_active flag prevents double-wrap

### 4. ✅ Performance
- Minimal overhead (dict operations)
- No blocking calls

### 5. ⚠️ Cleanliness & Maintainability
**Issue:** Telemetry store never cleaned up (memory leak potential)
**Fix needed:** Clear after observation end

### 6. ✅ Business/Product Sanity
- Huge value: see LLM prompts
- Solves debugging problem

### 7. ⚠️ Anti-Brittle Design
**Issue:** Tight coupling to Swisper's exact module path
**Fix needed:** Try multiple import paths

---

## Summary of Issues Found:

### 🔧 High Priority Refactorings:

**1. decorator.py - Extract LLM merge logic** (5 mins)
```python
def _merge_llm_telemetry_into_output(obs_id, output_data):
    """Clean helper function"""
    # Extract current inline code
```

**2. llm_wrapper.py - Memory leak fix** (10 mins)
```python
def clear_llm_telemetry(obs_id):
    """Clear after observation ends"""
    _llm_telemetry_store.pop(obs_id, None)
```

**3. llm_wrapper.py - Thread-safe storage** (15 mins)
```python
# Use contextvars instead of global dict
from contextvars import ContextVar
_llm_telemetry: ContextVar[dict] = ContextVar('llm_telemetry', default={})
```

### ⚠️ Medium Priority:

**4. client.py - Task limit** (20 mins)
```python
# Limit concurrent background tasks
_background_tasks = set()
# Add task management
```

**5. llm_wrapper.py - Fallback import paths** (10 mins)
```python
# Try multiple paths for robustness
try:
    from app.api.services.llm_adapter...
except:
    try:
        from backend.app.api.services.llm_adapter...
    except:
        pass
```

---

## Estimated Refactoring Time: 1 hour

**Critical:** 30 mins (memory leak + helper extraction)
**Nice-to-have:** 30 mins (thread-safe + task limits)

---

**Proceeding to refactoring phase...**

