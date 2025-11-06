# SDK Migration Guide: v0.3.4 → v0.4.0

**Date:** 2025-11-06  
**Migration Time:** ~15 minutes  
**Breaking Changes:** None (backward compatible with deprecation warnings)

---

## 🎯 What's New in v0.4.0

### **Major Features:**

1. 🚀 **Redis Streams Architecture** - 50x faster (500ms → 10ms overhead)
2. 🧠 **LLM Reasoning Capture** - See thinking process (`<think>...</think>`)
3. 📡 **Connection Status** - Heartbeat-based health monitoring
4. ⚙️ **Per-Node Configuration** - Control reasoning capture per node

### **Performance Improvements:**

| Metric | v0.3.4 (HTTP) | v0.4.0 (Redis) | Improvement |
|--------|---------------|----------------|-------------|
| Observation overhead | 50-100ms | 1-2ms | **50x faster** |
| 5 nodes total | 500ms | 10ms | **50x faster** |
| User-facing impact | Noticeable | Imperceptible | ✅ Zero |

---

## 📋 Migration Checklist

- [ ] Install SDK v0.4.0
- [ ] Add Redis configuration
- [ ] Update initialization code
- [ ] Configure reasoning capture (optional)
- [ ] Restart application
- [ ] Verify connection status
- [ ] Test with sample request

**Estimated Time:** 15 minutes

---

## 🔧 Step-by-Step Migration

### **Step 1: Install SDK v0.4.0** (2 minutes)

```bash
# Uninstall old version
pip uninstall swisper-studio-sdk -y

# Install new version
pip install swisper-studio-sdk==0.4.0

# Or if using local development:
pip install -e /path/to/swisper_studio/sdk

# Verify installation
python -c "import swisper_studio_sdk; print(f'SDK Version: {swisper_studio_sdk.__version__}')"
# Should show: SDK Version: 0.4.0
```

**Dependencies Added:**
- `redis>=5.0.0` (automatically installed)

---

### **Step 2: Update Configuration** (5 minutes)

#### **Add to your `config.py` or `.env`:**

```python
# SwisperStudio Observability (Redis Streams)
SWISPER_STUDIO_REDIS_URL: str = "redis://redis:6379"  # Your Redis instance
SWISPER_STUDIO_STREAM_NAME: str = "observability:events"
SWISPER_STUDIO_PROJECT_ID: str = "YOUR-PROJECT-ID-FROM-SWISPERSTUDIO"

# Optional: Reasoning capture settings
SWISPER_STUDIO_CAPTURE_REASONING: bool = True  # Default: True
SWISPER_STUDIO_REASONING_MAX_LENGTH: int = 50000  # 50 KB default
```

#### **Remove (deprecated, but won't break if left):**

```python
# OLD HTTP configuration (v0.3.x) - can be removed
# SWISPER_STUDIO_URL: str = "http://..."
# SWISPER_STUDIO_API_KEY: str = "..."
```

---

### **Step 3: Update Initialization Code** (5 minutes)

#### **Before (v0.3.4):**

```python
# In your main.py or startup code
from swisper_studio_sdk import initialize_tracing

# Sync initialization (HTTP-based)
initialize_tracing(
    api_url=settings.SWISPER_STUDIO_URL,
    api_key=settings.SWISPER_STUDIO_API_KEY,
    project_id=settings.SWISPER_STUDIO_PROJECT_ID,
)
```

#### **After (v0.4.0 - Recommended):**

```python
# In your main.py or startup code
from swisper_studio_sdk import initialize_redis_publisher

# Async initialization (Redis Streams-based)
await initialize_redis_publisher(
    redis_url=settings.SWISPER_STUDIO_REDIS_URL,
    stream_name=settings.SWISPER_STUDIO_STREAM_NAME,
    project_id=settings.SWISPER_STUDIO_PROJECT_ID,
    verify_consumer=True,  # Check if SwisperStudio consumer is running
)
logger.info("✅ SwisperStudio observability initialized (Redis Streams)")
```

#### **Migration Note:**

If your startup is **not async**, wrap it:

```python
# Option A: Make startup async
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_redis_publisher(...)
    yield
    # Shutdown
    from swisper_studio_sdk import close_redis_publisher
    await close_redis_publisher()

app = FastAPI(lifespan=lifespan)

# Option B: Run in background task
@app.on_event("startup")
def startup():
    asyncio.create_task(initialize_redis_publisher(...))
```

