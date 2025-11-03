# Phase 4: Configuration Management - Analysis

**Version:** v1.0  
**Last Updated:** 2025-11-02  
**Last Updated By:** AI Assistant  
**Status:** Active

---

## Changelog

### v1.0 - 2025-11-02
- Initial analysis for Phase 4
- Analyzed Swisper config structure
- Analyzed Langfuse settings UI patterns
- Documented SAP design approach
- Identified implementation strategy

---

## Executive Summary

Phase 4 aims to build a **data-driven admin UI** for managing Swisper configuration without code changes. This analysis covers:

1. **Current State**: How Swisper handles configuration today
2. **Reference Patterns**: Langfuse settings UI structure
3. **SAP Design**: Proposed Swisper Admin Protocol specification
4. **Implementation Strategy**: Recommended approach for Phase 4

**Key Finding:** Swisper already has database tables for LLM node configuration. We need to:
- Create SAP endpoints to expose these tables  
- Build data-driven UI that auto-generates forms from schema
- Implement "Test Live" (cache updates) and "Deploy to Prod" (Git commits)

---

## 1. Current Swisper Configuration Structure

### 1.1 Configuration Storage

Swisper uses **multiple configuration mechanisms**:

#### A. Database Tables (PostgreSQL)

**`Configuration` table** (`backend/app/models.py:204-214`)
```python
class Configuration(SQLModel, table=True):
    """System-wide configuration stored in database"""
    name: str = Field(primary_key=True, max_length=255, index=True)
    value: dict[str, Any] | None = Field(default=None, sa_column=Column(sa.dialects.postgresql.JSONB))
```
- **Purpose**: Generic key-value config storage
- **Use case**: System-wide settings
- **Format**: JSONB (flexible schema)

**`LLMNodeConfiguration` table** (`backend/app/models.py:216-246`)
```python
class LLMNodeConfiguration(SQLModel, table=True):
    """LLM node configuration for agent-specific model settings"""
    __tablename__ = "llm_node_configuration"
    
    node_name: str = Field(primary_key=True, max_length=100)
    
    # Default parameters (for Kvant provider)
    default_temperature: float = Field(default=0.2)
    default_max_tokens: int = Field(default=10000)
    default_log_reasoning: bool = Field(default=False)
    default_model: str = Field(max_length=255)
    
    # Azure-specific overrides
    azure_model: str | None = Field(default=None, max_length=255)
    azure_temperature: float | None = Field(default=None)
    azure_max_tokens: int | None = Field(default=None)
    
    # LangSmith tracing configuration
    langsmith_tracing: bool = Field(default=True)
    
    description: str | None = Field(default=None)
```
- **Purpose**: Per-node LLM configuration
- **Use case**: Agent-specific model settings (global_planner, intent_classification, etc.)
- **Fields**: Model, temperature, max_tokens, tracing, provider overrides

#### B. YAML Configuration Files

**`backend/config/fact_preloading.yaml`**
```yaml
# Fact Preloading Configuration
max_facts: 3
min_confidence: 0.7

time_windows:
  imminent_future: 3
  imminent_past: 3
  near_future: 7
  # ... more settings

priority_weights:
  time_urgency_max: 50
  fact_type_max: 30
  # ... more weights
```
- **Purpose**: Domain-specific configuration
- **Use case**: Fact retrieval, prioritization logic
- **Format**: YAML with comments and documentation

#### C. Environment Variables

**`backend/app/core/config.py`**
```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env")
    
    # Infrastructure
    POSTGRES_SERVER: str
    REDIS_URL: str = "redis://localhost:6379"
    
    # LLM Configuration
    DEFAULT_LLM_MODEL: str = "inference-llama4-maverick"
    AZURE_HOSTED_ENDPOINT: str | None = None
    KVANT_ENDPOINT: str = "https://maas.ai-2.kvant.cloud/v1/chat/completions"
    
    # Feature Flags
    EMAIL_ENABLED: bool = False
    VOICE_ENABLED: bool = True
    JOBS_ENABLED: bool = False
    
    # Voice Configuration
    AZURE_SPEECH_KEY: str = ""
    VOICE_MAX_CONCURRENT_SESSIONS: int = 100
    VOICE_SESSION_TIMEOUT_SECONDS: int = 300
    
    # ... 100+ more settings
```
- **Purpose**: Deployment-specific configuration
- **Use case**: Secrets, endpoints, feature flags, resource limits
- **Format**: Environment variables (`.env` file)

