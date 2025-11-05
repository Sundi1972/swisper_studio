# Swisper Team Handover - Integration Guide

**Date:** November 4, 2025  
**For:** Swisper Development Team  
**From:** SwisperStudio Team  
**Purpose:** Integrate Swisper with SwisperStudio for observability and configuration management

---

## 🎯 Overview

**What This Enables:**
1. **Observability** - See every Swisper request execution in SwisperStudio
   - View state transitions at each node
   - See LLM prompts and responses
   - Track token usage and costs
   - Debug production issues with full context

2. **Configuration Management** - Manage LLM configs from SwisperStudio UI
   - Change model parameters without code deployment
   - Test configs live before production
   - Version control for configurations
   - Multi-environment support (dev, staging, production)

---

## 📋 Table of Contents

1. [Quick Start (20 minutes)](#quick-start)
2. [Part 1: SDK Integration](#part-1-sdk-integration)
3. [Part 2: SAP Implementation](#part-2-sap-implementation)
4. [Testing & Verification](#testing--verification)
5. [Troubleshooting](#troubleshooting)
6. [Reference Documentation](#reference-documentation)

---

## ⚡ Quick Start

**Time:** 20-30 minutes  
**Goal:** Get basic tracing working (state transitions visible in SwisperStudio)

### Step 1: Install SDK (5 mins)

```bash
cd /path/to/swisper/backend
uv pip install -e /path/to/swisper_studio/sdk
```

### Step 2: Initialize Tracing (5 mins)

Add to `swisper/backend/app/main.py`:

```python
from swisper_studio_sdk import initialize_tracing

# Add in startup event or at module level
initialize_tracing(
    api_url="http://localhost:8001",  # SwisperStudio backend
    api_key="dev-api-key-change-in-production",
    project_id="0d7aa606-cb29-4a31-8a59-50fa61151a32",  # From SwisperStudio
    enabled=True
)
```

### Step 3: Wrap Graph (2 mins)

Find where global_supervisor graph is created and wrap it:

```python
from swisper_studio_sdk import create_traced_graph

# BEFORE:
# workflow = StateGraph(GlobalSupervisorState)
# ... add nodes ...
# graph = workflow.compile()

# AFTER:
graph = create_traced_graph(
    GlobalSupervisorState,
    trace_name="global_supervisor"
)
# ... add nodes to 'graph' ...
# graph will auto-compile with tracing
```

### Step 4: Test (5 mins)

```bash
# Send a test request to Swisper
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What's my next meeting?"}'

# Check SwisperStudio
# Go to: http://localhost:3000/projects/0d7aa606-cb29-4a31-8a59-50fa61151a32/tracing
# You should see a new trace!
```

---

## 📚 Part 1: SDK Integration

**Full Guide:** [`docs/guides/SWISPER_SDK_INTEGRATION_GUIDE.md`](docs/guides/SWISPER_SDK_INTEGRATION_GUIDE.md)

### What the SDK Does:

✅ **Automatic Trace Creation** - Every request creates a trace  
✅ **State Capture** - Before/after state at each node  
✅ **Observation Tree** - Parent-child nesting  
✅ **Duration Tracking** - Execution time per node  
✅ **Error Tracking** - Failed nodes marked with ERROR  
✅ **Graceful Degradation** - Won't break Swisper if SwisperStudio is down

### Integration Points:

**Files to Modify:**
1. `swisper/backend/app/main.py` - Add `initialize_tracing()`
2. `swisper/backend/app/api/services/agents/global_supervisor/*.py` - Wrap graph
3. (Optional) Individual nodes - Add `@traced()` decorator for more detail

**Files to Check:**
- `sdk/README.md` - SDK overview
- `sdk/swisper_studio_sdk/__init__.py` - Available functions
- `sdk/test_sdk_locally.py` - Local test script

### SDK Capabilities (v0.2.0):

**Implemented:**
- ✅ Trace creation
- ✅ State before/after capture
- ✅ Observation nesting
- ✅ Type detection (GENERATION, TOOL, AGENT, SPAN)

**Deferred (Phase 5.2 - Optional):**
- ⏸️ LLM prompt auto-capture (infrastructure ready, needs Swisper code)
- ⏸️ Tool call auto-capture (infrastructure ready)
- ⏸️ Token counting (needs tiktoken integration)

**Result:** You get **state transitions and execution flow** immediately. Prompts/tokens can be added later if needed.

---

## ⚙️ Part 2: SAP Implementation

**SAP = Swisper Admin Protocol** - Standard API for config management

**Full Spec:** [`docs/specs/spec_sap_v1_comprehensive.md`](docs/specs/spec_sap_v1_comprehensive.md)  
**Implementation Guide:** [`docs/architecture/swisper_sap_implementation_guide.md`](docs/architecture/swisper_sap_implementation_guide.md)  
**Contract:** [`docs/SAP_CONTRACT.md`](docs/SAP_CONTRACT.md)

### What SAP Enables:

✅ **Live Config Testing** - Change LLM parameters, test immediately  
✅ **Multi-Environment** - Separate configs for dev/staging/production  
✅ **Version Control** - Track config changes over time  
✅ **No-Code Deployment** - PO can adjust configs without developers

### SAP Endpoints to Implement:

**Required Endpoints (4):**

```python
# 1. Get schema (what tables/fields exist)
@router.get("/api/admin/config/schema")
async def get_schema():
    return {
        "tables": [
            {
                "name": "llm_node_config",
                "fields": [
                    {"name": "node_name", "type": "string", "required": True},
                    {"name": "default_model", "type": "select", "options": [...]},
                    {"name": "default_temperature", "type": "number", "min": 0, "max": 2},
                    ...
                ]
            }
        ]
    }

# 2. List all records
@router.get("/api/admin/config/llm_node_config")
async def list_llm_configs():
    return {
        "table": "llm_node_config",
        "records": [...],  # From your database
        "count": 22
    }

# 3. Get single record
@router.get("/api/admin/config/llm_node_config/{node_name}")
async def get_config(node_name: str):
    return {"node_name": "global_planner", "default_model": "gpt-4-turbo", ...}

# 4. Update record
@router.put("/api/admin/config/llm_node_config/{node_name}")
async def update_config(node_name: str, data: dict):
    # Update in database + hot-reload config
    return updated_config
```

### Hot-Reload Mechanism:

**After config update, you need to:**
1. Update database
2. Update in-memory cache (so next request uses new config)
3. Optionally: Restart specific service/worker

**Example:**
```python
# In Swisper
async def update_config(node_name: str, data: dict):
    # 1. Update DB
    await db.update("llm_node_config", node_name, data)
    
    # 2. Hot-reload cache
    config_manager.reload_config(node_name)
    
    # 3. Return updated
    return data
```

---

## 🧪 Testing & Verification

### Test Plan:

**SDK Integration Tests:**
1. ✅ Send request to Swisper
2. ✅ Check SwisperStudio shows new trace
3. ✅ Verify all nodes appear in observation tree
4. ✅ Verify state transitions visible
5. ✅ Verify parent-child nesting correct

**SAP Integration Tests:**
1. ✅ Open SwisperStudio config page
2. ✅ Select "llm_node_config" table
3. ✅ See all 22 node configurations
4. ✅ Edit a config (change temperature)
5. ✅ Verify config updated in Swisper
6. ✅ Send request, verify new config used

### Verification URLs:

**SwisperStudio:**
- Tracing: http://localhost:3000/projects/0d7aa606-cb29-4a31-8a59-50fa61151a32/tracing
- Config: http://localhost:3000/projects/0d7aa606-cb29-4a31-8a59-50fa61151a32/config
- System Architecture: http://localhost:3000/system-architecture

**Test Credentials:**
- Email: `admin@swisperstudio.com`
- Password: `admin123`

---

## 🐛 Troubleshooting

**Full Guide:** [`docs/guides/SDK_TROUBLESHOOTING_GUIDE.md`](docs/guides/SDK_TROUBLESHOOTING_GUIDE.md)

### Common Issues:

**1. No traces appearing:**
- Check: SwisperStudio backend running on port 8001?
- Check: API key matches?
- Check: Project ID correct?
- Check: Firewall/network allows connections?

**2. Observations but no state:**
- Check: TypedDict serialization working?
- Check: State is dict-like (not custom class)?

**3. Config changes not applying:**
- Check: SAP endpoints returning correct data?
- Check: Hot-reload called after update?
- Check: Cache invalidated?

---

## 📦 Reference Documentation

### **For SDK Integration:**

**Primary:**
1. **[SWISPER_SDK_INTEGRATION_GUIDE.md](docs/guides/SWISPER_SDK_INTEGRATION_GUIDE.md)** ⭐ START HERE
   - Step-by-step SDK installation
   - Code examples
   - Where to add tracing calls

2. **[SDK_TROUBLESHOOTING_GUIDE.md](docs/guides/SDK_TROUBLESHOOTING_GUIDE.md)**
   - Common issues and solutions
   - Debugging tips

3. **[SDK_READY_FOR_INTEGRATION.md](SDK_READY_FOR_INTEGRATION.md)**
   - SDK test results
   - What's working vs what's deferred

**Secondary:**
4. **[docs/plans/plan_sdk_basic_integration.md](docs/plans/plan_sdk_basic_integration.md)** - Implementation plan
5. **[docs/analysis/sdk_gap_analysis.md](docs/analysis/sdk_gap_analysis.md)** - What SDK can/can't do
6. **[sdk/README.md](sdk/README.md)** - SDK package overview

---

### **For SAP Implementation:**

**Primary:**
1. **[docs/specs/spec_sap_v1_comprehensive.md](docs/specs/spec_sap_v1_comprehensive.md)** ⭐ SAP SPECIFICATION
   - Complete API contract
   - Endpoint definitions
   - Data formats
   - Examples

2. **[docs/architecture/swisper_sap_implementation_guide.md](docs/architecture/swisper_sap_implementation_guide.md)** ⭐ IMPLEMENTATION GUIDE
   - How to implement SAP in Swisper
   - Code examples
   - Database queries
   - Hot-reload patterns

3. **[docs/SAP_CONTRACT.md](docs/SAP_CONTRACT.md)** - API Contract
   - Endpoint URLs
   - Request/response formats
   - Error codes

**Secondary:**
4. **[docs/architecture/swisper_sap_implementation_todo.md](docs/architecture/swisper_sap_implementation_todo.md)** - TODO checklist
5. **[docs/specs/spec_sap_v1.md](docs/specs/spec_sap_v1.md)** - Original spec (v1.0)

---

## 🗂️ File Structure for Handover

### **Core Integration Files:**

```
swisper_studio/
├── sdk/                                    ← SDK Package (copy to Swisper)
│   ├── README.md                          ← SDK overview
│   ├── pyproject.toml                     ← Dependencies
│   ├── swisper_studio_sdk/                ← Python package
│   │   ├── __init__.py                    ← Main exports
│   │   ├── tracing/                       ← Core tracing
│   │   └── wrappers/                      ← LLM/tool wrappers (Phase 5.2)
│   └── test_sdk_locally.py                ← Test script
│
├── docs/guides/                            ← Integration Guides
│   ├── SWISPER_SDK_INTEGRATION_GUIDE.md   ⭐ SDK: Start here
│   └── SDK_TROUBLESHOOTING_GUIDE.md       ← SDK: Debug help
│
├── docs/specs/                             ← SAP Specifications
│   └── spec_sap_v1_comprehensive.md       ⭐ SAP: Complete spec
│
├── docs/architecture/                      ← Implementation Guides
│   ├── swisper_sap_implementation_guide.md ⭐ SAP: How to implement
│   └── swisper_sap_implementation_todo.md  ← SAP: Checklist
│
└── docs/                                   ← Supporting Docs
    ├── SAP_CONTRACT.md                     ← SAP: API contract
    ├── SDK_READY_FOR_INTEGRATION.md        ← SDK: Status & capabilities
    └── QUICK_START.md                      ← SwisperStudio overview
```

---

## 📖 Recommended Reading Order

### **For SDK Integration (20-30 mins):**
1. Read: `docs/guides/SWISPER_SDK_INTEGRATION_GUIDE.md` (15 mins)
2. Review: `sdk/README.md` (5 mins)
3. Test: Run `sdk/test_sdk_locally.py` (5 mins)
4. Implement: Add 3 lines to Swisper (5 mins)
5. Verify: Send request, check SwisperStudio (5 mins)

**Total: ~30 minutes to working integration**

---

### **For SAP Implementation (3-5 days):**
1. Read: `docs/specs/spec_sap_v1_comprehensive.md` (30 mins)
2. Read: `docs/architecture/swisper_sap_implementation_guide.md` (30 mins)
3. Design: Plan Swisper SAP architecture (1-2 hours)
4. Implement: 4 SAP endpoints (2-3 days)
   - GET /api/admin/config/schema
   - GET /api/admin/config/llm_node_config
   - GET /api/admin/config/llm_node_config/{node_name}
   - PUT /api/admin/config/llm_node_config/{node_name}
5. Hot-reload: Config cache invalidation (1 day)
6. Test: End-to-end with SwisperStudio (1 day)

**Total: ~3-5 days for complete config management**

---

## 🎯 Priority Recommendation

**Phase 1: SDK Integration (This Week)** 🔥
- **Effort:** 30 minutes
- **Value:** Immediate observability
- **Risk:** Very low
- **Blocker:** None

**Phase 2: SAP Implementation (Next 1-2 Weeks)**
- **Effort:** 3-5 days
- **Value:** High - PO can manage configs
- **Risk:** Medium - needs careful testing
- **Blocker:** Requires backend changes

**Recommendation:** Start with SDK to get tracing working, then implement SAP.

---

## 🔑 SwisperStudio Access

**Demo Instance:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/api/v1/docs

**Credentials:**
- Email: `admin@swisperstudio.com`
- Password: `admin123`

**Test Project:**
- Name: "AAA Swisper Production Test"
- ID: `0d7aa606-cb29-4a31-8a59-50fa61151a32`
- Has sample traces already (for comparison)

---

## 📞 Support

**Questions?**
- Check: `docs/guides/SDK_TROUBLESHOOTING_GUIDE.md`
- Check: `docs/specs/spec_sap_v1_comprehensive.md` (FAQ section)
- Contact: SwisperStudio team

**Found a bug?**
- SDK issues: Check `sdk/` code
- SAP spec issues: Check `docs/specs/spec_sap_v1_comprehensive.md`

---

## ✅ Success Criteria

### **SDK Integration Complete When:**
- ✅ Swisper requests create traces in SwisperStudio
- ✅ All nodes visible in observation tree
- ✅ State transitions showing (green/red diff view)
- ✅ Parent-child nesting correct
- ✅ Can click any observation to see state

### **SAP Implementation Complete When:**
- ✅ SwisperStudio config page shows all LLM node configs
- ✅ Can edit temperature/max_tokens in UI
- ✅ Changes apply immediately in Swisper
- ✅ Hot-reload working (no restart needed)
- ✅ All 3 environments (dev/staging/prod) working

---

## 🎁 Bonus: What's Already Done

**SwisperStudio is production-ready with:**
- ✅ User authentication (JWT, RBAC)
- ✅ Beautiful UI (state diffs, prompts, graphs)
- ✅ Multi-environment support
- ✅ Version control for configs
- ✅ 123 backend tests passing
- ✅ Mock SAP already implemented (for your reference)
- ✅ 6 agents visualized (including new GK Catalog!)
- ✅ Complete documentation

**You just need to:**
1. Install SDK (3 lines of code)
2. Implement SAP endpoints (4 endpoints)

---

## 📦 Files to Copy

**Minimum Required:**
```bash
# Copy these to Swisper team:
swisper_studio/sdk/                                          # SDK package
swisper_studio/docs/guides/SWISPER_SDK_INTEGRATION_GUIDE.md  # SDK guide
swisper_studio/docs/guides/SDK_TROUBLESHOOTING_GUIDE.md      # SDK troubleshooting
swisper_studio/docs/specs/spec_sap_v1_comprehensive.md       # SAP spec
swisper_studio/docs/architecture/swisper_sap_implementation_guide.md  # SAP guide
swisper_studio/docs/SAP_CONTRACT.md                          # SAP contract
swisper_studio/SWISPER_TEAM_HANDOVER.md                      # This file
```

**Nice to Have:**
```bash
swisper_studio/SDK_READY_FOR_INTEGRATION.md         # SDK capabilities
swisper_studio/docs/analysis/sdk_gap_analysis.md    # What's missing
swisper_studio/docs/plans/plan_sdk_basic_integration.md  # Implementation plan
swisper_studio/backend/app/api/routes/mock_sap.py   # SAP reference implementation
```

---

## 🚀 Next Steps

**For Swisper Team:**

**This Week:**
1. ✅ Read SDK integration guide (15 mins)
2. ✅ Install SDK in Swisper (5 mins)
3. ✅ Add initialization code (5 mins)
4. ✅ Wrap global_supervisor graph (2 mins)
5. ✅ Test and verify (10 mins)
6. 📝 Share feedback with SwisperStudio team

**Next 1-2 Weeks:**
1. 📖 Read SAP specification (30 mins)
2. 🏗️ Design SAP implementation (1-2 hours)
3. 💻 Implement 4 SAP endpoints (2-3 days)
4. 🔄 Implement hot-reload (1 day)
5. 🧪 Test end-to-end (1 day)
6. 🚀 Deploy to staging

---

## 📊 Expected Results

**After SDK Integration:**
- See real Swisper traces in SwisperStudio
- Understand execution flow visually
- Debug production issues faster
- Track state transitions

**After SAP Implementation:**
- PO can change LLM configs without code deploy
- Test configs in dev before production
- Version control for all config changes
- Faster iteration on prompt/model tuning

---

**Ready to start!** 🎉  
**Any questions? Check the guides or reach out to SwisperStudio team.**

---

**Last Updated:** November 4, 2025  
**SwisperStudio Version:** 0.2.0  
**SDK Version:** 0.2.0  
**SAP Specification:** v1.1

