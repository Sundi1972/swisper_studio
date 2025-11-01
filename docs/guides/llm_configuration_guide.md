# LLM Configuration Management Guide

**Version:** v1.0  
**Last Updated:** 2025-10-30  
**Last Updated By:** heiko  
**Status:** Active

---

## Changelog

### v1.0 - 2025-10-30
- Initial creation
- Added YAML-based configuration system
- Added prestart sync mechanism

---

## Overview

This system allows you to manage LLM node configurations (model, temperature, tokens, tracing) via version-controlled YAML files, automatically synced to the database on deployment.

---

## How to Update LLM Configurations via PR

### ✅ The Right Way (Configuration as Code)

**File:** `backend/config/llm_nodes.yaml`

**Process:**
1. Edit the YAML file
2. Commit and create PR
3. Reviewers can see the changes in the diff
4. On deploy, prestart automatically syncs to database

**Example PR:**
```yaml
# Change Qwen model for intent classification
intent_classification:
  default_model: "qwen-32b"  # Changed from gpt-4
  default_temperature: 0.2
  default_max_tokens: 2000
  langsmith_tracing: false
```

### ❌ Wrong Ways (Don't Do These)

**DON'T use Alembic migrations for config data:**
```python
# ❌ WRONG - This is data, not schema!
def upgrade():
    op.execute("UPDATE llm_node_configuration SET default_model='qwen-32b'")
```

**DON'T manually UPDATE database:**
```sql
-- ❌ WRONG - Changes not version-controlled!
UPDATE llm_node_configuration SET default_model='qwen-32b';
```

---

## Architecture

### Files

```
backend/
├── config/
│   └── llm_nodes.yaml              # ← Edit this in PRs
├── app/
│   ├── core/
│   │   └── llm_config_sync.py      # ← Sync logic
│   ├── backend_pre_start.py        # ← Calls sync on startup
│   └── models.py                   # ← LLMNodeConfiguration model
```

### Flow

```
1. Developer edits llm_nodes.yaml
   └─> Commits to branch
   └─> Creates PR

2. Reviewer reviews YAML changes
   └─> Approves PR

3. PR merged to main
   └─> CI/CD deploys

4. Container starts
   └─> prestart.sh runs
   └─> backend_pre_start.py calls sync_llm_configs()
   └─> YAML → Database sync
   └─> Application starts with new configs
```

---

## Configuration Schema

Each node in `llm_nodes.yaml` supports these fields (from `LLMNodeConfiguration` model):

```yaml
node_name:
  default_model: string          # Model name (e.g., "qwen-32b", "gpt-4o")
  default_temperature: float     # 0.0-1.0 (creativity)
  default_max_tokens: int        # Max response length
  langsmith_tracing: bool        # Enable/disable tracing (for cost control)
  description: string            # Human-readable description
  
  # Optional Azure overrides
  azure_model: string           # Azure-specific model name
  azure_temperature: float      # Azure-specific temperature
  azure_max_tokens: int         # Azure-specific max tokens
```

---

## Common Scenarios

### Scenario 1: Switch Node to Qwen 32B

**Goal:** Use cheaper Qwen 32B instead of GPT-4 for intent classification

**Steps:**
1. Edit `backend/config/llm_nodes.yaml`:
   ```yaml
   intent_classification:
     default_model: "qwen-32b"  # Changed from "gpt-4o"
     default_temperature: 0.2
     default_max_tokens: 2000
     langsmith_tracing: false
   ```

2. Commit and create PR
3. On deploy, automatically applies

### Scenario 2: Disable Tracing for High-Volume Node

**Goal:** Save LangSmith tokens on email classification (runs 1000s of times/day)

**Steps:**
1. Edit `backend/config/llm_nodes.yaml`:
   ```yaml
   email_classification:
     langsmith_tracing: false  # Changed from true
   ```

2. Commit and create PR
3. On deploy, automatically applies

### Scenario 3: Add New Node Configuration

**Goal:** Add configuration for new "summary_generator" node

**Steps:**
1. Edit `backend/config/llm_nodes.yaml`:
   ```yaml
   summary_generator:
     default_model: "qwen-32b"
     default_temperature: 0.4
     default_max_tokens: 1500
     langsmith_tracing: false
     description: "Generate email summaries"
   ```

2. Commit and create PR
3. On deploy, automatically creates in database

---

## Testing

### Test Sync Locally

```bash
# In backend directory
python -m app.core.llm_config_sync
```

### Test in Docker

```bash
# Start containers (will auto-sync)
docker compose up -d

# Check logs
docker compose logs backend | grep "LLM config"

# Should see:
# "Loading LLM configurations from..."
# "LLM config sync complete: 8 total, 0 created, 8 updated"
```

### Verify in Database

```bash
docker compose exec db psql -U app -d app -c "SELECT node_name, default_model, langsmith_tracing FROM llm_node_configuration;"
```

---

## FAQ

### Q: What happens if YAML file is missing?

A: Prestart logs a warning and continues. Existing DB configs remain unchanged.

### Q: What happens if YAML is invalid?

A: Prestart logs an error and continues. Existing DB configs remain unchanged.

### Q: Can I update configs without restarting?

A: Yes! The configs are cached, but you can clear the cache via API or restart the backend service:
```bash
docker compose restart backend
```

### Q: What if I need to update configs urgently in production?

A: For emergencies only:
1. Use database SQL directly (but not version-controlled)
2. Follow up with PR to update YAML
3. Next deploy will sync YAML → DB

### Q: Should I use Alembic migrations for config?

A: **NO!** Alembic is for **schema** (tables, columns), not **data** (configuration).

---

## Comparison: Alembic vs Configuration File

| Aspect | Alembic Migration | Configuration File (This Approach) |
|--------|-------------------|-------------------------------------|
| **Purpose** | Database schema changes | Application configuration |
| **What it changes** | Tables, columns, indexes, constraints | Data in existing tables |
| **When it runs** | Once per migration | Every deployment (idempotent) |
| **Version control** | Yes (migration files) | Yes (YAML file) |
| **PR review** | Reviewers see SQL/Python code | Reviewers see clean YAML diff |
| **Rollback** | `alembic downgrade` | Edit YAML and redeploy |
| **Best for** | Schema evolution | Dynamic configuration |

---

## Related Documentation

- **Model Definition:** `backend/app/models.py` → `LLMNodeConfiguration`
- **Service:** `backend/app/api/services/llm_node_configuration_service.py`
- **Alembic Policy:** `.cursor/rules/41-alembic-migrations.mdc`

---

**Questions?** See AGENTS.md or ask in dev channel.

