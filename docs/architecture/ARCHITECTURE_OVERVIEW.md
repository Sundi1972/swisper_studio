# SwisperStudio Architecture Overview

**Version:** 1.0  
**Date:** 2025-11-07  
**Status:** Current Architecture (85% MVP Complete)

---

## 📊 High-Level Architecture

```
┌─────────────────────────────────────┐         ┌──────────────────────────────────┐
│      SwisperStudio Platform         │         │          Swisper                 │
│                                     │         │                                  │
│  ┌──────────────┐  ┌──────────────┐│         │  ┌───────────────────────────┐  │
│  │   Frontend   │  │   Backend    ││         │  │    Swisper Backend        │  │
│  │              │  │              ││         │  │    + SDK v0.5.0           │  │
│  │  React + MUI │◄─┤   FastAPI    ││         │  │                           │  │
│  │  + Vite      │  │  + SQLModel  ││         │  │  Port 8000                │  │
│  │              │  │              ││         │  └─────────┬─────────────────┘  │
│  │  Port 3000   │  │  Port 8001   ││         │            │                    │
│  └──────────────┘  └──────┬───────┘│         │  ┌─────────▼─────────────────┐  │
│                           │        │         │  │  SwisperStudio SDK        │  │
│  ┌──────────────┐  ┌──────▼───────┐│         │  │                           │  │
│  │  PostgreSQL  │  │    Redis     ││         │  │  • @traced decorator      │  │
│  │              │  │              ││◄────────┼──┤  • State capture          │  │
│  │  Traces      │  │  Streams     ││ Events  │  │  • Tool extraction        │  │
│  │  Observations│  │  Cache       ││         │  │  • Redis publisher        │  │
│  │  Pricing     │  │              ││         │  └───────────────────────────┘  │
│  │              │  │              ││         │            │                    │
│  │  Port 5433   │  │  Port 6379   ││         │  ┌─────────▼─────────────────┐  │
│  └──────────────┘  └──────────────┘│         │  │  4 LangGraph Agents       │  │
│                                     │         │  │                           │  │
└─────────────────────────────────────┘         │  │  • Research Agent         │  │
                                                │  │  • Productivity Agent     │  │
                                                │  │  • Wealth Agent           │  │
                                                │  │  • Document Agent         │  │
                                                │  └───────────────────────────┘  │
                                                │                                  │
                                                └──────────────────────────────────┘
```

---

## 🏗️ Component Breakdown

### **SwisperStudio Platform**

#### **1. Frontend (Port 3000)**
- **Tech Stack:** React 18 + MUI v7 + Vite + TypeScript
- **Features:**
  - Trace Viewer (tree, graph, timeline)
  - Cost Management (CRUD for model pricing)
  - Configuration UI (data-driven from SAP schema)
  - User Management (admin only)
  - Real-time updates via polling

#### **2. Backend (Port 8001)**
- **Tech Stack:** FastAPI + SQLModel + Alembic + Python 3.11
- **Features:**
  - REST API with OpenAPI docs
  - JWT Authentication
  - Cost Calculation (18 models, CHF pricing)
  - Redis Consumer (observability stream)
  - Model Pricing Management
  - Trace/Observation CRUD

#### **3. PostgreSQL (Port 5433)**
- **Tables:**
  - `traces` - Top-level execution records
  - `observations` - Nested nodes (SPAN, GENERATION, TOOL, AGENT)
  - `model_pricing` - 18 models with CHF/1M token pricing
  - `projects` - Multi-project support
  - `users` - User management (future)
  - `config_versions` - Configuration history

#### **4. Redis (Port 6379)**
- **Use Cases:**
  - **Observability Stream:** Real-time trace events from Swisper SDK
  - **Tracing Toggle Cache:** Per-project on/off state (immediate effect)
  - **Consumer Group:** `swisper_studio_consumers`
  - **Stream:** `observability:events`

---

### **Swisper Platform**

#### **5. Swisper Backend (Port 8000)**
- **Tech Stack:** FastAPI + LangGraph + Python
- **Integration:** SwisperStudio SDK v0.5.0 installed in-process
- **Features:**
  - 4 LangGraph-based agents
  - Chat API endpoint
  - Tool execution (research, productivity, wealth, doc)

