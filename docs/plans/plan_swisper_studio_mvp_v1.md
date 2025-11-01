# SwisperStudio MVP - Build Plan

**Version:** v1.0
**Date:** 2025-11-01
**Last Updated By:** heiko
**Status:** Approved for Implementation
**Timeline:** 12 weeks
**Decision:** Build from scratch using Langfuse as living spec

---

## Changelog

### v1.0 - 2025-11-01
- Initial MVP plan approved
- Scope: Traceability, Agent Visualizer, Prompt Editor, Admin UI
- Architecture decisions documented
- Integration strategy defined

---

## Executive Summary

**Goal:** Build SwisperStudio as observability & config management platform for Swisper SDK

**Approach:** Build from scratch (Python/React) using Langfuse fork as architectural reference

**Timeline:** 12 weeks to MVP

**Team:** 1-2 developers

---

## MVP Scope

### ✅ **In Scope:**
1. **Traceability** - View traces, observations, costs
2. **Agent Visualizer** - Graph view of agent execution
3. **Prompt Editor MVP** - Create/edit/version/deploy prompts
4. **Admin UI** - Manage Swisper config, users, API keys

### ❌ **Out of Scope (Post-MVP):**
- State tracking (V2)
- Advanced prompt editor (state-aware placeholders) (V2)
- Agent builder (visual editor) (V3)
- Code generation (V3)
- Advanced analytics (V2)

---

## Repository Strategy

### **Setup:**

```bash
# New production repo
github.com/Fintama/swisper_studio (new)
├── backend/           # Python/FastAPI
├── frontend/          # React/Vite
├── reference/         # Git submodule
│   └── langfuse/      # Fork (living spec)
└── docs/
```

**Existing fork kept as reference:**
```bash
github.com/Sundi1972/swisper_studio (existing)
# Keep unchanged
# Use as living spec when building
# Copy data models, patterns, UI designs
```

---

## Architecture Overview

### **System Diagram:**

```
┌────────────────────────────────────────────────┐
│            Swisper Ecosystem                   │
├────────────────────────────────────────────────┤
│                                                │
│  ┌──────────────────────────────────────────┐ │
│  │    Swisper Backend (FastAPI)             │ │
│  │    github.com/Fintama/helvetiq           │ │
│  ├──────────────────────────────────────────┤ │
│  │  • AI Assistant                          │ │
│  │  • Domain Agents                         │ │
│  │  • @traced decorator usage               │ │
│  └──────────────────────────────────────────┘ │
│      │ sends traces    │ reads config/prompts │
│      ▼                 ▼                       │
│  ┌──────────────────────────────────────────┐ │
│  │  SwisperStudio (Python/FastAPI + React)  │ │
│  │  github.com/Fintama/swisper_studio       │ │
│  ├──────────────────────────────────────────┤ │
│  │  Ingestion API  │  Config API  │  Admin  │ │
│  │  • POST traces  │  • GET config│  • Users│ │
│  │  • POST scores  │  • GET prompt│  • Keys │ │
│  └──────────────────────────────────────────┘ │
│      │                                         │
│  ┌───┴──────────────────────────────────────┐ │
│  │  SwisperStudio DB  │  Swisper DB         │ │
│  │  • Traces          │  • Users            │ │
│  │  • Prompts         │  • Sessions         │ │
│  │  • Studio Config   │  • App Data         │ │
│  └────────────────────────────────────────────┘
│                                                │
└────────────────────────────────────────────────┘
```

### **Key Decisions:**

1. **Separate Databases** ✅
   - SwisperStudio DB: Traces, prompts, studio config
   - Swisper DB: Users, sessions, application data
   - Communication via APIs

2. **API-Driven Integration** ✅
   - Swisper calls SwisperStudio APIs
   - No direct DB access between systems
   - Clean separation of concerns

3. **Git-Based Deployment** ✅
   - Edit in SwisperStudio UI
   - Deploy generates YAML/Markdown files
   - Commits to Git repo
   - Swisper syncs from Git

---

## Admin Integration - Data-Driven UI

### **Concept:** Auto-Adapting Admin Panel

**Swisper Backend exposes admin schema:**

