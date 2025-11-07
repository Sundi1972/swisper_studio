# Bug Report: SDK Logger Issues + Q2 Toggle Not Working

**Date:** 2025-11-06
**Reporter:** Swisper Team (Helvetiq)
**SDK Version:** v0.5.0
**Environment:** Production testing with tracing toggle
**Priority:** HIGH (P1)

---

## 🎯 Executive Summary

**Two critical bugs discovered during Q2 Tracing Toggle testing:**

1. ✅ **FIXED BY US LOcally:** Missing logger imports in 2 SDK files (decorator.py, graph_wrapper.py) still needs to be updated in swisper_studio side
2. ❌ **NEEDS YOUR ATTENTION:** Q2 Tracing Toggle not working - traces still created when toggle is OFF

**Impact:**
- Logger bugs caused crashes when Q2 toggle was OFF
- After fixing logger bugs, toggle still doesn't prevent trace creation
- User functionality not affected, but Q2 feature non-functional

---

## 🐛 BUG #1: Missing Logger Imports (FIXED)

**Status:** ✅ RESOLVED (by Swisper team locally, still needs to be fixed in the sdk by studio team !!!!!!)
**Severity:** HIGH (caused crashes)
**Files Affected:** 2

---

### Bug #1a: decorator.py Missing Logger

**File:** `sdk/swisper_studio_sdk/tracing/decorator.py`
**Lines Affected:** 259, 263, 265

**Error:**
```
NameError: name 'logger' is not defined
asyncio - ERROR - Task exception was never retrieved
```

**Full Traceback:**
```python
Traceback (most recent call last):
  File "/app/swisper_studio_sdk_v050/swisper_studio_sdk/tracing/decorator.py", line 259, in async_wrapper
    logger.debug(f"Extracted {tool_count} tools from {obs_name} observation")
    ^^^^^^
NameError: name 'logger' is not defined
```

