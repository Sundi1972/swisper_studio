# SDK Gap Analysis - Before Real Swisper Integration

**Date:** November 3, 2025  
**Purpose:** Identify what the SDK is missing before we integrate with real Swisper  
**Reference:** Mock test data shows what we NEED to capture

---

## 📊 Current SDK Status

**Location:** `sdk/swisper_studio_sdk/`

**What exists (Phase 1 - Basic SDK):**
- ✅ `create_traced_graph()` - Wraps LangGraph StateGraph
- ✅ `@traced` decorator - Wraps individual functions
- ✅ Basic state capture (input/output)
- ✅ HTTP client (sends to SwisperStudio)
- ✅ Context management (trace/observation nesting)
- ✅ Error handling (graceful degradation)

**Status:** ✅ **Working but INCOMPLETE**

---

## ❌ Critical Gaps (What's Missing)

### **Gap 1: LLM Call Tracking** ❌ CRITICAL

**What we NEED (from mock data):**
```json
{
  "type": "GENERATION",
  "input": {
    "prompt": "**ROLE**: You are an expert...",
    "messages": [
      {"role": "system", "content": "..."},
      {"role": "user", "content": "..."}
    ]
  },
  "model": "kvant-72b",
  "model_parameters": {
    "temperature": 0.3,
    "max_tokens": 500,
    "top_p": 1.0
  },
  "prompt_tokens": 280,
  "completion_tokens": 65
}
```

**What SDK currently captures:**
```json
{
  "type": "SPAN",  // ❌ Wrong type (should be GENERATION)
  "input": {"user_message": "..."},  // ❌ No prompt
  "model": null,  // ❌ Missing
  "model_parameters": null,  // ❌ Missing
  "prompt_tokens": null,  // ❌ Missing
  "completion_tokens": null  // ❌ Missing
}
```

**Impact:** Cannot see prompts or LLM details in SwisperStudio

**Planned Solution (Phase 2.5):**
```python
# LLM wrapper to auto-capture
from swisper_studio_sdk import wrap_llm

llm = wrap_llm(ChatOpenAI(model="gpt-4-turbo"))
# Automatically creates GENERATION observation with full details
```

---

### **Gap 2: Tool Call Tracking** ❌ CRITICAL

**What we NEED (from mock data):**
```json
{
  "type": "TOOL",
  "input": {
    "tool_call": {
      "function": "search_calendar_events",
      "arguments": {
        "attendee_email": "sarah.johnson@company.com",
        "start_time": "2025-11-03T14:30:00Z",
        "max_results": 5
      }
    }
  },
  "output": {
    "calendar_results": [...],
    "tool_response": {
      "status": "success",
      "events_found": 2
    }
  }
}
```

**What SDK currently captures:**
```json
{
  "type": "SPAN",  // ❌ Wrong type (should be TOOL)
  "input": {"state": "..."},  // ❌ No tool_call structure
  "output": {"state": "..."}  // ❌ No tool_response metadata
}
```

**Impact:** Cannot see tool calls or arguments in SwisperStudio

**Planned Solution (Phase 2.5):**
```python
# Tool wrapper to auto-capture
from swisper_studio_sdk import wrap_tool

search_calendar = wrap_tool(search_calendar_events)
# Automatically creates TOOL observation with arguments/response
```

---

### **Gap 3: Prompt Extraction** ❌ IMPORTANT

**What we NEED:**
- Full prompt text (for GENERATION nodes)
- System message, user message, assistant message
- Structured format for display

**What SDK currently does:**
- Only captures state (TypedDict)
- No prompt extraction from LLM calls

**Where prompts come from in Swisper:**
```python
# In Swisper's intent_classification_node:
system_prompt = build_intent_classification_prompt(...)  # From .md file
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_message}
]
result = await llm_adapter.get_structured_output(messages=messages, ...)
```

**SDK needs to intercept:**
- The `messages` array
- The `system_prompt` text
- Store in `observation.input.prompt` and `observation.input.messages`

---

### **Gap 4: Model Metadata** ❌ IMPORTANT

**What we NEED:**
```json
{
  "model": "kvant-72b",
  "model_parameters": {
    "temperature": 0.3,
    "max_tokens": 500,
    "top_p": 1.0
  }
}
```

**What SDK currently captures:**
- None - all null

**Where this comes from in Swisper:**
```python
# Swisper's LLM adapter
await llm_adapter.get_structured_output(
    messages=messages,
    schema=OptimizedIntentResult,
    agent_type="intent_classification",  # ← Used to lookup config
    ...
)
```

**SDK needs:**
- Intercept LLM adapter calls
- Extract model name from config
- Extract temperature, max_tokens, etc.
- Store in observation

---

### **Gap 5: Token Counting** ❌ IMPORTANT

**What we NEED:**
```json
{
  "prompt_tokens": 280,
  "completion_tokens": 65,
  "total_tokens": 345
}
```

**What SDK currently captures:**
- All null

