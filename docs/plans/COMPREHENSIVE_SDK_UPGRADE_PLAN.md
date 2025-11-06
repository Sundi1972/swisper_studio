# Comprehensive SDK Upgrade Plan - Redis Streams + LLM Reasoning + Connection Status

**Date:** 2025-11-06  
**Version:** 2.0  
**Status:** STRATEGIC DECISION REQUIRED  
**Estimated Time:** 4-5 days (vs 5-6 days if done separately)

---

## 🎯 Executive Summary

**Strategic Question:** Should we migrate to Redis Streams NOW (while implementing LLM reasoning)?

**Answer:** **YES!** Combine three initiatives into one coordinated upgrade:

1. ✅ **Redis Streams migration** (Performance: 500ms → 10ms)
2. ✅ **LLM reasoning capture** (Feature: See thinking process)
3. ✅ **Connection status** (UX: Know if connected)

**Why together is better:**
- **Faster overall:** 4-5 days vs 5-6 days separately
- **One breaking change:** SDK v0.3.4 → v0.4.0 (one migration for users)
- **Better architecture:** Build reasoning on Redis (simpler than HTTP)
- **Testing efficiency:** Test all features together

---

## 📊 Comparison: Incremental vs Combined Approach

| Approach | Timeline | User Impact | Architecture Quality |
|----------|----------|-------------|---------------------|
| **Incremental** (HTTP → Features → Redis) | 5-6 days | 2 migrations | Medium (technical debt) |
| **Combined** (Redis + Features) | 4-5 days | 1 migration | High (production-ready) |

**Recommendation:** ✅ **Combined approach** (Redis Streams + LLM Reasoning + Connection Status)

---

## 🏗️ Architecture Overview

### Current (SDK v0.3.4)
```
Swisper → HTTP POST/PATCH → SwisperStudio
          └─ 400-600ms latency
          └─ Race conditions (retry logic)
          └─ No connection status
```

### Proposed (SDK v0.4.0)
```
Swisper → Redis XADD → Redis Stream → Consumer → SwisperStudio DB
          └─ 1-2ms latency (250x faster!)
          └─ No race conditions (ordered delivery)
          └─ Connection status via heartbeat
          └─ LLM reasoning in event data
```

---

## 📋 Feature Breakdown

### Feature 1: Redis Streams Migration

**What:**
- Replace HTTP calls with Redis XADD
- Add consumer service in SwisperStudio
- Event-based architecture

**Why:**
- ✅ **250x faster** (500ms → 2ms)
- ✅ **No race conditions** (ordered stream)
- ✅ **Better reliability** (persistent queue)
- ✅ **Scalable** (100k events/sec)

**Effort:** 3 days

---

### Feature 2: LLM Reasoning Capture

**What:**
- Capture reasoning chunks (`<think>...</think>`)
- Capture streaming responses (user_interface)
- **Node-level configuration** (enable/disable per node)
- Store in observation output

**Why:**
- ✅ See LLM thinking process
- ✅ Debug decisions
- ✅ 100% LLM coverage

**Configuration:**
```python
# Global default
SWISPER_STUDIO_CAPTURE_REASONING: bool = True
SWISPER_STUDIO_REASONING_MAX_LENGTH: int = 50000  # 50 KB

# Per-node override
@traced("classify_intent", capture_reasoning=True, max_reasoning_length=10000)
async def classify_intent_node(state):
    ...

@traced("memory_node", capture_reasoning=False)  # Disable for this node
async def memory_node(state):
    ...
```

**With Redis Streams:** Simpler than HTTP!
```python
# Just add reasoning to event data
await publish_event(
    event_type="observation_end",
    data={
        "output": {...},
        "_llm_reasoning": reasoning_text,  # ← Added!
        "_llm_result": result
    }
)
```

**Effort:** 1 day (with Redis) vs 2 days (with HTTP)

---

### Feature 3: Connection Status

**What:**
- SDK checks consumer heartbeat
- Consumer writes heartbeat to Redis
- UI shows live connection status

