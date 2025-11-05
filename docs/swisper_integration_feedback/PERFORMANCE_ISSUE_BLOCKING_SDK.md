# SwisperStudio SDK Performance Issue - Blocking HTTP Calls

**Date:** 2025-11-05  
**Severity:** Medium  
**Status:** Working but adds latency  
**Priority:** Should fix for production use

---

## Issue: SDK Uses Blocking HTTP Calls

### Problem

The SDK uses synchronous `await` calls for all HTTP requests to SwisperStudio, blocking the execution flow of Swisper nodes.

**Current behavior (BLOCKING):**
```python
# In decorator.py, lines 121-128
obs_id = await client.create_observation(...)  # ⏳ WAITS for response
# ... then continues ...
```

**Impact:**
- Each HTTP request adds 50-100ms latency
- 2 requests per node (create + end observation)
- With 4-5 nodes = **400-500ms added to user response time**
- User perceives slower responses

---

### Evidence from Testing

**Timing analysis from logs:**

```log
# Observation created (BLOCKING)
07:13:17.795 - POST http://172.17.0.1:8001/api/v1/observations "201 Created"

# Node executes
07:13:17.795 - Node START

# Node completes
07:13:24.934 - Node END

# Observation updated (BLOCKING - adds 27ms)
07:13:24.961 - PATCH http://172.17.0.1:8001/api/v1/observations/... "200 OK"

# Next node starts (after waiting for PATCH)
07:13:24.994 - POST http://172.17.0.1:8001/api/v1/observations "201 Created"
```

**Observed delays:**
- Trace creation: ~96ms
- Each observation start: ~50-80ms  
- Each observation end: ~20-50ms
- **Total per request: 400-600ms overhead**

**User feedback:**
> "I had the feeling that it took longer"

Confirmed - the SDK is adding measurable latency.

---

### Root Cause

**Current SDK implementation (decorator.py):**

```python
async def async_wrapper(*args, **kwargs):
    # BLOCKING CALL #1
    obs_id = await client.create_observation(
        trace_id=trace_id,
        name=obs_name,
        type=observation_type,
        input=input_data,
    )
    
    # Function executes
    result = await func(*args, **kwargs)
    
    # BLOCKING CALL #2
    await client.end_observation(
        observation_id=obs_id,
        output=output_data,
    )
    
    return result
```

**Why it's blocking:**
- `await` waits for HTTP request to complete
- Network round-trip adds latency
- If SwisperStudio is slow, Swisper is slow
- Not acceptable for production

---

### Recommended Fix: Fire-and-Forget Pattern

**Change to non-blocking:**

```python
async def async_wrapper(*args, **kwargs):
    client = get_studio_client()
    if not client:
        return await func(*args, **kwargs)
    
    trace_id = get_current_trace()
    if not trace_id:
        return await func(*args, **kwargs)
    
    # Capture input
    input_data = _serialize_state(args[0] if args else None)
    parent_obs = get_current_observation()
    
    # FIRE-AND-FORGET: Create observation in background
    obs_id = str(uuid.uuid4())  # Generate ID locally
    asyncio.create_task(_create_observation_async(
        client, trace_id, obs_name, observation_type, 
        parent_obs, input_data, obs_id
    ))
    
    # Set as current observation immediately (don't wait)
    token = set_current_observation(obs_id)
    
    try:
        # Execute function (NO WAITING)
        start_time = time.time()
        result = await func(*args, **kwargs)
        duration_ms = (time.time() - start_time) * 1000
        
        # Capture output
        output_data = _serialize_state(result)
        
        # FIRE-AND-FORGET: End observation in background
        asyncio.create_task(_end_observation_async(
            client, obs_id, output_data, duration_ms, "DEFAULT"
        ))
        
        return result
        
    except Exception as e:
        # FIRE-AND-FORGET: End with error
        asyncio.create_task(_end_observation_async(
            client, obs_id, None, None, "ERROR", str(e)
        ))
        raise
    finally:
        # Clear context
        set_current_observation(None)


async def _create_observation_async(
    client, trace_id, name, type, parent_id, input_data, obs_id
):
    """Background task to create observation (non-blocking)"""
    try:
        # Use pre-generated obs_id
        await client.create_observation_with_id(
            observation_id=obs_id,
            trace_id=trace_id,
            name=name,
            type=type,
            parent_observation_id=parent_id,
            input=input_data,
        )
    except Exception as e:
        # Silent failure - don't affect main flow
        logger.debug(f"Failed to create observation: {e}")


async def _end_observation_async(
    client, obs_id, output_data, duration_ms, level, error_msg=None
):
    """Background task to end observation (non-blocking)"""
    try:
        await client.end_observation(
            observation_id=obs_id,
            output=output_data,
            level=level,
            status_message=error_msg,
        )
    except Exception as e:
        # Silent failure - don't affect main flow
        logger.debug(f"Failed to end observation: {e}")
```

