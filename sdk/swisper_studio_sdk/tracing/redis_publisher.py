"""
Redis Streams publisher for non-blocking observability.

Publishes trace events to Redis Streams with 1-2ms latency.

Architecture:
- SDK publishes events via Redis XADD (fire-and-forget)
- SwisperStudio consumer reads from stream and stores in DB
- Heartbeat mechanism for connection verification

v0.4.0: Redis Streams migration from HTTP
"""

import redis.asyncio as redis
import json
import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Global state
_redis_client: Optional[redis.Redis] = None
_stream_name: str = "observability:events"
_max_stream_length: int = 100000
_project_id: str = ""


async def initialize_redis_publisher(
    redis_url: str,
    stream_name: str = "observability:events",
    project_id: str = "",
    max_stream_length: int = 100000,
    verify_consumer: bool = True,
) -> Dict[str, bool]:
    """
    Initialize Redis publisher for observability events.

    Args:
        redis_url: Redis connection URL (e.g., "redis://redis:6379")
        stream_name: Stream name for events
        project_id: SwisperStudio project ID
        max_stream_length: Max events to keep in stream (FIFO eviction)
        verify_consumer: If True, check that consumer is running

    Returns:
        dict: Verification results
            {
                "redis": bool,      # Redis connectivity OK
                "write": bool,      # Write permission OK
                "consumer": bool,   # Consumer detected and healthy
            }
    """
    global _redis_client, _stream_name, _max_stream_length, _project_id

    verification_results = {
        "redis": False,
        "write": False,
        "consumer": False,
    }

    try:
        # Connect to Redis
        _redis_client = redis.from_url(redis_url, decode_responses=False)
        _stream_name = stream_name
        _max_stream_length = max_stream_length
        _project_id = project_id

        # Test connection
        await _redis_client.ping()
        verification_results["redis"] = True
        logger.info("✅ Redis connectivity: OK")

        # Test write permission
        await _redis_client.xadd(
            "observability:health_check",
            {b"test": b"ping", b"timestamp": str(time.time()).encode()},
            maxlen=10
        )
        verification_results["write"] = True
        logger.info("✅ Redis write permission: OK")

        # Check consumer heartbeat (if requested)
        if verify_consumer:
            consumer_healthy = await _verify_consumer_health(_redis_client)
            verification_results["consumer"] = consumer_healthy
            
            if consumer_healthy:
                logger.info("✅ Consumer detected: HEALTHY")
            else:
                logger.warning("⚠️ Consumer not detected")
                logger.warning("   Events will queue until consumer starts")

        logger.info(f"✅ Redis publisher initialized successfully")
        logger.info(f"   Stream: {stream_name}")
        logger.info(f"   Project: {project_id}")

        return verification_results

    except redis.ConnectionError as e:
        logger.error(f"❌ Cannot connect to Redis at {redis_url}")
        logger.error(f"   Error: {e}")
        logger.error("   Check Redis is running and accessible")
        raise

    except redis.AuthenticationError as e:
        logger.error("❌ Redis authentication failed")
        logger.error("   Check Redis password in configuration")
        raise

    except Exception as e:
        logger.error(f"❌ Redis publisher initialization failed: {e}")
        raise


async def _verify_consumer_health(
    redis_client: redis.Redis,
    timeout: float = 3.0
) -> bool:
    """
    Verify SwisperStudio consumer is running and healthy.

    Checks for consumer heartbeat written every 5 seconds.
    Returns True if consumer active, False otherwise.
    """
    try:
        # Check for heartbeat key
        import asyncio
        heartbeat_data = await asyncio.wait_for(
            redis_client.get("swisper_studio:consumer:heartbeat"),
            timeout=timeout
        )

        if not heartbeat_data:
            logger.warning("⚠️ SwisperStudio consumer heartbeat not found")
            logger.warning("   Consumer may not be running")
            return False

        # Parse heartbeat (decode if bytes)
        if isinstance(heartbeat_data, bytes):
            heartbeat_data = heartbeat_data.decode('utf-8')
        
        heartbeat = json.loads(heartbeat_data)
        timestamp = datetime.fromisoformat(heartbeat["timestamp"])
        age_seconds = (datetime.utcnow() - timestamp).total_seconds()

        if age_seconds > 10:
            logger.warning(f"⚠️ SwisperStudio consumer heartbeat stale ({age_seconds:.0f}s old)")
            logger.warning("   Consumer may be stopped or lagging")
            return False

        logger.info(f"   Last seen: {age_seconds:.1f} seconds ago")
        logger.info(f"   Events processed: {heartbeat.get('events_processed', 'N/A')}")
        logger.info(f"   Stream length: {heartbeat.get('stream_length', 'N/A')}")
        return True

    except asyncio.TimeoutError:
        logger.warning("⚠️ Timeout checking consumer heartbeat")
        return False
    except json.JSONDecodeError:
        logger.warning("⚠️ Invalid heartbeat data format")
        return False
    except Exception as e:
        logger.warning(f"⚠️ Failed to verify consumer: {e}")
        return False


