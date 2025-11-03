# SwisperStudio - Platform Overview

**Version:** v1.0  
**Last Updated:** 2025-11-03  
**Last Updated By:** heiko  
**Status:** Active

**This is the high-level overview and specification for SwisperStudio.**

---

## What is SwisperStudio?

**SwisperStudio** is an **observability and configuration management platform** for Swisper AI deployments.

It provides:
- 🔍 **Complete observability** - Every LLM call, state change, tool execution
- 📊 **Visual debugging** - Interactive graphs of agent execution
- ⚙️ **No-code config management** - Change LLM models without deployments
- 🌍 **Multi-environment** - Separate dev, staging, production
- 📈 **Cost tracking** - Token usage and spending per trace
- 🔄 **Version control** - Config history with rollback

**Target Users:**
- Product Owners (manage configs)
- Developers (debug production issues)
- DevOps (monitor performance)
- Executives (track costs)

---

## Core Capabilities

### 1. Multi-Environment Management

**Every customer project has 3 environments:**
```
Project: "Customer A"
├── Dev Environment
│   ├── URL: https://dev.customer-a.com
│   └── Purpose: Testing and iteration
├── Staging Environment  
│   ├── URL: https://staging.customer-a.com
│   └── Purpose: QA and UAT
└── Production Environment
    ├── URL: https://prod.customer-a.com
    └── Purpose: Live customer traffic
```

**Environment selector visible on ALL pages** - always know which environment you're viewing.

---

### 2. End-to-End Tracing

**Captures everything:**
- Full state at each node (input/output/diff)
- LLM prompts and responses
- Token counts and costs
- Model parameters (temperature, max_tokens)
- Tool calls and results
- Error tracking
- Performance metrics

**Visual debugging:**
- Tree view (nested observations)
- Graph view (force-directed layout)
- System architecture (all agents)

---

### 3. Configuration Management

**No-code config changes:**
- Select config table (e.g., LLM Node Config)
- View all records in searchable/sortable table
- Edit any record
- Save as version (v1, v2, v3...)
- Deploy to dev → test → deploy to staging → deploy to production

**Features:**
- Auto-generated forms (from SAP schema)
- Version history with lineage
- Deployment tracking
- Rollback support
- Immediate effect (hot-reload)

---

### 4. Data-Driven UI

**Auto-adapts to Swisper:**
- Fetches schema from Swisper via SAP
- Generates forms automatically
- New config table in Swisper → Shows in UI automatically
- New field → Appears in form automatically

**No hardcoded forms!**

---

## Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────┐
│ SwisperStudio Frontend (React + MUI)           │
│ http://localhost:3000                           │
│                                                 │
│ - Environment selector                          │
│ - Trace viewer (tree + graph)                   │
│ - Config management (auto-generated)            │
│ - DataTable (reusable, search + sort)          │
└─────────────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────────────┐
│ SwisperStudio Backend (FastAPI)                │
│ http://localhost:8001                           │
│                                                 │
│ - Environment API                               │
│ - Config version API                            │
│ - Trace ingestion API                           │
│ - Graph builder service                         │
└─────────────────────────────────────────────────┘
      ↕                           ↕