**Why:**
- ✅ Know if observability working
- ✅ Immediate feedback on startup
- ✅ Operational visibility

**With Redis Streams (Simpler!):**
```python
# SDK checks heartbeat (reads from Redis)
async def verify_connectivity():
    heartbeat = await redis.get("swisper_studio:consumer:heartbeat")
    if heartbeat:
        hb_data = json.loads(heartbeat)
        age = (datetime.utcnow() - datetime.fromisoformat(hb_data["timestamp"])).total_seconds()
        return age < 10  # Consumer alive if <10s old
    return False

# Consumer writes heartbeat (every 5s)
async def _heartbeat_worker():
    while running:
        await redis.setex(
            "swisper_studio:consumer:heartbeat",
            15,  # Expire in 15s
            json.dumps({
                "timestamp": datetime.utcnow().isoformat(),
                "status": "healthy",
                "events_processed": counter,
            })
        )
        await asyncio.sleep(5)
```

**Benefits over HTTP heartbeat:**
- ✅ No separate HTTP endpoint needed
- ✅ Reuses existing Redis connection
- ✅ <1ms latency (vs 50ms HTTP)
- ✅ Simpler implementation

**Effort:** 0.5 days (with Redis) vs 1 day (with HTTP)

---

## 🎨 UX Design with All Features

### Startup Logs (Swisper)
```log
✅ SwisperStudio Redis publisher initialized
   Redis: redis://redis:6379
   Stream: observability:events
   ✅ Redis connectivity: OK
   ✅ Consumer detected: HEALTHY
   ✅ LLM reasoning capture: ENABLED
   ✅ Max reasoning length: 50 KB
   ✅ End-to-end verified: WORKING
```

### Frontend Display (SwisperStudio)
```
classify_intent (LLM) 🧠 ⚡ 1.2s | 450 tokens
  [✨ Response]  [Details ▼]
     └─ Prompt (System + User messages)
     └─ Reasoning (2,543 chars) 🧠 ← Only shows if captured
     └─ Metadata (Model, tokens, duration)

Project Status:
● Swisper Production - Connected ✅
  Last seen: 5 seconds ago
  Events in queue: 0
  LLM reasoning: Enabled
```

---

## 🔧 Implementation Plan

### Phase 1: Redis Streams Migration (Day 1-3)

**Day 1: SDK Publisher**
- [ ] Add `redis_publisher.py`
- [ ] Update `decorator.py` to use Redis
- [ ] Update `graph_wrapper.py` to use Redis
- [ ] Add initialization with connectivity check
- [ ] Tests

**Day 2: SwisperStudio Consumer**
- [ ] Add `observability_consumer.py`
- [ ] Add consumer startup in `main.py`
- [ ] Add heartbeat worker
- [ ] Tests

**Day 3: Integration & Testing**
- [ ] End-to-end test (Swisper → Redis → Consumer → DB)
- [ ] Performance testing (verify <10ms overhead)
- [ ] Connection status verification
- [ ] Deployment to Swisper

---

### Phase 2: LLM Reasoning Capture (Day 4)

**Morning: SDK Changes**
- [ ] Add reasoning accumulator to `llm_wrapper.py`
- [ ] Add per-node configuration
- [ ] Implement 50 KB truncation
- [ ] Add streaming response capture
- [ ] Tests

**Afternoon: Frontend Changes**
- [ ] Add `ReasoningViewer` component
- [ ] Update observation detail view
- [ ] Conditional rendering (only if reasoning exists)
- [ ] Tests

---

### Phase 3: Polish & Documentation (Day 5)

**Morning: UX Polish**
- [ ] Connection status in Project Settings
- [ ] Live status indicators
- [ ] Error handling and edge cases
- [ ] Performance optimization

**Afternoon: Documentation**
- [ ] Update SDK README
- [ ] Migration guide (v0.3.4 → v0.4.0)
- [ ] Configuration examples
- [ ] Troubleshooting guide

---

## 📊 Per-Node Reasoning Configuration

### Design

**Three levels of control:**