### 1.2 Current Config Loading Flow

```
1. Application Startup
   ├─ Load Settings (Pydantic BaseSettings from .env)
   ├─ Load YAML files (yaml.safe_load)
   └─ Query Database tables (SQLModel ORM)

2. Runtime Access
   ├─ Settings: from app.core.config import settings
   ├─ YAML: Loaded once into memory at startup
   └─ Database: Query per-node (LLMNodeConfiguration)
```

**Issues with Current Approach:**
- ❌ **No hot-reload**: Requires restart for config changes
- ❌ **Code deployment required**: YAML changes require Git commit + deploy
- ❌ **No UI**: PO must edit YAML or SQL directly
- ❌ **No testing mode**: Can't test configs without deploying
- ❌ **No audit trail**: No tracking of who changed what

---

## 2. Langfuse Settings UI Patterns

### 2.1 Architecture

Langfuse uses a **paged settings container** with nested routing:

```
/project/{projectId}/settings
  ├─ /index (General)
  ├─ /api-keys
  ├─ /models
  │  └─ /[modelId] (Edit specific model)
  ├─ /llm-connections
  ├─ /integrations
  │  ├─ /slack
  │  ├─ /posthog
  │  └─ /mixpanel
  └─ /notifications
```

**Key Component: `PagedSettingsContainer`**
- Renders a sidebar with settings pages
- Content area for selected page
- Search/filter via cmd+k

### 2.2 Model Settings Page

**From**: `web/src/pages/project/[projectId]/settings/models/[modelId].tsx`

**UI Structure:**
```tsx
<Page
  headerProps={{
    title: model.modelName,
    breadcrumb: [
      { name: "Models", href: "/project/{id}/settings/models" },
      { name: model.modelName }
    ],
    actionButtons: (
      <EditModelButton />
      <DeleteModelButton />
      <CloneModelButton />
    )
  }}
>
  <Card>
    <CardHeader>
      <CardTitle>Model Configuration</CardTitle>
    </CardHeader>
    <CardContent>
      {/* Model fields rendered here */}
      <JSONView json={model.prices} />
      <PriceUnitSelector />
    </CardContent>
  </Card>
</Page>
```

**Key Patterns:**
1. ✅ **Card-based layout** - Each config section in a Card
2. ✅ **Action buttons** - Edit, Delete, Clone in header
3. ✅ **Breadcrumbs** - Easy navigation
4. ✅ **JSON viewer** - Debug/inspect raw data
5. ✅ **Form components** - Specialized inputs (PriceUnitSelector)

### 2.3 General Settings Pattern

**From**: `web/src/pages/project/[projectId]/settings/index.tsx`

```tsx
const settingsPages = [
  {
    title: "General",
    slug: "index",
    content: (
      <div className="flex flex-col gap-6">
        <HostNameProject />
        <RenameProject />
        <ConfigureRetention />
        <JSONView title="Metadata" json={{...}} />
        <SettingsDangerZone items={[...]} />
      </div>
    )
  },
  {
    title: "API Keys",
    slug: "api-keys",
    content: <ApiKeyList />
  },
  // ... more pages
]
```

**Pattern: Settings Pages Array**
- Each page has title, slug, content
- Rendered in `PagedSettingsContainer`
- Easy to add new pages

---

## 3. SAP (Swisper Admin Protocol) Design

### 3.1 Goals

**SAP should provide:**
1. ✅ **Schema introspection** - Auto-discover config tables and fields
2. ✅ **CRUD operations** - Create, Read, Update, Delete config records
3. ✅ **Validation** - Field types, constraints, allowed values
4. ✅ **Hot-reload** - Cache updates without restart
5. ✅ **Git deployment** - Generate YAML + commit when ready

### 3.2 Schema Format

**Inspired by JSON Schema + Django Admin + Strapi**