---

### **Step 4: Optional - Configure Reasoning Capture** (3 minutes)

Control reasoning capture per node:

```python
from swisper_studio_sdk import traced

# Enable reasoning with custom limit
@traced("classify_intent", capture_reasoning=True, reasoning_max_length=20000)
async def classify_intent_node(state):
    return state

# Disable reasoning for specific nodes (faster, less data)
@traced("memory_node", capture_reasoning=False)
async def memory_node(state):
    return state

# Use default settings (reasoning enabled, 50KB limit)
@traced("global_planner")
async def global_planner_node(state):
    return state
```

---

### **Step 5: Restart & Verify** (3 minutes)

```bash
# Restart your application
docker compose restart backend

# Check logs for successful initialization
docker compose logs backend | grep "SwisperStudio"
```

**Expected logs:**

```log
✅ Redis connectivity: OK
✅ Redis write permission: OK
✅ Consumer detected: HEALTHY
   Last seen: 2.3 seconds ago
   Events processed: 1,247
   Stream length: 0
✅ Redis publisher initialized successfully
   Stream: observability:events
   Project: 0d7aa606-cb29-4a31-8a59-50fa61151a32
```

**If consumer not running:**

```log
✅ Redis connectivity: OK
✅ Redis write permission: OK
⚠️ Consumer not detected
   Events will queue until consumer starts
✅ Redis publisher initialized successfully
```

This is **OK** - events will queue in Redis until SwisperStudio consumer starts.

---

### **Step 6: Test** (2 minutes)

Send a test request through your application:

```bash
# Example: Send message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Test observability"}'

# Wait 2 seconds for processing
sleep 2

# Check SwisperStudio UI
# http://localhost:3000/projects/YOUR-PROJECT-ID/tracing
```

**What to expect in SwisperStudio:**

```
global_supervisor (AGENT)
  ├─ classify_intent (LLM) [Prompt] [Reasoning] [Response] ✅
  ├─ memory_node (PROC)
  ├─ global_planner (LLM) [Prompt] [Reasoning] [Response] ✅
  └─ user_interface (LLM) [Prompt] [Response] ✅
```

**Click [Reasoning] button:**
- See LLM thinking process
- Markdown-formatted
- Truncated at 50KB if longer
- Character count shown

---

## 🔄 Rollback Plan

If you need to roll back to v0.3.4:

```bash
# Uninstall v0.4.0
pip uninstall swisper-studio-sdk -y

# Install v0.3.4
pip install swisper-studio-sdk==0.3.4

# Revert code changes
# 1. Change initialize_redis_publisher() back to initialize_tracing()
# 2. Remove Redis configuration
# 3. Add back HTTP configuration

# Restart
docker compose restart backend
```

**Note:** v0.3.4 will continue working with no issues.

---

## ⚠️ Breaking Changes

**None!** v0.4.0 is fully backward compatible.

**Deprecated (but still works):**
- `initialize_tracing()` - use `initialize_redis_publisher()` instead

**Will be removed in v1.0.0:**
- HTTP-based tracing (replaced by Redis Streams)

---

## 🆕 New Features Guide

### **Feature 1: Connection Status Verification**

SDK automatically checks if SwisperStudio consumer is healthy:

```python
verification = await initialize_redis_publisher(
    redis_url="redis://redis:6379",
    project_id="...",
    verify_consumer=True,  # ← Checks consumer heartbeat
)

# Returns:
# {
#     "redis": True,      # Redis connectivity
#     "write": True,      # Write permission
#     "consumer": True,   # Consumer detected and healthy
# }
```

**Logs show status:**
```log
✅ Redis connectivity: OK
✅ Consumer detected: HEALTHY
   Last seen: 3.2 seconds ago
   Events processed: 5,432
   Stream length: 2
```

---

### **Feature 2: LLM Reasoning Capture**

Automatically captures `<think>...</think>` tags from models like DeepSeek R1:

**SDK (automatic):**
- Reasoning chunks captured during LLM call
- Accumulated and sent to SwisperStudio
- Truncated at 50KB (configurable)

**Frontend:**
- [Reasoning] button appears if reasoning available
- Click to view thinking process
- Markdown-formatted with syntax highlighting

**Configuration:**

