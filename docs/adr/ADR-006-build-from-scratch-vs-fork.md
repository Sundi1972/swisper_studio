# ADR-006: Build from Scratch vs Fork Langfuse

**Status:** ✅ Accepted  
**Date:** 2025-11-01  
**Deciders:** Development Team, Product Owner  
**Context:** Overall Strategy - Foundation Decision

---

## Context and Problem Statement

SwisperStudio needs observability and development tools similar to Langfuse. Langfuse is open-source with a fork already available as reference.

**Question:** Should we fork Langfuse and customize it, or build SwisperStudio from scratch using Langfuse as a reference?

---

## Decision Drivers

* **Time to market** - How fast can we deliver MVP?
* **Customization needs** - How much do we need to change?
* **Maintenance burden** - Can we keep up with Langfuse updates?
* **Learning curve** - How familiar is team with Langfuse codebase?
* **Technical debt** - Will we inherit issues from Langfuse?
* **Feature fit** - Does Langfuse do what we need?

---

## Considered Options

1. **Fork Langfuse** - Start with full Langfuse codebase, modify as needed
2. **Build from scratch** - New codebase, use Langfuse as reference/spec
3. **Hybrid** - Fork some parts, build others from scratch

---

## Decision Outcome

**Chosen option:** "Build from scratch using Langfuse as living spec"

**Rationale:**

After analyzing Langfuse's codebase and our specific requirements, building from scratch is better because:

1. **Langfuse is enterprise SaaS** - Has features we don't need (multi-tenancy, billing, RBAC)
2. **Our needs are specific** - Data-driven admin UI, SAP protocol, Swisper integration
3. **Technology differences** - We want to use FastAPI (not Next.js), MUI (not Tailwind)
4. **Clean slate** - No technical debt, no legacy patterns
5. **Learning opportunity** - Team understands every line of code

**But we HEAVILY reference Langfuse:**
- Use their data models (Trace, Observation structure)
- Copy their UX patterns (trace list, detail views)
- Learn from their architecture decisions
- Reference their code as "living spec"

### Positive Consequences

* ✅ **Clean architecture** from day one (no technical debt)
* ✅ **Exact fit** for our needs (no unused features)
* ✅ **Technology choices** we prefer (FastAPI, MUI)
* ✅ **Team ownership** - We understand every component
* ✅ **Easier to maintain** - Smaller, focused codebase
* ✅ **Fast iterations** - No upstream dependencies
* ✅ **Perfect integration** with Swisper (tailored for our needs)

### Negative Consequences

* ❌ Longer initial development (can't skip UI work)
* ❌ Don't automatically get Langfuse updates
* ❌ Need to implement everything ourselves
* ❌ Risk of missing important patterns from Langfuse

---

## Pros and Cons of the Options

### Option 1: Fork Langfuse

**Pros:**
* Faster to MVP (start with working system)
* All features already implemented
* Proven architecture
* Active community

**Cons:**
* ❌ **Customization difficulty** (changing Next.js → FastAPI is massive)
* ❌ **Unused features** (multi-tenancy, billing, 100+ features we don't need)
* ❌ **Technology lock-in** (Next.js, Prisma, TypeScript backend)
* ❌ **Merge conflicts** (keeping up with upstream)
* ❌ **Learning curve** (large codebase to understand)
* ❌ **Technical debt** (inherit Langfuse's legacy decisions)

### Option 2: Build from scratch ✅ CHOSEN

**Pros:**
* ✅ **Clean codebase** (only what we need)
* ✅ **Technology freedom** (FastAPI, MUI, etc.)
* ✅ **Perfect fit** (Swisper-specific features)
* ✅ **Team ownership** (full understanding)
* ✅ **No legacy issues**

**Cons:**
* Longer development time
* Need to implement everything
* Risk of missing patterns

### Option 3: Hybrid

**Pros:**
* Cherry-pick best parts

**Cons:**
* ❌ **Complexity** (mixing two codebases)
* ❌ **Unclear boundaries** (what's forked vs. new?)
* ❌ **Merge conflicts** still exist

---

## How We Use Langfuse

**Langfuse as "Living Spec":**

```
reference/langfuse/  (Git submodule)
└── Used for:
    ✅ Data model inspiration (Trace, Observation structure)
    ✅ UX patterns (trace list, detail views)
    ✅ API design (pagination, filtering)
    ✅ Architecture decisions (soft deletes, idempotency)
    ❌ NOT for direct code copying (different tech stack)
```

**Analysis Workflow:**

Each phase starts with:
1. **Study Langfuse implementation** of that feature
2. **Document patterns** to copy
3. **Adapt to our stack** (FastAPI instead of Next.js, MUI instead of Tailwind)
4. **Implement** using learned patterns

**Example from Phase 1:**
- Studied: `langfuse/packages/shared/prisma/schema.prisma` (Project model)
- Learned: Use cuid, soft deletes, metadata JSON field
- Adapted: UUID instead of cuid (Python-friendly), same patterns otherwise
- Implemented: `backend/app/models/project.py`

---

## Implementation Strategy

### What We Copy from Langfuse

1. **Data Models**
   - Trace structure (id, name, user_id, session_id, input, output, meta, timestamp)
   - Observation structure (id, trace_id, parent_id, type, start/end time, tokens, cost)
   - Project structure (id, name, created_at, soft delete)

2. **API Patterns**
   - Pagination (page starts at 1, return meta)
   - Idempotency (check if ID exists)
   - Validation (strict schemas)
   - Error handling (typed errors)

3. **UX Flows**
   - Trace list (table with filters)
   - Trace detail (timeline + tree view)
   - Project selection
   - Date range filtering

### What We Build Differently

1. **Backend Framework**
   - Langfuse: Next.js API routes + tRPC
   - SwisperStudio: FastAPI + REST

2. **Frontend Framework**
   - Langfuse: Next.js + Tailwind
   - SwisperStudio: Vite + React + MUI

3. **Database**
   - Langfuse: Prisma + ClickHouse
   - SwisperStudio: SQLModel + Alembic (PostgreSQL only for MVP)

4. **Features**
   - Langfuse: Multi-tenant, billing, advanced RBAC
   - SwisperStudio: Single-tenant, data-driven config, SAP protocol

---

## Links

* **Previous Analysis:** `docs/analysis/ANALYSIS_COMPLETE.md`
* **Fork Comparison:** `docs/analysis/swisper_studio_fork_vs_build.md`
* **Langfuse Features:** `docs/analysis/langfuse_features/`
* **Reference Code:** `reference/langfuse/` (Git submodule)

---

## Validation

**Success Metrics:**
- ✅ MVP delivered in 10-12 weeks (competitive with fork + customization time)
- ✅ Codebase is < 50% size of Langfuse (only what we need)
- ✅ Team understands 100% of code (can explain any component)
- ✅ Zero unused features in production
- ✅ Perfect integration with Swisper (tailored features)

**Review Date:** After MVP completion (Week 12)

---

## Notes

**Why This Decision Was Made:**

From original analysis (`docs/analysis/ANALYSIS_COMPLETE.md`):
- Langfuse is 2000+ files, 100K+ lines of code
- 80%+ of features we don't need for MVP
- Technology stack mismatch (Next.js vs. our preference for FastAPI)
- Easier to build clean than to rip out unused code

**Langfuse Still Valuable:**
- Serves as architectural reference
- Validates our data models
- Provides UX patterns
- Living documentation of what works

**Not Reinventing the Wheel:**
- We're not inventing new concepts
- We're implementing proven patterns
- Langfuse shows us "what" to build
- We implement "how" in our tech stack