def get_redis_client() -> Optional[redis.Redis]:
    """Get the global Redis client"""
    return _redis_client


def get_project_id() -> str:
    """Get the configured project ID"""
    return _project_id


async def publish_event(
    event_type: str,
    trace_id: str,
    observation_id: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Publish observability event to Redis Stream.

    Non-blocking - returns in 1-2ms.

    Args:
        event_type: Event type (trace_start, observation_start, observation_end, etc.)
        trace_id: Trace identifier
        observation_id: Observation identifier (if applicable)
        data: Event data (will be JSON serialized)

    Event types:
        - trace_start: New trace created
        - observation_start: Observation started
        - observation_end: Observation completed
        - observation_error: Observation failed
    """
    client = get_redis_client()
    if not client:
        # Tracing disabled or not initialized
        return

    try:
        # Build event payload (all fields as bytes for Redis)
        event = {
            b"event_type": event_type.encode(),
            b"trace_id": trace_id.encode(),
            b"project_id": _project_id.encode(),
            b"timestamp": str(time.time()).encode(),
        }

        if observation_id:
            event[b"observation_id"] = observation_id.encode()

        if data:
            # Serialize data to JSON
            event[b"data"] = json.dumps(data, default=str).encode()

        # XADD - publish to stream (1-2ms!)
        await client.xadd(
            _stream_name,
            event,
            maxlen=_max_stream_length,  # Prevent unbounded growth
        )

        # Debug logging (disabled in production)
        logger.debug(f"Published {event_type} event to {_stream_name}")

    except Exception as e:
        # Silent failure - don't break main application
        logger.debug(f"Failed to publish event: {e}")
        pass


async def is_tracing_enabled_for_project(project_id: str) -> bool:
    """
    Check if tracing is enabled for this project (Q2: Tracing Toggle).
    
    Uses Redis cache for speed (1-2ms).
    Cache is managed by SwisperStudio backend.
    
    Performance:
    - Cache hit: ~1ms (Redis GET)
    - Cache miss: Defaults to enabled (fail-open)
    - Cache TTL: 5 minutes (set by backend)
    
    Args:
        project_id: Project UUID
        
    Returns:
        True if tracing enabled (or if unable to check), False if disabled
        
    Behavior:
    - Cache value "true" → enabled
    - Cache value "false" → disabled
    - Cache miss (None) → enabled (fail-open)
    - Redis error → enabled (fail-open)
    
    This is called on every graph invocation (per-request check).
    """
    client = get_redis_client()
    if not client:
        # Tracing not initialized, default to enabled
        return True
    
    cache_key = f"tracing:{project_id}:enabled"
    
    try:
        cached = await client.get(cache_key)
        
        # Cached value
        if cached == b"true":
            logger.debug(f"Tracing enabled for project {project_id[:8]}...")
            return True
        elif cached == b"false":
            logger.debug(f"Tracing disabled for project {project_id[:8]}...")
            return False
        
        # Cache miss - default to enabled (fail-open)
        # Backend will populate cache when project settings are accessed
        logger.debug(f"Cache miss for project {project_id[:8]}..., defaulting to enabled")
        return True
    
    except Exception as e:
        # Redis error - default to enabled (fail-open)
        logger.debug(f"Redis error checking tracing status: {e}, defaulting to enabled")
        return True


async def close_redis_publisher() -> None:
    """
    Close Redis connection gracefully.

    Call this on application shutdown.
    """
    global _redis_client

    if _redis_client:
        try:
            await _redis_client.close()
            logger.info("✅ Redis publisher closed")
        except Exception as e:
            logger.warning(f"⚠️ Error closing Redis publisher: {e}")
        finally:
            _redis_client = None