```json
{
  "version": "1.0",
  "tables": [
    {
      "name": "llm_node_config",
      "description": "LLM configuration per LangGraph node",
      "primary_key": "node_name",
      "fields": [
        {
          "name": "node_name",
          "type": "string",
          "required": true,
          "immutable": true,
          "max_length": 100,
          "description": "LangGraph node identifier"
        },
        {
          "name": "default_model",
          "type": "select",
          "required": true,
          "options": ["inference-llama4-maverick", "gpt-4-turbo", "claude-3-opus"],
          "default": "inference-llama4-maverick",
          "description": "Default LLM model for this node"
        },
        {
          "name": "default_temperature",
          "type": "number",
          "min": 0.0,
          "max": 2.0,
          "step": 0.1,
          "default": 0.7,
          "description": "Sampling temperature (0 = deterministic, 2 = creative)"
        },
        {
          "name": "langsmith_tracing",
          "type": "boolean",
          "default": true,
          "description": "Enable LangSmith tracing for this node"
        }
      ]
    }
  ]
}
```

**Field Types:**
- `string` - Text input (with max_length, pattern)
- `number` - Numeric input (with min, max, step)
- `select` - Dropdown (with options list)
- `boolean` - Checkbox
- `textarea` - Multi-line text
- `json` - JSON editor

**Validation Properties:**
- `required` - Field must have value
- `immutable` - Can't be changed after creation
- `min/max` - Numeric constraints
- `max_length` - String length limit
- `pattern` - Regex validation
- `options` - Allowed values (for select)
- `default` - Default value

### 3.3 API Endpoints

**Schema Introspection:**
```
GET /api/admin/config/schema
→ Returns schema for all config tables
```

**CRUD Operations:**
```
GET    /api/admin/config/{table}              # List all records
GET    /api/admin/config/{table}/{id}         # Get single record
POST   /api/admin/config/{table}              # Create new record
PUT    /api/admin/config/{table}/{id}         # Update record
DELETE /api/admin/config/{table}/{id}         # Delete record
```

**Live Testing:**
```
POST /api/admin/config/{table}/{id}/test-live
→ Update cache immediately (no Git commit)
→ Effect: Instant without redeploy
```

**Production Deployment:**
```
POST /api/admin/config/{table}/deploy
→ Generate YAML from current DB state
→ Commit to Git repository
→ Trigger CI/CD (optional)
→ Effect: Permanent, source of truth
```

### 3.4 Cache Hot-Reload Strategy

**Two-tier caching:**

```python
class ConfigManager:
    def __init__(self):
        self._cache = {}  # In-memory cache (Redis optional)
        self._db_pool = get_db_pool()
    
    def get_config(self, table: str, key: str):
        """Cache-first read strategy"""
        cache_key = f"{table}:{key}"
        
        # Try cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Fallback to database
        config = self._fetch_from_db(table, key)
        self._cache[cache_key] = config
        return config
    
    def update_config(self, table: str, key: str, value: dict):
        """Update DB and cache (hot-reload)"""
        # Update database
        self._update_db(table, key, value)
        
        # Update cache (immediate effect!)
        cache_key = f"{table}:{key}"
        self._cache[cache_key] = value
        
        # Notify other instances (if distributed)
        self._notify_cache_update(cache_key)
```

**Benefits:**
- ✅ **Zero-downtime updates** - No restart required
- ✅ **Instant effect** - Cache updated immediately
- ✅ **Consistency** - DB is source of truth
- ✅ **Distributed-ready** - Can notify other instances via Redis pub/sub

---

## 4. Implementation Strategy

### 4.1 Start Simple, Then Expand

**Phase 4a: MVP (Week 1-2)**
- Implement SAP for 1 table only: `llm_node_config`
- Test Live mode (cache updates)
- SwisperStudio UI with auto-generated forms
- Verify end-to-end flow

**Phase 4b: Full Implementation (Week 2-3)**
- Add more config tables (fact_preloading, feature_flags)
- Deploy to Prod mode (Git commits)
- Config history/audit trail
- YAML generation

**Why incremental?**
- ✅ Reduce risk
- ✅ Get feedback early
- ✅ Easier to debug
- ✅ Can pivot if needed

### 4.2 Which Tables to Expose via SAP?

**Priority 1 (MVP):**
- ✅ `llm_node_config` - High-value, PO changes frequently
  - Fields: node_name, model, temperature, max_tokens, tracing