#### **6. SwisperStudio SDK v0.5.0**
- **Package:** `swisper-studio-sdk`
- **Components:**
  - **`@traced` Decorator:** Wraps LangGraph nodes for auto-instrumentation
  - **Graph Wrapper:** Captures state before/after each node
  - **Tool Observer:** Extracts tool calls from `_tools_executed` field
  - **Redis Publisher:** Publishes events to observability stream
  - **Cost Calculator:** Tracks tokens/costs per LLM call

#### **7. LangGraph Agents (4 Total)**
- **Research Agent:** Web search, news, fact retrieval
- **Productivity Agent:** Email, calendar, tasks
- **Wealth Agent:** Financial data, portfolio
- **Document Agent:** Document processing

---

## 🔄 Data Flow

### **Trace Creation Flow**

```
1. User Request
   └─► Swisper Frontend (Port 5173)
       └─► Swisper Backend API (Port 8000)

2. LangGraph Execution
   └─► SDK wraps graph.ainvoke()
       └─► Creates Trace (user_id, session_id, name)
       
3. Node Execution
   └─► @traced decorator captures:
       • State (before/after)
       • LLM calls (prompts, responses, tokens)
       • Tool executions (arguments, results)
       • Errors (if any)

4. Event Publishing
   └─► SDK publishes to Redis Streams
       └─► Event: { type, trace_id, observation, metadata }

5. SwisperStudio Consumption
   └─► Backend consumer reads Redis stream
       └─► Stores in PostgreSQL (traces + observations)
       └─► Calculates costs (model_pricing table)

6. Frontend Display
   └─► User opens SwisperStudio
       └─► Fetches traces via REST API
       └─► Displays tree/graph/timeline with state + costs
```

### **Tracing Toggle Flow (Q2 Feature)**

```
1. Admin toggles tracing OFF for project
   └─► Frontend: PATCH /projects/{id}/tracing { enabled: false }

2. Backend updates cache
   └─► Redis: SET tracing:project:{id} "false" (immediate)
   └─► PostgreSQL: UPDATE projects SET tracing_enabled = false

3. Next Swisper request
   └─► SDK checks: is_tracing_enabled_for_project(project_id)
       └─► Redis lookup (< 2ms)
       └─► If disabled: Skip all tracing (zero overhead)
       └─► If enabled: Normal tracing flow
```

---

## 🗄️ Database Schema

### **Traces Table**
```sql
id (UUID)
project_id (FK)
user_id (String)
session_id (String)
name (String)
input (JSON)
output (JSON)
metadata (JSON)
created_at (Timestamp)
```

### **Observations Table**
```sql
id (UUID)
trace_id (FK)
parent_observation_id (FK, nullable)
type (SPAN, GENERATION, TOOL, AGENT, EVENT)
name (String)
input (JSON)        -- State before / LLM prompt
output (JSON)       -- State after / LLM response
metadata (JSON)
level (INFO, WARNING, ERROR)
status_message (String)

-- Telemetry
start_time (Timestamp)
end_time (Timestamp)
model (String)
model_parameters (JSON)
prompt_tokens (Integer)
completion_tokens (Integer)
total_tokens (Integer)
total_cost (Decimal)        -- Calculated from model_pricing
```

### **Model Pricing Table**
```sql
id (UUID)
project_id (FK, nullable)   -- NULL = global pricing
hosting_provider (String)   -- e.g., "inference-apertus-8b"
model_name (String)         -- e.g., "swiss-ai/Apertus-8B-Instruct-2509"
type (String)               -- Chat, Embedding, Multimodal, etc.
description (Text)          -- Model capabilities
input_price_per_million (Decimal)   -- CHF
output_price_per_million (Decimal)  -- CHF
created_at (Timestamp)
updated_at (Timestamp)

UNIQUE (project_id, hosting_provider, model_name)
```

---

## 🚀 Key Features

### **1. End-to-End Tracing**
- ✅ Full LangGraph execution captured
- ✅ Nested observations (parent-child relationships)
- ✅ State diffs (before/after each node)
- ✅ LLM prompts/responses
- ✅ Tool calls with arguments/results
- ✅ Error tracking

### **2. Cost Tracking**
- ✅ 18 models configured (KVANT, Meta, Google, IBM, Qwen, etc.)
- ✅ CHF pricing per 1M tokens
- ✅ Real-time cost calculation
- ✅ Per-observation cost breakdown
- ✅ Total trace cost aggregation