1. **Global default** (config)
```python
# In Swisper's config
SWISPER_STUDIO_CAPTURE_REASONING: bool = True
SWISPER_STUDIO_REASONING_MAX_LENGTH: int = 50000
```

2. **Graph-level** (initialization)
```python
graph = create_traced_graph(
    GlobalSupervisorState,
    trace_name="global_supervisor",
    capture_reasoning=True,  # Default for all nodes
    reasoning_max_length=50000
)
```

3. **Node-level** (decorator)
```python
# Enable for this specific node
@traced("classify_intent", capture_reasoning=True, reasoning_max_length=10000)
async def classify_intent_node(state):
    ...

# Disable for this specific node (override global)
@traced("memory_node", capture_reasoning=False)
async def memory_node(state):
    ...

# Use graph default (no override)
@traced("global_planner")
async def global_planner_node(state):
    ...
```

### Implementation

```python
# In decorator.py
def traced(
    name: str | None = None,
    observation_type: str = "AUTO",
    capture_reasoning: bool | None = None,  # None = use graph default
    reasoning_max_length: int | None = None,  # None = use graph default
):
    """
    Trace decorator with per-node reasoning control.
    
    Args:
        capture_reasoning: Enable/disable reasoning capture for this node
                          None = inherit from graph settings
        reasoning_max_length: Max reasoning characters (truncate if longer)
                             None = use global/graph default
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Determine reasoning settings
            should_capture = (
                capture_reasoning 
                if capture_reasoning is not None 
                else _get_graph_reasoning_setting()  # From graph config
            )
            
            max_length = (
                reasoning_max_length 
                if reasoning_max_length is not None 
                else _get_graph_max_length_setting()
            )
            
            # Store in context for llm_wrapper to use
            set_reasoning_config(should_capture, max_length)
            
            # ... rest of decorator logic
```

**Example Usage in Swisper:**

```python
# In global_supervisor.py

# Nodes that benefit from reasoning visibility
@traced("classify_intent", capture_reasoning=True, reasoning_max_length=20000)
async def classify_intent_wrapper(state):
    return await classify_intent_node(state, ...)

@traced("global_planner", capture_reasoning=True, reasoning_max_length=50000)
async def global_planner_wrapper(state):
    return await global_planner_node(state, ...)

# Nodes where reasoning is unnecessary/noisy
@traced("memory_node", capture_reasoning=False)  # Embeddings don't have reasoning
async def memory_node_wrapper(state):
    return await memory_node(state, ...)

@traced("user_in_the_loop_handler", capture_reasoning=False)  # No LLM
async def user_in_the_loop_handler(state):
    return await user_in_the_loop_handler_node(state)

# Nodes using graph default
@traced("agent_execution")  # Uses graph default (True)
async def agent_execution_wrapper(state):
    return await agent_execution_node(state, ...)
```

---

## 🔒 Data Schema (Redis Events)

### Event Structure

```python
# Event in Redis Stream
{
    "event_type": "observation_end",
    "trace_id": "abc-123",
    "observation_id": "def-456",
    "project_id": "0d7aa606...",
    "timestamp": "2025-11-06T...",
    "data": {
        "output": {
            // User's actual state/data
            "messages": [...],
            "intent": "calendar",
            
            // SDK metadata (underscore prefix)
            "_llm_messages": [...],      # Prompts
            "_llm_reasoning": "...",     # Reasoning (if enabled & captured)
            "_llm_result": {...},        # Final response
            "_llm_tokens": {...}
        },
        "level": "DEFAULT",
        "end_time": "2025-11-06T..."
    }
}
```

### Reasoning Field Rules

```python
# When to include _llm_reasoning:
if node_config.capture_reasoning and llm_reasoning_text:
    # Truncate if needed
    if len(llm_reasoning_text) > node_config.max_length:
        output["_llm_reasoning"] = (
            llm_reasoning_text[:node_config.max_length] +
            f"\n\n... [Truncated. Full length: {len(llm_reasoning_text)} chars]"
        )
    else:
        output["_llm_reasoning"] = llm_reasoning_text
# Otherwise: field not included (saves bandwidth)
```

