# ADR-003: Two-Mode Configuration System

**Status:** ✅ Accepted  
**Date:** 2025-11-01  
**Deciders:** Development Team, Product Owner  
**Context:** Phase 4 - Configuration Management

---

## Context and Problem Statement

Product Owners and developers need to test and iterate on Swisper configurations (LLM models, temperatures, feature flags) without waiting for full CI/CD cycles. However, production configurations must be version-controlled and auditable.

**Question:** How should configuration updates be deployed - instant API updates or Git-based deployments?

---

## Decision Drivers

* **Fast iteration** for testing configs (PO needs immediate feedback)
* **Production safety** (Git as source of truth)
* **Audit trail** (who changed what, when?)
* **Rollback capability** (revert bad configs)
* **Runtime testing** (A/B test different LLM settings)

---

## Considered Options

1. **Git-only deployment** - All config changes go through Git + CI/CD
2. **API-only deployment** - Direct database writes, no Git
3. **Two-mode system** - Test live via API, deploy to production via Git

---

## Decision Outcome

**Chosen option:** "Two-mode system"

**Rationale:**

Different use cases need different deployment speeds:
- **Testing:** Needs instant feedback (< 5 seconds)
- **Production:** Needs safety and auditability (Git workflow)

The two-mode system provides both.

### How It Works

```
┌─────────────────────────────────────────┐
│ SwisperStudio UI                        │
│                                         │
│ Config Editor:                          │
│ - Node: intent_classification           │
│ - Model: gpt-4-turbo [changed]          │
│ - Temperature: 0.8 [changed]            │
│                                         │
│ [Test Live] [Deploy to Production]      │
└─────────────────────────────────────────┘
        │              │
        │              │
        ▼              ▼
   Test Mode     Production Mode
   (instant)     (Git commit)
```

#### Mode 1: "Test Live" (Instant Updates)

```python
# SwisperStudio → Swisper API
POST /api/admin/config/llm_node_config
{
  "node_name": "intent_classification",
  "model": "gpt-4-turbo",
  "temperature": 0.8,
  "mode": "test"  # ← Test mode
}

# Swisper Backend
async def update_config_live(table: str, config: dict, mode: str):
    if mode == "test":
        # Update cache (immediate effect on next request)
        config_manager.update_cache(table, config)
        
        # Also update DB (survives until next deployment)
        await db.execute(f"UPDATE {table} SET ...", config)
        
        return {"status": "live", "expires": "next deployment"}
```

**Result:** Next Swisper request uses new config immediately!

#### Mode 2: "Deploy to Production" (Git Commit)

```python
# SwisperStudio → Swisper API
POST /api/admin/config/llm_node_config
{
  "node_name": "intent_classification",
  "model": "gpt-4-turbo",
  "temperature": 0.8,
  "mode": "production"  # ← Production mode
}

# SwisperStudio Backend
async def deploy_config_to_production(table: str, config: dict):
    # 1. Save to audit history
    await studio_db.save_config_history(config)
    
    # 2. Generate YAML
    yaml_content = generate_yaml_from_config(table, config)
    
    # 3. Commit to Git
    await git_client.commit(
        repo="swisper",
        file=f"backend/config/{table}.yaml",
        content=yaml_content,
        message=f"Config: {table} update via SwisperStudio"
    )
    
    return {"status": "deployed", "commit": "abc123"}
```

**Result:** Config committed to Git, Swisper loads on next deployment (permanent)

### Positive Consequences

* ✅ **Fast iteration** - Test configs in seconds, not minutes/hours
* ✅ **A/B testing** - Try different models/temperatures instantly
* ✅ **Safe production** - Git commits only when PO approves
* ✅ **Full audit trail** - SwisperStudio history + Git log
* ✅ **Rollback** - Git revert bad configs
* ✅ **Best of both worlds** - Speed + Safety

### Negative Consequences

