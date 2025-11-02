# 🚀 SwisperStudio Development Handover

**Last Updated:** November 1, 2025
**Status:** ✅ Ready for Implementation
**Workspace:** `/root/projects/swisper_studio`

---

## 🎯 Mission

Build **SwisperStudio** from scratch: An AI-powered observability and development platform for Swisper, providing:
- 📊 **Tracing & Observability** - LangGraph execution monitoring
- 📝 **Prompt Management** - Version control, testing, deployment
- 🎨 **Agent Visualizer** - Graph-based workflow visualization
- ⚙️ **Admin UI** - Data-driven Swisper configuration
- 🔧 **Agent Builder** - Scaffold new domain agents with node libraries

---

## 📚 **CORE DOCUMENTS (Read First)**

### **1. Primary Plan** ⭐
**Location:** `docs/plans/plan_swisper_studio_mvp_v1.md`

**What's Inside:**
- 12-week MVP roadmap
- 4 phases (Traceability → Visualizer → Prompts → Admin)
- Tech stack (FastAPI + React + PostgreSQL + ClickHouse)
- Architecture diagrams
- Data models
- Week-by-week milestones

**Why Important:** This is your implementation blueprint. Everything you build references this plan.

---

### **2. Integration Guide** ⭐
**Location:** `docs/guides/swisper_studio_integration_guide.md`

**What's Inside:**
- How SwisperStudio integrates with Helvetiq (Swisper app)
- Repository strategy (separate repos, symlinks)
- Two-database approach (SwisperStudio DB + Swisper DB)
- API-driven communication
- `@traced` decorator design
- Data-driven admin UI architecture

**Why Important:** Explains the "glue" between the two systems.

---

### **3. Analysis & Decision Docs** 📊
**Location:** `docs/analysis/`

**Key Files:**
- `ANALYSIS_COMPLETE.md` - Final recommendation (build from scratch)
- `swisper_studio_fork_vs_build.md` - Fork vs build comparison
- `langfuse_features/` - Feature-by-feature analysis of Langfuse

**Why Important:** Explains WHY we chose to build from scratch and what we learned from Langfuse.

---

## 🏗️ **Project Structure**

```
swisper_studio/
├── HANDOVER.md                          ← YOU ARE HERE
├── README.md                            ← Project overview
├── SETUP_COMPLETE.md                    ← What's ready
├── PARALLEL_DEV_SETUP.md                ← Working with both repos
├── WORKSPACE_RESTORE_GUIDE.md           ← Restore dual-workspace setup
│
├── backend/                             ← EMPTY (ready for Week 1)
│   ├── app/                             (FastAPI backend)
│   │   ├── api/
│   │   │   ├── routes/                  (API endpoints)
│   │   │   └── services/                (Business logic)
│   │   ├── core/                        (Config, auth, logging)
│   │   ├── models.py                    (SQLModel schemas)
│   │   └── main.py                      (FastAPI entry)
│   ├── tests/                           (pytest tests)
│   ├── pyproject.toml                   (Poetry dependencies)
│   └── Dockerfile
│
├── frontend/                            ← EMPTY (ready for Week 1)
│   ├── src/
│   │   ├── features/                    (Feature modules)
│   │   ├── domain/                      (Types & logic)
│   │   └── lib/                         (Utilities)
│   ├── package.json                     (npm dependencies)
│   └── Dockerfile
│
├── reference/                           ← Langfuse & Helvetiq code
│   ├── langfuse/                        (Langfuse patterns - symlink)
│   └── swisper/                         (Helvetiq components - symlink)
│
├── docs/
│   ├── plans/                           ⭐ Implementation plans
│   │   └── plan_swisper_studio_mvp_v1.md
│   ├── guides/                          ⭐ Integration guides
│   │   └── swisper_studio_integration_guide.md
│   └── analysis/                        📊 Analysis docs
│
├── docker-compose.yml                   ← Local dev environment
├── .cursor/                             ← Cursor workspace rules
└── .gitignore
```

