# SDK LLM Reasoning Capture - Implementation Plan

**Date:** 2025-11-06  
**Version:** 1.0  
**Status:** DRAFT - Awaiting Review  
**Complexity:** Medium  
**Estimated Time:** 3-4 hours (including testing)

---

## 🎯 Objective

Capture **prompts**, **reasoning process**, and **final responses** from all LLM calls in Swisper, with proper separation for UX clarity.

---

## 📊 Current State Analysis

### What We Capture Now (SDK v0.3.4):

| LLM Call Type | Prompts | Reasoning | Response | Coverage |
|---------------|---------|-----------|----------|----------|
| `get_structured_output()` | ✅ | ❌ | ✅ | 66% |
| `stream_message_from_LLM()` | ❌ | ❌ | ❌ | 0% |

**Total Coverage:** ~70% (structured calls only)

### Swisper's LLM Architecture:

```python
# Two LLM call patterns in Swisper:

# 1. Structured Output (classify_intent, global_planner, etc.)
result = await llm_adapter.get_structured_output(
    messages=[...],
    schema=DecisionSchema,
    on_reasoning_chunk=callback,  # ← Reasoning streamed here!
)
# Returns: StructuredOutputResult(result={...}, tokens={...})

# 2. Streaming (user_interface node)
async for chunk in llm_adapter.stream_message_from_LLM(
    messages=[...],
):
    # Chunks: {"content": "...", "usage": {...}}
```

---

## 🚨 Critical Pitfalls Identified

### **Pitfall 1: Callback Interception Race Condition** 🔥

**Problem:**
```python
# Swisper creates callback BEFORE we can intercept it
on_reasoning_chunk = await initialize_streaming(...)

# Then passes it to get_structured_output
result = await llm_adapter.get_structured_output(
    ...,
    on_reasoning_chunk=on_reasoning_chunk  # ← Already created!
)
```

**Impact:** We can't intercept the callback - it's created in Swisper's code!

**Solution:** Wrap at a different level - intercept the **method** not the callback.

---

### **Pitfall 2: Reasoning Chunks vs Final Reasoning** 🔥

**Problem:**
```python
# Reasoning comes in chunks:
chunk_1: "Let me analyze"
chunk_2: " this request..."
chunk_3: " I should check"
# ...50 more chunks

# We need full text: "Let me analyze this request... I should check..."
```

**Issues:**
- Memory: Storing 50+ chunks per observation
- Order: Chunks must be concatenated in correct order
- Cleanup: Need to clear chunks after observation ends

**Solution:** Accumulate in temporary buffer, merge on completion, then clear.

---

### **Pitfall 3: Streaming Response Accumulation** 🔥

**Problem:**
```python
# Streaming can yield 100+ chunks:
chunk_1: {"content": "Hello"}
chunk_2: {"content": " there"}
chunk_3: {"content": "!"}
# ...100 more

# Final response: "Hello there!..."
```

**Issues:**
- Memory: 100+ strings in memory per streaming call
- Performance: String concatenation in tight loop
- Tokens: Token data only in LAST chunk

**Solution:** Use efficient string buffer (list of strings), join once at end.

---

### **Pitfall 4: Multiple Observations Using Same LLM Call** 🔥

**Problem:**
```python
# Context stack:
observation_A (parent)
  observation_B (child) ← get_current_observation() returns this!
    [LLM call happens here]

# Where do we store reasoning?
# - observation_A? (wrong - not the LLM caller)
# - observation_B? (correct - but what if nested deeper?)
```

**Issues:**
- Context confusion: Which observation owns the LLM data?
- Nested calls: Recursion could overwrite data
- Memory leaks: Old observation data never cleaned up

**Solution:** Use observation ID as key, clean up after observation ends.

---

### **Pitfall 5: Fire-and-Forget Timing** 🔥

**Problem:**
```python
# Current SDK flow:
1. create_observation_background()  # Fire-and-forget POST
2. Execute function (with LLM call)
3. Accumulate reasoning chunks
4. end_observation_background()     # Fire-and-forget PATCH
5. LLM might still be streaming!   # ← Race condition!

# Reasoning chunks arrive AFTER observation ended!
```