```python
# Global default
SWISPER_STUDIO_CAPTURE_REASONING: bool = True
SWISPER_STUDIO_REASONING_MAX_LENGTH: int = 50000  # 50 KB

# Per-node override
@traced("classify_intent", capture_reasoning=True, reasoning_max_length=10000)
async def classify_intent_node(state):
    ...

@traced("memory_node", capture_reasoning=False)  # Disable for this node
async def memory_node(state):
    ...
```

---

### **Feature 3: Streaming Response Capture**

Now captures final responses from streaming LLM calls:

**Before (v0.3.4):**
- ❌ `user_interface` node showed as PROC (no LLM data)

**After (v0.4.0):**
- ✅ `user_interface` node shows as LLM
- ✅ [Prompt] button shows prompts
- ✅ [Response] shows full streamed response

**Zero performance impact** - streaming passes through immediately.

---

## 📊 Feature Comparison

| Feature | v0.3.4 | v0.4.0 |
|---------|--------|--------|
| **Architecture** | HTTP | Redis Streams |
| **Performance** | 500ms overhead | 10ms overhead |
| **LLM Coverage** | 70% (structured only) | 100% (structured + streaming) |
| **Reasoning** | ❌ Not captured | ✅ Captured with <think> tags |
| **Connection Status** | ❌ No verification | ✅ Heartbeat-based |
| **Configuration** | Global only | Global + per-node |
| **Memory Leaks** | Possible | ✅ Auto-cleanup |

---

## 🐛 Troubleshooting

### **Issue: "Consumer not detected"**

**Cause:** SwisperStudio consumer not running

**Solution:**
```bash
# Check SwisperStudio backend is running
docker compose ps

# Check consumer logs
docker compose logs backend | grep "Observability consumer"

# Should see:
# ✅ Observability consumer started
# ✅ Consumer heartbeat started
```

---

### **Issue: "Cannot connect to Redis"**

**Cause:** Redis URL incorrect or Redis not running

**Solution:**
```bash
# Verify Redis is running
docker compose ps | grep redis

# Test Redis connectivity
redis-cli -h localhost -p 6379 ping
# Should return: PONG

# Check Redis URL in config
echo $SWISPER_STUDIO_REDIS_URL
```

---

### **Issue: "Reasoning not showing in UI"**

**Cause:** Model doesn't produce `<think>` tags

**Solution:**
- Only certain models produce reasoning (DeepSeek R1, o1, etc.)
- GPT-4 Turbo, Claude, etc. don't use `<think>` tags
- This is expected behavior - reasoning button only shows when available

---

### **Issue: "Events not appearing in SwisperStudio"**

**Debugging steps:**

```bash
# 1. Check events are being published
redis-cli -h localhost -p 6379 XLEN observability:events
# Should show number of queued events

# 2. Check consumer is processing
docker compose logs backend | grep "Processed.*events"
# Should see: ✅ Processed 5 events

# 3. Check database
# In SwisperStudio, query traces table
# Should have recent traces
```

---

## 📈 Performance Validation

After migration, verify performance improvement:

**Measure overhead:**

```bash
# Send request and measure time
time curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'

# Compare:
# - v0.3.4: ~2.5-3.0 seconds
# - v0.4.0: ~2.0-2.1 seconds (500ms faster!)
```

---

## ✅ Success Criteria

After migration, you should have:

- ✅ SDK version shows 0.4.0
- ✅ No errors in startup logs
- ✅ Consumer heartbeat detected
- ✅ Traces appear in SwisperStudio
- ✅ Reasoning visible for applicable LLMs
- ✅ Response time improved by ~500ms

---

## 🆘 Need Help?

**Common issues:**
1. Redis connectivity → Check Redis URL and network
2. Consumer not starting → Check SwisperStudio backend logs
3. Events not appearing → Check Redis stream length

**Contact:**
- Check GitHub issues
- Review troubleshooting guide
- Check SwisperStudio documentation

---

## 📚 Additional Resources

- **SDK README:** `/sdk/README.md` - Full API reference
- **Architecture Doc:** `/docs/plans/COMPREHENSIVE_SDK_UPGRADE_PLAN.md`
- **Reasoning Plan:** `/docs/plans/SDK_LLM_REASONING_CAPTURE_PLAN.md`

---

**Happy observability! 🚀**

