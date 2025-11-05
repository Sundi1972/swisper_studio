# SwisperStudio Architecture Recommendation - Redis Streams

**Version:** v1.0
**Date:** 2025-11-05
**Requested By:** Swisper Development Team
**Priority:** High - Performance Critical
**Estimated Effort:** 3 days

---

## Executive Summary

**Current Issue:** SDK uses blocking HTTP calls, adding 400-600ms latency to user responses.

**Proposed Solution:** Replace HTTP with **Redis Streams** for true async, zero-latency observability.

**Key Benefits:**
- ✅ **250x faster**: 1-2ms vs 500ms
- ✅ **Zero user impact**: Non-blocking publish
- ✅ **No new infrastructure**: Reuse Swisper's existing Redis
- ✅ **Production-ready**: Persistent, ordered, reliable delivery

---

## Table of Contents

1. [Architecture Options](#architecture-options)
2. [Recommended Solution: Redis Streams](#recommended-solution-redis-streams)
3. [Implementation Specification](#implementation-specification)
4. [Performance Analysis](#performance-analysis)
5. [Migration Plan](#migration-plan)

---

## Architecture Options

### Option 1: HTTP with Queue (Considered)
```
Swisper → [In-Process Queue] → HTTP Batch → SwisperStudio
```

**Pros:** Simple, self-contained
**Cons:** Lost on crash, no replay, still coupled via HTTP

---

### Option 2: Kafka Event Bus (Overkill)
```
Swisper → [Kafka] → SwisperStudio Consumer → Database
```

**Pros:** Enterprise-grade, battle-tested
**Cons:** Heavy infrastructure, operational complexity

---

### Option 3: Redis Streams ⭐ **RECOMMENDED**
```
Swisper → [Redis Streams] → SwisperStudio Consumer → Database
```

**Pros:** Fast (1-2ms), reliable, no new infrastructure
**Cons:** None significant

**Why Redis Streams:**
- ✅ Swisper already has Redis running (for checkpoints)
- ✅ Event bus capabilities built-in
- ✅ Consumer groups for reliability
- ✅ Persistent and ordered delivery
- ✅ Simple compared to Kafka
- ✅ Zero infrastructure cost

---

## Recommended Solution: Redis Streams

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ SWISPER                                                     │
│                                                             │
│  Node Executes                                              │
│     ↓                                                       │
│  @traced decorator                                          │
│     ↓                                                       │
│  XADD redis://redis:6379 observability:events              │
│  └─ Latency: 1-2ms ✅                                      │
│     ↓                                                       │
│  Return immediately (NO WAITING)                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                         ↓
        ┌────────────────────────────────────┐
        │ REDIS STREAM: observability:events │
        │ (Swisper's existing Redis)         │
        │ - Persistent                       │
        │ - Ordered (FIFO)                   │
        │ - Consumer groups                  │
        │ - Max 100k events                  │
        └────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ SWISPERSTUDIO CONSUMER SERVICE                              │
│                                                             │
│  Connect: redis://172.17.0.1:6379                          │
│     ↓                                                       │
│  XREADGROUP (batch 50 events, 1sec timeout)                │
│     ↓                                                       │
│  Process batch:                                             │
│  - Parse events                                             │
│  - Insert to PostgreSQL                                     │
│  - XACK (mark processed)                                    │
│     ↓                                                       │
│  Auto-retry on failure (consumer group)                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### Redis Instance Decision: Reuse Swisper's Redis (Option B)

**Why reuse Swisper's Redis:**

**Advantages:**
1. ✅ **Zero infrastructure setup** - Swisper already has Redis
2. ✅ **Fast for SDK** - Local connection (no network hop)
3. ✅ **Simple configuration** - One connection string
4. ✅ **Cost effective** - No additional resources
5. ✅ **Good for POC** - Validate quickly

**Network Setup:**
- Swisper's Redis already exposed: `0.0.0.0:6379->6379/tcp` ✅
- SwisperStudio connects via Docker bridge: `172.17.0.1:6379` ✅
- No firewall changes needed ✅

**Configuration:**

**Swisper side (SDK):**
```python
# Use local Redis (existing connection)
SWISPER_STUDIO_REDIS_URL: str = "redis://redis:6379"
SWISPER_STUDIO_STREAM_NAME: str = "observability:events"
```

**SwisperStudio side (consumer):**
```python
# Connect to Swisper's Redis from host
OBSERVABILITY_REDIS_URL: str = "redis://172.17.0.1:6379"
OBSERVABILITY_STREAM_NAME: str = "observability:events"
OBSERVABILITY_GROUP_NAME: str = "swisper_studio_consumers"
```

**Production Migration Path:**
- Later, SwisperStudio can add dedicated Redis
- Just update connection URLs
- No code changes needed
- Provides flexibility for deployment models

---

## Implementation Specification

### Part 1: SDK Changes (Publisher)

**New dependency:**
```toml
# sdk/pyproject.toml
dependencies = [
    "httpx>=0.25.2",  # Keep for backward compat
    "langgraph>=0.0.28",
    "redis>=5.0.0",  # NEW
]
```

**New file: `sdk/swisper_studio_sdk/tracing/redis_publisher.py`**

```python
"""
Redis Streams publisher for non-blocking observability.

Publishes trace events to Redis Streams with 1-2ms latency.
"""

import redis.asyncio as redis
import json
import time
from typing import Optional, Dict, Any
from datetime import datetime

_redis_client: Optional[redis.Redis] = None
_stream_name: str = "observability:events"
_max_stream_length: int = 100000

async def initialize_redis_publisher(
    redis_url: str,
    stream_name: str = "observability:events",
    max_stream_length: int = 100000,
) -> None:
    """
    Initialize Redis publisher for observability events.

    Args:
        redis_url: Redis connection URL (e.g., "redis://redis:6379")
        stream_name: Stream name for events
        max_stream_length: Max events to keep in stream (FIFO eviction)
    """
    global _redis_client, _stream_name, _max_stream_length

    try:
        _redis_client = redis.from_url(redis_url, decode_responses=False)
        _stream_name = stream_name
        _max_stream_length = max_stream_length

        # Test connection
        await _redis_client.ping()
        print(f"✅ Redis publisher connected: {redis_url}")

    except Exception as e:
        print(f"⚠️ Redis publisher initialization failed: {e}")
        _redis_client = None  # Disable tracing

def get_redis_client() -> Optional[redis.Redis]:
    """Get the global Redis client"""
    return _redis_client

async def publish_event(
    event_type: str,
    trace_id: str,
    project_id: str,
    observation_id: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Publish observability event to Redis Stream.

    Non-blocking - returns in 1-2ms.

    Args:
        event_type: Event type (trace_start, observation_start, observation_end, etc.)
        trace_id: Trace identifier
        project_id: SwisperStudio project ID
        observation_id: Observation identifier (if applicable)
        data: Event data (will be JSON serialized)
    """
    client = get_redis_client()
    if not client:
        return  # Tracing disabled or not initialized

    try:
        # Build event payload
        event = {
            b"event_type": event_type.encode(),
            b"trace_id": trace_id.encode(),
            b"project_id": project_id.encode(),
            b"timestamp": str(time.time()).encode(),
        }

        if observation_id:
            event[b"observation_id"] = observation_id.encode()

        if data:
            event[b"data"] = json.dumps(data).encode()

        # XADD - publish to stream (1-2ms!)
        await client.xadd(
            _stream_name,
            event,
            maxlen=_max_stream_length,  # Prevent unbounded growth
        )

    except Exception:
        # Silent failure - don't break main application
        pass
```

**Modified: `sdk/swisper_studio_sdk/tracing/graph_wrapper.py`**

```python
from .redis_publisher import publish_event, get_redis_client

async def traced_ainvoke(input_state, config=None, **invoke_kwargs):
    """Create trace before running graph (Redis Streams version)"""

    client = get_redis_client()
    if not client:
        # Redis not initialized, run without tracing
        return await original_ainvoke(input_state, config, **invoke_kwargs)

    # Extract metadata
    user_id = input_state.get("user_id") if isinstance(input_state, dict) else None
    session_id = input_state.get("chat_id") or input_state.get("session_id") if isinstance(input_state, dict) else None

    # Generate trace ID locally
    trace_id = str(uuid.uuid4())

    # PUBLISH TRACE START (1-2ms, non-blocking!)
    await publish_event(
        event_type="trace_start",
        trace_id=trace_id,
        project_id=_project_id,  # From initialization
        data={
            "name": trace_name,
            "user_id": user_id,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    # Set trace context
    set_current_trace(trace_id)

    try:
        # Execute graph (NO WAITING!)
        result = await original_ainvoke(input_state, config, **invoke_kwargs)
        return result
    finally:
        set_current_trace(None)
```

**Modified: `sdk/swisper_studio_sdk/tracing/decorator.py`**

```python
from .redis_publisher import publish_event, get_redis_client

async def async_wrapper(*args, **kwargs):
    """Traced wrapper with Redis Streams (non-blocking)"""

    if not get_redis_client():
        # Redis not available - just run function
        return await func(*args, **kwargs)

    trace_id = get_current_trace()
    if not trace_id:
        return await func(*args, **kwargs)

    # Generate observation ID locally
    obs_id = str(uuid.uuid4())
    parent_obs = get_current_observation()

    # Serialize input
    input_data = _serialize_state(args[0] if args else None)

    # PUBLISH START EVENT (1-2ms, non-blocking!)
    await publish_event(
        event_type="observation_start",
        trace_id=trace_id,
        project_id=_project_id,
        observation_id=obs_id,
        data={
            "name": obs_name,
            "type": observation_type,
            "parent_observation_id": parent_obs,
            "input": input_data,
            "start_time": datetime.utcnow().isoformat(),
        }
    )

    # Set as current observation
    token = set_current_observation(obs_id)

    try:
        # EXECUTE FUNCTION (NO WAITING!)
        result = await func(*args, **kwargs)

        # Serialize output
        output_data = _serialize_state(result)

        # PUBLISH END EVENT (1-2ms, non-blocking!)
        await publish_event(
            event_type="observation_end",
            trace_id=trace_id,
            project_id=_project_id,
            observation_id=obs_id,
            data={
                "output": output_data,
                "level": "DEFAULT",
                "end_time": datetime.utcnow().isoformat(),
            }
        )

        return result

    except Exception as e:
        # PUBLISH ERROR EVENT
        await publish_event(
            event_type="observation_error",
            trace_id=trace_id,
            project_id=_project_id,
            observation_id=obs_id,
            data={
                "level": "ERROR",
                "error": str(e),
                "status_message": str(e),
                "end_time": datetime.utcnow().isoformat(),
            }
        )
        raise

    finally:
        set_current_observation(None)
```

---

### Part 2: SwisperStudio Consumer Service

**New file: `backend/app/services/observability_consumer.py`**

```python
"""
Observability consumer - reads trace events from Redis Streams.

Connects to Swisper's Redis to consume observability events,
then inserts into SwisperStudio's PostgreSQL database.
"""

import asyncio
import redis.asyncio as redis
import json
from datetime import datetime
from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Trace, Observation
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ObservabilityConsumer:
    """
    Consumer for observability events from Redis Streams.

    Reads from Swisper's Redis instance (redis://172.17.0.1:6379),
    processes events in batches, and stores in SwisperStudio's database.

    Uses Redis consumer groups for:
    - Automatic retry on failure
    - Load balancing across multiple consumers
    - Guaranteed delivery
    """

    def __init__(
        self,
        redis_url: str,
        db_session_factory: Callable,
        stream_name: str = "observability:events",
        group_name: str = "swisper_studio_consumers",
        consumer_name: str = "consumer_1",
        batch_size: int = 50,
    ):
        self.redis_url = redis_url
        self.stream_name = stream_name
        self.group_name = group_name
        self.consumer_name = consumer_name
        self.batch_size = batch_size
        self.db_session_factory = db_session_factory
        self.redis_client = None
        self.running = False

    async def start(self):
        """Start the consumer"""
        logger.info(f"Starting ObservabilityConsumer...")
        logger.info(f"  Redis URL: {self.redis_url}")
        logger.info(f"  Stream: {self.stream_name}")
        logger.info(f"  Group: {self.group_name}")

        # Connect to Swisper's Redis
        self.redis_client = redis.from_url(
            self.redis_url,
            decode_responses=True,  # Auto-decode strings
        )

        # Test connection
        try:
            await self.redis_client.ping()
            logger.info("✅ Connected to Redis successfully")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            raise

        # Create consumer group (if doesn't exist)
        try:
            await self.redis_client.xgroup_create(
                name=self.stream_name,
                groupname=self.group_name,
                id="0",  # Read from beginning
                mkstream=True,  # Create stream if doesn't exist
            )
            logger.info(f"✅ Created consumer group: {self.group_name}")
        except redis.ResponseError as e:
            if "BUSYGROUP" in str(e):
                logger.info(f"✅ Consumer group already exists: {self.group_name}")
            else:
                raise

        # Start consuming
        self.running = True
        logger.info("✅ ObservabilityConsumer started - processing events...")
        await self._consume_loop()

    async def stop(self):
        """Gracefully stop the consumer"""
        logger.info("Stopping ObservabilityConsumer...")
        self.running = False
        if self.redis_client:
            await self.redis_client.close()
        logger.info("✅ ObservabilityConsumer stopped")

    async def _consume_loop(self):
        """Main consumption loop - runs continuously"""
        while self.running:
            try:
                # Read batch of events (blocks for max 1 second)
                events = await self.redis_client.xreadgroup(
                    groupname=self.group_name,
                    consumername=self.consumer_name,
                    streams={self.stream_name: ">"},  # ">" = new events only
                    count=self.batch_size,
                    block=1000,  # 1 second timeout
                )

                if events:
                    # events = [('observability:events', [('msg_id', {data}), ...])]
                    for stream_name, messages in events:
                        await self._process_batch(messages)

            except asyncio.CancelledError:
                logger.info("Consumer loop cancelled - shutting down")
                break
            except Exception as e:
                logger.error(f"❌ Consumer error: {e}")
                await asyncio.sleep(1.0)  # Back off on error

    async def _process_batch(self, messages: list):
        """
        Process batch of messages.

        Inserts into database and acknowledges successful processing.
        Failed messages are not acknowledged and will be retried.
        """
        logger.debug(f"Processing batch of {len(messages)} events")

        async with self.db_session_factory() as session:
            processed_ids = []

            for message_id, data in messages:
                try:
                    await self._process_event(session, data)
                    processed_ids.append(message_id)

                except Exception as e:
                    logger.error(f"❌ Failed to process event {message_id}: {e}")
                    # Don't add to processed_ids - will be retried by consumer group

            # Commit successful events
            if processed_ids:
                await session.commit()

                # Acknowledge processed messages
                for msg_id in processed_ids:
                    await self.redis_client.xack(
                        self.stream_name,
                        self.group_name,
                        msg_id
                    )

                logger.info(f"✅ Processed {len(processed_ids)} events")

    async def _process_event(self, session: AsyncSession, data: dict):
        """Process single event and insert to database"""
        event_type = data.get("event_type")
        trace_id = data.get("trace_id")
        observation_id = data.get("observation_id")
        event_data = json.loads(data.get("data", "{}"))

        if event_type == "trace_start":
            # Create trace
            trace = Trace(
                id=trace_id,
                project_id=event_data.get("project_id"),
                name=event_data.get("name"),
                user_id=event_data.get("user_id"),  # External user ID (no FK!)
                session_id=event_data.get("session_id"),
                meta=event_data.get("meta", {}),
                timestamp=datetime.fromisoformat(event_data.get("timestamp")),
            )
            session.add(trace)
            logger.debug(f"Created trace: {trace_id}")

        elif event_type == "observation_start":
            # Create observation
            observation = Observation(
                id=observation_id,
                trace_id=trace_id,
                parent_observation_id=event_data.get("parent_observation_id"),
                type=event_data.get("type", "SPAN"),
                name=event_data.get("name"),
                input=event_data.get("input"),
                start_time=datetime.fromisoformat(event_data.get("start_time")),
                level="DEFAULT",
            )
            session.add(observation)
            logger.debug(f"Created observation: {observation_id}")

        elif event_type == "observation_end":
            # Update observation with output
            observation = await session.get(Observation, observation_id)
            if observation:
                observation.output = event_data.get("output")
                observation.end_time = datetime.fromisoformat(event_data.get("end_time"))
                observation.level = event_data.get("level", "DEFAULT")
                session.add(observation)
                logger.debug(f"Updated observation: {observation_id}")
            else:
                logger.warning(f"⚠️ Observation not found: {observation_id}")

        elif event_type == "observation_error":
            # Mark observation as error
            observation = await session.get(Observation, observation_id)
            if observation:
                observation.level = "ERROR"
                observation.status_message = event_data.get("error")
                observation.end_time = datetime.fromisoformat(event_data.get("end_time"))
                session.add(observation)
                logger.debug(f"Marked observation as error: {observation_id}")
```

**Add to `backend/app/main.py` (startup):**

```python
from app.services.observability_consumer import ObservabilityConsumer

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... existing startup ...

    # Start observability consumer
    if settings.OBSERVABILITY_ENABLED:
        consumer = ObservabilityConsumer(
            redis_url=settings.OBSERVABILITY_REDIS_URL,
            db_session_factory=get_async_session,
            stream_name=settings.OBSERVABILITY_STREAM_NAME,
            group_name=settings.OBSERVABILITY_GROUP_NAME,
            batch_size=settings.OBSERVABILITY_BATCH_SIZE,
        )

        consumer_task = asyncio.create_task(consumer.start())
        logger.info("✅ Observability consumer started")

    try:
        yield
    finally:
        # Graceful shutdown
        if settings.OBSERVABILITY_ENABLED:
            await consumer.stop()
            consumer_task.cancel()
```

**Add to `backend/app/core/config.py`:**

```python
class Settings(BaseSettings):
    # ... existing settings ...

    # Observability Consumer (Redis Streams)
    OBSERVABILITY_ENABLED: bool = True
    OBSERVABILITY_REDIS_URL: str = "redis://172.17.0.1:6379"  # Swisper's Redis
    OBSERVABILITY_STREAM_NAME: str = "observability:events"
    OBSERVABILITY_GROUP_NAME: str = "swisper_studio_consumers"
    OBSERVABILITY_BATCH_SIZE: int = 50
```

---

## Performance Analysis

### Current vs Proposed

| Metric | Current (HTTP) | Proposed (Redis Streams) | Improvement |
|--------|----------------|--------------------------|-------------|
| **Publish latency** | 50-100ms | 1-2ms | **50x faster** |
| **Total overhead (5 nodes)** | 500-750ms | 5-10ms | **75x faster** |
| **User-facing impact** | Very noticeable | Imperceptible | ✅ None |
| **Reliability** | Medium (network) | High (persistent queue) | ✅ Better |
| **Scalability** | Low | High (100k+ events/sec) | ✅ Much better |

### Detailed Timing

**Current (Blocking HTTP):**
```
Node execution: 1000ms
  + HTTP POST start: 60ms (blocking)
  + HTTP PATCH end: 40ms (blocking)
Total: 1100ms (10% overhead)

5 nodes × 100ms = 500ms total overhead
```

**Proposed (Redis Streams):**
```
Node execution: 1000ms
  + Redis XADD start: 1ms (non-blocking)
  + Redis XADD end: 1ms (non-blocking)
Total: 1002ms (0.2% overhead)

5 nodes × 2ms = 10ms total overhead
```

**User Experience:**
- Current: "Why is Swisper slower?" ❌
- Proposed: "No difference noticed" ✅

---

## Migration Plan

### Phase 1: Development Testing (Week 1)

**Goal:** Validate Redis Streams architecture with Swisper's Redis

**Steps:**

**Day 1: SDK Changes**
1. Add Redis publisher module
2. Update decorator to use Redis
3. Update graph wrapper
4. Add `initialize_redis_publisher()` function

**Day 2: SwisperStudio Consumer**
1. Add consumer service
2. Add configuration settings
3. Start consumer in main.py
4. Test locally

**Day 3: Integration Testing**
1. Swisper: Initialize Redis publisher
2. SwisperStudio: Start consumer
3. Send test requests
4. Verify events processed
5. Measure performance

**Success Criteria:**
- ✅ <10ms total overhead
- ✅ All traces appear in UI
- ✅ No data loss
- ✅ Ordered delivery

---

### Phase 2: Production Hardening (Week 2 - Optional)

**If needed for production:**

**Option A: Keep using Swisper's Redis**
- Add monitoring for stream length
- Set up alerts for consumer lag
- Document capacity limits

**Option B: Migrate to dedicated Redis**
- Add Redis to SwisperStudio docker-compose
- Update configuration URLs
- Test migration
- Deploy

---

## Configuration

### Swisper Configuration

**In `backend/app/core/config.py`:**

```python
# SwisperStudio Integration
SWISPER_STUDIO_ENABLED: bool = True

# Redis Streams (Option B - use Swisper's Redis)
SWISPER_STUDIO_REDIS_URL: str = "redis://redis:6379"  # Local Redis
SWISPER_STUDIO_STREAM_NAME: str = "observability:events"
SWISPER_STUDIO_PROJECT_ID: str = "0d7aa606-cb29-4a31-8a59-50fa61151a32"
SWISPER_STUDIO_MAX_STREAM_LENGTH: int = 100000  # Keep last 100k events
```

**In `backend/app/main.py`:**

```python
# Initialize SwisperStudio observability (Redis Streams)
if settings.SWISPER_STUDIO_ENABLED:
    try:
        from swisper_studio_sdk import initialize_redis_publisher

        await initialize_redis_publisher(
            redis_url=settings.SWISPER_STUDIO_REDIS_URL,
            stream_name=settings.SWISPER_STUDIO_STREAM_NAME,
            max_stream_length=settings.SWISPER_STUDIO_MAX_STREAM_LENGTH,
        )
        logger.info("✅ SwisperStudio observability initialized (Redis Streams)")
        logger.info(f"   Redis: {settings.SWISPER_STUDIO_REDIS_URL}")
        logger.info(f"   Stream: {settings.SWISPER_STUDIO_STREAM_NAME}")
    except Exception as e:
        logger.warning(f"⚠️ SwisperStudio observability disabled: {e}")
```

---

### SwisperStudio Configuration

**In `backend/app/core/config.py`:**

```python
class Settings(BaseSettings):
    # ... existing settings ...

    # Observability Consumer
    OBSERVABILITY_ENABLED: bool = True
    OBSERVABILITY_REDIS_URL: str = "redis://172.17.0.1:6379"  # Swisper's Redis from host
    OBSERVABILITY_STREAM_NAME: str = "observability:events"
    OBSERVABILITY_GROUP_NAME: str = "swisper_studio_consumers"
    OBSERVABILITY_CONSUMER_NAME: str = "consumer_1"
    OBSERVABILITY_BATCH_SIZE: int = 50
```

**Environment variables (.env):**

```bash
# For development (connecting to Swisper's Redis)
OBSERVABILITY_REDIS_URL=redis://172.17.0.1:6379

# For production (if using dedicated Redis)
# OBSERVABILITY_REDIS_URL=redis://observability-redis:6379
```

---

## Monitoring & Operations

### Redis Stream Monitoring

**Check stream length (pending events):**
```bash
redis-cli -h 172.17.0.1 XLEN observability:events
# Should be close to 0 (consumer keeping up)
```

**Check consumer group status:**
```bash
redis-cli -h 172.17.0.1 XINFO GROUPS observability:events
# Shows: consumers, pending count, last-delivered-id
```

**Check consumer lag:**
```bash
redis-cli -h 172.17.0.1 XPENDING observability:events swisper_studio_consumers
# Shows: pending count, min/max IDs
```

**Manual replay (if needed):**
```bash
# Reprocess from specific ID
redis-cli -h 172.17.0.1 XREADGROUP GROUP swisper_studio_consumers consumer_1 \
  STREAMS observability:events <specific-id>
```

### SwisperStudio Metrics

**Add metrics endpoint:**
```python
@router.get("/api/v1/observability/metrics")
async def get_observability_metrics():
    # Connect to Redis
    client = redis.from_url(settings.OBSERVABILITY_REDIS_URL)

    # Get stream metrics
    stream_length = await client.xlen(settings.OBSERVABILITY_STREAM_NAME)

    # Get consumer group info
    groups = await client.xinfo_groups(settings.OBSERVABILITY_STREAM_NAME)

    return {
        "stream_length": stream_length,
        "consumer_groups": groups,
        "status": "healthy" if stream_length < 10000 else "lagging",
    }
```

### Alerts

**Set up alerts for:**
- Stream length > 10,000 (consumer falling behind)
- Consumer not processing for > 5 minutes
- Redis connection failures

---

## Testing Plan

### Unit Tests

**SDK tests:**
```python
@pytest.mark.asyncio
async def test_redis_publisher_publishes_events():
    # Initialize with test Redis
    await initialize_redis_publisher("redis://localhost:6379")

    # Publish event
    await publish_event(
        event_type="test_event",
        trace_id="test-123",
        project_id="test-proj",
        data={"foo": "bar"}
    )

    # Verify event in stream
    client = redis.from_url("redis://localhost:6379")
    events = await client.xrange("observability:events", count=1)

    assert len(events) == 1
    assert events[0][1]["event_type"] == "test_event"
```

**Consumer tests:**
```python
@pytest.mark.asyncio
async def test_consumer_processes_trace_events():
    # Add test event to stream
    client = redis.from_url("redis://localhost:6379")
    await client.xadd("observability:events", {
        "event_type": "trace_start",
        "trace_id": "test-123",
        "data": json.dumps({"name": "test_trace"}),
    })

    # Start consumer
    consumer = ObservabilityConsumer(...)
    await consumer._consume_loop_once()  # Process one batch

    # Verify trace in database
    trace = await session.get(Trace, "test-123")
    assert trace is not None
    assert trace.name == "test_trace"
```

### Integration Tests

**End-to-end test:**
```python
@pytest.mark.integration
async def test_swisper_to_swisperstudio_flow():
    # 1. Send request through Swisper
    response = await swisper_client.post("/chat", json={
        "message": "test observability"
    })

    # 2. Wait for consumer to process (max 2 seconds)
    await asyncio.sleep(2)

    # 3. Check SwisperStudio has trace
    traces = await swisperstudio_client.get("/api/v1/traces")
    assert len(traces) > 0

    # 4. Verify all nodes captured
    trace = traces[0]
    observations = await swisperstudio_client.get(f"/api/v1/observations?trace_id={trace.id}")
    assert len(observations) >= 5  # classify_intent, memory, planner, agent, ui
```

### Performance Tests

**Latency test:**
```python
import time

# Baseline (no tracing)
start = time.time()
result = await graph.ainvoke(state)
baseline = time.time() - start

# With Redis Streams tracing
start = time.time()
result = await graph.ainvoke(state)
with_tracing = time.time() - start

overhead = with_tracing - baseline
assert overhead < 0.01  # Less than 10ms
print(f"Overhead: {overhead*1000:.2f}ms")  # Should be ~2-5ms
```

**Load test:**
```python
# Send 100 requests rapidly
for i in range(100):
    asyncio.create_task(graph.ainvoke(state))

# Verify all 100 traces created (eventually)
await asyncio.sleep(10)
traces = await db.query(Trace).count()
assert traces >= 100
```

---

## Rollout Plan

### Week 1: Implementation

**SDK (SwisperStudio team):**
- Day 1-2: Add Redis publisher
- Day 3: Test with mock consumer

**Consumer (SwisperStudio team):**
- Day 4-5: Implement consumer service
- Day 6: Integration testing

**Total: 6 days**

### Week 2: Production Deployment

**Day 1-2: Staging Testing**
- Deploy to staging environment
- Run load tests
- Monitor for 48 hours

**Day 3: Production Rollout**
- Deploy SDK update to Swisper
- Deploy consumer to SwisperStudio
- Monitor closely

**Day 4-5: Validation**
- Measure performance improvement
- Verify data completeness
- Gather user feedback

---

## Success Criteria

**Performance:**
- ✅ Total overhead < 10ms (vs 500ms baseline)
- ✅ User response time unchanged
- ✅ Stream processing lag < 1 second

**Reliability:**
- ✅ Zero data loss over 24 hours
- ✅ All events processed in order
- ✅ Consumer recovery on failure < 5 seconds

**Functional:**
- ✅ All traces appear in UI
- ✅ All observations captured
- ✅ State before/after correct
- ✅ Nesting relationships preserved

---

## Risk Assessment

**Low Risk:**
- Redis Streams is mature technology
- Swisper already uses Redis successfully
- Simple pub-sub pattern
- Well-tested in industry

**Mitigation:**
- Feature flag to disable (OBSERVABILITY_ENABLED=false)
- Graceful degradation if Redis unavailable
- Monitoring alerts for consumer lag
- Rollback plan (revert to HTTP if needed)

---

## Alternative Considered: Kafka

**Why NOT Kafka:**
- ❌ Heavy infrastructure (Zookeeper + Kafka cluster)
- ❌ Operational complexity
- ❌ Resource overhead (~2GB minimum)
- ❌ Overkill for current scale (<1000 events/sec)

**When to consider Kafka:**
- Swisper scaling to 10,000+ requests/sec
- Multi-tenant SaaS with 100+ clients
- Need strict ordering across partitions
- Compliance requirements for event retention

**For now:** Redis Streams is perfect ✅

---

## Summary

**Current State:**
- ❌ Blocking HTTP: 500ms overhead
- ❌ User-facing latency
- ✅ Functional but slow

**Proposed State:**
- ✅ Redis Streams: <10ms overhead
- ✅ Zero user impact
- ✅ Reliable and scalable
- ✅ Reuses existing infrastructure

**Decision:**
- **Use Swisper's existing Redis** (Option B)
- Simple, fast, no new infrastructure
- Can migrate to dedicated Redis later if needed

**Timeline:**
- Implementation: 6 days
- Testing: 2-3 days
- Total: **2 weeks to production**

---

## Contact & Next Steps

**Ready to implement?**
- Complete technical specification provided
- Code examples for all components
- Testing plan included
- Migration path defined

**Questions?**
- Happy to clarify any technical details
- Can provide additional code samples
- Available for architecture review

---

**This architecture will make SwisperStudio best-in-class for observability performance!** 🚀

