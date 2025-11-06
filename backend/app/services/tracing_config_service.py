"""
Tracing configuration service with Redis caching.

Provides fast per-request checks for tracing enabled/disabled status.

Performance:
- Cache hit: ~1ms (Redis GET)
- Cache miss: ~5ms (DB query + Redis SET)
- TTL: 300 seconds (5 minutes)

Architecture:
- SwisperStudio backend updates cache on settings change
- SDK checks cache before creating traces (per-request)
- Fail-open: Default to enabled if Redis unavailable
"""

import redis.asyncio as redis
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.models import Project
from app.core.config import settings

logger = logging.getLogger(__name__)

# Global Redis client for caching
_redis_client: Optional[redis.Redis] = None


async def init_tracing_cache():
    """
    Initialize Redis client for tracing config cache.
    
    Called on application startup.
    Uses same Redis as observability consumer.
    """
    global _redis_client
    
    try:
        _redis_client = redis.from_url(
            settings.OBSERVABILITY_REDIS_URL,
            decode_responses=False  # We'll handle decoding
        )
        
        # Test connection
        await _redis_client.ping()
        logger.info("✅ Tracing config cache initialized (Redis)")
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to initialize tracing cache: {e}")
        logger.warning("   Tracing config will fallback to database queries")
        _redis_client = None


async def is_tracing_enabled(project_id: str, session: AsyncSession) -> bool:
    """
    Check if tracing is enabled for a project (cached).
    
    This function is called by the backend API and can also be used
    by the consumer if needed.
    
    Performance:
    - Cache hit: ~1ms (Redis GET)
    - Cache miss: ~5ms (DB query + Redis SET)
    - TTL: 300 seconds (5 minutes)
    
    Args:
        project_id: Project UUID
        session: Database session
        
    Returns:
        True if tracing enabled, False if disabled
        
    Behavior:
    - Cache hit: Return cached value immediately
    - Cache miss: Query DB, cache result, return
    - Redis error: Query DB, return (skip caching)
    - Project not found: Default to True
    """
    cache_key = f"tracing:{project_id}:enabled"
    
    # Try cache first
    if _redis_client:
        try:
            cached = await _redis_client.get(cache_key)
            
            if cached == b"true":
                logger.debug(f"Cache HIT: Tracing enabled for {project_id[:8]}...")
                return True
            elif cached == b"false":
                logger.debug(f"Cache HIT: Tracing disabled for {project_id[:8]}...")
                return False
            # None = cache miss, query DB
            logger.debug(f"Cache MISS: Querying DB for {project_id[:8]}...")
            
        except Exception as e:
            # Redis error - fallback to DB
            logger.debug(f"Redis error, fallback to DB: {e}")
    
    # Cache miss or Redis unavailable - query database
    result = await session.execute(
        select(Project.tracing_enabled)
        .where(Project.id == project_id)
    )
    enabled = result.scalar()
    
    if enabled is None:
        # Project not found - default to enabled (fail-open)
        logger.warning(f"Project {project_id[:8]}... not found, defaulting to enabled")
        enabled = True
    
    # Update cache (best effort - don't fail if cache update fails)
    if _redis_client:
        try:
            await _redis_client.setex(
                cache_key,
                300,  # 5 minute TTL
                b"true" if enabled else b"false"
            )
            logger.debug(f"Cache SET: {project_id[:8]}... = {enabled}")
        except Exception as e:
            # Don't fail if cache update fails
            logger.debug(f"Cache update failed: {e}")
    
    return enabled


async def invalidate_tracing_cache(project_id: str, new_value: bool):
    """
    Update cache immediately when settings change.
    
    Called by the API endpoint after updating project.tracing_enabled.
    Sets the new value immediately for instant effect (no waiting for TTL).
    
    Args:
        project_id: Project UUID
        new_value: New tracing_enabled value (True/False)
    """
    if _redis_client:
        try:
            cache_key = f"tracing:{project_id}:enabled"
            # SET the new value immediately (instant effect!)
            await _redis_client.setex(
                cache_key,
                300,  # 5 minute TTL
                b"true" if new_value else b"false"
            )
            logger.info(f"✅ Cache updated immediately for project {project_id[:8]}... = {new_value}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to update cache: {e}")
            # Don't raise - will fallback to DB query


async def close_tracing_cache():
    """
    Close Redis connection gracefully.
    
    Called on application shutdown.
    """
    global _redis_client
    
    if _redis_client:
        try:
            await _redis_client.close()
            logger.info("✅ Tracing config cache closed")
        except Exception as e:
            logger.warning(f"⚠️ Error closing tracing cache: {e}")
        finally:
            _redis_client = None