---

## 📈 Performance Impact

### With Redis Streams + Reasoning

| Operation | Current (HTTP) | Proposed (Redis) | Improvement |
|-----------|----------------|------------------|-------------|
| Observation start | 50ms | 1ms | **50x faster** |
| Observation end (no reasoning) | 50ms | 1ms | **50x faster** |
| Observation end (with reasoning 10KB) | 60ms | 2ms | **30x faster** |
| Observation end (with reasoning 50KB) | 80ms | 3ms | **27x faster** |
| **5 nodes total** | 500ms | 10ms | **50x faster** |

**User experience:**
- Current: Noticeable slowdown ❌
- Proposed: Imperceptible ✅

---

## 🚦 Connection Status with Redis

### Architecture

```
┌─────────────────────────────────────────┐
│ SDK (Swisper)                           │
│                                         │
│ On startup:                             │
│ 1. Connect to Redis                     │
│ 2. Test write (XADD health_check)      │
│ 3. Read consumer heartbeat              │
│ 4. Verify heartbeat < 10s old           │
│ 5. Log status                           │
│                                         │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ Redis                                   │
│                                         │
│ Key: swisper_studio:consumer:heartbeat  │
│ Value: {                                │
│   "timestamp": "2025-11-06T...",       │
│   "status": "healthy",                  │
│   "events_processed": 12345,           │
│   "stream_length": 5                   │
│ }                                       │
│ TTL: 15 seconds                         │
│                                         │
└─────────────────────────────────────────┘
                 ↑
┌─────────────────────────────────────────┐
│ Consumer (SwisperStudio)                │
│                                         │
│ Background worker (every 5s):           │
│ - Update heartbeat key                  │
│ - Include status metrics                │
│ - Auto-expire after 15s                 │
│                                         │
└─────────────────────────────────────────┘
```

### Verification Flow

**SDK initialization:**
```python
async def initialize_redis_publisher(redis_url: str, ...):
    global _redis_client
    
    try:
        # Connect to Redis
        _redis_client = redis.from_url(redis_url)
        await _redis_client.ping()
        logger.info("✅ Redis connectivity: OK")
        
        # Test write
        await _redis_client.xadd(
            "observability:health_check",
            {"test": "ping", "timestamp": str(time.time())},
            maxlen=10
        )
        logger.info("✅ Redis write permission: OK")
        
        # Check consumer heartbeat
        heartbeat = await _redis_client.get("swisper_studio:consumer:heartbeat")
        if heartbeat:
            hb_data = json.loads(heartbeat)
            timestamp = datetime.fromisoformat(hb_data["timestamp"])
            age = (datetime.utcnow() - timestamp).total_seconds()
            
            if age < 10:
                logger.info(f"✅ Consumer detected: HEALTHY ({age:.1f}s ago)")
                logger.info(f"   Events processed: {hb_data.get('events_processed', 'N/A')}")
                logger.info(f"   Stream length: {hb_data.get('stream_length', 'N/A')}")
            else:
                logger.warning(f"⚠️ Consumer heartbeat stale ({age:.0f}s old)")
                logger.warning("   Consumer may be stopped or lagging")
        else:
            logger.warning("⚠️ Consumer not detected")
            logger.warning("   Events will queue until consumer starts")
        
        logger.info("✅ Redis publisher initialized successfully")
        
    except redis.ConnectionError:
        logger.error(f"❌ Cannot connect to Redis at {redis_url}")
        raise
    except Exception as e:
        logger.error(f"❌ Redis initialization failed: {e}")
        raise
```

**Consumer heartbeat worker:**
```python
async def _heartbeat_worker(self):
    """Write heartbeat every 5 seconds"""
    while self.running:
        try:
            # Get current stream length
            stream_length = await self.redis_client.xlen(self.stream_name)
            
            # Write heartbeat
            await self.redis_client.setex(
                "swisper_studio:consumer:heartbeat",
                15,  # Expire in 15 seconds
                json.dumps({
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "healthy",
                    "consumer_name": self.consumer_name,
                    "events_processed": self.events_processed_counter,
                    "stream_length": stream_length,
                })
            )
            
            await asyncio.sleep(5)  # Every 5 seconds
            
        except Exception as e:
            logger.warning(f"Failed to write heartbeat: {e}")
            await asyncio.sleep(5)
```