* ❌ Two code paths to maintain (test mode + production mode)
* ❌ Potential confusion (what's in Git vs. what's running?)
* ❌ Test mode changes lost on redeploy (need clear UI warning)

---

## Pros and Cons of the Options

### Option 1: Git-only deployment

**Pros:**
* Simple (one deployment path)
* Git is always source of truth
* Easy to understand

**Cons:**
* ❌ **Slow iteration** (wait for CI/CD)
* ❌ **Testing friction** (PO can't experiment quickly)
* ❌ **Deployment spam** (many small commits for testing)

### Option 2: API-only deployment

**Pros:**
* Instant updates
* Fast iteration

**Cons:**
* ❌ **No version control** (lost if DB corrupted)
* ❌ **No rollback** (how to undo bad config?)
* ❌ **No audit trail** (who changed what?)

### Option 3: Two-mode system ✅ CHOSEN

**Pros:**
* ✅ Fast testing (instant API updates)
* ✅ Safe production (Git commits)
* ✅ Full audit trail (both systems)
* ✅ Rollback capability

**Cons:**
* Two code paths to maintain
* Need clear UI to show mode

---

## Implementation Details

### UI Indicators

```tsx
<ConfigEditor>
  <StatusBanner>
    {mode === 'test' && (
      <Alert severity="warning">
        Test Mode: Changes take effect immediately but will be 
        lost on next deployment. Click "Deploy to Production" 
        to make permanent.
      </Alert>
    )}
  </StatusBanner>
  
  <ConfigForm />
  
  <Actions>
    <Button onClick={() => updateConfig('test')}>
      Test Live
    </Button>
    <Button onClick={() => updateConfig('production')}>
      Deploy to Production
    </Button>
  </Actions>
</ConfigEditor>
```

### Config Loading (Swisper Backend)

```python
class ConfigManager:
    async def load_config(self):
        """Load on startup"""
        # 1. Load from YAML (source of truth)
        yaml_config = load_yaml("backend/config/llm_config.yaml")
        
        # 2. Check if DB has test overrides
        db_config = await load_from_db()
        
        # 3. Merge (DB overrides YAML for test mode)
        merged = {**yaml_config, **db_config}
        
        # 4. Cache in memory
        self.config_cache = merged
    
    async def update_live(self, table: str, config: dict):
        """Test mode - update cache + DB"""
        self.config_cache[table] = config
        await self.db.update(table, config)
    
    def get_config(self, table: str) -> dict:
        """Runtime read from cache"""
        return self.config_cache.get(table)
```

---

## Links

* **Related:** [ADR-004: Data-Driven Admin UI](ADR-004-data-driven-admin-ui.md)
* **Implementation:** Phase 4 - Configuration Management
* **Plan:** [Phase 4 Details](../plans/swisper_studio_implementation_plan.md#phase-4)

---

## Validation

**Success Metrics:**
- ✅ Test mode updates take < 5 seconds
- ✅ Production mode creates Git commit
- ✅ Rollback works (git revert → redeploy)
- ✅ PO reports 10x faster config iteration
- ✅ Zero production config issues (Git protects us)

**Review Date:** After Phase 4 completion

---

## Notes

**User Experience Flow:**

1. PO wants to test gpt-4-turbo on intent_classification
2. Click "Test Live" → Immediate effect
3. Send test messages to Swisper
4. Review traces in SwisperStudio
5. See gpt-4-turbo responses
6. If good → Click "Deploy to Production"
7. Config committed to Git
8. Next Swisper deployment loads new config from Git
9. Config is now permanent

**Warning in UI:**
- Test mode changes show warning banner
- Clear indication that changes are temporary
- Prompt to deploy to production when satisfied

**Future Enhancement:**
- "Deploy + Redeploy" button (commits + triggers immediate Swisper restart)
- Scheduled deployments (deploy at midnight, low traffic)
- Approval workflows (PO proposes, dev approves)

