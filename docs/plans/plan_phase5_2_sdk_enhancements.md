# Phase 5.2: SDK Enhancements - LLM & Tool Tracking

**Date:** November 3, 2025  
**Status:** ✅ Infrastructure Complete (Deferred full implementation to Phase 5.1)  
**Actual Duration:** 30 minutes  
**Planned Duration:** 4-5 days  
**Priority:** Medium - Enhances observability  
**Dependencies:** Basic SDK already working (Phase 5.1 prep complete)

---

## Executive Summary

**Current State:**
- ✅ SDK captures state transitions
- ✅ SDK creates observation tree
- ✅ State diff viewer working
- ⚠️ All observations are type=SPAN (not semantically correct)
- ❌ No LLM prompts captured
- ❌ No token counting
- ❌ No tool call details

**Target State:**
- ✅ LLM calls automatically captured (prompts, responses, tokens)
- ✅ Tool calls automatically captured (arguments, responses)
- ✅ Correct observation types (GENERATION, TOOL, AGENT)
- ✅ Token counting for cost calculation
- ✅ Model parameters captured (temperature, max_tokens)

**Value:** Complete observability matching our beautiful UI from Phase 2.5

---

## Requirements

### Functional Requirements

**1. LLM Wrapper**
- Intercept `llm_adapter.get_structured_output()` calls in Swisper
- Extract prompt messages before sending to LLM
- Extract model name and parameters (temperature, max_tokens, top_p)
- Count tokens from response
- Store in observation (input, output, model, model_parameters)
- Set observation type = GENERATION

**2. Tool Wrapper**
- Detect when tools are executed
- Capture tool name and arguments
- Capture tool responses
- Store in observation
- Set observation type = TOOL

**3. Observation Type Detection**
- Auto-detect LLM calls → GENERATION type
- Auto-detect tool calls → TOOL type
- Auto-detect agent nodes → AGENT type
- Default → SPAN type

