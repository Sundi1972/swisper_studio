# Tracing Indicator - Quick Implementation Guide

**For:** Swisper Team  
**Effort:** 30-60 minutes  
**Date:** 2025-11-07  
**SDK Version:** v0.5.0+heartbeat

---

## 🎯 Goal

Add indicator bubble in Swisper sidebar showing SwisperStudio tracing health.

```
🟢 Green  = Tracing ON + SDK alive (heartbeat <30s)
🟡 Orange = Tracing ON + SDK stale (heartbeat >30s)
⚪ Gray   = Tracing OFF
```

**Why:** Shows not just toggle state, but if SDK is actually publishing!

---

## 💓 **SDK Heartbeat (Already Implemented)**

✅ **SwisperStudio SDK now publishes heartbeat every 10 seconds**

**When:** Only when tracing is enabled (toggle ON)  
**Where:** Redis Stream `observability:events`  
**Format:**
```json
{
  "event_type": "heartbeat",
  "data": {
    "project_id": "0d7aa606-...",
    "sdk_version": "0.5.0",
    "timestamp": "2025-11-07T07:30:15Z"
  }
}
```

---

## 💡 Implementation

### **Backend - Check Status (30-60 mins)**

```python
import redis.asyncio as redis
from datetime import datetime, timedelta

async def get_tracing_status():
    redis_client = redis.from_url("redis://172.17.0.1:6379")
    project_id = "0d7aa606-cb29-4a31-8a59-50fa61151a32"
    
    # 1. Check toggle state
    enabled = await redis_client.get(f"tracing:{project_id}:enabled")
    
    if enabled != b"true":
        return {"status": "gray", "message": "Tracing disabled"}
    
    # 2. Check heartbeat (last 20 events from stream)
    messages = await redis_client.xrevrange("observability:events", count=20)
    
    last_heartbeat = None
    for msg_id, msg_data in messages:
        if msg_data.get(b'event_type') == b'heartbeat':
            # Parse data JSON
            import json
            data = json.loads(msg_data[b'data'])
            last_heartbeat = data['timestamp']
            break
    
    # 3. Calculate age
    if not last_heartbeat:
        return {"status": "gray", "message": "No heartbeat yet"}
    
    heartbeat_time = datetime.fromisoformat(last_heartbeat)
    age = (datetime.utcnow() - heartbeat_time).total_seconds()
    
    if age < 30:
        return {"status": "green", "message": f"Active ({age:.0f}s ago)"}
    else:
        return {"status": "orange", "message": f"Stale ({age:.0f}s ago)"}
```

---

### **Frontend - Show Indicator (30 mins)**

```tsx
// Poll status every 30 seconds
const { data } = useQuery({
  queryKey: ['tracing-status'],
  queryFn: () => api.get('/tracing-status'),
  refetchInterval: 30000,  // 30 seconds
});

// Color mapping
const getBubbleColor = (status: string) => {
  if (status === 'green') return '#4caf50';  // Green
  if (status === 'orange') return '#ff9800'; // Orange
  return '#9e9e9e';  // Gray
};

// In sidebar (next to Overview or any item)
<Box sx={{ position: 'relative' }}>
  <OverviewIcon />
  {data?.status && (
    <Box 
      sx={{
        position: 'absolute',
        top: -2,
        right: -2,
        width: 8,
        height: 8,
        borderRadius: '50%',
        bgcolor: getBubbleColor(data.status),
        border: '1px solid #fff',
      }}
      title={data.message}  // Tooltip: "Active (5s ago)"
    />
  )}
</Box>
```

---

## 📋 What You Need

**All Already Available:**
- ✅ Redis URL: `redis://172.17.0.1:6379` (same as Swisper uses)
- ✅ Stream: `observability:events`
- ✅ Cache key: `tracing:{project_id}:enabled`
- ✅ Heartbeat: Published every 10s by SDK (when toggle ON)

**Your Project ID:**
```
0d7aa606-cb29-4a31-8a59-50fa61151a32
```

---

## ✅ **Summary**

**What SDK Does (Automatic):**
- Publishes heartbeat every 10 seconds when tracing enabled
- Includes project_id, sdk_version, timestamp
- Stops when tracing disabled

**What You Implement:**
1. Backend: Read Redis stream for latest heartbeat (~30 lines)
2. Check toggle state in Redis cache (~5 lines)
3. Return status: green/orange/gray
4. Frontend: Show colored bubble based on status (~15 lines)

**Total Effort:** 30-60 minutes for full health monitoring!
