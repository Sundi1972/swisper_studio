#!/usr/bin/env python3
"""
Create GK Catalog Agent test trace

Scenario: "Can you help me build a kitchen shelf"

Flow:
1. global_supervisor: Intent Classification → Memory → Global Planner → Agent Execution (GK Catalog)
2. gk_catalog_agent: Project Discovery (HITL: shelf type) → Product Matcher (HITL: adhesive) → Store Navigation → Shopping List Builder

This creates realistic test data for demonstrations.
"""

import asyncio
import uuid
import httpx
from datetime import datetime, timedelta

# SwisperStudio API
API_URL = "http://localhost:8000/api/v1"
API_KEY = "dev-api-key-change-in-production"
PROJECT_ID = "0d7aa606-cb29-4a31-8a59-50fa61151a32"


async def create_gk_catalog_trace():
    """Create comprehensive GK Catalog Agent trace"""
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session_maker() as session:
        project_id = "0d7aa606-cb29-4a31-8a59-50fa61151a32"
        trace_id = f"trace-gk-catalog-{int(datetime.now().timestamp())}"
        
        base_time = datetime.utcnow()
        
        print(f"Creating GK Catalog trace: {trace_id}")
        
        # Create trace
        await session.execute(text("""
            INSERT INTO traces (id, project_id, name, user_id, session_id, timestamp, input, output, tags)
            VALUES (:id, :project_id, :name, :user_id, :session_id, :timestamp, :input, :output, :tags)
        """), {
            "id": trace_id,
            "project_id": project_id,
            "name": "User Request: Can you help me build a kitchen shelf?",
            "user_id": None,
            "session_id": "session_diy_kitchen",
            "timestamp": base_time,
            "input": {"message": "Can you help me build a kitchen shelf?", "chat_id": "chat_123"},
            "output": None,
            "tags": ["gk_catalog", "diy", "kitchen", "demo"]
        })
        
        # Track observation IDs
        obs_ids = {}
        current_time = base_time
        
        # ========================================================================
        # GLOBAL SUPERVISOR OBSERVATIONS
        # ========================================================================
        
        # 1. Intent Classification (60ms)
        obs_ids['intent'] = str(uuid.uuid4())
        current_time += timedelta(milliseconds=10)
        start_time = current_time
        current_time += timedelta(milliseconds=60)
        
        await session.execute(text("""
            INSERT INTO observations (
                id, trace_id, type, name, start_time, end_time,
                input, output, model, model_parameters,
                prompt_tokens, completion_tokens, level
            ) VALUES (
                :id, :trace_id, :type, :name, :start_time, :end_time,
                :input, :output, :model, :model_parameters,
                :prompt_tokens, :completion_tokens, :level
            )
        """), {
            "id": obs_ids['intent'],
            "trace_id": trace_id,
            "type": "GENERATION",
            "name": "classify_intent",
            "start_time": start_time,
            "end_time": current_time,
            "input": {
                "messages": [
                    {"role": "system", "content": "Classify user intent as: simple_chat, complex_chat, greeting, file_upload"},
                    {"role": "user", "content": "Can you help me build a kitchen shelf?"}
                ]
            },
            "output": {
                "intent": "complex_chat",
                "confidence": 0.95,
                "reasoning": "User is asking for help with a DIY project which requires planning and steps"
            },
            "model": "gpt-4-turbo",
            "model_parameters": {"temperature": 0.3, "max_tokens": 500},
            "prompt_tokens": 45,
            "completion_tokens": 25,
            "level": "DEFAULT"
        })
        
        # 2. Memory Node (40ms)
        obs_ids['memory'] = str(uuid.uuid4())
        current_time += timedelta(milliseconds=5)
        start_time = current_time
        current_time += timedelta(milliseconds=40)
        
        await session.execute(text("""
            INSERT INTO observations (
                id, trace_id, type, name, start_time, end_time,
                input, output, level
            ) VALUES (
                :id, :trace_id, :type, :name, :start_time, :end_time,
                :input, :output, :level
            )
        """), {
            "id": obs_ids['memory'],
            "trace_id": trace_id,
            "type": "SPAN",
            "name": "memory_node",
            "start_time": start_time,
            "end_time": current_time,
            "input": {"intent": "complex_chat", "user_message": "Can you help me build a kitchen shelf?"},
            "output": {
                "facts_loaded": 2,
                "facts": [
                    {"type": "preference", "content": "User prefers DIY projects"},
                    {"type": "skill", "content": "User has basic carpentry skills"}
                ]
            },
            "level": "DEFAULT"
        })
        
        # 3. Global Planner (120ms)
        obs_ids['planner'] = str(uuid.uuid4())
        current_time += timedelta(milliseconds=5)
        start_time = current_time
        current_time += timedelta(milliseconds=120)
        
        await session.execute(text("""
            INSERT INTO observations (
                id, trace_id, type, name, start_time, end_time,
                input, output, model, model_parameters,
                prompt_tokens, completion_tokens, level
            ) VALUES (
                :id, :trace_id, :type, :name, :start_time, :end_time,
                :input, :output, :model, :model_parameters,
                :prompt_tokens, :completion_tokens, :level
            )
        """), {
            "id": obs_ids['planner'],
            "trace_id": trace_id,
            "type": "GENERATION",
            "name": "global_planner",
            "start_time": start_time,
            "end_time": current_time,
            "input": {
                "messages": [
                    {"role": "system", "content": "You are a planning assistant. Create a step-by-step plan."},
                    {"role": "user", "content": "Can you help me build a kitchen shelf?"},
                    {"role": "assistant", "content": "Memory: User prefers DIY, has basic skills"}
                ]
            },
            "output": {
                "plan": "1. Determine shelf type and design\n2. Get materials list from DIY tutorial\n3. Match materials to available products\n4. Add store locations\n5. Create shopping list with instructions",
                "agent_needed": "gk_catalog_agent",
                "reasoning": "This requires retail shopping assistance and DIY project guidance"
            },
            "model": "gpt-4-turbo",
            "model_parameters": {"temperature": 0.7, "max_tokens": 1000},
            "prompt_tokens": 120,
            "completion_tokens": 85,
            "level": "DEFAULT"
        })
        
        # 4. Agent Execution - GK Catalog Agent (parent for nested observations)
        obs_ids['agent_exec'] = str(uuid.uuid4())
        current_time += timedelta(milliseconds=10)
        agent_exec_start = current_time
        
        # Create parent observation (will update end_time later)
        await session.execute(text("""
            INSERT INTO observations (
                id, trace_id, type, name, start_time,
                input, level
            ) VALUES (
                :id, :trace_id, :type, :name, :start_time,
                :input, :level
            )
        """), {
            "id": obs_ids['agent_exec'],
            "trace_id": trace_id,
            "type": "AGENT",
            "name": "agent_execution",
            "start_time": agent_exec_start,
            "input": {
                "agent": "gk_catalog_agent",
                "plan": "Help user build kitchen shelf with product recommendations"
            },
            "level": "DEFAULT"
        })
        
        # ========================================================================
        # GK CATALOG AGENT NESTED OBSERVATIONS
        # ========================================================================
        
        # 4a. Project Discovery - Call to DocAgent + Shelf Selection HITL (180ms)
        obs_ids['project_discovery'] = str(uuid.uuid4())
        current_time += timedelta(milliseconds=15)
        start_time = current_time
        current_time += timedelta(milliseconds=180)
        
        await session.execute(text("""
            INSERT INTO observations (
                id, trace_id, parent_observation_id, type, name, start_time, end_time,
                input, output, model, model_parameters,
                prompt_tokens, completion_tokens, level
            ) VALUES (
                :id, :trace_id, :parent_id, :type, :name, :start_time, :end_time,
                :input, :output, :model, :model_parameters,
                :prompt_tokens, :completion_tokens, :level
            )
        """), {
            "id": obs_ids['project_discovery'],
            "trace_id": trace_id,
            "parent_id": obs_ids['agent_exec'],
            "type": "GENERATION",
            "name": "project_discovery",
            "start_time": start_time,
            "end_time": current_time,
            "input": {
                "messages": [
                    {"role": "system", "content": "Call DocAgent to get DIY shelf tutorials. Present options to user."},
                    {"role": "user", "content": "Kitchen shelf project"}
                ],
                "doc_agent_query": "kitchen shelf tutorial"
            },
            "output": {
                "shelf_types": ["floating_spice", "corner_shelf", "pot_rack"],
                "selected_shelf_type": "floating_spice",
                "shelf_name": "Floating Spice Shelf",
                "tutorial": "# Floating Spice Shelf\n\n## Materials:\n- MDF board (60x20cm)\n- Wall brackets (2x)\n- Wood screws (8x)\n- Adhesive mounting strips\n- Sandpaper\n\n## Steps:\n1. Cut MDF to size\n2. Sand edges smooth\n3. Apply finish\n4. Install brackets\n5. Mount shelf",
                "materials_needed": ["MDF board", "Wall brackets", "Wood screws", "Adhesive mounting strips", "Sandpaper"],
                "estimated_cost": 25.50,
                "hitl_interaction": "User selected: floating_spice (Option 1 of 3)"
            },
            "model": "gpt-4-turbo",
            "model_parameters": {"temperature": 0.8, "max_tokens": 2000},
            "prompt_tokens": 180,
            "completion_tokens": 320,
            "level": "DEFAULT"
        })
        
        # 4b. Product Matcher - Match materials + Adhesive HITL (150ms)
        obs_ids['product_matcher'] = str(uuid.uuid4())
        current_time += timedelta(milliseconds=10)
        start_time = current_time
        current_time += timedelta(milliseconds=150)
        
        await session.execute(text("""
            INSERT INTO observations (
                id, trace_id, parent_observation_id, type, name, start_time, end_time,
                input, output, model, model_parameters,
                prompt_tokens, completion_tokens, level
            ) VALUES (
                :id, :trace_id, :parent_id, :type, :name, :start_time, :end_time,
                :input, :output, :model, :model_parameters,
                :prompt_tokens, :completion_tokens, :level
            )
        """), {
            "id": obs_ids['product_matcher'],
            "trace_id": trace_id,
            "parent_id": obs_ids['agent_exec'],
            "type": "GENERATION",
            "name": "product_matcher",
            "start_time": start_time,
            "end_time": current_time,
            "input": {
                "messages": [
                    {"role": "system", "content": "Match required materials to catalog products. Present adhesive options to user."},
                    {"role": "user", "content": "Materials: MDF board, Wall brackets, Wood screws, Adhesive mounting strips, Sandpaper"}
                ],
                "materials_needed": ["MDF board", "Wall brackets", "Wood screws", "Adhesive mounting strips", "Sandpaper"]
            },
            "output": {
                "matched_products": [
                    {"product_id": "MDF-001", "name": "MDF Board 60x20cm", "price": 8.99, "sku": "MDF60X20", "in_stock": True},
                    {"product_id": "BRK-002", "name": "Wall Bracket Set (2pc)", "price": 6.50, "sku": "WBKT2", "in_stock": True},
                    {"product_id": "SCR-003", "name": "Wood Screws 4x40mm (10pc)", "price": 2.99, "sku": "WS4X40", "in_stock": True},
                    {"product_id": "ADH-004", "name": "3M Command Strips Heavy Duty", "price": 5.99, "sku": "CMD3M", "in_stock": True},
                    {"product_id": "SND-005", "name": "Sandpaper Assorted Pack", "price": 3.99, "sku": "SNDPK", "in_stock": True}
                ],
                "total_matched": 5,
                "adhesive_choice": "mounting_strips",
                "hitl_interaction": "User selected: 3M Command Strips (Option 1 of 2: mounting strips vs wood glue)"
            },
            "model": "gpt-4-turbo",
            "model_parameters": {"temperature": 0.7, "max_tokens": 1500},
            "prompt_tokens": 250,
            "completion_tokens": 180,
            "level": "DEFAULT"
        })
        
        # 4c. Store Navigation - Add aisle locations (30ms)
        obs_ids['store_nav'] = str(uuid.uuid4())
        current_time += timedelta(milliseconds=5)
        start_time = current_time
        current_time += timedelta(milliseconds=30)
        
        await session.execute(text("""
            INSERT INTO observations (
                id, trace_id, parent_observation_id, type, name, start_time, end_time,
                input, output, level
            ) VALUES (
                :id, :trace_id, :parent_id, :type, :name, :start_time, :end_time,
                :input, :output, :level
            )
        """), {
            "id": obs_ids['store_nav'],
            "trace_id": trace_id,
            "parent_id": obs_ids['agent_exec'],
            "type": "SPAN",
            "name": "store_navigation",
            "start_time": start_time,
            "end_time": current_time,
            "input": {
                "matched_products": ["MDF-001", "BRK-002", "SCR-003", "ADH-004", "SND-005"]
            },
            "output": {
                "enriched_products": [
                    {"product_id": "MDF-001", "aisle": "A3", "section": "Building Materials", "category": "Wood"},
                    {"product_id": "BRK-002", "aisle": "B7", "section": "Hardware", "category": "Brackets"},
                    {"product_id": "SCR-003", "aisle": "B5", "section": "Hardware", "category": "Fasteners"},
                    {"product_id": "ADH-004", "aisle": "C2", "section": "Adhesives", "category": "Mounting"},
                    {"product_id": "SND-005", "aisle": "D4", "section": "Tools & Supplies", "category": "Finishing"}
                ],
                "optimal_route": ["A3", "B5", "B7", "C2", "D4"],
                "estimated_walking_time": "8 minutes"
            },
            "level": "DEFAULT"
        })
        
        # 4d. Shopping List Builder - Generate final output (90ms)
        obs_ids['shopping_list'] = str(uuid.uuid4())
        current_time += timedelta(milliseconds=5)
        start_time = current_time
        current_time += timedelta(milliseconds=90)
        
        await session.execute(text("""
            INSERT INTO observations (
                id, trace_id, parent_observation_id, type, name, start_time, end_time,
                input, output, model, model_parameters,
                prompt_tokens, completion_tokens, level
            ) VALUES (
                :id, :trace_id, :parent_id, :type, :name, :start_time, :end_time,
                :input, :output, :model, :model_parameters,
                :prompt_tokens, :completion_tokens, :level
            )
        """), {
            "id": obs_ids['shopping_list'],
            "trace_id": trace_id,
            "parent_id": obs_ids['agent_exec'],
            "type": "GENERATION",
            "name": "shopping_list_builder",
            "start_time": start_time,
            "end_time": current_time,
            "input": {
                "messages": [
                    {"role": "system", "content": "Format shopping list with tutorial, products, store locations, and total price."},
                    {"role": "user", "content": "Create shopping list for floating spice shelf"}
                ],
                "products": ["MDF-001", "BRK-002", "SCR-003", "ADH-004", "SND-005"],
                "tutorial": "# Floating Spice Shelf..."
            },
            "output": {
                "shopping_list": """# Your Kitchen Shelf Shopping List 🛒

## Project: Floating Spice Shelf
**Estimated Cost:** $28.46
**Estimated Time:** 2 hours
**Walking Route:** A3 → B5 → B7 → C2 → D4 (8 mins)

## Products to Buy:
1. ✅ **MDF Board 60x20cm** - $8.99
   - Location: Aisle A3, Building Materials
   - SKU: MDF60X20

2. ✅ **Wall Bracket Set (2pc)** - $6.50
   - Location: Aisle B7, Hardware
   - SKU: WBKT2

3. ✅ **Wood Screws 4x40mm (10pc)** - $2.99
   - Location: Aisle B5, Hardware  
   - SKU: WS4X40

4. ✅ **3M Command Strips Heavy Duty** - $5.99
   - Location: Aisle C2, Adhesives
   - SKU: CMD3M

5. ✅ **Sandpaper Assorted Pack** - $3.99
   - Location: Aisle D4, Tools & Supplies
   - SKU: SNDPK

## Building Instructions:
[Full tutorial attached]

Happy building! 🔨
""",
                "total_price": 28.46,
                "formatted": True
            },
            "model": "gpt-4-turbo",
            "model_parameters": {"temperature": 0.9, "max_tokens": 2000},
            "prompt_tokens": 420,
            "completion_tokens": 280,
            "level": "DEFAULT"
        })
        
        # Update agent_execution end time
        current_time += timedelta(milliseconds=5)
        await session.execute(text("""
            UPDATE observations 
            SET end_time = :end_time, 
                output = :output
            WHERE id = :id
        """), {
            "id": obs_ids['agent_exec'],
            "end_time": current_time,
            "output": {
                "agent": "gk_catalog_agent",
                "status": "complete",
                "shopping_list_generated": True,
                "total_price": 28.46
            }
        })
        
        # 5. User Interface - Format final response (50ms)
        obs_ids['ui'] = str(uuid.uuid4())
        current_time += timedelta(milliseconds=5)
        start_time = current_time
        current_time += timedelta(milliseconds=50)
        
        await session.execute(text("""
            INSERT INTO observations (
                id, trace_id, type, name, start_time, end_time,
                input, output, model, model_parameters,
                prompt_tokens, completion_tokens, level
            ) VALUES (
                :id, :trace_id, :type, :name, :start_time, :end_time,
                :input, :output, :model, :model_parameters,
                :prompt_tokens, :completion_tokens, :level
            )
        """), {
            "id": obs_ids['ui'],
            "trace_id": trace_id,
            "type": "GENERATION",
            "name": "user_interface",
            "start_time": start_time,
            "end_time": current_time,
            "input": {
                "messages": [
                    {"role": "system", "content": "Format response for user in friendly markdown."},
                    {"role": "assistant", "content": "Shopping list ready with tutorial"}
                ],
                "shopping_list": "# Your Kitchen Shelf Shopping List..."
            },
            "output": {
                "response": "I've created a complete shopping list for your floating spice shelf project! You'll need 5 items totaling $28.46. I've included store locations and a step-by-step tutorial. Ready to start shopping?",
                "formatted": True,
                "includes_tutorial": True
            },
            "model": "gpt-4-turbo",
            "model_parameters": {"temperature": 1.0, "max_tokens": 800},
            "prompt_tokens": 520,
            "completion_tokens": 95,
            "level": "DEFAULT"
        })
        
        # Update trace output
        await session.execute(text("""
            UPDATE traces 
            SET output = :output
            WHERE id = :id
        """), {
            "id": trace_id,
            "output": {
                "response": "I've created a complete shopping list for your floating spice shelf project!",
                "shopping_list_url": "attached",
                "total_cost": 28.46,
                "products": 5
            }
        })
        
        await session.commit()
        
        print(f"✅ Created trace with {len(obs_ids)} observations")
        print(f"   Trace ID: {trace_id}")
        print(f"   Total duration: {(current_time - base_time).total_seconds() * 1000:.0f}ms")
        print(f"   Observations:")
        print(f"     1. classify_intent (GENERATION) - 60ms")
        print(f"     2. memory_node (SPAN) - 40ms")
        print(f"     3. global_planner (GENERATION) - 120ms")
        print(f"     4. agent_execution (AGENT) - parent")
        print(f"        4a. project_discovery (GENERATION) - 180ms")
        print(f"        4b. product_matcher (GENERATION) - 150ms")
        print(f"        4c. store_navigation (SPAN) - 30ms")
        print(f"        4d. shopping_list_builder (GENERATION) - 90ms")
        print(f"     5. user_interface (GENERATION) - 50ms")
        print(f"\n🌐 View at: http://localhost:3000/projects/{project_id}/tracing/{trace_id}")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_gk_catalog_trace())

