# Bug Report: SDK v0.3.2 Dependency Conflict - BLOCKING Production Use

**Date:** 2025-11-06  
**From:** Swisper Development Team  
**Severity:** 🔥 **CRITICAL - BLOCKING**  
**Status:** SDK v0.3.2 has incompatible dependencies - Immediate fix required  
**Priority:** P0 - Production blocker

---

## 🚨 CRITICAL ISSUE

### **SDK v0.3.2 Is Broken - Do Not Release**

**What Happened:**
1. SDK v0.3.2 was released with observation fixes ✅
2. SDK pulls in `langgraph-checkpoint 3.0.1` as dependency ❌
3. langgraph-checkpoint 3.0.1 is **INCOMPATIBLE** with existing code ❌
4. **Crashes user's production system** ❌

**Impact on Users:**
- ❌ **Productivity agents CRASH** (can't serialize state)
- ❌ **Checkpointing FAILS** (can't resume conversations)
- ❌ **Production systems DOWN**
- ✅ Observability still works (but users can't run their app!)

**We installed SDK v0.3.2 and our system broke immediately!**

---

## 🐛 Issue Summary

**Problem:** SDK v0.3.2 dependencies allow `langgraph-checkpoint 3.0.1` which is **INCOMPATIBLE**

**What Breaks:**
```python
# When user installs SDK v0.3.2:
pip install -e /path/to/swisper_studio_sdk

# It installs:
langgraph>=0.4.8  # Pulls in langgraph 1.0.2 ✅
# Which requires:
langgraph-checkpoint>=3.0.0  # Pulls in 3.0.1 ❌ BROKEN!

# But users also have:
langgraph-checkpoint-redis==0.1.2  # Not compatible with 3.0! ❌
```

**Errors in Production:**
```
AttributeError: 'JsonPlusRedisSerializer' object has no attribute 'dumps'
TypeError: Type is not JSON serializable: ToolOperation
TypeError: Type is not JSON serializable: GlobalPlannerDecision
```

**Production Impact - CRITICAL:**
- ❌ **Productivity agent crashes** during email/calendar operations
- ❌ **Graph execution fails** mid-run
- ❌ **Users get no response** from their assistant
- ❌ **Agent state can't be saved** to checkpoints
- ❌ **Conversations can't resume** after interrupts
- ✅ Observability works (traces sent) but **app is broken!**

**What We Observed:**
```
2025-11-06 05:12:28 - ProductivityAgent executing ✅
2025-11-06 05:12:35 - Productivity planner result ✅
2025-11-06 05:12:35 - ERROR: 'super' object has no attribute 'dumps' ❌
→ CRASH - No response to user ❌
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

## 🚨 IMMEDIATE ACTION REQUIRED

### **DO NOT RELEASE SDK v0.3.2 to other users!**

**Why:**
- ❌ Breaks production systems
- ❌ Causes agent crashes
- ❌ No workaround for users
- ❌ Will require emergency rollback

### **URGENT: Release SDK v0.3.3 with Fixed Dependencies**

---

## 🔧 Required Fix for SDK (30 minutes)

### **File:** `sdk/pyproject.toml`

**Current in SDK v0.3.2 (BROKEN):**
```toml
dependencies = [
    "httpx>=0.25.2",
    "langgraph>=0.4.8",  # ❌ Allows 1.0+ which pulls checkpoint 3.0.1 (broken!)
]
```

**MUST CHANGE TO:**
```toml
dependencies = [
    "httpx>=0.25.2",
    "langgraph>=1.0.0,<2.0.0",  # Allow langgraph 1.0.x
    "langgraph-checkpoint>=2.1.0,<3.0.0",  # 🔥 CRITICAL: Pin to 2.x (3.0 breaks!)
]
```

**Or be even more explicit (safer):**
```toml
dependencies = [
    "httpx>=0.25.2",
    "langgraph==1.0.2",  # Latest stable
    "langgraph-checkpoint==2.1.2",  # Latest that works with Redis
]
```

**Why This Fix Works:**
- ✅ langgraph 1.0.2 - latest, stable
- ✅ langgraph-checkpoint 2.1.2 - latest Redis-compatible version
- ✅ Works with all user systems
- ✅ No crashes
- ✅ Checkpointing works
- ✅ Observability works

**Why v0.3.2 Breaks:**
- langgraph-checkpoint 3.0.1 changed serializer API
- langgraph-checkpoint-redis 0.1.2 not updated yet
- Users hit serialization errors
- Agents crash on state save

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

---

## ⏱️ Timeline & Urgency

### **Immediate (Today):**

**Action 1: Pull SDK v0.3.2** (if already distributed)
- Don't let other users install it
- Will break their production systems

**Action 2: Fix Dependencies** (30 minutes)
```bash
# In swisper_studio/sdk/pyproject.toml
dependencies = [
    "httpx>=0.25.2",
    "langgraph==1.0.2",
    "langgraph-checkpoint==2.1.2",  # Pin to working version!
]
```

**Action 3: Test Fix** (15 minutes)
```bash
# Clean install
pip uninstall swisper-studio-sdk langgraph langgraph-checkpoint -y
pip install -e /path/to/sdk

# Verify versions
pip list | grep langgraph
# Should show:
#   langgraph                 1.0.2
#   langgraph-checkpoint      2.1.2

# Test checkpoint works
# (run Swisper request that uses agents)
# Should complete without errors
```

**Action 4: Release SDK v0.3.3** (1 hour)
- Same features as v0.3.2
- Fixed dependencies
- Mark v0.3.2 as broken in release notes

**Total Time:** ~2 hours to fixed release

---

### **Our Current Workaround:**

**We manually downgraded:**
```bash
pip install 'langgraph-checkpoint==2.1.2' --force-reinstall
```

**This works, but:**
- Every user will hit this issue
- They won't know how to fix it
- Will create support tickets
- Will lose trust in SDK

**Better:** Fix in SDK so users never see it!

---

## 📞 Escalation

**Severity:** P0 - Production Blocker  
**Impact:** Breaks all users who upgrade to SDK v0.3.2  
**Users Affected:** Anyone using LangGraph with checkpointing  
**Timeline:** Need fix within 24 hours

**Swisper Team Status:**
- ✅ Identified root cause
- ✅ Tested workaround (works)
- ✅ Provided exact fix (30 minutes)
- ⏳ Waiting for SDK v0.3.3 release

**We can test SDK v0.3.3 immediately when ready!**

---

**This is a critical SDK dependency issue - not a minor bug. Needs immediate hotfix release!** 🚨