**4. Backward Compatibility**
- SDK still works if Swisper doesn't use our LLM adapter
- Graceful degradation (falls back to SPAN if can't detect type)
- No breaking changes to existing SDK API

---

## Technical Approach

### Option A: Monkey Patching (Recommended) ⭐

**Intercept at SDK initialization:**
```python
# In SDK's initialize_tracing()
def initialize_tracing(...):
    # Existing setup
    ...
    
    # NEW: Wrap LLM adapter
    _wrap_llm_adapter()
    
    # NEW: Wrap tool executor (if exists)
    _wrap_tool_executor()

def _wrap_llm_adapter():
    """Monkey patch llm_adapter.get_structured_output"""
    try:
        from swisper.backend.app.services import llm_adapter
        original_get_output = llm_adapter.get_structured_output
        
        async def wrapped_get_output(*args, **kwargs):
            # Extract prompt, model, params
            messages = kwargs.get('messages', [])
            model = kwargs.get('model', 'unknown')
            temperature = kwargs.get('temperature')
            
            # Call original
            result = await original_get_output(*args, **kwargs)
            
            # Store in current observation context
            _store_llm_telemetry(messages, result, model, temperature)
            
            return result
        
        llm_adapter.get_structured_output = wrapped_get_output
    except ImportError:
        # Swisper doesn't have this adapter, skip
        pass
```

**Pros:**
- ✅ Zero code changes in Swisper nodes
- ✅ Automatic capture
- ✅ Easy to enable/disable

**Cons:**
- ⚠️ Fragile if Swisper refactors llm_adapter
- ⚠️ Import path hardcoded

---

### Option B: Decorator Pattern (Alternative)

**Swisper nodes use decorator:**
```python
@traced_llm("intent_classification")
async def intent_node(state):
    result = await llm_adapter.get_structured_output(...)
    return state
```

**Pros:**
- ✅ Explicit, not magic
- ✅ More maintainable

**Cons:**
- ❌ Requires code changes in every Swisper node
- ❌ Not automatic

**Decision:** Use **Option A (Monkey Patching)** for automatic capture

---

## Implementation Plan

### Sprint 1: LLM Wrapper (Day 1 - 4 hours)

**Files to Create:**
- `sdk/swisper_studio_sdk/wrappers/llm_wrapper.py` - LLM interception
- `sdk/swisper_studio_sdk/wrappers/__init__.py` - Exports

**Files to Modify:**
- `sdk/swisper_studio_sdk/__init__.py` - Call wrappers in initialize_tracing()
- `sdk/swisper_studio_sdk/tracing/decorator.py` - Store LLM telemetry in observation

**What to Capture:**
```python
# From LLM call
observation.input = {
    "messages": [
        {"role": "system", "content": "You are..."},
        {"role": "user", "content": "What's my next meeting?"}
    ]
}
observation.output = {
    "intent": "calendar_query",
    "confidence": 0.95
}
observation.model = "gpt-4-turbo"
observation.model_parameters = {
    "temperature": 0.8,
    "max_tokens": 2000
}
observation.prompt_tokens = 150
observation.completion_tokens = 50
observation.type = "GENERATION"
```

**Testing:**
- Create test that calls llm_adapter.get_structured_output()
- Verify prompt captured in observation
- Verify tokens counted
- Verify type = GENERATION

---

### Sprint 2: Tool Wrapper (Day 1 - 2 hours)

**Files to Create:**
- `sdk/swisper_studio_sdk/wrappers/tool_wrapper.py` - Tool interception

**What to Capture:**
```python
# From tool call
observation.input = {
    "tool_name": "get_calendar_events",
    "arguments": {
        "start_date": "2024-11-03",
        "end_date": "2024-11-04"
    }
}
observation.output = {
    "events": [
        {"title": "Meeting with Sarah", "time": "10:00"}
    ]
}
observation.type = "TOOL"
```

**Challenge:** Need to identify tool execution pattern in Swisper
- Check if tools are in `backend/app/tools/` 
- Look for common wrapper/executor
- May need to wrap individual tools

---

### Sprint 3: Type Detection (Day 1 - 2 hours)

**Logic:**
```python
def detect_observation_type(observation_name: str, has_llm_data: bool, has_tool_data: bool):
    """Auto-detect observation type based on captured data"""
    
    # If we captured LLM telemetry
    if has_llm_data:
        return ObservationType.GENERATION
    
    # If we captured tool data
    if has_tool_data:
        return ObservationType.TOOL
    
    # If name contains "agent" or ends with "_agent"
    if "agent" in observation_name.lower():
        return ObservationType.AGENT
    
    # Default
    return ObservationType.SPAN
```

**Files to Modify:**
- `sdk/swisper_studio_sdk/tracing/decorator.py` - Call type detection

---

## Testing Strategy

### Test Plan (8 tests)

**LLM Wrapper Tests (4 tests):**
1. Test LLM call captures prompt messages
2. Test LLM call captures model name and parameters
3. Test LLM call counts tokens
4. Test observation type set to GENERATION

**Tool Wrapper Tests (2 tests):**
1. Test tool call captures arguments
2. Test tool call captures response
3. Test observation type set to TOOL

**Type Detection Tests (2 tests):**
1. Test agent nodes get AGENT type
2. Test default nodes get SPAN type

**Integration Test (1 test):**
1. Test end-to-end with mock Swisper graph (LLM + tool + agent)

---

## Success Criteria

**MVP Complete When:**
- ✅ LLM calls automatically captured (prompts visible in UI)
- ✅ Token counting works (costs calculated)
- ✅ Tool calls automatically captured (arguments visible)
- ✅ Observation types correct (GENERATION=pink, TOOL=orange badges)
- ✅ No code changes required in Swisper nodes (automatic)
- ✅ All tests passing
- ✅ Tested with real Swisper request
- ✅ Documentation updated

---

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| llm_adapter import path changes | Medium | Medium | Try-except, fallback to no wrapping |
| Tool execution pattern unclear | High | Low | Manual mapping if needed |
| Token counting inaccurate | Low | Low | Use tiktoken library (OpenAI standard) |
| Performance overhead | Low | Medium | Async capture, optional disable |

---

## File Structure

```
sdk/
├── swisper_studio_sdk/
│   ├── __init__.py (MODIFY - add wrapper init)
│   ├── wrappers/
│   │   ├── __init__.py (NEW)
│   │   ├── llm_wrapper.py (NEW - LLM interception)
│   │   └── tool_wrapper.py (NEW - Tool interception)
│   └── tracing/
│       └── decorator.py (MODIFY - store telemetry, detect types)
└── tests/
    └── test_wrappers.py (NEW - 8 tests)
```

---

## Timeline

**Day 1 (8 hours):**
- Morning (4h): LLM wrapper + tests
- Afternoon (2h): Tool wrapper + tests
- Evening (2h): Type detection + integration test

**Day 2 (if needed - 2-3 hours):**
- Refinements based on testing
- Documentation updates
- Final validation

**Stretch goal:** Complete in 1 day (8 hours) given our efficiency

---

## Deferred Features (Post-5.2)

**Not in scope for this phase:**
- Token estimation for non-OpenAI models
- Streaming LLM capture
- Function calling details (OpenAI)
- Fine-tuning metrics
- LLM caching detection

---

**Status:** Ready for detailed sub-plan approval ✅  
**Next:** Create detailed implementation breakdown and get approval


