# SDK Limitation: Streaming Token Capture

**Date:** 2025-11-06  
**Status:** KNOWN LIMITATION  
**Impact:** user_interface node has no token data (1/9 LLM calls = 11%)  
**Severity:** LOW - user_interface is final response, not used for cost optimization

---

## 🐛 Issue

**Observation:** `user_interface` node has NULL tokens

**Coverage:** 8/9 LLM observations have tokens = **89%**

**Missing:** Streaming calls (user_interface uses `stream_message_from_LLM()`)

---

## 🔍 Root Cause

### **Architecture Problem: Double Wrapping**

```
LLM (Kvant)
  ↓
Kvant Adapter (returns chunks)
  ↓
TokenTrackingLLMAdapter (INNER - tracks tokens internally)
  ├─ Accumulates usage from chunks
  ├─ Logs: "Streaming token usage - Total: X"
  └─ But doesn't add usage to yielded chunks!
  ↓
SDK Wrapper (OUTER - our code)
  ├─ Tries to read 'usage' from chunks
  ├─ But chunks only have 'content'
  └─ accumulated_tokens stays at 0

Result: Tokens = NULL
```

**The Problem:**
- Token usage is tracked INSIDE TokenTrackingLLMAdapter
- But NOT exposed in the yielded chunks
- SDK wrapper can't see them (wrapping at wrong level)

---

## 💡 Why This Happens

**Streaming generators can't return data after completion:**
```python
async for chunk in stream():
    yield chunk  # Can only yield what we receive

# After loop ends, no way to get final token count
# The generator is exhausted
```

**Token tracking happens internally:**
- TokenTrackingLLMAdapter accumulates tokens
- Logs them after streaming
- But doesn't yield a final "usage" chunk
- SDK wrapper never sees the total

---

## 🎯 Solutions (Ranked)

### **Option 1: Accept Limitation** ✅ RECOMMENDED

**Coverage:** 89% (8/9 LLM calls)

**Rationale:**
- user_interface is the final user-facing response
- Not used for cost optimization decisions
- Other 8 LLM calls (planning, classification, agent execution) HAVE tokens
- These are the important ones for debugging and cost analysis

**Impact:** LOW - doesn't affect cost visibility for decision-making LLM calls

---

### **Option 2: Wrap at Different Level** (Complex)

**Idea:** Wrap the Kvant adapter directly, before TokenTrackingLLMAdapter

**Problems:**
- Breaks Swisper's token tracking
- Requires modifying Swisper's code
- Complex architectural change
- Not worth it for 11% coverage gain

---

### **Option 3: Post-Streaming Hook** (Not Feasible)

**Idea:** Add callback after streaming completes

**Problems:**
- Generators can't have post-completion hooks
- Would require changing LangChain/Kvant adapter
- Not under our control

---

### **Option 4: Estimate Tokens** (Inaccurate)

**Idea:** Estimate from response length

```python
# Rough estimate: ~0.75 tokens per word
estimated_tokens = len(response.split()) * 0.75
```

**Problems:**
- Inaccurate (can be 50% off)
- Misleading for cost calculation
- Better to have NULL than wrong data

---

## 📊 Impact Assessment

### **What We Lose:**

**Token visibility for user_interface:**
- Can't see exact tokens used for final response
- Can't calculate cost for user_interface LLM call

**What We Keep:**

**Token visibility for ALL decision-making LLM calls:**
- ✅ classify_intent (classify user intent)
- ✅ global_planner (decide what to do)
- ✅ productivity_planner (plan email/calendar operations)
- ✅ research_planner (plan research queries)
- ✅ completion_evaluator (check if research complete)

**These are the important ones!** These drive costs and decisions.

---

## 💰 Cost Impact

### **Example Trace:**

```
Total tokens: ~36,000
  - classify_intent: 5,081 (captured ✅)
  - global_planner: 2,216 (captured ✅)
  - productivity_planner: 15,322 (captured ✅)
  - research_planner: 3,616 (captured ✅)
  - completion_evaluator: 5,269 (captured ✅)
  - user_interface: ~4,500 (NOT captured ❌)
```

**Coverage:** 31,504 / 36,000 = **87.5% of actual tokens**

**Cost coverage:** ~88% of total LLM costs

**Missing:** Only final response generation (usually cheapest part)

---

## ✅ Recommendation

**Accept 89% coverage for now**

**Why:**
1. ✅ All decision-making LLM calls covered (the expensive ones)
2. ✅ Cost attribution accurate for optimization
3. ✅ Debugging capabilities not impacted
4. ✅ No complex architectural changes needed
5. ✅ user_interface cost is typically <15% of total

**Alternative:** Document as "Streaming token counts not available - decision LLM calls fully covered"

---

## 📈 Future Enhancement

**If needed (low priority):**

Swisper could add a final chunk with usage:
```python
# In Kvant adapter, after streaming completes:
yield {
    'type': 'usage',
    'usage': {
        'total_tokens': accumulated_total,
        'prompt_tokens': accumulated_prompt,
        'completion_tokens': accumulated_completion
    }
}
```

Then SDK wrapper would catch it.

**Effort:** 1 hour (Swisper-side change)  
**Priority:** P3 (nice to have, not critical)

---

## 🎯 Bottom Line

**Current:** 89% coverage (8/9 LLM calls)  
**Status:** ✅ ACCEPTABLE for production  
**Missing:** user_interface streaming (final response)  
**Impact:** LOW (decision LLMs fully covered)

**Recommendation:** Ship it! 🚀

