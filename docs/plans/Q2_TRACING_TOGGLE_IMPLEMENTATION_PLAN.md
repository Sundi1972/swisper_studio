# Q2: Tracing Toggle - Per-Request Dynamic Control

**Date:** 2025-11-06  
**Requirement:** Per-request tracing control with Redis caching  
**Estimated Time:** 1 hour  
**Approach:** Systematic implementation following 00-workflow

---

## 🎯 Requirements (From You)

1. **Per-request checking** (not just startup)
2. **Project-level toggle** (can turn tracing on/off per project)
3. **Redis caching layer** (fast checks, <2ms overhead)
4. **Future:** Per-user level control

---

## 🏗️ Architecture Design

```
┌─────────────────────────────────────────────┐
│ SWISPERSTUDIO UI                            │
│                                             │
│  Project Settings Page:                     │
│    Tracing: [ON] [OFF]  ← User toggles      │
│                                             │
│  API: PATCH /api/v1/projects/{id}           │
│    {tracing_enabled: false}                 │
│                                             │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ SWISPERSTUDIO BACKEND                        │
│                                             │
│  1. Update database:                        │
│     UPDATE projects                          │
│     SET tracing_enabled = false             │
│                                             │
│  2. Update Redis cache (instant):           │
│     SET tracing:{project_id}:enabled false  │
│     EXPIRE 300  # 5 min TTL                 │
│                                             │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ SWISPER SDK (Per-Request Check)             │
│                                             │
│  Before creating trace:                     │
│                                             │
│  # Step 1: Check Redis cache (1-2ms)        │
│  enabled = await redis_client.get(          │
│      f"tracing:{project_id}:enabled"        │
│  )                                          │
│                                             │
│  if enabled == "false":                     │
│      return  # Skip tracing!                │
│                                             │
│  if enabled == "true":                      │
│      # Proceed with tracing                 │
│                                             │
│  if enabled is None:                        │
│      # Cache miss - query database          │
│      # (happens once per 5 minutes)         │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 📋 Implementation Steps

### **Step 1: Database (DONE ✅)**
- Add projects.tracing_enabled column
- Default: true (existing projects continue tracing)

### **Step 2: Redis Cache Helper (30 mins)**

**File:** `backend/app/services/tracing_config_service.py` (NEW)

```python
"""
Tracing configuration service with Redis caching.
Provides fast per-request checks for tracing enabled/disabled.
"""

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Project
from app.core.config import settings

# Global Redis client for caching
_redis_client = None

async def init_tracing_cache():
    """Initialize Redis client for tracing config cache"""
    global _redis_client
    _redis_client = redis.from_url(settings.OBSERVABILITY_REDIS_URL)

async def is_tracing_enabled(project_id: str, session: AsyncSession) -> bool:
    """
    Check if tracing is enabled for a project (cached).
    
    Performance:
    - Cache hit: ~1ms (Redis GET)
    - Cache miss: ~5ms (DB query + Redis SET)
    - TTL: 300 seconds (5 minutes)
    
    Returns:
        True if tracing enabled, False if disabled
    """
    cache_key = f"tracing:{project_id}:enabled"
    
    # Try cache first
    if _redis_client:
        try:
            cached = await _redis_client.get(cache_key)
            if cached == b"true":
                return True
            elif cached == b"false":
                return False
            # None = cache miss, query DB
        except:
            # Redis error - fallback to DB
            pass
    
    # Cache miss or Redis unavailable - query database
    result = await session.execute(
        select(Project.tracing_enabled)
        .where(Project.id == project_id)
    )
    enabled = result.scalar()
    
    if enabled is None:
        enabled = True  # Default for non-existent projects
    
    # Update cache
    if _redis_client:
        try:
            await _redis_client.setex(
                cache_key,
                300,  # 5 minute TTL
                "true" if enabled else "false"
            )
        except:
            pass  # Don't fail if cache update fails
    
    return enabled

async def invalidate_tracing_cache(project_id: str):
    """Invalidate cache when settings change"""
    if _redis_client:
        await _redis_client.delete(f"tracing:{project_id}:enabled")
