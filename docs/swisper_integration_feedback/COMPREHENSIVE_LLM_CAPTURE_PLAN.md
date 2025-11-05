# Comprehensive LLM Capture - All Methods

**Date:** November 5, 2025  
**Current:** Only `get_structured_output()` wrapped  
**Needed:** Wrap all 5 LLM methods  
**Priority:** Medium (after validating current integration)

---

## 🔍 LLM Methods in Swisper

### **1. get_structured_output()** ✅ **WORKING**
**Used by:** classify_intent, global_planner, productivity_planner, etc.  
**Status:** ✅ Wrapped and capturing prompts!  
**Evidence:** classify_intent shows `_llm_messages` in UI

### **2. stream_message_from_LLM()** ❌ **NOT CAPTURED**
**Used by:** user_interface_node (line 509)  
**Purpose:** Stream LLM responses to user  
**Status:** ❌ Not wrapped - no prompts captured for UI responses

### **3. embed_documents()** ❌ **NOT CAPTURED**
**Used by:** memory_node, fact storage, RAG  
**Purpose:** Generate embeddings for semantic search  
**Status:** ❌ Not wrapped - can't see embedding calls

### **4. embed_text()** ❌ **NOT CAPTURED**
**Used by:** query embedding  
**Purpose:** Single text embedding  
**Status:** ❌ Not wrapped

### **5. on_reasoning_chunk (SSE)** ❌ **NOT CAPTURED**
**Used by:** global_planner streaming reasoning  
**Purpose:** Stream thinking process to frontend  
**Status:** ❌ Callback-based, complex to capture

---

## 📋 Implementation Plan

### **Phase 1: Stream Capture** (1-2 hours)

**Wrap `stream_message_from_LLM()`:**

```python
# In llm_wrapper.py
original_stream = TokenTrackingLLMAdapter.stream_message_from_LLM

async def wrapped_stream(self, messages, agent_type=None, metadata=None):
    """Capture streaming LLM calls"""
    obs_id = get_current_observation()
    
    if obs_id:
        # Store messages before streaming
        _store_llm_input({
            "messages": messages,
            "agent_type": agent_type,
            "method": "stream"
        })
    
    accumulated_content = ""
    accumulated_tokens = 0
    
    # Stream through and accumulate
    async for chunk in original_stream(self, messages, agent_type, metadata):
        # Accumulate content
        if isinstance(chunk, dict):
            if 'choices' in chunk and chunk['choices']:
                delta = chunk['choices'][0].get('delta', {})
                if 'content' in delta:
                    accumulated_content += delta['content']
            if 'usage' in chunk:
                accumulated_tokens = chunk['usage'].get('total_tokens', 0)
        
        yield chunk  # Pass through unchanged
    
    # Store accumulated result
    if obs_id:
        _store_llm_output({
            "result": accumulated_content,
            "total_tokens": accumulated_tokens,
            "method": "stream"
        })

TokenTrackingLLMAdapter.stream_message_from_LLM = wrapped_stream
```

**Benefit:** Capture UI node prompts and responses

---

### **Phase 2: Embedding Capture** (1 hour)

**Wrap `embed_documents()` and `embed_text()`:**

```python
original_embed_docs = TokenTrackingLLMAdapter.embed_documents
original_embed_text = TokenTrackingLLMAdapter.embed_text

async def wrapped_embed_docs(self, texts, agent_type=None):
    obs_id = get_current_observation()
    
    if obs_id:
        _store_llm_input({
            "texts": texts[:3],  # First 3 for preview
            "count": len(texts),
            "agent_type": agent_type,
            "method": "embed_documents"
        })
    
    result = await original_embed_docs(self, texts, agent_type)
    
    if obs_id:
        _store_llm_output({
            "embeddings_count": len(result),
            "dimensions": len(result[0]) if result else 0,
            "method": "embed_documents"
        })
    
    return result

async def wrapped_embed_text(self, text, agent_type=None):
    obs_id = get_current_observation()
    
    if obs_id:
        _store_llm_input({
            "text": text[:200],  # Preview
            "agent_type": agent_type,
            "method": "embed_text"
        })
    
    result = await original_embed_text(self, text, agent_type)
    
    if obs_id:
        _store_llm_output({
            "dimensions": len(result),
            "method": "embed_text"
        })
    
    return result

TokenTrackingLLMAdapter.embed_documents = wrapped_embed_docs
TokenTrackingLLMAdapter.embed_text = wrapped_embed_text
```

**Benefit:** See embedding calls in memory_node

---

### **Phase 3: Reasoning SSE** (Complex - 2-3 hours)

**Challenge:** Reasoning streams via SSE callback  
**Current:** `on_reasoning_chunk` callback  
**Difficulty:** Need to intercept callback, not just method

**Approach:**
```python
# Wrap the callback itself
original_get_structured = TokenTrackingLLMAdapter.get_structured_output

async def wrapped_get_structured(..., on_reasoning_chunk=None, ...):
    obs_id = get_current_observation()
    accumulated_reasoning = ""
    
    # Wrap the callback
    async def wrapped_callback(chunk):
        nonlocal accumulated_reasoning
        accumulated_reasoning += chunk
        
        # Call original callback
        if on_reasoning_chunk:
            await on_reasoning_chunk(chunk)
    
    # Use wrapped callback
    result = await original_get_structured(
        ...,
        on_reasoning_chunk=wrapped_callback if on_reasoning_chunk else None,
        ...
    )
    
    # Store reasoning
    if obs_id and accumulated_reasoning:
        _store_llm_output({"reasoning": accumulated_reasoning})
    
    return result
```

**Benefit:** See thinking process in global_planner

---

## 🎯 Recommended Approach:

**For Now (Current Integration):**
- ✅ Keep current wrapper (get_structured_output only)
- ✅ Validate it's working
- ✅ Get Swisper team feedback

**Phase 5.3 (After Validation):**
- Add stream_message_from_LLM wrapper
- Add embedding wrappers
- Add reasoning capture

**Rationale:**
- Current wrapper captures 80% of LLM calls (most nodes use get_structured_output)
- Stream/embedding capture adds complexity
- Better to validate core integration first
- Then enhance incrementally

---

## 📊 Coverage Analysis:

| Node | Method | Captured? |
|------|--------|-----------|
| **classify_intent** | get_structured_output | ✅ YES |
| **global_planner** | get_structured_output | ✅ YES |
| **productivity_planner** | get_structured_output | ✅ YES |
| **user_interface** | stream_message_from_LLM | ❌ NO (Phase 5.3) |
| **memory_node** | embed_documents | ❌ NO (Phase 5.3) |
| **fact_extraction** | get_structured_output | ✅ YES |

**Current Coverage:** ~80% of LLM interactions  
**With Phase 5.3:** ~100%

---

## 💡 Recommendation:

**Today:** Validate current integration works  
**This Week:** Add stream + embedding wrappers if needed  
**Timeline:** 2-3 hours additional work

**Decision point:** Does Swisper team need 100% coverage now, or is 80% sufficient for MVP?

---

**For now, SDK v0.3.0 captures the most important LLM calls (structured output).  
Stream and embedding capture can be Phase 5.3 enhancement.**