---

## 🔄 **Current Status**

### ✅ **Completed**
- [x] Analysis phase (Langfuse feature review)
- [x] Decision: Build from scratch (not fork)
- [x] MVP plan created (12 weeks)
- [x] Integration architecture designed
- [x] Repository structure initialized
- [x] Documentation copied from Helvetiq
- [x] Dual-workspace setup saved
- [x] Handover document created

### 🎯 **Next Steps (Week 1)**
- [ ] Backend scaffolding (FastAPI + SQLModel)
- [ ] Database setup (PostgreSQL + ClickHouse)
- [ ] Trace ingestion API
- [ ] `@traced` decorator implementation
- [ ] Basic trace storage

---

## 📖 **Essential Reading (Before Coding)**

### **For Backend Development:**
1. `docs/plans/plan_swisper_studio_mvp_v1.md` - Week 1-2 tasks
2. `docs/guides/swisper_studio_integration_guide.md` - SDK design
3. `.cursor/rules/00-workflow.mdc` - TDD workflow
4. `.cursor/rules/development-sop.mdc` - Development process

### **For Frontend Development:**
1. `docs/plans/plan_swisper_studio_mvp_v1.md` - Week 3-4 tasks
2. `reference/langfuse/` - UI patterns to reference
3. `reference/swisper/` - Shared components

### **For Database Design:**
1. `docs/plans/plan_swisper_studio_mvp_v1.md` - Data models
2. `.cursor/rules/40-db-policy.mdc` - Database policy
3. `.cursor/rules/41-alembic-migrations.mdc` - Migration standards

---

## 🛠️ **Development Workflow**

### **Step 1: Read the Plan**
```bash
# In swisper_studio window
cat docs/plans/plan_swisper_studio_mvp_v1.md
```

### **Step 2: Follow TDD Workflow**
```bash
# See: .cursor/rules/00-workflow.mdc
1. Write tests (pytest)
2. Update Docker container: docker compose cp backend/. backend:/code/
3. Run tests: docker compose exec backend pytest -vv
4. Verify RED (tests fail)
5. Implement code
6. Run tests again
7. Verify GREEN (tests pass)
```

### **Step 3: Reference Langfuse**
```bash
# Browse Langfuse code for patterns
cd reference/langfuse/
# Look at:
# - web/src/components/ (Frontend patterns)
# - packages/shared/src/server/ (Backend API patterns)
```

### **Step 4: Use Helvetiq Components**
```bash
# Access shared UI components
cd reference/swisper/packages/components/
# Access icons
cd reference/swisper/packages/icons/
```

---

## 🎯 **Week 1 Implementation Checklist**

Based on `docs/plans/plan_swisper_studio_mvp_v1.md` - Phase 1, Week 1-2:

### **Backend (Days 1-5)**
- [ ] Initialize FastAPI project structure
- [ ] Set up SQLModel + Alembic
- [ ] Configure PostgreSQL connection
- [ ] Configure ClickHouse connection
- [ ] Create trace data models:
  - [ ] `Trace` (top-level execution)
  - [ ] `Span` (individual steps)
  - [ ] `SpanEvent` (state changes, errors)
- [ ] Implement trace ingestion API:
  - [ ] `POST /api/v1/traces/ingest` - Accept trace data
  - [ ] Validate trace structure
  - [ ] Store in PostgreSQL + ClickHouse
- [ ] Write tests for all endpoints (TDD)

### **SDK (Days 6-7)**
- [ ] Implement `@traced` decorator:
  - [ ] Capture function inputs/outputs
  - [ ] Capture LangGraph state
  - [ ] Auto-send to SwisperStudio API
  - [ ] Error handling
- [ ] Create `create_traced_graph()` utility
- [ ] Write SDK tests
- [ ] Document SDK usage