**Impact:** Reasoning data arrives after PATCH sent → lost data!

**Solution:** Ensure all LLM data accumulated BEFORE calling `end_observation_background()`.

---

### **Pitfall 6: Error Handling in Callbacks** 🔥

**Problem:**
```python
async def reasoning_interceptor(chunk: str):
    reasoning_chunks.append(chunk)  # What if this throws?
    await original_callback(chunk)   # What if this throws?
    # Exception crashes LLM call!
```

**Impact:** SDK bug breaks user's LLM calls → production crash!

**Solution:** Try-catch ALL SDK code, never propagate errors to user code.

---

### **Pitfall 7: Memory Leaks** 🔥

**Problem:**
```python
# Global storage grows unbounded:
_llm_telemetry_store = {
    "obs-1": {...},  # 1 KB
    "obs-2": {...},  # 1 KB
    "obs-3": {...},  # 1 KB
    # ...after 10,000 requests = 10 MB in memory!
}

# Never cleaned up!
```

**Impact:** Memory leak → server OOM after days of operation.

**Solution:** Implement cleanup mechanism (LRU cache or explicit cleanup).

---

## 🎨 UX Design Considerations

### **Challenge 1: Information Overload**

**Problem:**
```
classify_intent (LLM) [Prompt] [Reasoning] [Response] [Tokens] [Model] [Duration]
                       ↑        ↑           ↑          ↑
                   6 buttons - overwhelming!
```

**Solution:**
- **Primary action:** [Response] (most important - what LLM decided)
- **Secondary actions:** [Prompt] [Reasoning] (debugging)
- **Metadata:** Tokens/Model/Duration as badges, not buttons

**Design:**
```
classify_intent (LLM) ⚡ 1.2s | 450 tokens | GPT-4
  [✨ Response]  [Details ▼]
                   └─ Prompt
                   └─ Reasoning (if available)
                   └─ Metadata
```

---

### **Challenge 2: Reasoning vs Response Confusion**

**Problem:** Users don't understand difference:
- **Reasoning:** "I should check calendar..." (thinking process)
- **Response:** `{"action": "check_calendar"}` (decision)

**Solution:**
- **Visual differentiation:**
  - Reasoning: 🧠 Yellow background, italics, "Thinking..."
  - Response: ✨ White background, bold, "Decision"
- **Labels matter:**
  - NOT: "Output" (confusing)
  - YES: "What it decided" (clear)

---

### **Challenge 3: Empty Reasoning**