---

## 🎯 Migration Path (v0.3.4 → v0.4.0)

### Breaking Changes

**None!** (Backward compatible)

**Old code (still works):**
```python
# Swisper's current code
initialize_tracing(
    api_url="http://172.17.0.1:8001",
    api_key="dev-api-key",
    project_id="0d7aa606...",
)
# Still works, but uses HTTP (deprecated)
```

**New code (recommended):**
```python
# Swisper upgrades to Redis
await initialize_redis_publisher(
    redis_url="redis://redis:6379",
    stream_name="observability:events",
    project_id="0d7aa606...",
    verify_consumer=True,
    capture_reasoning=True,
    reasoning_max_length=50000,
)
```

### Migration Steps for Swisper

**Step 1: Update SDK**
```bash
pip uninstall swisper-studio-sdk -y
pip install swisper-studio-sdk==0.4.0
```

**Step 2: Update Configuration**
```python
# In backend/app/core/config.py

# OLD (remove these)
# SWISPER_STUDIO_URL: str = "http://172.17.0.1:8001"
# SWISPER_STUDIO_API_KEY: str = "dev-api-key"

# NEW (add these)
SWISPER_STUDIO_REDIS_URL: str = "redis://redis:6379"
SWISPER_STUDIO_STREAM_NAME: str = "observability:events"
SWISPER_STUDIO_PROJECT_ID: str = "0d7aa606-cb29-4a31-8a59-50fa61151a32"
SWISPER_STUDIO_CAPTURE_REASONING: bool = True
SWISPER_STUDIO_REASONING_MAX_LENGTH: int = 50000
```

**Step 3: Update Initialization**
```python
# In backend/app/main.py

# OLD (remove this)
# from swisper_studio_sdk import initialize_tracing
# initialize_tracing(...)

# NEW (add this)
from swisper_studio_sdk import initialize_redis_publisher

await initialize_redis_publisher(
    redis_url=settings.SWISPER_STUDIO_REDIS_URL,
    stream_name=settings.SWISPER_STUDIO_STREAM_NAME,
    project_id=settings.SWISPER_STUDIO_PROJECT_ID,
    verify_consumer=True,
    capture_reasoning=settings.SWISPER_STUDIO_CAPTURE_REASONING,
    reasoning_max_length=settings.SWISPER_STUDIO_REASONING_MAX_LENGTH,
)
logger.info("✅ SwisperStudio observability initialized (Redis Streams)")
```

**Step 4: Restart & Verify**
```bash
docker compose restart backend

# Check logs:
# ✅ Redis connectivity: OK
# ✅ Consumer detected: HEALTHY
# ✅ LLM reasoning capture: ENABLED
```

**Total migration time: 15 minutes**

---

## ✅ Success Criteria

### Performance
- [ ] Total overhead < 10ms (vs 500ms baseline)
- [ ] User response time unchanged
- [ ] Stream processing lag < 1 second
- [ ] Reasoning capture adds < 2ms overhead

### Functional
- [ ] All traces appear in UI
- [ ] All observations captured
- [ ] Reasoning visible for enabled nodes
- [ ] Reasoning hidden for disabled nodes
- [ ] Reasoning truncated at 50 KB
- [ ] Connection status shows correctly

### Reliability
- [ ] Zero data loss over 24 hours
- [ ] All events processed in order
- [ ] Consumer recovery on failure < 5 seconds
- [ ] No memory leaks from reasoning buffers

### UX
- [ ] Clear startup logs (connection status)
- [ ] Reasoning button only if data exists
- [ ] Reasoning renders correctly in UI
- [ ] Connection status updates within 10s
- [ ] No frontend performance issues

---