**Priority 2 (Full Phase 4):**
- ✅ `fact_preloading_config` - Convert YAML to database table
  - Fields: max_facts, min_confidence, time_windows, priority_weights
- ✅ `feature_flags` - New table for feature toggles
  - Fields: feature_name, enabled, description

**Priority 3 (Future):**
- ✅ `llm_route` - Routing rules for model selection
- ✅ `system_settings` - Migrate from Configuration JSONB to structured tables

### 4.3 Data-Driven Form Generation

**Approach: React Hook Form + Zod + Auto-generation**

```tsx
// Auto-generate form from schema
function DataDrivenConfigForm({ schema, data, onSubmit }) {
  const formSchema = schemaToZod(schema); // Convert SAP schema to Zod
  const form = useForm({ resolver: zodResolver(formSchema), defaultValues: data });
  
  return (
    <Form {...form}>
      {schema.fields.map(field => (
        <FormField
          key={field.name}
          name={field.name}
          render={({ field }) => (
            <FieldRenderer fieldSchema={field} {...field} />
          )}
        />
      ))}
    </Form>
  );
}

// Auto-render field based on type
function FieldRenderer({ fieldSchema, ...props }) {
  switch (fieldSchema.type) {
    case "string":
      return <Input type="text" maxLength={fieldSchema.max_length} {...props} />;
    case "number":
      return <Input type="number" min={fieldSchema.min} max={fieldSchema.max} step={fieldSchema.step} {...props} />;
    case "select":
      return (
        <Select {...props}>
          {fieldSchema.options.map(opt => <SelectItem value={opt}>{opt}</SelectItem>)}
        </Select>
      );
    case "boolean":
      return <Checkbox {...props} />;
    default:
      return <Input {...props} />;
  }
}
```

**Benefits:**
- ✅ **No hardcoded forms** - Auto-generated from schema
- ✅ **Type-safe** - Zod validation
- ✅ **Extensible** - Easy to add new field types
- ✅ **DRY** - Single source of truth (schema)

---

## 5. Git Deployment Workflow

### 5.1 YAML Generation

**Convert DB config → YAML**

```python
def generate_yaml_from_config(table_name: str) -> str:
    """Generate YAML file from database config"""
    records = db.query(table_name).all()
    
    if table_name == "llm_node_config":
        config = {
            record.node_name: {
                "default_model": record.default_model,
                "default_temperature": record.default_temperature,
                "default_max_tokens": record.default_max_tokens,
                "langsmith_tracing": record.langsmith_tracing,
            }
            for record in records
        }
        return yaml.dump({"llm_nodes": config}, default_flow_style=False)
    
    elif table_name == "fact_preloading":
        # Generate fact_preloading.yaml
        pass
```

### 5.2 Git Commit Strategy

**Option A: Direct Commit (Simple)**
```python
import subprocess

def commit_config_to_git(file_path: str, message: str):
    """Commit config file to Swisper repository"""
    subprocess.run(["git", "add", file_path], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
```

**Option B: Pull Request (Safer)**
```python
def create_config_pr(file_path: str, message: str):
    """Create PR for config changes"""
    branch_name = f"config/{table_name}-{timestamp}"
    
    subprocess.run(["git", "checkout", "-b", branch_name], check=True)
    subprocess.run(["git", "add", file_path], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)
    subprocess.run(["git", "push", "origin", branch_name], check=True)
    
    # Create PR via GitHub API
    create_github_pr(branch_name, "main", message)
```

**Recommendation for MVP: Option A (Direct Commit)**
- Simpler
- Faster feedback
- Can add PR workflow later

---

## 6. Risks and Mitigations

### Risk 1: Schema Evolution

**Problem:** Config tables change, schema becomes outdated

**Mitigation:**
- ✅ Version SAP schema (v1.0, v1.1, v2.0)
- ✅ Backward compatibility checks
- ✅ Schema diffing (detect breaking changes)
- ✅ Auto-regenerate schema from SQLModel annotations

### Risk 2: Cache Consistency

**Problem:** Cache and DB get out of sync

**Mitigation:**
- ✅ DB is source of truth (always)
- ✅ Cache TTL (refresh every 5 minutes)
- ✅ Manual cache flush endpoint
- ✅ Redis pub/sub for distributed systems

### Risk 3: Git Merge Conflicts

**Problem:** Multiple users deploy configs, conflicts occur