**Problem:**
- Not all LLMs produce reasoning (GPT-4 Turbo doesn't use `<think>`)
- Button shows, user clicks, sees empty modal → confusion

**Solution:**
- **Hide button if no reasoning:**
  ```jsx
  {observation.output._llm_reasoning && (
    <Button>Reasoning</Button>
  )}
  ```
- **Show indicator when reasoning available:**
  ```
  classify_intent (LLM) 🧠  ← Badge means "has reasoning"
  ```

---

### **Challenge 4: Long Reasoning Text**

**Problem:**
- Reasoning can be 5,000+ characters
- Modal becomes scrolling nightmare
- Hard to find relevant parts

**Solution:**
- **Collapsible sections:**
  ```
  🧠 Reasoning (2,543 characters)
  ▼ Analysis Phase (500 chars)
  ▼ Decision Making (1,200 chars)
  ▼ Validation (843 chars)
  ```
- **Search within reasoning**
- **Copy to clipboard button**

---

### **Challenge 5: Streaming Progress Indication**

**Problem:**
- Streaming takes 3-10 seconds
- User sees "loading..." but not what's happening

**Solution:**
- **Progressive disclosure:**
  ```
  user_interface (LLM) 🔄 Streaming...
    ├─ Chunks received: 45/~50
    ├─ Response length: 1,234 chars
    └─ Estimated time: 3s
  ```
- **After completion:**
  ```
  user_interface (LLM) ✅ 
    [Response] (1,234 chars, 3.2s)
  ```

---

## 🏗️ Architecture Plan

### **Approach: Two-Phase Capture**

```
Phase 1: DURING execution
├─ Intercept callback (reasoning chunks)
├─ Accumulate in memory buffer
└─ Pass through to original callback (zero delay)

Phase 2: AFTER execution
├─ Merge accumulated data
├─ Store in observation output
├─ Clean up buffers
└─ Send to SwisperStudio
```

### **Data Structure:**

```python
# Observation output format:
{
  "observation": {
    "output": {
      // User's actual state/data
      "messages": [...],
      "intent": "calendar",
      
      // SDK metadata (underscore prefix)
      "_llm_messages": [        # Prompts
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."}
      ],
      "_llm_reasoning": "...",  # Full reasoning text (if available)
      "_llm_result": {...},     # Final response/decision
      "_llm_tokens": {
        "total": 450,
        "prompt": 200,
        "completion": 250
      },
      "_llm_model": "gpt-4-turbo",
      "_llm_duration_ms": 1234
    }
  }
}
```

### **Storage Strategy:**

```python
# Temporary buffer (cleared after observation ends)
_llm_telemetry_store = {
  "obs-id-123": {
    "input": {...},
    "output": {...},
    "reasoning_chunks": ["chunk1", "chunk2", ...],  # Temporary
    "response_chunks": ["Hello", " there", ...],    # Temporary
  }
}

# Cleanup after observation ends:
def _cleanup_observation(obs_id: str):
    if obs_id in _llm_telemetry_store:
        del _llm_telemetry_store[obs_id]
```

---

## 🔧 Implementation Strategy

### **Step 1: Enhance llm_wrapper.py (60 mins)**

**Changes:**
1. Add reasoning chunk accumulator
2. Add streaming response accumulator
3. Implement safe callback interception
4. Add error handling (try-catch all SDK code)
5. Add cleanup mechanism

**Key Code:**
```python
async def wrapped_get_structured_output(..., on_reasoning_chunk=None, ...):
    obs_id = get_current_observation()
    
    if obs_id:
        # Initialize buffers
        _init_buffers(obs_id)
        
        # Create safe interceptor
        original_callback = on_reasoning_chunk
        
        async def safe_reasoning_interceptor(chunk: str):
            try:
                # Accumulate for SDK
                _accumulate_reasoning(obs_id, chunk)
                
                # Pass through to original (user's callback)
                if original_callback:
                    await original_callback(chunk)
            except Exception as e:
                # NEVER crash user's LLM call!
                logger.debug(f"SDK reasoning capture failed: {e}")
        
        # Replace callback
        on_reasoning_chunk = safe_reasoning_interceptor
    
    # Call original method
    result = await original_get_structured_output(...)
    
    if obs_id:
        # Merge accumulated data
        reasoning_text = _get_accumulated_reasoning(obs_id)
        _store_llm_output(obs_id, {
            "reasoning": reasoning_text,
            "result": result.result.model_dump(),
            ...
        })
        # Cleanup happens in decorator after observation ends
    
    return result
```

---

### **Step 2: Update decorator.py (30 mins)**

**Changes:**
1. Merge reasoning into output
2. Add cleanup call after observation ends
3. Handle both structured and streaming outputs

**Key Code:**
```python
# In decorator.py, after function execution:
if llm_data:
    final_output['_llm_messages'] = llm_data['input']['messages']
    final_output['_llm_result'] = llm_data['output']['result']
    
    # Add reasoning if available
    if llm_data['output'].get('reasoning'):
        final_output['_llm_reasoning'] = llm_data['output']['reasoning']
    
    final_output['_llm_tokens'] = {...}

# After sending to SwisperStudio:
_cleanup_observation_buffers(obs_id)  # Prevent memory leak
```

---

### **Step 3: Frontend UX (60 mins)**

**Changes:**
1. Update `ObservationDetail.tsx`
2. Add `ReasoningViewer` component
3. Update type badges/indicators
4. Add progressive disclosure UI

**Component Hierarchy:**
```
ObservationDetail
├─ ObservationHeader (badges: tokens, duration, model)
├─ PrimaryActions
│  └─ ResponseButton (always visible for GENERATION)
├─ SecondaryActions (dropdown)
│  ├─ PromptButton
│  ├─ ReasoningButton (conditional: if _llm_reasoning exists)
│  └─ MetadataButton
└─ Modals
   ├─ PromptViewer
   ├─ ReasoningViewer (NEW)
   └─ ResponseViewer
```

---

### **Step 4: Testing Strategy (60 mins)**

**Test Cases:**

**TC1: Structured Output with Reasoning**
```bash
# Trigger global_planner (uses reasoning)
curl -X POST /chat -d '{"message": "Schedule meeting tomorrow"}'

# Verify in SwisperStudio:
# - global_planner shows [Response] [Reasoning]
# - Reasoning contains "<think>..." content
# - Response shows final decision
```

**TC2: Structured Output without Reasoning**
```bash
# Trigger classify_intent (no reasoning)
curl -X POST /chat -d '{"message": "Hello"}'

# Verify:
# - classify_intent shows [Response] only (no Reasoning button)
# - Response shows intent classification
```

**TC3: Streaming Response**
```bash
# Trigger user_interface (streaming)
curl -X POST /chat -d '{"message": "Tell me about your capabilities"}'

# Verify:
# - user_interface shows [Response]
# - Response shows full streamed text
# - No reasoning (streaming doesn't use <think>)
```

**TC4: Memory Leak Test**
```bash
# Send 1000 requests
for i in {1..1000}; do
  curl -X POST /chat -d '{"message": "Test '$i'"}'
done

# Verify:
# - Backend memory doesn't grow unbounded
# - _llm_telemetry_store cleaned up after each request
```

**TC5: Error Handling**
```bash
# Inject error in callback (modify SDK temporarily)
# Verify:
# - LLM call still succeeds (SDK error doesn't propagate)
# - Observation created (even without SDK data)
# - Logs show SDK error (but app continues)
```

---

## 🚧 Edge Cases & Solutions

### **Edge Case 1: Nested LLM Calls**

**Scenario:**
```python
observation_A
  └─ LLM call 1 (classify_intent)
     observation_B
       └─ LLM call 2 (nested tool)
```

**Solution:**
- Each observation tracks its own LLM data
- Use observation ID as key (no collision)
- Cleanup happens per observation

---

### **Edge Case 2: Concurrent LLM Calls**

**Scenario:**
```python
# Two observations running in parallel:
observation_A → LLM call (global_planner)
observation_B → LLM call (classify_intent)

# Both accumulating reasoning chunks simultaneously
```

**Solution:**
- Per-observation buffers (keyed by obs_id)
- Thread-safe (asyncio context vars are isolated)
- No race conditions

---

### **Edge Case 3: LLM Call After Observation Ended**

**Scenario:**
```python
# Observation ends
end_observation_background(obs_id)

# But LLM still streaming chunks!
reasoning_chunk("more thinking...")  # ← Arrives late!
```

**Solution:**
```python
def _accumulate_reasoning(obs_id: str, chunk: str):
    # Check if observation still active
    if obs_id not in _llm_telemetry_store:
        logger.debug(f"Ignoring late chunk for ended observation {obs_id}")
        return  # Silently ignore
    
    _llm_telemetry_store[obs_id]['reasoning_chunks'].append(chunk)
```

---

### **Edge Case 4: Very Large Reasoning (10 MB+)**

**Scenario:**
- DeepSeek R1 produces 50,000 character reasoning
- 10 MB JSON payload to SwisperStudio
- Network timeout?

**Solution:**
```python
MAX_REASONING_LENGTH = 50_000  # 50 KB limit

def _get_accumulated_reasoning(obs_id: str) -> str:
    chunks = _llm_telemetry_store[obs_id].get('reasoning_chunks', [])
    full_text = ''.join(chunks)
    
    if len(full_text) > MAX_REASONING_LENGTH:
        # Truncate with indicator
        return (
            full_text[:MAX_REASONING_LENGTH] + 
            f"\n\n... [Truncated. Full length: {len(full_text)} chars]"
        )
    
    return full_text
```

---

## ⚠️ Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Memory leak from buffers | HIGH | HIGH | Implement cleanup, add LRU cache |
| Callback interception breaks | MEDIUM | HIGH | Comprehensive error handling |
| Frontend performance (large reasoning) | MEDIUM | MEDIUM | Lazy loading, virtualization |
| Race condition (streaming) | LOW | MEDIUM | Proper async/await ordering |
| Breaking existing functionality | LOW | CRITICAL | Unit tests, integration tests |

---

## ✅ Success Criteria

**Technical:**
- [ ] 100% LLM coverage (structured + streaming)
- [ ] Reasoning captured for applicable LLMs
- [ ] Zero memory leaks (tested with 1,000 requests)
- [ ] Zero latency added to user experience
- [ ] No errors in production logs

**UX:**
- [ ] Clear visual separation (Reasoning vs Response)
- [ ] Intuitive button placement
- [ ] Performance: <100ms to render large reasoning
- [ ] Mobile responsive design

**Business:**
- [ ] Developers can debug LLM decisions
- [ ] Visibility into "why" LLM made choices
- [ ] Reduced debugging time by 50%

---

## 📅 Implementation Timeline

**Phase 1: SDK Changes (Day 1)**
- [ ] 9:00-10:00 - Implement reasoning accumulator
- [ ] 10:00-11:00 - Implement streaming wrapper
- [ ] 11:00-12:00 - Error handling & cleanup
- [ ] 12:00-13:00 - Unit tests

**Phase 2: Frontend Changes (Day 1)**
- [ ] 14:00-15:00 - Update ObservationDetail component
- [ ] 15:00-16:00 - Create ReasoningViewer component
- [ ] 16:00-17:00 - UX polish & responsive design

**Phase 3: Integration Testing (Day 2)**
- [ ] 9:00-10:00 - End-to-end testing (all nodes)
- [ ] 10:00-11:00 - Memory leak testing
- [ ] 11:00-12:00 - Performance testing
- [ ] 12:00-13:00 - Bug fixes

**Phase 4: Documentation & Handover (Day 2)**
- [ ] 14:00-15:00 - Update SDK README
- [ ] 15:00-16:00 - Update frontend docs
- [ ] 16:00-17:00 - Create demo video
- [ ] 17:00-18:00 - Final review & deployment

**Total:** 2 days (16 hours)

---

## 🎯 Recommendation

**GREEN LIGHT** - Proceed with implementation with following safeguards:

1. **Start with structured output only** (lower risk)
2. **Add comprehensive error handling** (never break user code)
3. **Implement cleanup from day 1** (prevent memory leaks)
4. **Progressive UX rollout** (start with simple design, enhance later)
5. **Monitor production metrics** (memory, latency, errors)

**ROI:**
- **High value:** Reasoning visibility is game-changing for debugging
- **Medium risk:** Well-understood technical challenges
- **Low complexity:** 2 days of focused work

---

## 📝 Open Questions

1. **Should we persist reasoning to database?**
   - Pro: Historical analysis, debugging
   - Con: Database size grows significantly
   - **Decision needed:** Keep in memory only vs. persist

2. **Should we limit reasoning capture to specific LLMs?**
   - Pro: Smaller payloads, faster transmission
   - Con: Less visibility
   - **Decision needed:** Capture all vs. selective

3. **Should we support reasoning search/filtering?**
   - Pro: Find specific reasoning patterns
   - Con: Complex implementation
   - **Decision needed:** V1 scope vs. future enhancement

---

**Author:** AI Assistant  
**Reviewers:** [ ]  
**Approved By:** [ ]  
**Status:** AWAITING APPROVAL

