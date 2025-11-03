#!/usr/bin/env python3
"""
Create realistic test traces for SwisperStudio based on actual Swisper implementation.

Scenario: User asks "What's my next meeting with Sarah?"
- Intent classification: complex_chat (needs calendar), temporal query, extracts "Sarah" entity
- Memory node: Loads avatar, presentation rules, conversation context, facts about Sarah
- Global planner: Routes to productivity_agent
- Productivity agent: Searches calendar, finds meeting
- UI node: Formats response with user's presentation preferences

This simulates a REAL Swisper execution flow with complete state transitions.
"""

import asyncio
import uuid
import httpx
from datetime import datetime, timedelta

# SwisperStudio API endpoint
API_URL = "http://backend:8000/api/v1"
API_KEY = "dev-api-key-change-in-production"
PROJECT_ID = "0d7aa606-cb29-4a31-8a59-50fa61151a32"


async def create_realistic_trace():
    """Create a realistic trace based on actual Swisper flow"""
    
    async with httpx.AsyncClient() as client:
        # ===================================================================
        # TRACE: "What's my next meeting with Sarah?"
        # ===================================================================
        trace_id = str(uuid.uuid4())
        trace_data = {
            "id": trace_id,
            "name": "User Request: What's my next meeting with Sarah?",
            "user_id": "user_alice",
            "session_id": "session_monday_morning",
            "project_id": PROJECT_ID,
            "input": {
                "user_message": "What's my next meeting with Sarah?",
                "modality": "text",
                "chat_id": "chat_xyz789"
            },
            "output": {
                "user_interface_response": "Your next meeting with Sarah is **Product Review** today at **2:00 PM** 📅"
            },
            "tags": ["calendar", "meeting", "temporal"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        headers = {"X-API-Key": API_KEY}
        
        print(f"Creating trace: {trace_id}")
        trace_response = await client.post(
            f"{API_URL}/traces",
            json=trace_data,
            headers=headers
        )
        print(f"Trace created: {trace_response.status_code}")
        
        base_time = datetime.utcnow()
        
        # ===================================================================
        # 1. GLOBAL SUPERVISOR (AGENT - orchestrator)
        # ===================================================================
        obs1_id = str(uuid.uuid4())
        obs1 = {
            "id": obs1_id,
            "trace_id": trace_id,
            "parent_observation_id": None,
            "type": "AGENT",
            "name": "global_supervisor",
            "start_time": base_time.isoformat(),
            "end_time": (base_time + timedelta(seconds=3)).isoformat(),
            "input": {
                # STATE AT START - minimal
                "user_message": "What's my next meeting with Sarah?",
                "model": "kvant-72b",
                "chat_id": "chat_xyz789",
                "user_id": "user_alice",
                "avatar_id": "avatar_friendly_assistant",
                "workspace_id": "workspace_personal",
                "user_timezone": "Europe/Zurich",
                "current_time": "2025-11-03T14:30:00Z",
                "modality": "text"
            },
            "output": {
                # STATE AT END - accumulated everything from all nodes
                "user_message": "What's my next meeting with Sarah?",
                "model": "kvant-72b",
                "chat_id": "chat_xyz789",
                "user_id": "user_alice",
                "avatar_id": "avatar_friendly_assistant",
                "workspace_id": "workspace_personal",
                "user_timezone": "Europe/Zurich",
                "current_time": "2025-11-03T14:30:00Z",
                "modality": "text",
                # Added by intent_classification:
                "intent_classification": {
                    "route": "complex_chat",
                    "is_temporal_query": True,
                    "temporal_query_type": "schedule",
                    "is_system_query": False,
                    "entities": [{"text": "Sarah", "type": "name"}],
                    "privacy_mode_change": None
                },
                # Added by memory_node:
                "avatar_name": "Friendly Assistant",
                "presentation_rules": {
                    "emoji_enabled": True,
                    "verbosity": "concise",
                    "tone": "friendly"
                },
                "memory_domain": {
                    "conversation_context": "User asked about upcoming meeting with Sarah",
                    "facts": {
                        "sarah_role": "colleague",
                        "sarah_email": "sarah.johnson@company.com",
                        "user_prefers_calendar_notifications": True
                    }
                },
                # Added by global_planner:
                "global_planner_decision": {
                    "next_step": "complete",
                    "current_plan": "Find next meeting with Sarah",
                    "target_domain_agent": "productivity_agent",
                    "is_final_step": True
                },
                # Added by productivity_agent:
                "agent_responses": {
                    "responses": [{
                        "agent_name": "productivity_agent",
                        "plan": "Find next meeting with Sarah",
                        "response": {
                            "meeting_title": "Product Review",
                            "meeting_time": "2025-11-03T14:00:00Z",
                            "meeting_duration": "60min",
                            "attendees": ["alice@company.com", "sarah.johnson@company.com"],
                            "location": "Conference Room A"
                        }
                    }]
                },
                # Added by ui_node:
                "user_interface_response": "Your next meeting with Sarah is **Product Review** today at **2:00 PM** 📅"
            },
            "level": "DEFAULT"
        }
        
        print(f"Creating observation: {obs1_id} (global_supervisor)")
        await client.post(f"{API_URL}/observations", json=obs1, headers=headers)
        
        # ===================================================================
        # 2. INTENT CLASSIFICATION (GENERATION - LLM call)
        # Classifies as complex_chat, temporal query, extracts "Sarah" entity
        # ===================================================================
        obs2_id = str(uuid.uuid4())
        obs2 = {
            "id": obs2_id,
            "trace_id": trace_id,
            "parent_observation_id": obs1_id,
            "type": "GENERATION",
            "name": "intent_classification",
            "start_time": (base_time + timedelta(milliseconds=50)).isoformat(),
            "end_time": (base_time + timedelta(milliseconds=850)).isoformat(),
            "input": {
                # STATE BEFORE: Just user message and IDs
                "user_message": "What's my next meeting with Sarah?",
                "model": "kvant-72b",
                "chat_id": "chat_xyz789",
                "user_id": "user_alice",
                "workspace_id": "workspace_personal",
                # Prompt (from actual Swisper intent_classification.md)
                "prompt": """You're working as a message classifier. Decide whether messages need "simple_chat" or "complex_chat" routing.

Can I answer this using just my knowledge, or do I need to access external systems?

**Current user message:**
What's my next meeting with Sarah?

**Instructions:**
1. Do they need external system access? (email, calendar, weather, etc.)
2. Do they need current real-time information?
3. Is this asking WHEN something happens (temporal)?
4. Extract any person/pet names

Return JSON matching OptimizedIntentResult schema:
- route: "simple_chat" or "complex_chat"
- is_temporal_query: true/false
- temporal_query_type: "specific_date" | "schedule" | "countdown" | "current" | null
- is_system_query: true/false (asking about me/Swisper)
- entities: [{text, type, role}] (extract "Sarah")
- privacy_mode_change: "enable" | "disable" | null""",
                "messages": [
                    {
                        "role": "system",
                        "content": "You're working as a message classifier..."
                    },
                    {
                        "role": "user",
                        "content": "What's my next meeting with Sarah?"
                    }
                ]
            },
            "output": {
                # STATE AFTER: Adds intent_classification
                "user_message": "What's my next meeting with Sarah?",
                "model": "kvant-72b",
                "chat_id": "chat_xyz789",
                "user_id": "user_alice",
                "workspace_id": "workspace_personal",
                "intent_classification": {  # ← ADDED BY THIS NODE
                    "route": "complex_chat",  # Needs calendar access
                    "is_temporal_query": True,  # Asking "when"
                    "temporal_query_type": "schedule",  # Schedule query
                    "is_system_query": False,  # Not asking about Swisper
                    "entities": [
                        {"text": "Sarah", "type": "name", "role": None}  # Extracted entity
                    ],
                    "privacy_mode_change": None
                }
            },
            "model": "kvant-72b",
            "model_parameters": {
                "temperature": 0.3,  # Low for classification
                "max_tokens": 500,
                "top_p": 1.0
            },
            "prompt_tokens": 280,
            "completion_tokens": 65,
            "level": "DEFAULT"
        }
        
        print(f"Creating observation: {obs2_id} (intent_classification)")
        await client.post(f"{API_URL}/observations", json=obs2, headers=headers)
        
        # ===================================================================
        # 3. MEMORY NODE (SPAN - loads context)
        # Loads avatar, presentation rules, facts about Sarah, conversation context
        # ===================================================================
        obs3_id = str(uuid.uuid4())
        obs3 = {
            "id": obs3_id,
            "trace_id": trace_id,
            "parent_observation_id": obs1_id,
            "type": "SPAN",
            "name": "memory_node",
            "start_time": (base_time + timedelta(milliseconds=900)).isoformat(),
            "end_time": (base_time + timedelta(milliseconds=1200)).isoformat(),
            "input": {
                # STATE BEFORE: Has intent classification
                "user_message": "What's my next meeting with Sarah?",
                "model": "kvant-72b",
                "chat_id": "chat_xyz789",
                "user_id": "user_alice",
                "avatar_id": "avatar_friendly_assistant",
                "workspace_id": "workspace_personal",
                "intent_classification": {
                    "route": "complex_chat",
                    "is_temporal_query": True,
                    "temporal_query_type": "schedule",
                    "entities": [{"text": "Sarah", "type": "name"}]
                }
            },
            "output": {
                # STATE AFTER: Adds avatar_name, presentation_rules, memory_domain
                "user_message": "What's my next meeting with Sarah?",
                "model": "kvant-72b",
                "chat_id": "chat_xyz789",
                "user_id": "user_alice",
                "avatar_id": "avatar_friendly_assistant",
                "workspace_id": "workspace_personal",
                "intent_classification": {
                    "route": "complex_chat",
                    "is_temporal_query": True,
                    "temporal_query_type": "schedule",
                    "entities": [{"text": "Sarah", "type": "name"}]
                },
                "avatar_name": "Friendly Assistant",  # ← ADDED (loaded from DB)
                "presentation_rules": {  # ← ADDED (loaded from DB/cache)
                    "emoji_enabled": True,
                    "verbosity": "concise",
                    "tone": "friendly",
                    "language": "en"
                },
                "memory_domain": {  # ← ADDED (loaded context + facts)
                    "conversation_context": "User asked about upcoming meeting with Sarah. Previous turn: User asked about today's schedule.",
                    "facts": {
                        # Facts about Sarah (loaded because entity extracted)
                        "sarah_role": "colleague",
                        "sarah_email": "sarah.johnson@company.com",
                        "sarah_department": "Product Management",
                        "sarah_last_meeting": "2025-10-28",
                        # User preferences (loaded from workspace)
                        "user_prefers_calendar_notifications": True,
                        "user_timezone": "Europe/Zurich"
                    },
                    "preloaded_facts_count": 6,
                    "entity_facts_loaded": ["Sarah"]
                }
            },
            "level": "DEFAULT"
        }
        
        print(f"Creating observation: {obs3_id} (memory_node)")
        await client.post(f"{API_URL}/observations", json=obs3, headers=headers)
        
        # ===================================================================
        # 4. GLOBAL PLANNER (GENERATION - decides routing)
        # ===================================================================
        obs4_id = str(uuid.uuid4())
        obs4 = {
            "id": obs4_id,
            "trace_id": trace_id,
            "parent_observation_id": obs1_id,
            "type": "GENERATION",
            "name": "global_planner",
            "start_time": (base_time + timedelta(milliseconds=1250)).isoformat(),
            "end_time": (base_time + timedelta(milliseconds=1500)).isoformat(),
            "input": {
                # STATE BEFORE: Has intent + memory
                "user_message": "What's my next meeting with Sarah?",
                "intent_classification": {
                    "route": "complex_chat",
                    "is_temporal_query": True,
                    "entities": [{"text": "Sarah", "type": "name"}]
                },
                "memory_domain": {
                    "conversation_context": "User asked about upcoming meeting with Sarah",
                    "facts": {
                        "sarah_role": "colleague",
                        "sarah_email": "sarah.johnson@company.com"
                    }
                },
                "prompt": """**ROLE**: You are a planning expert. Decide which agent should handle this request.

**USER REQUEST**: What's my next meeting with Sarah?

**CONTEXT**: 
- Route: complex_chat (needs external tools)
- Temporal query: schedule
- Entity: Sarah (colleague, sarah.johnson@company.com)

**AVAILABLE AGENTS**:
- productivity_agent: Calendar, email, tasks, contacts
- research_agent: Web search, weather, news
- wealth_agent: Financial data, stocks
- doc_agent: Document search, RAG

**INSTRUCTIONS**:
1. Which agent should handle this?
2. What's the plan/task for that agent?
3. Can we execute directly or need the agent to plan?

**OUTPUT**:
{
  "target_domain_agent": "productivity_agent",
  "current_plan": "Find next meeting with Sarah",
  "next_step": "execute_directly"
}"""
            },
            "output": {
                # STATE AFTER: Adds global_planner_decision
                "user_message": "What's my next meeting with Sarah?",
                "intent_classification": {
                    "route": "complex_chat",
                    "is_temporal_query": True,
                    "entities": [{"text": "Sarah", "type": "name"}]
                },
                "memory_domain": {
                    "conversation_context": "User asked about upcoming meeting with Sarah",
                    "facts": {
                        "sarah_role": "colleague",
                        "sarah_email": "sarah.johnson@company.com"
                    }
                },
                "global_planner_decision": {  # ← ADDED BY THIS NODE
                    "next_step": "execute_directly",
                    "current_plan": "Find next meeting with Sarah Johnson (sarah.johnson@company.com)",
                    "target_domain_agent": "productivity_agent",
                    "is_final_step": True
                }
            },
            "model": "kvant-72b",
            "model_parameters": {
                "temperature": 0.5,
                "max_tokens": 300
            },
            "prompt_tokens": 220,
            "completion_tokens": 45,
            "level": "DEFAULT"
        }
        
        print(f"Creating observation: {obs4_id} (global_planner)")
        await client.post(f"{API_URL}/observations", json=obs4, headers=headers)
        
        # ===================================================================
        # 5. PRODUCTIVITY AGENT (AGENT - calendar handling)
        # ===================================================================
        obs5_id = str(uuid.uuid4())
        obs5 = {
            "id": obs5_id,
            "trace_id": trace_id,
            "parent_observation_id": obs1_id,
            "type": "AGENT",
            "name": "productivity_agent",
            "start_time": (base_time + timedelta(milliseconds=1550)).isoformat(),
            "end_time": (base_time + timedelta(milliseconds=2400)).isoformat(),
            "input": {
                # STATE BEFORE: Has planner decision
                "user_message": "What's my next meeting with Sarah?",
                "current_plan": "Find next meeting with Sarah Johnson (sarah.johnson@company.com)",
                "memory_domain": {
                    "facts": {
                        "sarah_email": "sarah.johnson@company.com"
                    }
                }
            },
            "output": {
                # STATE AFTER: Adds agent_responses
                "user_message": "What's my next meeting with Sarah?",
                "current_plan": "Find next meeting with Sarah Johnson (sarah.johnson@company.com)",
                "memory_domain": {
                    "facts": {
                        "sarah_email": "sarah.johnson@company.com"
                    }
                },
                "agent_responses": {  # ← ADDED BY THIS AGENT
                    "responses": [{
                        "agent_name": "productivity_agent",
                        "plan": "Find next meeting with Sarah Johnson",
                        "response": {
                            "status": "success",
                            "meeting_found": True,
                            "meeting_title": "Product Review",
                            "meeting_time": "2025-11-03T14:00:00Z",
                            "meeting_duration_minutes": 60,
                            "attendees": ["alice@company.com", "sarah.johnson@company.com"],
                            "location": "Conference Room A",
                            "meeting_url": "https://meet.company.com/product-review-abc"
                        }
                    }]
                }
            },
            "level": "DEFAULT"
        }
        
        print(f"Creating observation: {obs5_id} (productivity_agent)")
        await client.post(f"{API_URL}/observations", json=obs5, headers=headers)
        
        # ===================================================================
        # 6. GET CALENDAR EVENTS (TOOL - nested under productivity_agent)
        # ===================================================================
        obs6_id = str(uuid.uuid4())
        obs6 = {
            "id": obs6_id,
            "trace_id": trace_id,
            "parent_observation_id": obs5_id,  # Child of productivity_agent
            "type": "TOOL",
            "name": "get_calendar_events",
            "start_time": (base_time + timedelta(milliseconds=1600)).isoformat(),
            "end_time": (base_time + timedelta(milliseconds=2200)).isoformat(),
            "input": {
                # STATE BEFORE: Has plan and Sarah's email
                "current_plan": "Find next meeting with Sarah Johnson",
                "sarah_email": "sarah.johnson@company.com",
                "user_timezone": "Europe/Zurich",
                # Tool call (how we invoked it)
                "tool_call": {
                    "function": "search_calendar_events",
                    "arguments": {
                        "attendee_email": "sarah.johnson@company.com",
                        "start_time": "2025-11-03T14:30:00Z",  # Current time
                        "end_time": "2025-11-10T23:59:59Z",  # Next 7 days
                        "max_results": 5
                    }
                }
            },
            "output": {
                # STATE AFTER: Adds calendar_results from API
                "current_plan": "Find next meeting with Sarah Johnson",
                "sarah_email": "sarah.johnson@company.com",
                "user_timezone": "Europe/Zurich",
                "calendar_results": [  # ← ADDED BY THIS TOOL
                    {
                        "id": "cal_event_001",
                        "title": "Product Review",
                        "start_time": "2025-11-03T14:00:00Z",
                        "end_time": "2025-11-03T15:00:00Z",
                        "attendees": [
                            {"email": "alice@company.com", "name": "Alice Chen"},
                            {"email": "sarah.johnson@company.com", "name": "Sarah Johnson"},
                            {"email": "david@company.com", "name": "David Park"}
                        ],
                        "location": "Conference Room A",
                        "status": "confirmed",
                        "meeting_url": "https://meet.company.com/product-review-abc"
                    },
                    {
                        "id": "cal_event_002",
                        "title": "Weekly 1:1 with Sarah",
                        "start_time": "2025-11-05T10:00:00Z",
                        "end_time": "2025-11-05T10:30:00Z",
                        "attendees": [
                            {"email": "alice@company.com", "name": "Alice Chen"},
                            {"email": "sarah.johnson@company.com", "name": "Sarah Johnson"}
                        ],
                        "location": "Virtual",
                        "status": "confirmed"
                    }
                ],
                "tool_response": {  # Tool-specific metadata
                    "status": "success",
                    "events_found": 2,
                    "api_latency_ms": 145,
                    "next_meeting_index": 0  # Index of next chronological meeting
                }
            },
            "level": "DEFAULT"
        }
        
        print(f"Creating observation: {obs6_id} (get_calendar_events)")
        await client.post(f"{API_URL}/observations", json=obs6, headers=headers)
        
        # ===================================================================
        # 7. UI NODE (GENERATION - formats final response)
        # Uses presentation rules to format response
        # ===================================================================
        obs7_id = str(uuid.uuid4())
        obs7 = {
            "id": obs7_id,
            "trace_id": trace_id,
            "parent_observation_id": obs1_id,
            "type": "GENERATION",
            "name": "ui_node",
            "start_time": (base_time + timedelta(milliseconds=2450)).isoformat(),
            "end_time": (base_time + timedelta(milliseconds=2950)).isoformat(),
            "input": {
                # STATE BEFORE: Has agent responses and presentation rules
                "user_message": "What's my next meeting with Sarah?",
                "agent_responses": {
                    "responses": [{
                        "agent_name": "productivity_agent",
                        "response": {
                            "meeting_title": "Product Review",
                            "meeting_time": "2025-11-03T14:00:00Z",
                            "attendees": ["alice@company.com", "sarah.johnson@company.com"],
                            "location": "Conference Room A"
                        }
                    }]
                },
                "presentation_rules": {
                    "emoji_enabled": True,
                    "verbosity": "concise",
                    "tone": "friendly"
                },
                "user_timezone": "Europe/Zurich",
                # Prompt (from actual Swisper ui_node)
                "prompt": """**ROLE**: You are Swisper, a friendly and professional AI assistant.

**TASK**: Format the meeting information for the user in a natural, conversational way.

**CONTEXT**:
User asked: "What's my next meeting with Sarah?"
Meeting found: Product Review at 2:00 PM today in Conference Room A

**USER PREFERENCES**:
- Emoji: enabled (use appropriate emojis)
- Verbosity: concise (keep it brief)
- Tone: friendly (warm and approachable)
- Timezone: Europe/Zurich

**INSTRUCTIONS**:
1. Be conversational and friendly
2. Include meeting title, time, and location
3. Use emoji (presentation_rules.emoji_enabled = true)
4. Keep it concise (presentation_rules.verbosity = concise)
5. Format time in user's timezone

**EXAMPLE OUTPUT**:
Your next meeting with Sarah is **Product Review** today at **2:00 PM** in Conference Room A 📅""",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are Swisper. Format meeting information naturally and concisely with emojis."
                    },
                    {
                        "role": "user",
                        "content": "Meeting: Product Review at 14:00 with Sarah in Conference Room A"
                    }
                ]
            },
            "output": {
                # STATE AFTER: Adds user_interface_response
                "user_message": "What's my next meeting with Sarah?",
                "agent_responses": {
                    "responses": [{
                        "agent_name": "productivity_agent",
                        "response": {
                            "meeting_title": "Product Review",
                            "meeting_time": "2025-11-03T14:00:00Z"
                        }
                    }]
                },
                "presentation_rules": {
                    "emoji_enabled": True,
                    "verbosity": "concise",
                    "tone": "friendly"
                },
                "user_timezone": "Europe/Zurich",
                "user_interface_response": "Your next meeting with Sarah is **Product Review** today at **2:00 PM** in Conference Room A 📅"  # ← ADDED BY THIS NODE
            },
            "model": "kvant-72b",
            "model_parameters": {
                "temperature": 0.8,  # Higher for creative formatting
                "max_tokens": 200
            },
            "prompt_tokens": 195,
            "completion_tokens": 32,
            "level": "DEFAULT"
        }
        
        print(f"Creating observation: {obs7_id} (ui_node)")
        await client.post(f"{API_URL}/observations", json=obs7, headers=headers)
        
        print(f"\n✅ Realistic trace created successfully!")
        print(f"   Trace ID: {trace_id}")
        print(f"   View at: http://localhost:3000/projects/{PROJECT_ID}/tracing/{trace_id}")
        print(f"\n📊 This trace demonstrates:")
        print(f"   - Complete GlobalSupervisorState flow")
        print(f"   - Real intent classification (complex_chat, temporal, entity extraction)")
        print(f"   - Memory loading (avatar, presentation rules, facts about Sarah)")
        print(f"   - Agent routing to productivity_agent")
        print(f"   - Tool call with realistic calendar API response")
        print(f"   - UI formatting with presentation preferences")
        print(f"   - State accumulation through 6 nodes")


async def main():
    """Create realistic test trace"""
    print("=" * 70)
    print("Creating REALISTIC test trace based on actual Swisper implementation")
    print("=" * 70)
    print()
    
    await create_realistic_trace()
    
    print()
    print("=" * 70)
    print("✅ Test data generation complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
