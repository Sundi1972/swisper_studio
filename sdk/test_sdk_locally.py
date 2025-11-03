#!/usr/bin/env python3
"""
Local SDK test - verify SDK works before integrating with Swisper

This script tests the SDK in isolation to ensure:
1. SDK can be imported
2. Tracing can be initialized
3. Traced graph can be created
4. Observations are sent to SwisperStudio
5. State is captured correctly

Run this BEFORE integrating with Swisper to catch issues early.
"""

import asyncio
from typing import TypedDict
from langgraph.graph import StateGraph
import sys

# Test imports
try:
    from swisper_studio_sdk import create_traced_graph, initialize_tracing
    print("✅ SDK imports successful")
except ImportError as e:
    print(f"❌ Failed to import SDK: {e}")
    print("   Install with: pip install -e /path/to/swisper_studio/sdk")
    sys.exit(1)


# Mock state (similar to GlobalSupervisorState)
class TestState(TypedDict):
    user_message: str
    step_count: int
    result: str | None


# Mock nodes
async def step1_node(state: TestState) -> TestState:
    """Simulates intent_classification"""
    print("  🔹 Step 1: Processing...")
    await asyncio.sleep(0.1)  # Simulate work
    return {
        **state,
        "step_count": state.get("step_count", 0) + 1,
        "intent": "test_intent"  # Adds new field
    }


async def step2_node(state: TestState) -> TestState:
    """Simulates memory_node"""
    print("  🔹 Step 2: Loading...")
    await asyncio.sleep(0.05)
    return {
        **state,
        "step_count": state.get("step_count", 0) + 1,
        "memory": {"fact": "test_fact"}  # Adds new field
    }


async def step3_node(state: TestState) -> TestState:
    """Simulates ui_node"""
    print("  🔹 Step 3: Finalizing...")
    await asyncio.sleep(0.05)
    return {
        **state,
        "step_count": state.get("step_count", 0) + 1,
        "result": "Test complete!"  # Adds final field
    }


async def test_sdk():
    """Test SDK end-to-end"""
    
    print("\n" + "="*60)
    print("SwisperStudio SDK - Local Test")
    print("="*60)
    
    # Step 1: Initialize tracing
    print("\n📡 Step 1: Initializing tracing...")
    try:
        initialize_tracing(
            api_url="http://backend:8000",  # Docker internal network
            api_key="dev-api-key-change-in-production",
            project_id="0d7aa606-cb29-4a31-8a59-50fa61151a32",  # Update with your project ID
            enabled=True
        )
        print("✅ Tracing initialized")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False
    
    # Step 2: Create traced graph
    print("\n🔧 Step 2: Creating traced graph...")
    try:
        graph = create_traced_graph(
            TestState,
            trace_name="sdk_local_test"
        )
        print("✅ Traced graph created")
    except Exception as e:
        print(f"❌ Failed to create graph: {e}")
        return False
    
    # Step 3: Add nodes
    print("\n🏗️  Step 3: Adding nodes to graph...")
    try:
        graph.add_node("step1", step1_node)
        graph.add_node("step2", step2_node)
        graph.add_node("step3", step3_node)
        
        graph.set_entry_point("step1")
        graph.add_edge("step1", "step2")
        graph.add_edge("step2", "step3")
        graph.set_finish_point("step3")
        
        app = graph.compile()
        print("✅ Graph compiled with 3 nodes")
    except Exception as e:
        print(f"❌ Failed to build graph: {e}")
        return False
    
    # Step 4: Execute graph
    print("\n▶️  Step 4: Executing graph...")
    try:
        initial_state = {
            "user_message": "Test SDK integration",
            "step_count": 0,
            "result": None
        }
        
        result = await app.ainvoke(initial_state)
        
        print("✅ Graph executed successfully")
        print(f"   Final state: {result}")
        print(f"   Steps executed: {result.get('step_count', 0)}")
        print(f"   Result: {result.get('result', 'None')}")
    except Exception as e:
        print(f"❌ Failed to execute: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 5: Verify trace was sent
    print("\n📊 Step 5: Verifying trace in SwisperStudio...")
    print("   Navigate to: http://localhost:3000/projects/0d7aa606-cb29-4a31-8a59-50fa61151a32/tracing")
    print("   Look for: 'sdk_local_test' trace")
    print("   Expected: 4 observations (root + 3 nodes)")
    
    print("\n" + "="*60)
    print("✅ SDK Test Complete!")
    print("="*60)
    print("\n📋 Next steps:")
    print("   1. Check SwisperStudio UI for the trace")
    print("   2. Click the trace to see observations")
    print("   3. Verify state transitions are visible")
    print("   4. If all looks good, integrate with Swisper!")
    print()
    
    return True


async def main():
    """Run the test"""
    success = await test_sdk()
    
    if success:
        print("🎉 SDK is working! Ready for Swisper integration.")
        return 0
    else:
        print("❌ SDK test failed. Check errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