## 📅 Timeline Summary

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Phase 1: Redis Streams | 3 days | Publisher + Consumer working |
| Phase 2: LLM Reasoning | 1 day | Reasoning capture + UI |
| Phase 3: Polish & Docs | 1 day | Production-ready |
| **Total** | **5 days** | **SDK v0.4.0 released** |

---

## 💰 Cost-Benefit Analysis

### Benefits

**Performance:**
- ✅ 50x faster observability (500ms → 10ms)
- ✅ User experience improved (no noticeable lag)

**Features:**
- ✅ LLM reasoning visibility (debug decisions)
- ✅ Connection status (operational visibility)
- ✅ 100% LLM coverage (structured + streaming)

**Architecture:**
- ✅ Production-ready event system
- ✅ Scalable to 100k+ events/sec
- ✅ No more race conditions
- ✅ Better reliability (persistent queue)

### Costs

**Development:**
- 5 days implementation
- 1 day testing (included)
- 0.5 days migration support

**Infrastructure:**
- Reuses Swisper's existing Redis ✅
- No new infrastructure needed ✅

**Maintenance:**
- Lower (simpler than HTTP)
- Better error handling
- Easier debugging

---

## 🚨 Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Redis connection issues | Low | High | Graceful degradation, clear logging |
| Consumer lag under load | Low | Medium | Monitoring, alerts, batching |
| Reasoning memory leaks | Medium | Medium | Cleanup mechanism, LRU cache |
| Breaking existing setups | Low | High | Backward compatible, migration guide |
| Frontend performance (large reasoning) | Medium | Low | Lazy loading, virtualization |

---

## 🎯 Recommendation

### **GREEN LIGHT - Combined Approach** ✅

**Proceed with:**
1. ✅ Redis Streams migration
2. ✅ LLM reasoning capture (per-node config, 50KB limit)
3. ✅ Connection status (heartbeat-based)

**Timeline:** 5 days (Day 1-3: Redis, Day 4: Reasoning, Day 5: Polish)

**Versioning:** SDK v0.4.0 (minor bump for major feature)

**Migration:** Backward compatible, 15-minute upgrade path for Swisper

**ROI:**
- **High value:** 3 major features in one release
- **Lower risk:** Test all features together
- **Better architecture:** Production-ready from day 1
- **Faster:** 5 days vs 6 days separately

---

## 📝 Open Questions

1. **Persist reasoning to database?**
   - ✅ **YES** (per Q1) - Enables historical analysis

2. **Node-level configuration?**
   - ✅ **YES** (per Q2) - Per-node decorator parameters

3. **Reasoning length limit?**
   - ✅ **50 KB** (per Q3) - Truncate with indicator

4. **Redis instance?**
   - ✅ **Reuse Swisper's Redis** (simple, fast)

5. **Start date?**
   - **DECISION NEEDED:** Start immediately or after current SDK testing?

---

## 🎬 Next Steps

**If approved:**

**Day 0 (Today):**
- [ ] Get approval for combined approach
- [ ] Confirm timeline works for team
- [ ] Prepare development environment

**Day 1 (Tomorrow):**
- [ ] Start Phase 1 (Redis Streams SDK)
- [ ] Create branch: `feature/sdk-v0.4.0-redis-reasoning`

**Day 5 (End):**
- [ ] SDK v0.4.0 released
- [ ] Documentation complete
- [ ] Ready for Swisper migration

---

## 💬 Decision Required

**Options:**

**A) ✅ Proceed with Combined Approach** (Recommended)
- Timeline: 5 days
- Deliverables: Redis + Reasoning + Connection Status
- Version: SDK v0.4.0

**B) ❌ Incremental Approach** (Not recommended)
- Timeline: 6 days
- Deliverables: Same features, done separately
- Version: SDK v0.3.5, v0.3.6, v0.4.0

**C) ⏸️ Defer Redis, do Reasoning only**
- Timeline: 2 days
- Deliverables: Reasoning only (HTTP-based)
- Version: SDK v0.3.5

**Your call?** 🤔

---

**Author:** AI Assistant  
**Status:** AWAITING DECISION  
**Estimated Start:** Upon approval  
**Estimated Complete:** 5 days from start