**Mitigation:**
- ✅ Lock table during deployment (prevent simultaneous deploys)
- ✅ Show warning if Git has uncommitted changes
- ✅ Auto-merge simple changes (if possible)
- ✅ Manual resolution UI (future)

### Risk 4: Invalid Config

**Problem:** User enters invalid config, breaks system

**Mitigation:**
- ✅ **Schema validation** - Enforce constraints before save
- ✅ **Test Live mode** - Test before deploying
- ✅ **Rollback button** - Revert to previous config
- ✅ **Dry-run validation** - Validate YAML before Git commit

---

## 7. Success Criteria

**Phase 4 is successful when:**

1. ✅ **SAP Specification Complete**
   - v1.0 documented
   - Endpoint contracts defined
   - Schema format specified
   - Examples provided

2. ✅ **Swisper Backend SAP-Compliant**
   - `/api/admin/config/schema` endpoint works
   - CRUD endpoints for `llm_node_config` work
   - Cache hot-reload functional
   - Tests passing (10+ tests)

3. ✅ **SwisperStudio Proxy Works**
   - Fetches schema from Swisper
   - Proxies CRUD requests
   - Logs config changes to audit history
   - Tests passing (8+ tests)

4. ✅ **SwisperStudio UI Complete**
   - Auto-generated form from schema
   - Can edit `llm_node_config` via UI
   - "Test Live" updates cache immediately
   - "Deploy to Prod" commits to Git
   - Diff viewer shows changes
   - Config history visible

5. ✅ **End-to-End Flow Works**
   - PO opens SwisperStudio
   - Navigates to Project → Configuration
   - Selects "LLM Node Config"
   - Edits temperature for global_planner
   - Clicks "Test Live"
   - Change takes effect in Swisper (no restart)
   - Clicks "Deploy to Prod"
   - YAML committed to Git
   - CI/CD deploys to production

---

## 8. Key Decisions

### Decision 1: Start with `llm_node_config`

**Rationale:**
- ✅ Already exists in database
- ✅ High-value (PO changes frequently)
- ✅ Well-defined schema
- ✅ Easy to test (change model → see LLM response)

### Decision 2: Cache-First Strategy

**Rationale:**
- ✅ Hot-reload without restart
- ✅ Fast reads (no DB query)
- ✅ DB still source of truth
- ✅ Can distribute via Redis

### Decision 3: Data-Driven UI

**Rationale:**
- ✅ No hardcoded forms
- ✅ Adapts to schema changes
- ✅ Extensible (new tables auto-work)
- ✅ Reduces SwisperStudio code

### Decision 4: Two-Mode System

**Rationale:**
- ✅ "Test Live" for experimentation (fast feedback)
- ✅ "Deploy to Prod" for permanence (source of truth)
- ✅ Best of both worlds

---

## 9. Next Steps

1. ✅ **Create SAP Specification** - `docs/specs/spec_sap_v1.md`
2. ✅ **Create Implementation Plan** - `docs/plans/plan_phase4_config_v1.md`
3. ✅ **Get User Approval** - Present plan, wait for confirmation
4. ✅ **Implement Swisper SAP endpoints** (Week 1)
5. ✅ **Implement SwisperStudio proxy** (Week 2)
6. ✅ **Implement SwisperStudio UI** (Week 2-3)
7. ✅ **End-to-End Testing** (Week 3)

---

## 10. References

**Swisper Config Files:**
- `reference/swisper/backend/app/models.py` - Configuration and LLMNodeConfiguration models
- `reference/swisper/backend/config/fact_preloading.yaml` - YAML config example
- `reference/swisper/backend/app/core/config.py` - Settings (Pydantic BaseSettings)

**Langfuse UI:**
- `reference/langfuse/web/src/pages/project/[projectId]/settings/index.tsx` - Settings structure
- `reference/langfuse/web/src/pages/project/[projectId]/settings/models/[modelId].tsx` - Model detail page

**Phase 4 Plan:**
- `docs/plans/swisper_studio_implementation_plan.md` - Phase 4 overview
- `PHASE4_HANDOVER.md` - Detailed Phase 4 requirements

---

**Analysis Complete!** ✅

**Next:** Create SAP specification and implementation plan, then get user approval before implementing.

