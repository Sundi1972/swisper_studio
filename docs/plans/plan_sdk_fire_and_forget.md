# SDK Fix: Fire-and-Forget HTTP Pattern

**Issue:** #5 from Swisper Integration Feedback  
**Priority:** 🔥 CRITICAL for Production  
**Effort:** 2-3 hours  
**Impact:** Removes 400-600ms latency from user responses

---

## Problem

**Current (Blocking):**
```python
obs_id = await client.create_observation(...)  # ⏳ Waits 50-80ms
result = await func(state)                     # User waits!
await client.end_observation(...)              # ⏳ Waits 20-50ms
return result                                  # Finally!
```

**Latency Impact:**
- 2 HTTP calls per node × 4-5 nodes = 8-10 HTTP calls
- Each call: 20-100ms
- **Total overhead: 400-600ms added to every request**
- User perceives slower responses

---

## Solution

**Fire-and-Forget Pattern:**
```python
obs_id = str(uuid.uuid4())  # Generate locally (instant)
asyncio.create_task(client.create_observation(...))  # Background
result = await func(state)  # No waiting! ✅
asyncio.create_task(client.end_observation(...))  # Background
return result  # Instant!
```

**Latency Impact:**
- User sees **zero added latency**
- HTTP calls happen in background
- Observations eventually consistent

---

## Implementation

### Changes Required:

**1. Generate IDs Locally**
- Don't wait for server to return observation ID
- Use `uuid.uuid4()` to generate client-side
- Server accepts pre-generated IDs

**2. Background Tasks**
- Use `asyncio.create_task()` for HTTP calls
- Don't await the tasks
- Silent failures (log but don't crash)

**3. API Support**
- Modify observation creation endpoint to accept `id` in request body
- Already supported! Just need to pass it

---

## Files to Modify:

1. `sdk/swisper_studio_sdk/tracing/decorator.py` - Fire-and-forget in @traced
2. `sdk/swisper_studio_sdk/tracing/graph_wrapper.py` - Fire-and-forget for parent obs
3. `sdk/swisper_studio_sdk/tracing/client.py` - Accept pre-generated IDs

---

## Success Criteria:

- ✅ Zero user-facing latency (< 10ms overhead)
- ✅ Observations still created (eventually)
- ✅ No data loss
- ✅ Silent failures don't crash app
- ✅ Proper error logging

---

**Ready to implement!**