```python
# Swisper Backend: /api/admin/schema
{
  "version": "1.0",
  "sections": [
    {
      "id": "features",
      "title": "Feature Flags",
      "fields": [
        {
          "type": "boolean",
          "key": "voice_enabled",
          "label": "Voice Interface",
          "description": "Enable voice input/output",
          "current_value": true
        },
        {
          "type": "boolean",
          "key": "fact_preloading",
          "label": "Fact Preloading",
          "current_value": true
        }
      ]
    },
    {
      "id": "llm",
      "title": "LLM Configuration",
      "fields": [
        {
          "type": "select",
          "key": "default_model",
          "label": "Default Model",
          "options": ["gpt-4", "gpt-4-turbo", "claude-3-opus"],
          "current_value": "gpt-4"
        },
        {
          "type": "slider",
          "key": "temperature",
          "label": "Temperature",
          "min": 0.0,
          "max": 2.0,
          "step": 0.1,
          "current_value": 0.7
        }
      ]
    }
  ]
}
```

**SwisperStudio Frontend auto-generates UI:**
- Fetches schema from Swisper
- Dynamically renders form
- Validates inputs
- Deploys changes to Git

**Benefits:**
- ✅ Zero config in SwisperStudio
- ✅ Add field in Swisper → UI auto-updates
- ✅ Type-safe, self-documenting
- ✅ Version-safe

---

## Traceability Integration - Developer Experience

### **Design Goal: Dead Simple** 🎯

**Swisper SDK provides `@traced` decorator:**

```python
# Usage in Swisper nodes:

from swisper_sdk import traced

@traced("intent_classification")  # ONE LINE!
def intent_classification_node(state: GlobalSupervisorState):
    intent = classify_intent(state.messages[-1])
    state.current_intent = intent
    return state

# Auto-captures:
# ✅ Input state
# ✅ Output state
# ✅ State diff
# ✅ Duration
# ✅ Errors
# ✅ Parent/child relationships
```

### **Auto-Instrumentation for LangGraph:**

```python
from swisper_sdk import create_traced_graph

# Replace:
graph = StateGraph(GlobalSupervisorState)

# With:
graph = create_traced_graph(
    GlobalSupervisorState,
    trace_name="global_supervisor",
    auto_trace_nodes=True  # 🎯 Auto-trace all nodes!
)

# All nodes automatically instrumented!
```

### **SDK Architecture:**

```
swisper_sdk/
├── tracing/
│   ├── decorator.py         # @traced decorator
│   ├── graph_wrapper.py     # create_traced_graph()
│   ├── context.py           # Trace context manager
│   └── client.py            # SwisperStudio API client
├── config/
│   └── loader.py            # Load config from SwisperStudio
└── prompts/
    └── loader.py            # Load prompts from SwisperStudio
```

---

## Implementation Timeline

### **Phase 1: Traceability** (4 weeks)

#### Week 1-2: Backend Foundations
- [ ] FastAPI project setup
- [ ] PostgreSQL + Alembic
- [ ] Copy Trace/Observation models from Langfuse
- [ ] Ingestion API endpoints
  - `POST /api/v1/traces`
  - `POST /api/v1/observations`
  - `POST /api/v1/scores`
- [ ] Basic auth (API keys)

#### Week 3-4: Frontend Basics
- [ ] React + Vite setup
- [ ] Trace list view (table)
- [ ] Trace detail view
- [ ] JSON viewer
- [ ] Basic search/filter

**Milestone:** Traces visible in UI

---

### **Phase 2: Agent Visualizer** (2 weeks)

#### Week 5-6: Graph Visualization
- [ ] React Flow integration
- [ ] Graph builder logic (backend)
- [ ] Auto-layout algorithm
- [ ] Node types (Agent, Span, Generation, Tool)
- [ ] Interactive features (click, hover, zoom)

**Milestone:** Agent flow visualization works

---

### **Phase 3: Prompt Editor MVP** (3 weeks)

#### Week 7-8: Prompt Management
- [ ] Prompt CRUD API
- [ ] Version management
- [ ] Label system (production, staging)
- [ ] Basic editor UI
- [ ] Version history UI

#### Week 9: Deployment Workflow
- [ ] Git integration (GitPython)
- [ ] Generate .md files from DB
- [ ] Commit + PR creation
- [ ] Deployment status tracking
- [ ] Swisper integration (load prompts via API)

**Milestone:** Deploy prompt to Git works

---