```

---

### **Step 3: API Endpoint (15 mins)**

**File:** `backend/app/api/routes/projects.py`

**Add endpoint:**

```python
@router.patch("/{project_id}/tracing")
async def update_project_tracing(
    project_id: str,
    data: dict,  # {"tracing_enabled": true/false}
    session: DBSession,
    auth: Auth
):
    """
    Enable/disable tracing for a project.
    
    Updates database and invalidates cache.
    Takes effect on next request from Swisper (~5s with cache TTL).
    """
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    
    # Update database
    project.tracing_enabled = data.get('tracing_enabled', True)
    session.add(project)
    await session.commit()
    
    # Invalidate cache (instant effect)
    from app.services.tracing_config_service import invalidate_tracing_cache
    await invalidate_tracing_cache(project_id)
    
    return {"status": "ok", "tracing_enabled": project.tracing_enabled}
```

---

### **Step 4: SDK Check (15 mins)**

**File:** `sdk/swisper_studio_sdk/tracing/redis_publisher.py`

**Add check before publishing:**

```python
async def is_tracing_enabled_for_project(project_id: str) -> bool:
    """
    Check if tracing is enabled for this project.
    
    Uses Redis cache for speed (1-2ms).
    Cache TTL: 5 minutes (balance between freshness and performance).
    """
    client = get_redis_client()
    if not client:
        return True  # Default to enabled if Redis unavailable
    
    cache_key = f"tracing:{project_id}:enabled"
    
    try:
        cached = await client.get(cache_key)
        
        # Cached value
        if cached == b"true":
            return True
        elif cached == b"false":
            return False
        
        # Cache miss - default to enabled
        # (SwisperStudio will set cache when project settings accessed)
        return True
    
    except:
        # Redis error - default to enabled (fail open)
        return True


# In graph_wrapper.py, before creating trace:
if not await is_tracing_enabled_for_project(project_id):
    logger.debug(f"Tracing disabled for project {project_id}, skipping")
    return await original_ainvoke(...)  # Run without tracing
```

---

## ⚡ Performance Impact

**Per-request overhead:**
- Cache hit: +1-2ms (Redis GET)
- Cache miss: +5ms (happens once per 5 min)

**User impact:** Negligible (adds to 10ms SDK overhead = 12ms total)

---

## 🎨 UI Component (15 mins)

**File:** `frontend/src/features/projects/components/project-settings.tsx`

**Add toggle:**

```typescript
<FormControlLabel
  control={
    <Switch
      checked={project.tracing_enabled}
      onChange={async (e) => {
        await updateProjectTracing(projectId, {
          tracing_enabled: e.target.checked
        });
        // Refresh project data
        refetch();
      }}
    />
  }
  label="Enable Tracing"
/>

<Typography variant="caption" color="text.secondary">
  Disable to stop collecting traces from Swisper.
  Takes effect within 5 minutes (cache TTL).
</Typography>
```

---

## 🧪 Testing Plan

**Test 1: Toggle OFF**
1. Go to project settings
2. Toggle tracing OFF
3. Send message through Swisper
4. Wait 5 minutes (cache TTL)
5. Send another message
6. Verify: No new traces in SwisperStudio

**Test 2: Toggle ON**
1. Toggle tracing ON
2. Send message
3. Verify: Trace appears in SwisperStudio

**Test 3: Cache Performance**
1. Enable tracing
2. Send 100 messages rapidly
3. Verify: <2ms overhead per check

---

## ✅ Success Criteria

- [ ] Database column exists (projects.tracing_enabled)
- [ ] Redis cache service working
- [ ] API endpoint working (PATCH /projects/{id}/tracing)
- [ ] SDK checks cache before tracing
- [ ] UI toggle working
- [ ] Cache TTL working (5 minutes)
- [ ] Performance: <2ms per check
- [ ] Fail-open: Defaults to enabled if Redis down

---

## 🎯 Approval Needed

**Before implementing, please confirm:**

1. ✅ Architecture looks good?
2. ✅ 5-minute cache TTL acceptable?
3. ✅ Fail-open behavior OK? (default to enabled if errors)
4. ✅ Ready to proceed?

---

**Awaiting your approval to implement!** 🙏