### **3. Tool Visibility**
- ✅ All 4 agents harmonized (`_tools_executed` format)
- ✅ Individual tool observations (🔧 icon)
- ✅ Anti-duplication (ownership tracking)
- ✅ Tool arguments + results visible

### **4. Q2 Tracing Toggle**
- ✅ Per-project on/off control
- ✅ Immediate effect (Redis cache)
- ✅ < 2ms overhead
- ✅ UI toggle in project settings

### **5. Real-time Streaming**
- ✅ Redis Streams (50x faster than HTTP)
- ✅ Consumer group for reliability
- ✅ Automatic retry on failure

### **6. Configuration Management**
- ✅ SAP (Swisper Admin Protocol) v1.1
- ✅ Data-driven UI (auto-generates from schema)
- ✅ Environment-aware (dev/staging/production)
- ✅ Version history tracking

---

## 🔧 Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Frontend** | React | 18 |
| | MUI (Material-UI) | 7 |
| | Vite | Latest |
| | TypeScript | 5.x |
| | TanStack Query | 5.x |
| | React Router | 6.x |
| **Backend** | FastAPI | 0.115+ |
| | SQLModel | 0.0.22 |
| | Alembic | Latest |
| | Python | 3.11+ |
| **Database** | PostgreSQL | 14+ |
| | Redis | 7+ |
| **SDK** | Python | 3.11+ |
| | LangGraph | Latest |
| **Deployment** | Docker Compose | v2 |
| | uv (package manager) | Latest |

---

## 📈 Performance Metrics

| Metric | Target | Current |
|--------|--------|---------|
| **Trace Ingestion** | < 50ms | ✅ ~20ms |
| **Redis Publish** | < 5ms | ✅ ~2ms |
| **Tracing Overhead** | < 10% | ✅ ~5% |
| **Toggle Check** | < 2ms | ✅ ~1ms |
| **Frontend Load** | < 2s | ✅ ~1.5s |
| **Graph Render** | < 2s | ✅ ~1s |

---

## 🔒 Security

### **Authentication**
- **Current:** API Key (dev mode)
- **Planned:** JWT with user roles (admin, developer, qa, viewer)

### **Authorization**
- **Current:** Single API key
- **Planned:** RBAC per environment
  - Admin: Full access
  - Developer: Edit dev/staging, read production
  - QA: Edit staging, read dev/production
  - Viewer: Read-only all environments

---

## 📊 Current Status (85% MVP Complete)

### **✅ Completed Phases:**
- Phase 0: Infrastructure Foundation
- Phase 1: "Hello World" E2E Proof
- Phase 2: Rich Tracing (Full Context)
- Phase 2.5: State Visualization
- Phase 3: Graph Visualization
- Phase 4: Configuration Management
- Phase 5.1: SDK Integration & Enhancements (v0.5.0)

### **⏸️ Pending:**
- Phase 5.2: Model Pricing Management GUI (completed!)
- Phase 5.3: User Authentication (1-2 weeks) - **Critical**
- Phase 5.4: SDK Publishing (1 day) - **Recommended next**
- Phase 5c: Server-Side DataTable (2-3 days) - **Backlog**

### **Outstanding - Swisper Team:**
- SPA (Swisper Admin Protocol) Implementation (3-4 days)

---

## 🎯 Next Steps

1. **Phase 5.4:** Publish SDK to GitHub Packages (1 day)
2. **Phase 5.3:** Implement User Authentication (1-2 weeks)
3. **Phase 5c:** Add server-side pagination for traces (when needed)
4. **Production:** Deploy with HTTPS, proper auth, monitoring

---

## 📚 Documentation

- **Implementation Plan:** `docs/plans/swisper_studio_implementation_plan.md` (v3.0)
- **Agent Development Guide:** `docs/guides/agent_guides/SWISPER_AGENT_DEVELOPMENT_GUIDE.md` (v2.0)
- **SDK Simplification:** `SDK_SIMPLIFICATION_PROPOSAL_FUTURE.md` (v1.0)
- **Session Handover:** `SESSION_HANDOVER_WEEK1_COMPLETE.md` (v1.0)

---

**For interactive diagram:** Open `swisper_studio_architecture.excalidraw` at https://excalidraw.com