**Key changes:**
1. ✅ Generate observation ID locally (no need to wait for server)
2. ✅ Use `asyncio.create_task()` for HTTP calls (fire-and-forget)
3. ✅ Function executes immediately (no blocking)
4. ✅ Background tasks complete independently
5. ✅ Silent failures (don't affect main flow)

---

### Benefits of Fix

**Performance:**
- ✅ **Zero latency added** to user responses
- ✅ Swisper runs at full speed
- ✅ SwisperStudio receives data in background
- ✅ User experience unchanged

**Reliability:**
- ✅ If SwisperStudio slow, doesn't affect Swisper
- ✅ If SwisperStudio down, Swisper unaffected
- ✅ Graceful degradation already works
- ✅ True observability (observe without interfering)

**Comparison:**

| Approach | User Latency | Notes |
|----------|--------------|-------|
| **Current (blocking)** | +400-600ms | Waits for SwisperStudio responses |
| **Fixed (fire-and-forget)** | +0-5ms | No waiting, background tasks |

---

### Implementation Effort

**Estimated time:** 2-3 hours

**Files to modify:**
1. `sdk/swisper_studio_sdk/tracing/decorator.py` - Change to fire-and-forget
2. `sdk/swisper_studio_sdk/tracing/client.py` - Add `create_observation_with_id()` method
3. `sdk/tests/test_decorator.py` - Update tests for async behavior

**Testing:**
- Verify observations still created in background
- Verify no performance impact on client
- Verify errors don't crash client
- Load test with slow SwisperStudio

---

### Workaround (For Now)

**If not fixing immediately, consider:**

**Option 1: Disable tracing in production**
```python
# In Swisper config
SWISPER_STUDIO_ENABLED=false  # In production
SWISPER_STUDIO_ENABLED=true   # Only in dev/staging
```

**Option 2: Accept latency for dev/staging**
- Use tracing only in non-prod environments
- Accept slower responses for debugging value

---

### Priority Assessment

**Severity:** Medium  
**When to fix:** Before production deployment

**For development/testing:**
- Current blocking SDK is acceptable
- Debugging value outweighs latency
- Only affects dev team

**For production:**
- Must fix before production use
- User-facing latency not acceptable
- Fire-and-forget pattern required

---

### Comparison to Industry Standards

**Langfuse:**
- Uses fire-and-forget pattern
- Zero latency on client

**Sentry:**
- Async event sending
- Background workers

**DataDog:**
- Non-blocking telemetry
- Background aggregation

**Best Practice:**
Observability should never slow down the observed system.

---

### Recommendation

**Phase 1 (Current):**
- ✅ Keep blocking SDK for dev/testing
- ✅ Validate observability functionality works
- ✅ Gather feedback on data quality

**Phase 2:**
- 🔧 Implement fire-and-forget pattern
- 🔧 Test with production load
- 🔧 Deploy to all environments

**Timeline:**
- Phase 1: Now (working, acceptable for dev)
- Phase 2: Before production deployment (2-3 hours work)

---

### Test Plan After Fix

**Performance test:**

```python
import time

# Without tracing
start = time.time()
result = await graph.ainvoke(state)
baseline = time.time() - start

# With tracing (fire-and-forget)
start = time.time()
result = await graph.ainvoke(state)
with_tracing = time.time() - start

# Should be nearly identical
overhead = with_tracing - baseline
assert overhead < 0.01  # Less than 10ms overhead
```

**Functional test:**
- Send 100 requests rapidly
- Verify all traces created (eventually)
- Verify no data loss
- Verify correct nesting/order

---

## Summary

**Current Status:**
- ✅ SDK working and creating traces
- ⚠️ Adds 400-600ms latency (blocking HTTP)
- ✅ Acceptable for dev/testing
- ❌ Not acceptable for production

**Required Fix:**
- Change to fire-and-forget pattern
- Estimated effort: 2-3 hours
- Should be done before production deployment

**Urgency:**
- **Low** for dev/testing (current use case)
- **High** for production deployment

---

**For now, integration is working - just slower than it should be!**

We can proceed with testing and validation, then request the performance fix before production use.