### **Phase 4: Admin UI** (3 weeks)

#### Week 10-11: Config Management
- [ ] Config CRUD API
- [ ] Data-driven admin schema endpoint (in Swisper)
- [ ] Auto-generating form UI (in SwisperStudio)
- [ ] YAML generation
- [ ] Git deployment (like prompts)
- [ ] Preview + diff viewer

#### Week 12: Basic Admin
- [ ] User management (CRUD)
- [ ] API key management
- [ ] Simple RBAC
- [ ] Login/logout

**Milestone:** MVP Complete ✅

---

## Data Models (Copied from Langfuse)

### **Core Tables:**

```python
class Trace(SQLModel, table=True):
    """Main trace record"""
    id: str
    name: str | None
    user_id: str | None
    session_id: str | None
    metadata: dict | None
    tags: list[str]
    input: dict | None
    output: dict | None
    timestamp: datetime
    project_id: str

class Observation(SQLModel, table=True):
    """Spans, generations, events"""
    id: str
    trace_id: str
    parent_observation_id: str | None
    type: ObservationType  # SPAN, GENERATION, EVENT, TOOL, AGENT
    name: str | None
    start_time: datetime
    end_time: datetime | None
    input: dict | None
    output: dict | None
    metadata: dict | None
    model: str | None
    prompt_tokens: int
    completion_tokens: int
    total_cost: Decimal | None

class Prompt(SQLModel, table=True):
    """Prompt versions"""
    id: str
    name: str
    version: int
    prompt: dict  # JSON content
    config: dict  # LLM config
    labels: list[str]  # production, staging, etc.
    commit_message: str | None
    created_by: str
    created_at: datetime

class SwisperConfig(SQLModel, table=True):
    """Swisper configuration"""
    id: str
    version: int
    config_data: dict  # Full YAML as JSON
    deployed: bool
    created_by: str
    created_at: datetime
    deployed_at: datetime | None
```

---

## Tech Stack

### **Backend:**
- FastAPI (API framework)
- SQLModel + Alembic (ORM + migrations)
- PostgreSQL (primary DB)
- ClickHouse (analytics, optional for MVP)
- Redis (cache/queue)
- GitPython (Git operations)
- Pydantic (validation)

### **Frontend:**
- React + Vite (framework)
- React Router (routing)
- TanStack Query (data fetching)
- React Flow (graph visualization)
- TanStack Table (data tables)
- Monaco Editor (code editing)
- Tailwind CSS + shadcn/ui (styling)
- Zod + React Hook Form (forms)

---

## Project Structure

```
swisper_studio/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── traces.py
│   │   │   │   ├── observations.py
│   │   │   │   ├── prompts.py
│   │   │   │   ├── config.py
│   │   │   │   └── admin.py
│   │   │   └── deps.py
│   │   ├── models/
│   │   │   ├── trace.py
│   │   │   ├── observation.py
│   │   │   ├── prompt.py
│   │   │   ├── config.py
│   │   │   └── user.py
│   │   ├── services/
│   │   │   ├── trace_service.py
│   │   │   ├── prompt_service.py
│   │   │   ├── config_service.py
│   │   │   └── git_service.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── database.py
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   │   ├── features/
│   │   │   ├── traces/
│   │   │   ├── prompts/
│   │   │   ├── config/
│   │   │   └── admin/
│   │   ├── components/
│   │   ├── lib/
│   │   └── main.tsx
│   └── package.json
│
├── reference/
│   └── langfuse/  # Git submodule (living spec)
│
└── docs/
    └── api/       # API documentation
```

---

## Swisper SDK Structure

```
# In helvetiq repo:
backend/
├── swisper_sdk/              # NEW PACKAGE
│   ├── __init__.py
│   ├── tracing/
│   │   ├── __init__.py
│   │   ├── decorator.py      # @traced decorator
│   │   ├── graph_wrapper.py  # create_traced_graph()
│   │   ├── context.py        # Trace context
│   │   └── client.py         # SwisperStudio API client
│   ├── config/
│   │   ├── __init__.py
│   │   └── loader.py         # Load config from SwisperStudio
│   └── prompts/
│       ├── __init__.py
│       └── loader.py         # Load prompts from SwisperStudio
│
└── app/
    └── api/
        └── services/
            └── agents/
                └── global_supervisor/
                    ├── global_supervisor.py  # Uses @traced
                    └── nodes/
                        ├── intent_classification_node.py  # @traced
                        ├── memory_node.py                 # @traced
                        └── ...
```

