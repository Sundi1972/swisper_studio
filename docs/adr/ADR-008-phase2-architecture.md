# ADR-008: Phase 2 Architecture - Model Pricing & Navigation

**Date:** November 2, 2025  
**Status:** Accepted  
**Context:** Phase 2 implementation (Rich Tracing)  
**Deciders:** Team + PO

---

## Context

Phase 2 introduces several architectural decisions that will impact the entire SwisperStudio platform:

1. **Model pricing configuration** - How to handle pricing for cost calculation
2. **Frontend navigation structure** - How users navigate the application
3. **Cost calculation approach** - Where and how costs are calculated

These decisions affect scalability, maintainability, and user experience.

---

## Decision 1: Project-Level Model Pricing with Provider Granularity

### Decision

Model pricing will be configured at **project level** with **provider + model name** granularity, stored in a dedicated `model_pricing` table.

### Schema

```python
class ModelPricing(SQLModel, table=True):
    id: UUID
    project_id: UUID | None  # NULL for default pricing
    hosting_provider: str    # "openai", "anthropic", "azure", etc.
    model_name: str          # "gpt-4-turbo", "claude-3-opus", etc.
    input_price_per_million: Decimal   # USD per 1M tokens
    output_price_per_million: Decimal  # USD per 1M tokens
    
    # Unique constraint: (project_id, hosting_provider, model_name)
```

### Rationale

**Why project-level:**
- Different projects may use different providers (OpenAI vs Azure vs self-hosted)
- Different teams may have different enterprise agreements/pricing
- Projects in different regions may have different costs
- Allows per-project cost tracking and budgeting

**Why provider + model granularity:**
- Same model name can exist across providers (e.g., "gpt-4-turbo" on OpenAI vs Azure)
- Providers have different pricing structures
- Fine-tuned models have custom pricing
- Swisper allows **per-node model configuration** → each observation can use a different model/provider

**Why database over configuration files:**
- Dynamic updates without deployment
- Per-project configuration UI (Phase 4)
- Historical pricing tracking
- Easier to query and validate

### Lookup Strategy

```python
def get_model_pricing(project_id: UUID, provider: str, model: str):
    # 1. Try project-specific pricing
    pricing = query(project_id=project_id, provider=provider, model=model)
    
    # 2. Fall back to default pricing (project_id=NULL)
    if not pricing:
        pricing = query(project_id=None, provider=provider, model=model)
    
    # 3. Log warning if still not found
    if not pricing:
        logger.warning(f"No pricing for {provider}/{model} in project {project_id}")
        return None
    
    return pricing
```

### Alternatives Considered

**Alternative 1: Hardcoded pricing**
- ❌ Can't handle custom models or enterprise pricing
- ❌ Requires code changes for price updates
- ❌ No per-project customization

**Alternative 2: Single global pricing table**
- ❌ Can't handle per-project pricing
- ❌ Difficult to manage multi-tenant scenarios

**Alternative 3: Model-only (no provider)**
- ❌ Ambiguity for same model on different providers
- ❌ Can't distinguish OpenAI GPT-4 vs Azure GPT-4 pricing

---

## Decision 2: Project Workspace with Sidebar Navigation

### Decision

Implement a **project workspace pattern** with persistent sidebar navigation when user is within a project context.

### Navigation Structure

```
Projects List (/projects)
    ↓ Click project card
Project Workspace (/projects/:projectId)
    ├─ Layout: Header + Sidebar + Content
    ├─ Sidebar Menu:
    │   ├─ 📊 Overview
    │   ├─ 🔍 Tracing
    │   ├─ 📈 Analytics (grayed out for MVP)
    │   ├─ 🌐 Graphs (grayed out for MVP)
    │   └─ ⚙️ Configuration
    └─ Routes:
        ├─ /projects/:projectId (Overview)
        ├─ /projects/:projectId/tracing (Trace List)
        ├─ /projects/:projectId/tracing/:traceId (Trace Detail)
        ├─ /projects/:projectId/analytics
        ├─ /projects/:projectId/graphs
        └─ /projects/:projectId/config
```

### Rationale

**Why workspace pattern:**
- **Context preservation** - User always knows which project they're in
- **Consistent navigation** - Sidebar persists across all project pages
- **Scalable** - Easy to add new sections (Analytics, Graphs, etc.)
- **Familiar** - Matches Swisper's agent sidebar pattern
- **Professional** - Standard SaaS application pattern

**Why sidebar navigation:**
- **Always visible** - No need to find menu
- **Quick switching** - One click to any section
- **Visual hierarchy** - Clear organization of features
- **Responsive** - Can collapse on mobile

**Why this menu structure:**
- **Overview first** - Landing page with quick stats
- **Tracing second** - Primary feature for MVP
- **Analytics third** - Natural progression from viewing to analyzing
- **Graphs fourth** - Visualization is advanced feature
- **Config last** - Settings typically at bottom

### Implementation

**Component Structure:**
```typescript
<ProjectLayout projectId={projectId}>
  <ProjectHeader project={project} />
  <ProjectSidebar activeRoute={currentRoute} />
  <ProjectContent>
    <Outlet /> {/* Nested routes render here */}
  </ProjectContent>
</ProjectLayout>
```

**Routing (React Router):**
```typescript
<Route path="/projects/:projectId" element={<ProjectLayout />}>
  <Route index element={<ProjectOverview />} />
  <Route path="tracing" element={<TracingPage />} />
  <Route path="tracing/:traceId" element={<TraceDetailPage />} />
  <Route path="config" element={<ConfigPage />} />
</Route>
```

