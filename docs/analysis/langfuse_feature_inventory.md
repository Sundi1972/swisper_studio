# Langfuse Feature Inventory & Analysis

**Version:** v1.0
**Date:** 2025-11-01
**Last Updated By:** heiko
**Status:** Active Analysis

---

## Purpose

Comprehensive analysis of Langfuse features to determine:
1. What features exist
2. How they work (architecture)
3. Relevance to Swisper SDK needs
4. Build vs Fork decision

---

## Core Requirements (Swisper SDK)

### Must-Have (P0):
1. **Detailed Tracing** - Across all graphs, tools, LLM calls
2. **Prompt Versioning** - See real prompts used in execution
3. **State Tracking** - Track state changes of all state objects

### Nice-to-Have (P1):
- Cost tracking
- Performance metrics
- Error tracking

### Not Needed:
- Multi-tenant features
- Enterprise features
- Payment/billing
- Social features

---

## Feature Categories

Based on codebase analysis:

```
├── CORE TRACING (Must-Have)
│   ├── traces/              # Execution traces
│   ├── observations/        # Spans/generations
│   ├── sessions/            # Session tracking
│   └── trace-graph-view/    # Visual trace viewer
│
├── PROMPT MANAGEMENT (Must-Have)
│   ├── prompts/             # Prompt versioning
│   └── playground/          # Prompt testing
│
├── EVALUATION (Nice-to-Have)
│   ├── scores/              # LLM output scoring
│   ├── evals/               # Evaluation templates
│   ├── datasets/            # Test datasets
│   └── experiments/         # A/B testing
│
├── ANALYTICS (Nice-to-Have)
│   ├── dashboard/           # Metrics dashboard
│   ├── models/              # Model usage tracking
│   └── widgets/             # Dashboard widgets
│
├── INFRASTRUCTURE (Need Some)
│   ├── auth/                # Authentication
│   ├── projects/            # Project management
│   ├── organizations/       # Multi-tenancy
│   └── public-api/          # Ingestion API
│
└── ENTERPRISE (Don't Need)
    ├── rbac/                # Role-based access
    ├── payment-banner/      # Billing
    ├── slack/               # Integrations
    ├── mixpanel-integration/
    └── posthog-integration/
```

---

## Detailed Feature Analysis

(Individual feature docs below - see index)

---

## Data Model Overview

### Core Tables (from Prisma schema):

**Tracing Core:**
- `LegacyPrismaTrace` - Main trace record
- `LegacyPrismaObservation` - Spans/generations
- `TraceSession` - User session grouping
- `LegacyPrismaScore` - Evaluation scores

**Prompt Management:**
- `Prompt` - Prompt versions
- `PromptDependency` - Prompt relationships
- `PromptProtectedLabels` - Label protection

**Datasets & Evaluation:**
- `Dataset` - Test datasets
- `DatasetItem` - Individual test cases
- `DatasetRuns` - Evaluation runs
- `DatasetRunItems` - Run results
- `EvalTemplate` - Evaluation templates

**Infrastructure:**
- `Organization` - Multi-tenant orgs
- `Project` - Projects within orgs
- `User` - User accounts
- `ApiKey` - API authentication

**Analytics:**
- `Model` - LLM model tracking
- `Price` - Cost calculation
- `ScoreConfig` - Score configurations

**ClickHouse (Analytics DB):**
- Separate schema for high-volume metrics
- Stores aggregated traces for fast queries
- Powers dashboard analytics

---

## Architecture Layers

### 1. Ingestion Layer
**What:** API endpoints for receiving traces from SDKs

**Components:**
- `POST /api/public/ingestion` - Main ingestion endpoint
- `POST /api/public/traces` - Create trace
- `POST /api/public/generations` - Create generation/span
- `POST /api/public/scores` - Add scores

**Tech Stack:**
- Next.js API routes
- tRPC for internal API
- PostgreSQL for storage
- Worker for async processing

**Complexity:** Medium (well-defined REST API)

---

### 2. Storage Layer
**What:** Data persistence

**Components:**
- **PostgreSQL** - Primary data (metadata, prompts, users)
- **ClickHouse** - Analytics data (traces, metrics)
- **Redis** - Queue & cache
- **S3/MinIO** - Large objects (media, exports)

**Sync:**
- Worker syncs PostgreSQL → ClickHouse
- Async via BullMQ job queue

**Complexity:** High (dual database sync)

---

### 3. Query Layer
**What:** Data retrieval and aggregation

**Components:**
- tRPC routers (`web/src/server/api/routers/`)
- ClickHouse queries for analytics
- PostgreSQL queries for metadata

**Tech Stack:**
- Prisma ORM (PostgreSQL)
- Raw SQL (ClickHouse)
- tRPC (type-safe API)

**Complexity:** Medium-High (complex aggregations)

---

### 4. UI Layer
**What:** Web interface

**Components:**
- Next.js 15 pages
- React components
- TanStack Table (data tables)
- Recharts (visualizations)

**Features:**
- Server-side rendering
- Real-time updates (polling)
- Complex filtering

**Complexity:** High (mature UI with many features)

---

### 5. Worker Layer
**What:** Background processing

**Components:**
- BullMQ jobs
- ClickHouse sync
- Batch exports
- Evaluations

**Tech Stack:**
- Node.js worker process
- BullMQ (Redis-backed queue)
- Same codebase as web

**Complexity:** Medium (job orchestration)

---

## State Tracking Analysis

**Your Requirement:** Track state changes of all state objects

**Langfuse Current State:**
❌ **Not natively supported**

**What Langfuse Tracks:**
- Traces (execution flow)
- Observations (LLM calls, tool usage)
- Scores (evaluation results)
- Metadata (arbitrary JSON)

**What Langfuse DOESN'T Track:**
- State object snapshots
- State transitions
- State diffs

**To Add State Tracking:**
Would need to:
1. Add `StateSnapshot` model to Prisma
2. Create ingestion endpoint for state updates
3. Add UI to visualize state timeline
4. Sync to ClickHouse for analytics

**Complexity:** Medium (new feature, well-defined)

---

## Feature Deep Dives

(See individual files in `docs/analysis/langfuse_features/`)

---

## Related Documentation

- Individual feature docs: `docs/analysis/langfuse_features/`
- Database analysis: `docs/specs/langfuse_database_strategy.md`
- ClickHouse analysis: `docs/specs/langfuse_clickhouse_analysis.md`
- Implementation plan: `docs/plans/plan_langfuse_self_hosting_v1.md`

---

## Next Steps

1. ✅ Feature inventory (this doc)
2. 🔄 Deep-dive per feature (creating now)
3. ⏳ Build vs Fork recommendation
4. ⏳ Implementation roadmap

---

**Analysis in progress...**