---

## Config Management Workflow

### **Developer Experience:**

```
1. Edit in SwisperStudio UI
   ├─ Form with validation
   ├─ Live preview (YAML)
   └─ Diff viewer (changes)

2. Click "Deploy"
   ├─ Generates swisper_config.yaml
   ├─ Commits to Git (helvetiq repo)
   ├─ Creates PR (optional)
   └─ Triggers CI/CD

3. CI/CD Pipeline
   ├─ Tests pass
   ├─ Merge PR
   └─ Deploy to production

4. Swisper Backend
   ├─ On startup: Load YAML → Sync to DB
   ├─ Runtime: Read from DB (fast)
   └─ Config reload: Watch file changes (optional)
```

---

## MVP Success Criteria

### **Week 12 - Definition of Done:**

✅ **Traceability:**
- [ ] Swisper sends traces to SwisperStudio
- [ ] Traces visible in list view
- [ ] Trace detail view shows observations
- [ ] Graph visualization displays agent flow
- [ ] Search and filter work
- [ ] Cost tracking is accurate

✅ **Prompts:**
- [ ] Create/edit prompts in UI
- [ ] Version management functional
- [ ] Label system works (production, staging)
- [ ] Deploy to Git successful
- [ ] Swisper loads prompts from SwisperStudio API
- [ ] Fallback to .md files if API unavailable

✅ **Config:**
- [ ] Data-driven admin schema works
- [ ] UI auto-generates from schema
- [ ] Edit config in UI
- [ ] Preview YAML changes
- [ ] Deploy to Git successful
- [ ] Swisper syncs config on deployment

✅ **Admin:**
- [ ] User login/logout
- [ ] Create/manage API keys
- [ ] Basic RBAC (admin/viewer roles)

✅ **Production Ready:**
- [ ] Docker images built
- [ ] docker-compose.yml for local dev
- [ ] CI/CD pipeline
- [ ] Health check endpoints
- [ ] Basic monitoring

---

## Post-MVP Roadmap

### **V2 Features** (Weeks 13-24):
- State tracking (requirement #3)
- Advanced prompt editor (state-aware placeholders)
- ClickHouse analytics dashboards
- Performance metrics
- Evaluation system (scores, datasets)

### **V3 Features** (Weeks 25-36):
- Agent builder (visual editor)
- Node library
- Code generation
- Advanced admin (user management, fine-grained RBAC)

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Langfuse reference becomes outdated | Low | Low | Pin to commit, periodic updates |
| Integration complexity | Medium | Medium | Start with simple SDK, iterate |
| Timeline slips | Medium | Medium | MVP scope is flexible, prioritize |
| Performance issues | Low | Medium | ClickHouse for analytics, optimize later |
| Git conflicts | Low | Medium | Clear deployment workflow, automation |

---

## Team & Resources

### **Resource Plan:**

**Option A: 2 Developers (6 weeks calendar)**
- Dev 1: Backend (models, APIs, Git integration)
- Dev 2: Frontend (UI, graph viz, forms)
- Pair on: Critical integrations

**Option B: 1 Developer (12 weeks calendar)**
- Sequential implementation
- Backend first (weeks 1-6)
- Frontend next (weeks 7-12)

### **Weekly Standups:**
- Demo progress
- Review blockers
- Adjust scope if needed

---

## Next Steps

### **Immediate (This Week):**
1. [ ] Create new `swisper_studio` repo
2. [ ] Add Langfuse fork as git submodule
3. [ ] Setup FastAPI boilerplate
4. [ ] Copy Trace/Observation models from Langfuse
5. [ ] Write first migration

### **Week 1:**
1. [ ] Backend foundations
2. [ ] Ingestion API
3. [ ] Basic auth

### **Week 2:**
1. [ ] Frontend setup
2. [ ] Trace list view
3. [ ] End-to-end test (send trace → see in UI)

---

## Approval

- [ ] Scope approved by PO
- [ ] Architecture approved by Tech Lead
- [ ] Timeline approved by Team
- [ ] Budget approved

**Approved by:** ___________
**Date:** ___________

---

**Ready to start implementation!** 🚀