**Where this comes from:**
- LLM API response metadata
- OpenAI/Anthropic return token counts
- Need to intercept response

---

## 🔍 **Comparison: Mock Data vs SDK Capabilities**

| Feature | Mock Data | SDK Captures | Gap? |
|---------|-----------|--------------|------|
| **State (input)** | ✅ Complete GlobalSupervisorState | ✅ Basic state dict | ⚠️ Partial |
| **State (output)** | ✅ Complete with additions | ✅ Basic state dict | ⚠️ Partial |
| **LLM Prompts** | ✅ Full prompt text + messages | ❌ Not captured | ❌ **GAP** |
| **LLM Responses** | ✅ In output state | ✅ In output state | ✅ OK |
| **Model name** | ✅ "kvant-72b" | ❌ null | ❌ **GAP** |
| **Model parameters** | ✅ temp, max_tokens, top_p | ❌ null | ❌ **GAP** |
| **Prompt tokens** | ✅ 280 | ❌ null | ❌ **GAP** |
| **Completion tokens** | ✅ 65 | ❌ null | ❌ **GAP** |
| **Tool calls** | ✅ Function + arguments | ❌ Not structured | ❌ **GAP** |
| **Tool responses** | ✅ Results + metadata | ❌ Not structured | ❌ **GAP** |
| **Observation type** | ✅ GENERATION, TOOL, AGENT | ⚠️ Defaults to SPAN | ⚠️ **GAP** |
| **Error tracking** | ✅ level + status_message | ✅ Partial | ⚠️ Partial |
| **Nesting** | ✅ Parent-child | ✅ Parent-child | ✅ OK |

---

## 🎯 **What Works vs What Doesn't**

### ✅ **What WILL Work with Current SDK:**

**If we integrate today, we get:**
1. ✅ Traces appear in SwisperStudio
2. ✅ Observation tree structure (nesting)
3. ✅ State before/after (basic)
4. ✅ Duration metrics
5. ✅ Error tracking (if node fails)
6. ✅ State diff viewer will work

**This is 50% of the value!**

---

### ❌ **What WON'T Work with Current SDK:**

**Missing features:**
1. ❌ **No prompts visible** - Can't see what was sent to LLM
2. ❌ **No model metadata** - Don't know which model/temp used
3. ❌ **No token counts** - Can't calculate costs
4. ❌ **No tool call details** - Can't see arguments/responses
5. ❌ **Wrong observation types** - Everything is SPAN (not GENERATION/TOOL)

**This is the other 50% of the value!**

---

## 🚀 **Two Paths Forward**

### **Path A: Ship with Basic SDK Now** ⚡ (Quick)

**Pros:**
- ✅ Can start using SwisperStudio immediately
- ✅ See state transitions (the core value!)
- ✅ Validate architecture works
- ✅ Gather real usage feedback