**When It Occurs:**
- After every agent execution
- During tool observation extraction
- Background task (doesn't block request)

**Impact:**
- 3 asyncio errors per request in logs
- Tool observations may not be created
- Ugly error messages
- User functionality still works (background task)

**Code Issue:**
```python
# File uses logger but never imports it!

# Missing at top of file:
# import logging
# logger = logging.getLogger(__name__)

# But used on line 259:
logger.debug(f"Extracted {tool_count} tools from {obs_name} observation")
```

**Fix Applied (by Swisper team):**
```python
# Added at top of decorator.py:
import logging  # Line 11
logger = logging.getLogger(__name__)  # Line 21
```

**Committed:** SwisperStudio repo commit `5a1c6e0`

**Testing Evidence:**
- Before fix: 3 asyncio errors per request
- After fix: 0 errors, clean logs
- Test correlation ID: c5f02aad-2338-45e3-94c6-7d0c8b7c8fe1

---

### Bug #1b: graph_wrapper.py Missing Logger (Q2 Toggle Code)

**File:** `sdk/swisper_studio_sdk/tracing/graph_wrapper.py`
**Lines Affected:** 110 (Q2 toggle log message)

**Error:**
```
NameError: name 'logger' is not defined
```

**Full Traceback:**
```python
Traceback (most recent call last):
  File "/app/swisper_studio_sdk_v050/swisper_studio_sdk/tracing/graph_wrapper.py", line 110, in traced_ainvoke
    logger.info(f"⏸️ Tracing disabled for project {project_id[:8]}..., skipping trace creation")
    ^^^^^^
NameError: name 'logger' is not defined
```

**When It Occurs:**
- **ONLY when Q2 toggle is OFF**
- When `is_tracing_enabled_for_project()` returns False
- Tries to log "Tracing disabled" message
- **This is why we didn't see it until we tested toggle OFF!**

**Impact:**
- Request crashes when tracing is OFF
- No response delivered to user
- Q2 toggle feature completely broken
- Makes toggle unusable

**Code Issue:**
```python
# File uses logger but never imports it!

# Missing at top of file:
# import logging
# logger = logging.getLogger(__name__)

# But used on line 110 (Q2 toggle code):
if not tracing_enabled:
    logger.info(f"⏸️ Tracing disabled for project {project_id[:8]}..., skipping trace creation")
    return await original_ainvoke(input_state, config, **invoke_kwargs)
```

**Fix Applied (by Swisper team):**
```python
# Added at top of graph_wrapper.py:
import logging  # Line 20
logger = logging.getLogger(__name__)  # Line 29
```

**Committed:** SwisperStudio repo commit `5a1c6e0` (same commit)

**Testing Evidence:**
- Before fix: Request crashed when toggle OFF, NameError
- After fix: Request completes, but toggle still doesn't work (see Bug #2)

---

## 🐛 BUG #2: Q2 Tracing Toggle Not Preventing Trace Creation (NEEDS FIX)

**Status:** ❌ OPEN (needs SwisperStudio team investigation)
**Severity:** HIGH (Q2 feature non-functional)
**Priority:** P1

---

### Problem Description

**Expected Behavior:**
1. User disables tracing in SwisperStudio UI
2. SwisperStudio sets `tracing:PROJECT_ID:enabled` = `false` in Redis
3. Swisper SDK checks Redis cache on each request
4. If `false`, SDK skips trace creation
5. No traces sent to SwisperStudio
6. No observations created

**Actual Behavior:**
1. User disables tracing in SwisperStudio UI ✅
2. SwisperStudio sets Redis cache (assumed working) ✅
3. Swisper SDK **does NOT skip trace creation** ❌
4. Traces **ARE created and sent** ❌
5. Observations **ARE stored in database** ❌
6. Toggle has **NO EFFECT** ❌

---

### Testing Evidence

**Test Setup:**
- Date: 2025-11-06, 07:05 UTC
- Action: Disabled tracing in SwisperStudio UI
- Query: "hi there swisper" (simple chat)
- Expected: No traces created

**Swisper Backend Logs (Correlation: affd72a2-af9d-43fe-b53a-2b93552d2210):**
```
07:05:01 - GlobalSupervisor started
07:05:01 - Graph wrapped with SwisperStudio tracing
07:05:04 - Intent classification
07:05:05 - Memory node
07:05:05 - User interface
07:05:08 - GlobalSupervisor complete

❌ NO "⏸️ Tracing disabled" message
❌ NO "skipping trace creation" message
✅ Request completed normally
```

**SwisperStudio Backend Logs:**
```
07:05:04 - INSERT INTO observations (memory_node)
07:05:05 - INSERT INTO observations (user_interface)
07:05:08 - UPDATE observations (with end times, tokens, costs)

❌ Observations WERE created
❌ Traces WERE stored
❌ Toggle had NO EFFECT
```

**Conclusion:** Toggle is being ignored, traces created anyway

---

### Possible Root Causes

**Theory 1: Toggle Check Not Being Called**

The `is_tracing_enabled_for_project()` function exists in SDK but may not be invoked in the graph wrapper flow.

Check:
- Does `graph_wrapper.py` actually call the function?
- Is it in the right place in the execution flow?
- Is the project_id passed correctly?

**Theory 2: Redis Cache Key Not Set**

SwisperStudio UI toggles the database value, but Redis cache may not be updated.

Check:
- Does `tracing_config_service.py` invalidate cache on toggle?
- Is cache key format correct: `tracing:{project_id}:enabled`?
- Does cache contain `b"false"` or `b"true"`?

**Theory 3: Project ID Mismatch**

SDK may be checking wrong project ID.

Check:
- What project_id does SDK use?
- Is it from config (settings.SWISPER_STUDIO_PROJECT_ID)?
- Does it match SwisperStudio project: `0d7aa606-cb29-4a31-8a59-50fa61151a32`?

**Theory 4: Fail-Open Behavior**

SDK defaults to "enabled" when cache check fails.

Check:
- Is cache miss returning default=True?
- Is Redis connection failing silently?
- Are errors being swallowed?

---

### How to Debug

**Step 1: Verify Redis Cache**

```bash
# Check if cache key exists
docker exec helvetiq-redis redis-cli GET "tracing:0d7aa606-cb29-4a31-8a59-50fa61151a32:enabled"

# Should return: "false" (when toggle OFF)
# Or: nil (if not set)
```

**Step 2: Add Debug Logging**

In `graph_wrapper.py`, add logs before toggle check:
```python
project_id = get_project_id()
print(f"DEBUG: Project ID = {project_id}")

if project_id:
    tracing_enabled = await is_tracing_enabled_for_project(project_id)
    print(f"DEBUG: Tracing enabled = {tracing_enabled}")

    if not tracing_enabled:
        logger.info(f"⏸️ Tracing disabled for project {project_id[:8]}...")
        return await original_ainvoke(input_state, config, **invoke_kwargs)
```

**Step 3: Verify Toggle API**

```bash
# Check database value
docker exec swisper_studio_postgres psql -U postgres -d swisper_studio -c \
  "SELECT id, tracing_enabled FROM projects WHERE id='0d7aa606-cb29-4a31-8a59-50fa61151a32';"

# Toggle OFF via API
curl -X PATCH http://localhost:8001/api/v1/projects/0d7aa606-cb29-4a31-8a59-50fa61151a32/tracing \
  -H "Content-Type: application/json" \
  -d '{"tracing_enabled": false}'

# Check Redis cache was set
docker exec helvetiq-redis redis-cli GET "tracing:0d7aa606-cb29-4a31-8a59-50fa61151a32:enabled"
```

**Step 4: Test Toggle Check Function**

```python
# In Swisper backend container
from swisper_studio_sdk.tracing.redis_publisher import is_tracing_enabled_for_project

result = await is_tracing_enabled_for_project("0d7aa606-cb29-4a31-8a59-50fa61151a32")
print(f"Tracing enabled: {result}")
# Should return False when toggle is OFF
```

---

### Code Review Needed

**File:** `sdk/swisper_studio_sdk/tracing/graph_wrapper.py`

**Line ~110 (Q2 toggle check):**

Please verify this code exists and is being executed:
```python
# Q2: Check if tracing is enabled for this project (per-request check)
project_id = get_project_id()
if project_id:
    tracing_enabled = await is_tracing_enabled_for_project(project_id)
    if not tracing_enabled:
        logger.info(f"⏸️ Tracing disabled for project {project_id[:8]}..., skipping trace creation")
        # Run graph without tracing
        return await original_ainvoke(input_state, config, **invoke_kwargs)
```

**Questions:**
1. Is this code actually in the traced_ainvoke function?
2. Is it placed BEFORE the trace creation?
3. Is `get_project_id()` returning the correct project ID?
4. Is `is_tracing_enabled_for_project()` checking the right Redis key?

---

## 📊 Impact Assessment

### Logger Bugs (Bug #1)

**User Impact:**
- ⚠️ Medium: Ugly errors in logs, tool observations may fail
- ✅ Workaround available: We fixed it locally
- ✅ Resolution: Fixed in commit 5a1c6e0

**Developer Impact:**
- Anyone using SDK v0.5.0 will encounter these errors
- Affects tool observation creation
- Makes logs noisy

**Recommended Action:**
- ✅ Include our fixes in next SDK release
- ✅ Add logger imports to all SDK files that use logging
- ✅ Add linter check for logger usage without import

---

### Q2 Toggle Not Working (Bug #2)

**User Impact:**
- ❌ High: Q2 feature completely non-functional
- ❌ Users cannot disable tracing to save costs
- ❌ No way to control observability overhead

**Developer Impact:**
- Integration testing blocked for Q2 feature
- Cannot verify toggle works as designed
- Documentation (Q2_TRACING_TOGGLE_DEPLOYMENT_GUIDE) not usable

**Business Impact:**
- Q2 feature cannot be released
- Cost control feature unavailable
- Promised functionality not delivered

**Recommended Action:**
- 🔴 HIGH PRIORITY: Debug and fix immediately
- Verify Redis cache integration
- Test end-to-end toggle flow
- Provide fixed SDK to Swisper team

---

## ✅ What We Fixed (Logger Bugs)

### Our Fixes (Commit 5a1c6e0)

**File 1:** `sdk/swisper_studio_sdk/tracing/decorator.py`

```diff
+ import logging
  import time
  import uuid
  from datetime import datetime
  from typing import TypeVar, Callable

+ logger = logging.getLogger(__name__)
```

**File 2:** `sdk/swisper_studio_sdk/tracing/graph_wrapper.py`

```diff
  from typing import Type, TypeVar
  from langgraph.graph import StateGraph
  import copy
  import functools
+ import logging
  import uuid
  from datetime import datetime

+ logger = logging.getLogger(__name__)
```

**Both files committed to SwisperStudio repo:** `feature/week-1-backend-foundation` branch, commit `5a1c6e0`

**Testing Evidence:**
- Before: 3+ asyncio errors per request
- After: 0 errors, clean logs
- Verified in correlation ID: c5f02aad-2338-45e3-94c6-7d0c8b7c8fe1

---

## ❌ What Still Needs Fixing (Q2 Toggle)

### Expected Behavior (Not Working)

**When Tracing Toggle is OFF:**

1. User disables tracing in SwisperStudio UI
2. SwisperStudio backend:
   - Updates `projects.tracing_enabled = false` in database
   - Sets Redis cache: `tracing:PROJECT_ID:enabled = "false"`
   - Cache TTL: 5 minutes
3. Swisper sends request
4. SDK calls `is_tracing_enabled_for_project(project_id)`
5. SDK reads Redis cache
6. Cache returns `b"false"`
7. SDK skips trace creation
8. SDK logs: "⏸️ Tracing disabled for project..."
9. Request processes normally WITHOUT creating trace
10. **No trace in SwisperStudio**

**What Actually Happens:**

1. User disables tracing ✅
2. SwisperStudio updates database ✅ (assumed)
3. Redis cache set? ❓ (unknown)
4. Swisper sends request ✅
5. SDK calls toggle check? ❓ (no log evidence)
6. Cache read? ❓ (unknown)
7. ❌ SDK creates trace anyway
8. ❌ No "Tracing disabled" message
9. Request processes normally ✅
10. ❌ **Trace IS in SwisperStudio** (unwanted!)

---

### Debug Information Needed

**From SwisperStudio Side:**

1. **Verify tracing_config_service.py:**
   - Does it set Redis cache on toggle?
   - What is the exact cache key format?
   - What are the cache values? (`"true"` or `b"true"` or boolean?)

2. **Check Database:**
   ```sql
   SELECT id, tracing_enabled FROM projects
   WHERE id = '0d7aa606-cb29-4a31-8a59-50fa61151a32';
   ```
   - Is `tracing_enabled` actually `false`?

3. **Check Redis:**
   ```bash
   redis-cli GET "tracing:0d7aa606-cb29-4a31-8a59-50fa61151a32:enabled"
   ```
   - Does key exist?
   - What is the value?

4. **Review graph_wrapper.py implementation:**
   - Is toggle check code actually in the released SDK?
   - Is it in the right place (before trace creation)?
   - Is `get_project_id()` working?

---

### Code to Verify

**File:** `sdk/swisper_studio_sdk/tracing/graph_wrapper.py`

**Expected around line 110:**
```python
async def traced_ainvoke(self, input_state, config=None, **invoke_kwargs):
    """
    Traced version of ainvoke that creates observations

    Q2: Per-request tracing toggle check (1-2ms overhead)
    """
    redis_client = get_redis_client()

    if not redis_client:
        # Tracing not initialized, run normally
        return await original_ainvoke(input_state, config, **invoke_kwargs)

    # Q2: Check if tracing is enabled for this project (per-request check)
    project_id = get_project_id()
    if project_id:
        tracing_enabled = await is_tracing_enabled_for_project(project_id)
        if not tracing_enabled:
            logger.info(f"⏸️ Tracing disabled for project {project_id[:8]}..., skipping trace creation")
            # Run graph without tracing
            return await original_ainvoke(input_state, config, **invoke_kwargs)

    # Continue with trace creation...
```

**Please verify:**
- [ ] This code exists in your SDK
- [ ] It's placed BEFORE trace creation
- [ ] `get_project_id()` is implemented
- [ ] It returns the correct project ID
- [ ] `is_tracing_enabled_for_project()` is implemented
- [ ] It reads the correct Redis key
- [ ] It returns boolean correctly

---

### Testing Request

**Please provide:**

1. **Current graph_wrapper.py code** (lines 90-150)
   - So we can see the actual toggle implementation

2. **Redis cache check results:**
   ```bash
   # After toggling OFF in UI:
   redis-cli GET "tracing:0d7aa606-cb29-4a31-8a59-50fa61151a32:enabled"
   ```

3. **Database check results:**
   ```sql
   SELECT tracing_enabled FROM projects
   WHERE id = '0d7aa606-cb29-4a31-8a59-50fa61151a32';
   ```

4. **Verification of functions:**
   - Does `get_project_id()` exist and return project ID?
   - Does `is_tracing_enabled_for_project()` exist in redis_publisher.py?

---

## 🔬 Diagnostic Steps We Tried

**What We Tested:**

1. ✅ Disabled tracing in SwisperStudio UI
2. ✅ Sent test request through Swisper
3. ✅ Checked Swisper logs for toggle messages (none found)
4. ✅ Checked SwisperStudio logs for trace creation (traces created!)
5. ✅ Verified request completed (worked, but with traces)

**What We Found:**

- ❌ No "Tracing disabled" log messages
- ❌ No "skipping trace creation" messages
- ❌ Traces were created anyway
- ✅ Request completed successfully (logger fix worked)

**Conclusion:**
- Toggle check either not called OR returning wrong value
- SDK may not have complete Q2 implementation
- Or integration issue with Redis cache

---

## 📋 Recommended Actions

### For SwisperStudio Team (Urgent)

**Priority 1: Fix Q2 Toggle (HIGH)**

1. Verify `graph_wrapper.py` has complete Q2 toggle code
2. Test `is_tracing_enabled_for_project()` function locally
3. Verify Redis cache key format matches expectations
4. Test toggle end-to-end in SwisperStudio environment
5. Provide verified working SDK to Swisper team

**Priority 2: Add Comprehensive SDK Testing**

1. Add unit tests for logger existence in all files
2. Add integration test for Q2 toggle ON/OFF
3. Add Redis cache tests
4. Add linter to catch logger usage without import

**Priority 3: Documentation**

1. Update Q2_TRACING_TOGGLE_DEPLOYMENT_GUIDE.md with verified steps
2. Document known issues and limitations
3. Provide troubleshooting guide

---

### For Swisper Team (Us)

**Immediate:**
1. ✅ Turn tracing back ON in SwisperStudio (keep system working)
2. ✅ Continue testing main integration (agents, multi-agent)
3. ✅ Document Q2 toggle as "not working yet"
4. ✅ Include logger fixes in our commits (done)

**When SDK Fixed:**
1. Get updated SDK from SwisperStudio team
2. Install in Swisper backend
3. Test Q2 toggle again
4. Verify traces are NOT created when OFF
5. Verify traces resume when ON
6. Document results

---

## 📊 Testing Matrix

### Logger Bugs (Bug #1)

| Test Case | Before Fix | After Fix |
|-----------|-----------|-----------|
| Normal request (tracing ON) | ❌ 3 asyncio errors | ✅ 0 errors |
| Tool observations created | ⚠️ May fail | ✅ Success |
| Logs clean | ❌ Noisy | ✅ Clean |

**Status:** ✅ RESOLVED

---

### Q2 Toggle (Bug #2)

| Test Case | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Toggle OFF → Send request | No trace | ❌ Trace created | ❌ FAIL |
| Toggle OFF → Check logs | "Tracing disabled" | ❌ No message | ❌ FAIL |
| Toggle ON → Send request | Trace created | ✅ Trace created | ✅ PASS |
| SwisperStudio UI toggle | Changes state | ✅ Works | ✅ PASS |
| Database value | Updates | ✅ Assumed | ❓ Needs verify |
| Redis cache | Set to "false" | ❓ Unknown | ❓ Needs verify |

**Status:** ❌ NOT WORKING

---

## 📝 Attachments

### Log Files

**Swisper Backend (Logger errors before fix):**
- Correlation ID: `6321f6e6-42de-48bc-91b2-986ec6f1eb65`
- Time: 18:55:36, 18:57:10, 18:58:08 UTC
- Error: `asyncio ERROR: Task exception was never retrieved`
- File: `decorator.py:259`

**Swisper Backend (Q2 toggle test):**
- Correlation ID: `affd72a2-af9d-43fe-b53a-2b93552d2210`
- Time: 07:05:01 - 07:05:08 UTC
- Toggle: OFF
- Result: Traces created anyway

**SwisperStudio Backend (Q2 toggle test):**
- Time: 07:05:04 - 07:05:08 UTC
- Observations inserted: `memory_node`, `user_interface`
- Proof toggle not respected

---

## 🔧 Files Modified (Our Fixes)

**SwisperStudio Repository:**
- `sdk/swisper_studio_sdk/tracing/decorator.py`
- `sdk/swisper_studio_sdk/tracing/graph_wrapper.py`
- Commit: `5a1c6e0`
- Branch: `feature/week-1-backend-foundation`

**Ready to merge** when you approve!

---

## 💬 Summary for SwisperStudio Team

**What We Found:**

1. ✅ **Logger bugs (2 files)** - We fixed them! (commit 5a1c6e0)
   - decorator.py: Missing logger import
   - graph_wrapper.py: Missing logger import
   - Both caused NameError crashes
   - Now working perfectly

2. ❌ **Q2 toggle not working** - Needs your investigation
   - Toggle UI works
   - Database updates (assumed)
   - But SDK doesn't skip trace creation
   - Traces created even when toggle is OFF
   - No "Tracing disabled" log messages

**What We Need:**

- Verify SDK has complete Q2 toggle implementation
- Check Redis cache integration
- Confirm our SDK version has the latest Q2 code
- Provide working SDK or guidance on debugging

**What Works Great:**

- ✅ SDK v0.5.0 integration successful
- ✅ Tool observations working
- ✅ Cost tracking working
- ✅ Multi-agent flow operational
- ✅ All agent fixes working perfectly

**Main integration is a success!** Just need Q2 toggle completed. 🚀

---

## 📞 Contact

**Swisper Team:**
- Fixed logger bugs locally
- Ready to test when Q2 toggle is working
- Can provide additional debug info if needed

**Files for Reference:**
- Our logger fixes: SwisperStudio repo commit `5a1c6e0`
- Test evidence: Correlation IDs in this document
- Integration status: `SESSION_HANDOVER_2025_11_06.md`

---

**Status:** WAITING FOR SWISPERSTUDIO TEAM RESPONSE ON Q2 TOGGLE

**Priority:** P1 (High) - Q2 feature non-functional

---

**End of Bug Report**

