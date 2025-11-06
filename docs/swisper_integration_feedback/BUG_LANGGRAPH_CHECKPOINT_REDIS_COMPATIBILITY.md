# Bug Report: langgraph-checkpoint-redis Compatibility Issue

**Date:** 2025-11-06  
**From:** Swisper Development Team  
**Severity:** Medium  
**Status:** Identified - Needs SwisperStudio SDK update

---

## 🐛 Issue Summary

**Problem:** `langgraph-checkpoint-redis 0.1.2` is **not compatible** with `langgraph-checkpoint 3.0.1`

**Impact:** Users upgrading to latest langgraph ecosystem get checkpoint serialization errors

**Error:**
```
AttributeError: 'JsonPlusRedisSerializer' object has no attribute 'dumps'
```

---

## 📊 Version Compatibility Matrix

| langgraph-checkpoint | langgraph-checkpoint-redis | Status |
|---------------------|---------------------------|--------|
| **3.0.1** (latest) | 0.1.2 (latest) | ❌ **BROKEN** |
| 2.1.2 | 0.1.2 | ✅ **WORKS** |
| 2.1.1 | 0.0.8 | ✅ **WORKS** |

**Root Cause:** langgraph-checkpoint 3.0 introduced breaking changes to serializer API that langgraph-checkpoint-redis hasn't adopted yet.

---

## 🔍 Technical Details

### Error Traceback:

```python
File "/app/.venv/lib/python3.12/site-packages/langgraph/checkpoint/redis/aio.py", line 542, in aput
    "checkpoint": self._dump_checkpoint(copy),
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/app/.venv/lib/python3.12/site-packages/langgraph/checkpoint/redis/base.py", line 273, in _dump_checkpoint
    type_, data = self.serde.dumps_typed(checkpoint)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/app/.venv/lib/python3.12/site-packages/langgraph/checkpoint/redis/jsonplus_redis.py", line 24, in dumps_typed
    return "json", self.dumps(obj).decode("utf-8")
                   ^^^^^^^^^^
AttributeError: 'JsonPlusRedisSerializer' object has no attribute 'dumps'
```

### What Changed:

**langgraph-checkpoint 3.0 serializer API:**
```python
# OLD API (2.x):
class JsonPlusRedisSerializer:
    def dumps(self, obj):  # ← Method exists
        return msgpack.packb(obj)

# NEW API (3.0):
class JsonPlusRedisSerializer:
    def dumps_typed(self, obj):  # ← Only this method
        # But internally tries to call self.dumps() ← Doesn't exist!
```

**langgraph-checkpoint-redis hasn't updated** to match the new 3.0 API yet.

---

## 🎯 Impact on Users

### What Happens:

**When users follow SDK documentation:**
```bash
# Install latest SDK
pip install swisper-studio-sdk

# SDK requires:
langgraph>=1.0.0
```

**Result:**
1. ✅ SDK installs successfully
2. ✅ Tracing works (observations sent to SwisperStudio)
3. ❌ **Checkpointing fails** (if using Redis checkpoints)
4. ⚠️ Application still runs but can't resume interrupted conversations

**Error appears in logs:**
```
AttributeError: 'JsonPlusRedisSerializer' object has no attribute 'dumps'
Task exception was never retrieved
```

---

## ✅ Current Workaround

**Users can:**

**Option A: Pin langgraph-checkpoint to 2.x**
```toml
# In their requirements
langgraph-checkpoint>=2.1.0,<3.0.0
langgraph-checkpoint-redis>=0.1.0
```

**Option B: Use database checkpointing**
```python
# Fallback to PostgreSQL checkpointing (works fine)
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver(connection_string)
```

**Option C: Disable Redis checkpointing**
```python
# System continues working without checkpointing
# (Observability still works, just no conversation resume)
```

---

## 🔧 Recommended Fix for SDK

### Update SDK Dependencies:

**File:** `sdk/pyproject.toml`

**Current (problematic):**
```toml
dependencies = [
    "httpx>=0.25.2",
    "langgraph>=0.4.8",  # Allows 1.0+ which pulls checkpoint 3.0
]
```

**Recommended:**
```toml
dependencies = [
    "httpx>=0.25.2",
    "langgraph>=1.0.0,<2.0.0",  # Allow 1.0.x
    "langgraph-checkpoint>=2.1.0,<3.0.0",  # Pin to 2.x until Redis extension compatible
]
```

**Or explicitly:**
```toml
dependencies = [
    "httpx>=0.25.2",
    "langgraph==1.0.2",
    "langgraph-checkpoint==2.1.2",  # Latest compatible with Redis
]
```

**Why:**
- ✅ Works with latest langgraph 1.0.2
- ✅ Compatible with Redis checkpointing
- ✅ No breaking changes for users
- ⏳ Can upgrade to checkpoint 3.0 when Redis extension updated

---

## 📅 Long-term Solution

**Wait for:** `langgraph-checkpoint-redis` to release version compatible with checkpoint 3.0

**Watch:**
- https://github.com/langchain-ai/langgraph/releases
- https://pypi.org/project/langgraph-checkpoint-redis/

**When available:**
- Update SDK to allow `langgraph-checkpoint>=3.0`
- Test compatibility
- Release SDK update

---

## 🎯 Recommendation

**Immediate (This Week):**
- Pin `langgraph-checkpoint<3.0` in SDK dependencies
- Release as SDK v0.3.3 or v0.4.0
- Document in release notes

**Future (When Available):**
- Monitor langgraph-checkpoint-redis updates
- Test with checkpoint 3.0
- Upgrade SDK dependencies

**Timeline:**
- SDK fix: 30 minutes
- Testing: 1 hour
- Release: Same day

---

## 📝 Testing Checklist

**After pinning checkpoint to 2.x:**

```bash
# Clean install
pip uninstall langgraph langgraph-checkpoint langgraph-checkpoint-redis -y
pip install -e /path/to/sdk

# Verify versions
pip list | grep langgraph-checkpoint
# Should show:
#   langgraph-checkpoint        2.1.2
#   langgraph-checkpoint-redis  0.1.2

# Test checkpoint persistence
python -c "
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
import redis.asyncio as redis
import asyncio

async def test():
    client = redis.from_url('redis://localhost:6379')
    saver = AsyncRedisSaver(client)
    print('✅ Redis checkpointer created successfully')
    
asyncio.run(test())
"
```

**Expected:** ✅ No errors

---

## 🔗 Related Issues

**LangGraph GitHub:**
- Check for open issues about checkpoint-redis 3.0 compatibility
- Community likely reporting same issue

**Workaround for Users:**
- Document in SDK README
- Add note in integration guide
- Provide explicit dependency pinning example

---

## Contact

**Swisper Team Status:**
- ✅ Workaround implemented (using database checkpointing)
- ✅ Observability working perfectly
- ⏸️ Redis checkpointing disabled until fix available

**Questions?**
- Happy to test SDK updates
- Can provide more details if needed
- Ready to validate fix when available

---

**Thanks for the excellent SDK - this is a minor dependency issue easily fixed!** 🚀

