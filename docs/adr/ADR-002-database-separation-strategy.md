# ADR-002: Database Separation Strategy

**Status:** ✅ Accepted  
**Date:** 2025-11-01  
**Deciders:** Development Team, Product Owner  
**Context:** Overall Architecture - Data Storage

---

## Context and Problem Statement

SwisperStudio needs to store traces, observations, projects, and configuration data. Swisper already has its own database with users, sessions, facts, entities, and application data.

**Question:** Should SwisperStudio use the same database as Swisper, or have its own separate database?

---

## Decision Drivers

* **Data isolation** and security
* **Independent deployment** and scaling
* **Schema evolution** (ability to change schemas independently)
* **Disaster recovery** and backup strategies
* **Development complexity** (one DB is simpler)
* **Production setup** (container separation)

---

## Considered Options

1. **Shared Database** - SwisperStudio uses Swisper's PostgreSQL instance
2. **Separate Databases** - SwisperStudio has its own PostgreSQL instance
3. **Hybrid** - Some tables shared, some separate

---

## Decision Outcome

**Chosen option:** "Separate Databases"

**Rationale:**

SwisperStudio and Swisper are **separate services** that happen to integrate with each other. They should have clean boundaries and independent lifecycles.

### Architecture

```
Production Setup:
├── SwisperStudio Stack
│   ├── swisper_studio_postgres:5433    ← NEW database
│   │   └── Tables: traces, observations, projects
│   └── swisper_studio_backend:8001
│
└── Swisper Stack (existing)
    ├── swisper_postgres:5432           ← EXISTING database
    │   └── Tables: users, sessions, facts, entities, chats
    └── swisper_backend:8000
```

**Communication:** API-only (no direct database access)

```
Swisper Backend ─────HTTP API────► SwisperStudio
                ◄────HTTP API─────

- Swisper sends traces: POST /api/v1/traces
- Swisper gets config: GET /api/v1/config
```

### Positive Consequences

* ✅ **Clean separation** - Each service owns its data
* ✅ **Independent deployment** - Deploy SwisperStudio without touching Swisper
* ✅ **Independent scaling** - Scale databases based on different workloads
* ✅ **Security isolation** - SwisperStudio has no access to Swisper user data
* ✅ **Schema freedom** - Change SwisperStudio schema without affecting Swisper
* ✅ **Disaster recovery** - Backup/restore each system independently
* ✅ **Development** - Can run SwisperStudio locally without full Swisper stack
* ✅ **Docker clarity** - Clear container separation in production

### Negative Consequences

* ❌ More infrastructure to manage (two databases)
* ❌ Can't use SQL joins across systems (must use API calls)
* ❌ Data synchronization via API (not transactions)
* ❌ Slightly higher latency (API calls vs. local queries)

---

## Pros and Cons of the Options

### Option 1: Shared Database

**Pros:**
* Simpler infrastructure (one database)
* Can use SQL joins
* Atomic transactions possible
* Lower latency (no API calls)

**Cons:**
* ❌ **Tight coupling** (schema changes affect both systems)
* ❌ **Security risk** (SwisperStudio has access to user data)
* ❌ **Deployment coupling** (migrate both together)
* ❌ **Scaling complexity** (can't scale independently)
* ❌ **Unclear ownership** (who owns which tables?)

### Option 2: Separate Databases ✅ CHOSEN

**Pros:**
* ✅ Clean boundaries
* ✅ Independent deployment
* ✅ Security isolation
* ✅ Scalable independently
* ✅ Clear ownership

**Cons:**
* More infrastructure complexity
* No SQL joins across systems
* API latency for data access

### Option 3: Hybrid

**Pros:**
* Some shared data (e.g., users)
* Some isolated data (e.g., traces)

**Cons:**
* ❌ **Confusing** (which tables are shared?)
* ❌ **Partial coupling** (still have dependencies)
* ❌ **Worst of both worlds** (complexity of both approaches)

---

## Database Contents

### SwisperStudio Database (`swisper_studio`)

**Owner:** SwisperStudio  
**Port:** 5433 (avoid conflict with Swisper on 5432)

**Tables:**
- `projects` - Swisper deployment connections
- `traces` - Top-level execution traces
- `observations` - Individual execution steps
- `prompts` - Prompt versions (Phase 3)
- `config_history` - Configuration audit trail (Phase 4)
- `api_keys` - SwisperStudio API keys (Phase 2)

### Swisper Database (`swisper`)

**Owner:** Swisper  
**Port:** 5432

**Tables:**
- `users` - Swisper users
- `sessions` - User sessions
- `chats` - Chat history
- `facts` - User facts
- `entities` - Person, Organization, etc.
- `llm_node_config` - LLM configuration
- `llm_route` - Routing configuration
- `fact_preloading_config` - Preloading settings

---

## Implementation Notes

### Docker Compose Configuration

```yaml
services:
  # SwisperStudio Database (NEW)
  postgres:
    container_name: swisper_studio_postgres
    ports:
      - "5433:5432"  # External port 5433
    environment:
      POSTGRES_DB: swisper_studio
      POSTGRES_USER: studio_user
      POSTGRES_PASSWORD: studio_pass

  # SwisperStudio Backend
  backend:
    environment:
      DATABASE_URL: postgresql+asyncpg://studio_user:studio_pass@postgres:5432/swisper_studio
```

### API Integration

SwisperStudio accesses Swisper data **only via API**:

```python
# SwisperStudio backend accessing Swisper config
async def get_swisper_config(project: Project, table_name: str):
    """Fetch config from Swisper via API"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{project.swisper_url}/api/admin/config/{table_name}",
            headers={"Authorization": f"Bearer {project.swisper_api_key}"}
        )
        return response.json()
```

---

## Links

* **Related:** [ADR-004: Data-Driven Admin UI](ADR-004-data-driven-admin-ui.md)
* **Docker Config:** `docker-compose.yml`
* **Database Models:** `backend/app/models/`

---

## Validation

**Success Metrics:**
- ✅ SwisperStudio and Swisper can deploy independently
- ✅ SwisperStudio database backup/restore doesn't affect Swisper
- ✅ Can run SwisperStudio locally without Swisper database
- ✅ No schema coupling between systems
- ✅ Clear container separation in production

**Review Date:** After Phase 2 (when we have real production load)

---

## Notes

**Future Consideration:**
- If we need to query Swisper user data (e.g., for RBAC), we'll do it via API
- If we need real-time sync, we can use webhooks (Swisper → SwisperStudio)
- Configuration sync happens via SAP (Swisper Admin Protocol) - see ADR-004

**Alternative Rejected:**
- Federation layer (GraphQL or similar) - Too complex for MVP
- Database replication - Creates tight coupling, not suitable for separate services