### **Documentation (Days 8-10)**
- [ ] Update `README.md` with setup instructions
- [ ] Create `GETTING_STARTED.md`
- [ ] Document API endpoints (OpenAPI)
- [ ] Write SDK integration guide

---

## 🔗 **Integration Points with Helvetiq**

### **1. Tracing (Week 1-2)**
```python
# In Helvetiq (Swisper app)
from swisper_studio_sdk import traced

@traced(trace_name="global_supervisor")
async def run_supervisor(state: GlobalSupervisorState):
    # Automatically traces to SwisperStudio
    pass
```

### **2. Prompt Management (Week 5-8)**
```python
# In Helvetiq
from swisper_studio_sdk import get_prompt

prompt = await get_prompt("ui_node", version="v2")
```

### **3. Admin Config (Week 9-12)**
```python
# In Helvetiq
from swisper_studio_sdk import get_config

config = await get_config("llm_settings")
```

---

## 📊 **Key Architecture Decisions**

### **1. Two Separate Databases**
- **SwisperStudio DB:** Traces, prompts, Studio config
- **Swisper DB:** Users, sessions, app data
- **Why:** Clean separation, independent scaling

### **2. API-Driven Communication**
- Swisper → SwisperStudio: REST API (send traces, fetch prompts)
- **Why:** Loose coupling, easy to deploy separately

### **3. Hybrid Prompt Management**
- **Edit in UI:** SwisperStudio web interface
- **Version in DB:** Store in SwisperStudio database
- **Deploy to Git:** Generate `.md` files, commit to Helvetiq repo
- **Why:** Best of both worlds (UI UX + Git traceability)

### **4. Data-Driven Admin UI**
- Swisper backend exposes admin schema
- SwisperStudio frontend auto-generates UI
- **Why:** Zero-config, type-safe, auto-adapting

### **5. `@traced` Decorator**
- Python SDK decorator for automatic tracing
- Works on functions and LangGraph nodes
- **Why:** Developer-friendly, minimal code changes

---

## 🎨 **Reference Langfuse Patterns**

### **UI Components to Study:**
```bash
reference/langfuse/web/src/components/
├── trace/                    # Trace viewer UI
├── table/                    # Data tables
├── prompt-editor/            # Prompt editing
└── layouts/                  # Page layouts
```

### **Backend Patterns to Study:**
```bash
reference/langfuse/packages/shared/src/server/
├── ingestion/                # Trace ingestion
├── repositories/             # Data access layer
└── services/                 # Business logic
```

### **Don't Fork, but DO Learn From:**
- Trace data models
- Ingestion API patterns
- UI component structure
- Database schema design

---

## 🚨 **Important Rules (From .cursor/rules/)**

### **Development Workflow:**
1. ✅ **ALWAYS follow TDD** - Tests first, then implementation
2. ✅ **ALWAYS run tests in Docker** - Use `docker compose exec backend pytest -vv`
3. ✅ **ALWAYS update container before tests** - Use `docker compose cp`
4. ✅ **ALWAYS use verbose mode** - Run with `-vv` flag

### **Code Quality:**
1. ✅ **Type hints everywhere** - Python: `mypy`, TypeScript: `tsc`
2. ✅ **Max 3 nesting levels** - Extract helpers
3. ✅ **Guard clauses** - Early returns
4. ✅ **Structured logging** - Include correlation IDs

### **Database:**
1. ✅ **One migration per PR** - Consolidate changes
2. ✅ **Single Alembic head** - No branching
3. ✅ **Test up and down** - Verify migrations work

---

## 🆘 **Getting Help**

### **Documentation:**
- **Implementation:** `docs/plans/plan_swisper_studio_mvp_v1.md`
- **Integration:** `docs/guides/swisper_studio_integration_guide.md`
- **Testing:** `docs/guides/TESTING_GUIDE.md`
- **Prompts:** `docs/guides/prompt_writing_guide.md`
- **Agents:** `docs/guides/agent_creation_guide.md`