### Alternatives Considered

**Alternative 1: Flat navigation (no sidebar)**
- ❌ No persistent context
- ❌ Harder to navigate deep pages
- ❌ Less professional appearance

**Alternative 2: Top tab navigation**
- ❌ Limited space for menu items
- ❌ Not mobile-friendly
- ❌ Can't show hierarchical structure

**Alternative 3: Dropdown menus**
- ❌ Hidden navigation (requires clicking)
- ❌ Slower access to features
- ❌ Less clear hierarchy

---

## Decision 3: Observation-Level Cost Calculation with DB Lookups

### Decision

Calculate costs **per observation** during trace ingestion, using **database pricing lookups**, and store calculated costs in the `observations` table.

### Implementation

**When:** During observation creation/update  
**Where:** Backend cost_calculation_service  
**How:**

```python
def create_observation(obs_data: ObservationCreate):
    # 1. Create observation
    observation = Observation(**obs_data)
    
    # 2. If has LLM telemetry, calculate cost
    if observation.prompt_tokens and observation.model:
        cost = calculate_llm_cost(
            project_id=observation.trace.project_id,
            hosting_provider=extract_provider(observation.model),
            model=observation.model,
            prompt_tokens=observation.prompt_tokens,
            completion_tokens=observation.completion_tokens
        )
        
        observation.calculated_input_cost = cost.input_cost
        observation.calculated_output_cost = cost.output_cost
        observation.calculated_total_cost = cost.total_cost
    
    # 3. Save with costs
    db.add(observation)
    db.commit()
```

### Rationale

**Why per-observation:**
- Swisper uses **different models per node** (per-node configuration)
- Trace can have observations with different models/providers
- Accurate cost attribution per operation

**Why during ingestion:**
- ✅ Costs calculated once, queried many times (performance)
- ✅ Historical accuracy (prices may change later)
- ✅ Simpler frontend (no client-side calculation)
- ✅ Enables efficient filtering/sorting by cost

**Why DB lookup:**
- ✅ Flexible pricing (no hardcoded values)
- ✅ Per-project customization
- ✅ Easy updates (no code deployment)
- ✅ Audit trail (can track pricing changes)

**Why store calculated costs:**
- ✅ Query performance (no calculation on read)
- ✅ Historical accuracy (pricing at time of execution)
- ✅ Enables cost-based filtering/sorting
- ✅ Simplifies aggregation queries

### Alternatives Considered

**Alternative 1: Client-side calculation**
- ❌ Expensive on every page load
- ❌ Inconsistent if pricing changes
- ❌ Can't filter/sort by cost efficiently

**Alternative 2: Calculate on-demand**
- ❌ Slow for large trace lists
- ❌ Pricing changes affect historical data
- ❌ More complex queries

**Alternative 3: Trace-level cost only**
- ❌ Doesn't account for per-node models
- ❌ Less detailed cost breakdown
- ❌ Harder to identify expensive operations

---

## Consequences

### Positive

1. **Scalable pricing model** - Handles multi-provider, multi-project scenarios
2. **Clear navigation** - Users can easily find features
3. **Accurate costs** - Per-observation calculation with historical accuracy
4. **Performance** - Costs calculated once, queried efficiently
5. **Flexibility** - Easy to add new providers/models/projects
6. **Professional UX** - Standard SaaS navigation pattern

### Negative

1. **Database complexity** - Additional table and indexes
2. **Migration needed** - Default pricing must be seeded
3. **Provider extraction** - Need logic to extract provider from model string
4. **More frontend components** - Sidebar, layout, overview page

### Mitigations

- **Seed defaults** - Migration includes common model pricing
- **Fallback logic** - Graceful handling of missing pricing
- **Provider patterns** - Standard mapping (openai/gpt-4 → provider: "openai")
- **Reuse Swisper patterns** - Copy sidebar styling from Swisper

---

## Implementation Notes

### Phase 2 Scope

**Must implement:**
- ✅ `ModelPricing` table and migration
- ✅ Cost calculation service with DB lookups
- ✅ Project layout with sidebar
- ✅ Project overview page (simple MVP)
- ✅ Read-only config page (show pricing)

**Deferred to Phase 4:**
- ❌ Model pricing CRUD UI (add/edit/delete pricing)
- ❌ Pricing history tracking
- ❌ Cost budget alerts
- ❌ Analytics dashboard

### Provider Extraction Logic

```python
def extract_provider(model: str) -> str:
    """Extract hosting provider from model string."""
    # Common patterns
    if model.startswith("gpt-") or model.startswith("text-"):
        return "openai"
    elif model.startswith("claude-"):
        return "anthropic"
    elif "azure" in model.lower():
        return "azure"
    else:
        # Default or extract from metadata
        return "unknown"
```

---

## References

- **Phase 2 Analysis:** `docs/analysis/phase2_rich_tracing_analysis.md`
- **Phase 2 Sub-Plan:** `docs/plans/phase2_detailed_subplan.md`
- **Swisper State Structure:** `reference/swisper/backend/app/api/services/agents/global_supervisor_state.py`
- **Langfuse Observation Model:** `reference/langfuse/packages/shared/src/observationsTable.ts`
- **ADR-001:** MUI v7 for frontend (navigation will use MUI components)

---

**Status:** Accepted and ready for implementation  
**Last Updated:** November 2, 2025