┌──────────────────┐    ┌─────────────────────────┐
│ PostgreSQL       │    │ Swisper (SAP)           │
│ - Traces         │    │ - Schema endpoint       │
│ - Observations   │    │ - Config CRUD           │
│ - Versions       │    │ - 18 Kvant models       │
│ - Deployments    │    └─────────────────────────┘
└──────────────────┘
```

### Technology Stack

**Backend:**
- FastAPI (Python web framework)
- PostgreSQL (database)
- SQLModel (ORM)
- Alembic (migrations)
- Docker (containers)

**Frontend:**
- React 18 (UI framework)
- Material-UI (MUI v7) (components)
- React Query (data fetching)
- React Router (navigation)
- Vis-Network (graph visualization)

**Testing:**
- Pytest (backend)
- Vitest (frontend)
- Browser testing (manual)

---

## Key Concepts

### SAP (Swisper Admin Protocol)

**The contract between SwisperStudio and Swisper:**
- REST API specification
- Schema format (JSON)
- Field types and validation
- CRUD operations
- Version: v1.1

**See:** `docs/SAP_CONTRACT.md`

---

### Environment-First Design

**Everything is scoped to an environment:**
- Traces from dev environment
- Graphs from dev environment
- Config deployed to dev environment

**Switch environments** → See different data immediately.

---

### Config Versioning

**How it works:**
```
1. Edit config → Save as v1
2. Deploy to dev → Test
3. Iterate → Save as v2, v3...
4. Happy? → Deploy to staging
5. QA approves? → Deploy to production
```

**Rollback:** Deploy previous version (v2 → v1)

---

### Data-Driven UI

**Schema-driven forms:**
```
SAP Schema → SwisperStudio → Auto-generated form
```

**Example:**
- Schema says: `type: "select", options: [18 models]`
- SwisperStudio renders: Dropdown with 18 models
- Schema says: `type: "number", step: 0.1`
- SwisperStudio renders: Number input (0.1 increments)

---

## Phases Delivered

| Phase | Name | Status | Duration | Tests |
|-------|------|--------|----------|-------|
| 0 | Infrastructure | ✅ Complete | 1 day | N/A |
| 1 | Hello World | ✅ Complete | 1 day | 23/23 |
| 2 | Rich Tracing | ✅ Complete | 1 day | 46/46 |
| 3 | Visualization | ✅ Complete | 2 days | 57/57 |
| 4 | Configuration | ✅ Complete | 2 days | 88/88 |
| 5 | Enhancements | ⏸️ Optional | TBD | TBD |

**Total:** 5 days (planned 12+ weeks)

---

## Success Metrics

**Phase 4 Delivered:**
- ✅ PO can change configs without developer
- ✅ Config changes deploy in < 2 seconds
- ✅ Multi-environment support
- ✅ Auto-generated UI
- ✅ Version history
- ✅ 88/88 tests passing

**Overall MVP:**
- ✅ Complete observability (traces, graphs, costs)
- ✅ No-code config management
- ✅ Multi-environment support
- ✅ Data-driven architecture
- ✅ Production-ready

---

## Quick Start

### For Developers:
1. Read: `docs/plans/swisper_studio_implementation_plan.md`
2. Setup: `README.md`
3. Reference: Phase handover docs (PHASE1_HANDOVER.md, etc.)

### For Product Owners:
1. Read: This document (overview)
2. Features: See "Core Capabilities" above
3. Try it: http://localhost:3000

### For Swisper Team:
1. Read: `docs/SAP_CONTRACT.md`
2. Implement: `docs/architecture/swisper_sap_implementation_guide.md`
3. Reference: `backend/app/api/routes/mock_sap.py`

---

## Related Documents

**Plans:**
- `docs/plans/swisper_studio_implementation_plan.md` - **Master plan**
- `docs/plans/plan_phase4_config_v1.md` - Phase 4 details

**Specs:**
- `docs/specs/spec_sap_v1_comprehensive.md` - SAP API specification

**Handovers:**
- `PHASE5_HANDOVER.md` - What's next
- `PHASE4_COMPLETE_SUMMARY.md` - What was delivered
- `PHASE4_HANDOVER.md` - Phase 4 kickoff (historical)

**Architecture:**
- `docs/SAP_CONTRACT.md` - Contract index
- `docs/architecture/swisper_sap_implementation_guide.md` - Swisper guide

**Analysis:**
- `docs/analysis/phase4_config_analysis.md` - Phase 4 research

---

**Document Owner:** heiko  
**Last Updated:** November 3, 2025  
**Status:** Active - SwisperStudio v1.0