### **Reference Code:**
- **Langfuse patterns:** `reference/langfuse/`
- **Helvetiq components:** `reference/swisper/`

### **Cursor Rules:**
- **Workflow:** `.cursor/rules/00-workflow.mdc`
- **Development SOP:** `.cursor/rules/development-sop.mdc`
- **Code quality:** `.cursor/rules/30-35-implementation-*.mdc`

---

## ✅ **Pre-Implementation Checklist**

Before writing code, ensure you've:

- [ ] Read `docs/plans/plan_swisper_studio_mvp_v1.md` (full MVP plan)
- [ ] Read `docs/guides/swisper_studio_integration_guide.md` (integration)
- [ ] Reviewed `.cursor/rules/00-workflow.mdc` (TDD workflow)
- [ ] Browsed `reference/langfuse/` (UI/backend patterns)
- [ ] Checked `reference/swisper/` (shared components)
- [ ] Understand two-database architecture
- [ ] Understand `@traced` decorator design
- [ ] Set up Docker environment (`docker-compose.yml`)

---

## 🚀 **Quick Start Command**

```bash
# In swisper_studio workspace
cd /root/projects/swisper_studio

# 1. Read the plan
less docs/plans/plan_swisper_studio_mvp_v1.md

# 2. Review integration guide
less docs/guides/swisper_studio_integration_guide.md

# 3. Start Week 1 implementation
# (Create backend structure, DB models, trace API)

# 4. Reference Langfuse patterns
cd reference/langfuse/
ls -la

# 5. Access Helvetiq components
cd reference/swisper/
ls -la
```

---

## 🎯 **Success Criteria (Week 1)**

You'll know you're done with Week 1 when:

- [ ] FastAPI backend is running
- [ ] PostgreSQL + ClickHouse are connected
- [ ] `POST /api/v1/traces/ingest` accepts trace data
- [ ] Traces are stored in database
- [ ] `@traced` decorator works on test function
- [ ] All tests pass (`pytest -vv`)
- [ ] Documentation is updated

---

## 📞 **Communication**

### **Working in Parallel:**
- **Window 1 (Helvetiq):** Swisper app development
- **Window 2 (SwisperStudio):** Platform development
- **Coordination:** See `PARALLEL_DEV_SETUP.md`

### **Branch Strategy:**
- **Helvetiq:** `main` (stable), `feature/*` (development)
- **SwisperStudio:** `main` (stable), `feature/*` (development)

### **Documentation Updates:**
- **Helvetiq:** Swisper features, agent guides
- **SwisperStudio:** Platform features, integration guides

---

## 🎉 **You're Ready!**

**Everything you need is here:**
- ✅ Plan documented
- ✅ Architecture designed
- ✅ Repository structured
- ✅ Documentation copied
- ✅ Langfuse available for reference
- ✅ Helvetiq components accessible

**Now go build SwisperStudio! 🚀**

---

## 📚 **Document Map**

Quick reference for all key documents:

| Type | Document | Purpose |
|------|----------|---------|
| **Plan** | `docs/plans/plan_swisper_studio_mvp_v1.md` | 12-week implementation roadmap |
| **Guide** | `docs/guides/swisper_studio_integration_guide.md` | Integration with Helvetiq |
| **Analysis** | `docs/analysis/ANALYSIS_COMPLETE.md` | Decision rationale |
| **Setup** | `SETUP_COMPLETE.md` | What's ready |
| **Parallel** | `PARALLEL_DEV_SETUP.md` | Working with both repos |
| **Restore** | `WORKSPACE_RESTORE_GUIDE.md` | Restore dual-workspace |
| **Testing** | `docs/guides/TESTING_GUIDE.md` | Testing standards |
| **Workflow** | `.cursor/rules/00-workflow.mdc` | TDD workflow |

---

**Last Updated:** November 1, 2025
**Status:** ✅ Ready for Week 1 Implementation

**Happy Coding! 🚀**