**Cons:**
- ❌ Missing prompts (can't debug LLM behavior)
- ❌ No cost tracking
- ❌ No tool call visibility

**When to choose:**
- You want to validate quickly
- State transitions alone are valuable
- You'll enhance SDK later

**Duration:** 1-2 days to integrate

---

### **Path B: Complete SDK First** 🔧 (Complete)

**Implement missing features:**
1. **LLM Wrapper** (2 days)
   - Intercept `llm_adapter.get_structured_output()` calls
   - Extract prompts, model, parameters
   - Count tokens from response
   - Store in observation

2. **Tool Wrapper** (1 day)
   - Detect tool calls in Swisper
   - Capture arguments
   - Capture responses
   - Create TOOL observations

3. **Observation Type Detection** (1 day)
   - Auto-detect GENERATION (LLM calls)
   - Auto-detect TOOL (tool executions)
   - Auto-detect AGENT (agent nodes)

**Pros:**
- ✅ Complete observability from day 1
- ✅ All Phase 2.5 features work (prompts, tools, etc.)
- ✅ Matches our beautiful UI
- ✅ Production-ready

**Cons:**
- ⏰ Takes 4-5 more days
- 🔧 More complex integration

**When to choose:**
- You want complete observability
- Prompts/tokens are critical
- You have time for proper implementation

**Duration:** 4-5 days development + 1-2 days integration

---

## 💡 **My Recommendation**

### **Path C: Hybrid - Ship Basic + Enhance Incrementally** ⭐

**Phase 1 (1-2 days):**
1. ✅ Integrate basic SDK with Swisper NOW
2. ✅ Get state transitions working
3. ✅ Validate architecture
4. ✅ See real execution flow

**Phase 2 (4-5 days):**
5. ✅ Add LLM wrapper (prompts + tokens)
6. ✅ Add tool wrapper (arguments + responses)
7. ✅ Enhanced SDK deployed
8. ✅ Now see EVERYTHING

**Benefits:**
- ⚡ Quick validation (state transitions in 1 day)
- 🎯 Incremental value (each feature adds benefit)
- 📊 Real data guides development (see what's actually needed)
- 🔧 Lower risk (smaller changes, easier debugging)

---

## 📝 **Action Plan: Path C (Recommended)**

### **Sprint 1: Basic Integration (This Week)**

**Day 1:**
- [ ] Review SDK installation process
- [ ] Create installation guide for Swisper team
- [ ] Test SDK locally (create simple test script)

**Day 2:**
- [ ] Install SDK in Swisper backend
- [ ] Add `initialize_tracing()` to Swisper startup
- [ ] Wrap `global_supervisor` graph with `create_traced_graph()`
- [ ] Run test request
- [ ] **MILESTONE:** First real trace in SwisperStudio! 🎉

**Day 3:**
- [ ] Debug any issues
- [ ] Test with different message types
- [ ] Verify state transitions work
- [ ] Document findings

**Deliverable:** Basic tracing working (state only)

---

### **Sprint 2: SDK Enhancements (Next Week)**

**Day 4-5: LLM Wrapper**
- [ ] Create `wrap_llm_adapter()` function
- [ ] Intercept `get_structured_output()` calls
- [ ] Extract prompts from messages
- [ ] Extract model parameters
- [ ] Count tokens from response
- [ ] Update observations with LLM data

**Day 6: Tool Wrapper**
- [ ] Create tool call detection
- [ ] Wrap tool executions
- [ ] Capture arguments
- [ ] Capture responses
- [ ] Create TOOL observations

**Day 7: Observation Type Auto-Detection**
- [ ] Detect LLM calls → GENERATION type
- [ ] Detect tool calls → TOOL type
- [ ] Detect agents → AGENT type
- [ ] Default → SPAN type

**Day 8-9: Testing & Polish**
- [ ] End-to-end testing
- [ ] Fix any bugs
- [ ] Performance optimization
- [ ] Documentation

**Deliverable:** Complete SDK with all features

---

## 🏠 **Getting Our House in Order**

Before we integrate, let's verify SwisperStudio is ready:

### **SwisperStudio Readiness Checklist:**

**Backend:**
- ✅ All APIs working (88/88 tests passing)
- ✅ Accepts observations with all fields
- ✅ Cost calculation ready
- ✅ Tree building working
- ✅ Graph generation working

**Frontend:**
- ✅ Trace list working
- ✅ Trace detail with state diff ✨
- ✅ Prompts/responses rendering ✨
- ✅ Tool calls visible ✨
- ✅ Full width responsive layout ✨
- ✅ All Phase 2.5 features complete ✨

**SDK:**
- ✅ Basic tracing works
- ⚠️ LLM wrapper missing (Phase 2.5 enhancement)
- ⚠️ Tool wrapper missing (Phase 2.5 enhancement)
- ⚠️ Observation type detection basic

**Documentation:**
- ✅ API documented
- ✅ Architecture documented
- ✅ Phase 0-4 complete
- ✅ Phase 2.5 complete
- ⏸️ SDK enhancement plan needed

---

## 📋 **Decision Matrix**

| Approach | Time to First Trace | Complete Features | Risk | Recommendation |
|----------|-------------------|------------------|------|----------------|
| **Path A: Basic SDK** | 1-2 days | State only (50%) | Low | ⭐ If urgent |
| **Path B: Complete SDK** | 5-7 days | Everything (100%) | Medium | ⭐⭐ If time available |
| **Path C: Hybrid** | 1-2 days (basic)<br>+4-5 days (complete) | Incremental | Low | ⭐⭐⭐ **Best** |

---

## 🎯 **Recommendation for You**

Given where we are, I recommend:

### **This Week:**
1. ✅ **Complete Phase 2.5** ← DONE! ✨
2. ✅ **Review SDK** ← Doing now
3. 🔧 **Create SDK Enhancement Plan** ← Next step
4. 🚀 **Option: Quick basic integration OR wait for complete SDK**

### **Your Decision:**

**Option 1: Ship with Basic SDK Now** (1-2 days)
- Get state transitions immediately
- Enhance SDK later
- Lower risk, faster feedback

**Option 2: Complete SDK First** (4-5 days)
- Full observability from day 1
- Matches our beautiful UI
- Higher upfront investment

**Option 3: Defer SDK work, focus on other Phase 5** 
- Analytics dashboard
- User management
- Config comparison
- Keep SDK as manual instrumentation

---

## 📚 **Next Steps**

**If you want to proceed with SDK enhancement:**
1. I'll create detailed SDK enhancement plan
2. We implement LLM + Tool wrappers
3. We test with mock LLM calls
4. Then integrate with real Swisper

**If you want to ship basic SDK now:**
1. I'll create integration guide for Swisper
2. We install SDK in Swisper
3. We trace one agent
4. We see what works/what's missing
5. Then decide on enhancements

**What's your preference?** 🤔

---

**Summary:** Our house (SwisperStudio) is in EXCELLENT order! The SDK is functional but incomplete. We can ship basic tracing now, or spend 4-5 days completing the SDK for full observability.
