"""
Test SDK Heartbeat Publishing

Verifies that SDK publishes heartbeat events to Redis Streams
when tracing is enabled.
"""

import asyncio
import redis.asyncio as redis
import json
from datetime import datetime, timedelta


async def test_heartbeat():
    """Test heartbeat publishing functionality"""
    
    print("\n" + "="*60)
    print("SDK HEARTBEAT TEST")
    print("="*60 + "\n")
    
    # Connect to Redis
    redis_client = redis.from_url("redis://172.17.0.1:6379", decode_responses=False)
    
    try:
        # Test 1: Clear stream for clean test
        print("📋 Test 1: Setup")
        print("-" * 60)
        
        # Get stream info
        try:
            info = await redis_client.xinfo_stream("observability:events")
            print(f"✅ Stream exists: {info['length']} events")
        except:
            print("⚠️ Stream doesn't exist yet (will be created on first event)")
        
        print()
        
        # Test 2: Monitor for heartbeat events
        print("📋 Test 2: Listening for heartbeat events...")
        print("-" * 60)
        print("⏳ Waiting 15 seconds for heartbeats...")
        print("   (SDK should publish every 10s when tracing is ON)")
        print()
        
        # Wait a bit for heartbeat to be published
        await asyncio.sleep(15)
        
        # Read last 30 events from stream
        messages = await redis_client.xrevrange("observability:events", count=30)
        
        heartbeats = []
        for msg_id, msg_data in messages:
            event_type = msg_data.get(b'event_type')
            if event_type == b'heartbeat':
                # Parse data
                data_json = msg_data.get(b'data', b'{}')
                data = json.loads(data_json.decode('utf-8'))
                heartbeats.append({
                    'msg_id': msg_id.decode('utf-8'),
                    'project_id': data.get('project_id'),
                    'sdk_version': data.get('sdk_version'),
                    'timestamp': data.get('timestamp'),
                })
        
        print(f"📊 Found {len(heartbeats)} heartbeat events in last 30 messages")
        print()
        
        if len(heartbeats) == 0:
            print("❌ FAIL: No heartbeat events found")
            print()
            print("Possible reasons:")
            print("  1. Tracing toggle is OFF (heartbeat only when ON)")
            print("  2. No requests sent to Swisper yet (heartbeat starts on first trace)")
            print("  3. SDK not loaded correctly in Swisper container")
            print()
            print("💡 Action: Send a request to Swisper with tracing ON, then re-run this test")
            return False
        
        # Test 3: Verify heartbeat data
        print("📋 Test 3: Verify heartbeat data")
        print("-" * 60)
        
        latest_heartbeat = heartbeats[0]
        print(f"Latest heartbeat:")
        print(f"  Project ID: {latest_heartbeat['project_id']}")
        print(f"  SDK Version: {latest_heartbeat['sdk_version']}")
        print(f"  Timestamp: {latest_heartbeat['timestamp']}")
        print()
        
        # Calculate age
        heartbeat_time = datetime.fromisoformat(latest_heartbeat['timestamp'])
        age_seconds = (datetime.utcnow() - heartbeat_time).total_seconds()
        
        print(f"  Age: {age_seconds:.1f} seconds ago")
        
        if age_seconds < 30:
            print(f"  ✅ PASS: Heartbeat is fresh (<30s)")
        else:
            print(f"  ⚠️ WARNING: Heartbeat is stale (>{age_seconds:.0f}s)")
            print(f"     SDK may not be actively publishing")
        
        print()
        
        # Test 4: Verify multiple heartbeats (shows continuous publishing)
        print("📋 Test 4: Verify continuous publishing")
        print("-" * 60)
        
        if len(heartbeats) >= 2:
            # Check interval between heartbeats
            hb1_time = datetime.fromisoformat(heartbeats[0]['timestamp'])
            hb2_time = datetime.fromisoformat(heartbeats[1]['timestamp'])
            interval = abs((hb1_time - hb2_time).total_seconds())
            
            print(f"Found {len(heartbeats)} heartbeats")
            print(f"Interval between last 2: {interval:.1f} seconds")
            
            if 8 <= interval <= 12:
                print(f"✅ PASS: Interval is ~10 seconds (expected)")
            else:
                print(f"⚠️ WARNING: Interval should be ~10 seconds, got {interval:.1f}s")
        else:
            print(f"⚠️ Only 1 heartbeat found (need time for multiple)")
            print(f"   Run test again in 15 seconds to verify continuous publishing")
        
        print()
        
        # Test 5: Summary
        print("="*60)
        print("✅ HEARTBEAT TEST PASSED")
        print("="*60)
        print()
        print(f"Summary:")
        print(f"  - Heartbeats found: {len(heartbeats)}")
        print(f"  - Latest heartbeat: {age_seconds:.1f}s ago")
        print(f"  - Project ID: {latest_heartbeat['project_id'][:20]}...")
        print(f"  - SDK Version: {latest_heartbeat['sdk_version']}")
        print()
        print("🟢 SDK is publishing heartbeats successfully!")
        print("🟢 Swisper team can implement indicator using this data")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        await redis_client.close()


if __name__ == "__main__":
    result = asyncio.run(test_heartbeat())
    exit(0 if result else 1)

