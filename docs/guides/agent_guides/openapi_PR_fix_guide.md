# OpenAPI CI Failures: Root Cause & Fix Guide

**Version:** v1.1
**Last Updated:** 2025-11-01
**Last Updated By:** heiko
**Status:** Active

---

## Changelog

### v1.1 - 2025-11-01
- Added comprehensive "Lessons Learned" section from real debugging session
- Documented all three root causes discovered during marathon debugging
- Added meta-lessons on debugging faster
- Added prevention checklist
- Added pattern recognition table for common errors
- Added time savings estimate (ROI)

### v1.0 - 2025-11-01
- Initial guide creation
- Documented root cause of recurring OpenAPI diff failures
- Provided step-by-step fix procedure
- Added prevention strategies

---

## 🚨 **The Problem**

After merging `main` into your feature branch or rebasing onto `main`, CI fails with:

### **Frontend Error:**
```
Error: src/generated/apis/index.ts(7,1): error TS2308: Module './AdminApi' has already exported a member named 'FactConfigSyncConfigRequest'. Consider explicitly re-exporting to resolve the ambiguity.
```

### **Backend Error:**
```
+ diff -w ../frontend/openapi/Swisper_Internal_api_v1_temp.json ../frontend/openapi/Swisper_Internal_api_v1.json
696,922d695
< "/api/v1/users/{user_id}/avatars/{avatar_id}": {
...
Files are different
Error: Process completed with exit code 1.
```

---

## 🔍 **Root Cause**

### **What's Happening:**

1. ✅ **Your feature branch** has code changes (e.g., new admin fact-config endpoints)
2. ✅ **Main branch** has OTHER new endpoints (e.g., avatars, preferences)
3. ✅ **You merge/rebase main** into your branch → Backend code NOW has ALL endpoints
4. ❌ **BUT your committed OpenAPI spec** (`frontend/openapi/Swisper_Internal_api_v1.json`) is OUTDATED
   - It has YOUR feature's endpoints
   - It's MISSING the endpoints from main
5. ❌ **CI generates a FRESH spec** from the backend → Includes ALL endpoints
6. ❌ **CI compares** fresh spec vs committed spec → **MISMATCH!**

### **Why TypeScript Generation Fails:**

When the OpenAPI spec is incomplete or has duplicate operation IDs/model names:
- OpenAPI Generator creates TypeScript types
- If multiple endpoints have same model names → Duplicate exports
- TypeScript compilation fails with "already exported" errors

---

## ✅ **The Fix (Step-by-Step)**

### **Step 1: Understand the Flow**

```
Backend Code (Python)
   ↓
OpenAPI Spec Generation (app.main.app.openapi())
   ↓
Committed Spec (frontend/openapi/Swisper_Internal_api_v1.json)
   ↓
TypeScript Generation (openapi-generator-cli)
   ↓
Frontend API Client (src/generated/apis/)
```

**Key Rule:** Committed spec MUST match what backend generates!

---

### **Step 2: Generate Complete OpenAPI Spec**

#### **Option A: Using Docker (Recommended for UAT)**

```bash
# 1. Ensure backend is running with LATEST code
cd /root/projects/helvetiq
docker compose build backend
docker compose up -d backend

# 2. Wait for backend to start
sleep 10

# 3. Generate spec from running backend
docker compose exec backend python -c "
import app.main
import json

data = app.main.app.openapi()
with open('/tmp/Swisper_complete.json', 'w') as f:
    json.dump(data, f, indent=2)
"

# 4. Copy spec from container to host
docker compose cp backend:/tmp/Swisper_complete.json frontend/openapi/Swisper_Internal_api_v1.json

#  5. Verify spec has all endpoints
echo "📊 Checking generated spec..."
python3 -c "
import json
with open('frontend/openapi/Swisper_Internal_api_v1.json', 'r') as f:
    data = json.load(f)
paths = data.get('paths', {})
avatar_paths = [p for p in paths if 'avatar' in p]
pref_paths = [p for p in paths if 'preference' in p]
fact_paths = [p for p in paths if 'fact-config' in p]
print(f'✅ Spec contains:')
print(f'  - {len(avatar_paths)} avatar endpoints')
print(f'  - {len(pref_paths)} preference endpoints')
print(f'  - {len(fact_paths)} fact-config endpoints')
print(f'  - {len(paths)} TOTAL endpoints')
"
```

#### **Option B: Using Script (Requires Poetry/UV Environment)**

```bash
cd /root/projects/helvetiq
bash scripts/generate-open-api-for-fe.sh
```

**Note:** This script may fail if you don't have the Python environment activated. Use Option A for reliability.

---

### **Step 3: Verify TypeScript Generation Works**

```bash
cd /root/projects/helvetiq/frontend

# Generate TypeScript API client
npm run generate:api

# Check for errors
echo "✅ If no TypeScript errors, generation succeeded!"
```

**Common Errors:**
- `error TS2308: Module './AdminApi' has already exported a member` → Duplicate model names
- **Fix:** Rename Pydantic models in backend to be unique (e.g., `FactConfigUpdateRequest` instead of `UpdateConfigRequest`)

---

### **Step 4: Commit and Push**

```bash
cd /root/projects/helvetiq

# Add regenerated spec
git add frontend/openapi/Swisper_Internal_api_v1.json

# Commit
git commit -m "fix: regenerate OpenAPI spec with all endpoints from merged main

- Includes avatar endpoints from main
- Includes preference endpoints from main
- Includes fact-config endpoints from feature branch
- Resolves CI OpenAPI diff check failure"

# Push
git push
```

---

## 🛡️ **Prevention Strategies**

### **1. Always Regenerate After Merging Main**

**Workflow:**
```bash
# Merge/rebase main
git checkout feature/my-feature
git merge main  # or: git rebase main

# IMMEDIATELY regenerate OpenAPI spec
docker compose build backend
docker compose up -d backend
sleep 10
docker compose exec backend python -c "
import app.main
import json
data = app.main.app.openapi()
with open('/tmp/spec.json', 'w') as f:
    json.dump(data, f, indent=2)
"
docker compose cp backend:/tmp/spec.json frontend/openapi/Swisper_Internal_api_v1.json

# Commit spec update
git add frontend/openapi/Swisper_Internal_api_v1.json
git commit -m "chore: regenerate OpenAPI spec after merging main"
git push
```

---

### **2. Add Pre-Push Hook (Optional)**

Create `.git/hooks/pre-push`:

```bash
#!/bin/bash
# Pre-push hook: Warn if OpenAPI spec might be outdated

echo "🔍 Checking if OpenAPI spec is current..."

# Check if backend routes changed
ROUTES_CHANGED=$(git diff origin/main...HEAD --name-only | grep "backend/app/api/routes/" || true)

if [ -n "$ROUTES_CHANGED" ]; then
  # Check if OpenAPI spec also changed
  SPEC_CHANGED=$(git diff origin/main...HEAD --name-only | grep "frontend/openapi/Swisper_Internal_api_v1.json" || true)

  if [ -z "$SPEC_CHANGED" ]; then
    echo "⚠️  WARNING: Backend routes changed but OpenAPI spec not updated!"
    echo "   Run: bash scripts/generate-open-api-for-fe.sh"
    echo ""
    read -p "Continue push anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      exit 1
    fi
  fi
fi

echo "✅ OpenAPI spec check passed"
```

Make executable:
```bash
chmod +x .git/hooks/pre-push
```

---

### **3. Add CI Check in PR Template**

Add to `.github/pull_request_template.md`:

```markdown
## Checklist

- [ ] If backend routes changed: Regenerated OpenAPI spec
- [ ] If OpenAPI spec changed: Ran `npm run generate:frontend` locally
- [ ] TypeScript compilation passes (`npm run test` in frontend/)
```

---

### **4. Document in AGENTS.md**

Add to development workflow section:

```markdown
## ⚠️ After Merging Main

**CRITICAL:** Always regenerate OpenAPI spec after merging `main`:

1. Rebuild backend: `docker compose build backend`
2. Generate spec: Use Docker or script (see guide)
3. Commit: `git add frontend/openapi/*.json && git commit -m "chore: regenerate OpenAPI spec"`

See: `docs/guides/openapi_PR_fix_guide.md`
```

---

## 🔧 **Troubleshooting**

### **Issue: Docker Container Won't Start**

**Symptom:**
```
Container helvetiq-prestart-1  service "prestart" didn't complete successfully: exit 1
```

**Fix:**
```bash
# Skip prestart service
docker compose up -d --no-deps backend

# Or fix the prestart failure (usually Alembic migration issue)
docker compose logs prestart
```

---

### **Issue: TypeScript Still Has Duplicate Exports**

**Symptom:**
```
error TS2308: Module './AdminApi' has already exported a member named 'FactConfigSyncConfigRequest'
```

**Root Cause #1:** Multiple tags on same endpoint

The TypeScript generator creates API classes based on tags. If an endpoint has multiple tags:
```python
# ❌ BAD - Creates operations in BOTH AdminApi.ts AND ConfigurationApi.ts
router = APIRouter(prefix="/admin/fact-config", tags=["admin", "configuration"])
```

This causes the same types to be exported from multiple files, creating ambiguity in `index.ts`.

**Fix #1:** Use only ONE tag per router:
```python
# ✅ GOOD - Creates operations ONLY in AdminApi.ts
router = APIRouter(prefix="/admin/fact-config", tags=["admin"])
```

---

**Root Cause #2:** Multiple endpoints using same Pydantic model names

**Fix #2:**
1. Rename Pydantic models to be unique:
   ```python
   # ❌ BAD (conflicts with other AdminApi routes)
   class SyncConfigRequest(BaseModel):
       ...

   # ✅ GOOD (unique per domain)
   class FactConfigSyncRequest(BaseModel):
       ...
   ```

2. Add unique `operation_id` to each endpoint:
   ```python
   @router.post("/sync", operation_id="fact_config-sync_config")
   async def sync_config(...):
       ...
   ```

3. Regenerate OpenAPI spec
4. Verify TypeScript generation works

---

### **Issue: Generated Spec Missing Endpoints**

**Symptom:** CI says spec has fewer endpoints than expected

**Possible Causes:**
1. Backend not fully started (wait longer)
2. Routes not imported in `app/api/main.py`
3. Docker container has stale code (rebuild)

**Fix:**
```bash
# Rebuild and wait longer
docker compose build backend
docker compose up -d backend
sleep 20  # Wait longer for startup

# Check backend logs
docker compose logs backend | grep "Application startup complete"

# Regenerate
docker compose exec backend python -c "..."
```

---

## 📋 **Quick Reference**

### **Fast Fix (Copy-Paste)**

```bash
# Run this after merging main or when CI fails
cd /root/projects/helvetiq && \
docker compose build backend && \
docker compose up -d backend && \
sleep 15 && \
docker compose exec backend python -c "
import app.main, json
data = app.main.app.openapi()
with open('/tmp/spec.json', 'w') as f: json.dump(data, f, indent=2)
" && \
docker compose cp backend:/tmp/spec.json frontend/openapi/Swisper_Internal_api_v1.json && \
git add frontend/openapi/Swisper_Internal_api_v1.json && \
git commit -m "fix: regenerate OpenAPI spec with complete endpoint list" && \
git push && \
echo "✅ OpenAPI spec regenerated and pushed!"
```

---

## 🎓 **Key Learnings from Real Debugging Session (Nov 2024)**

### **The Journey: 3+ Hours of Debugging**

This guide was created after a marathon debugging session that revealed THREE distinct root causes for OpenAPI/TypeScript failures. Here's what we learned:

---

### **Root Cause #1: Incomplete OpenAPI Spec After Merge**

**What Happened:**
- Feature branch added new admin fact-config endpoints
- Merged `main` which added avatar and preference endpoints
- Committed OpenAPI spec was missing the main branch endpoints
- CI generated fresh spec → Mismatch → **Backend diff check failed**

**Why It Was Hard to Find:**
- The error message just said "Files are different"
- Showed hundreds of lines of missing endpoints
- Not obvious it was a merge-related issue

**The Fix:**
```bash
# After ANY merge/rebase, ALWAYS regenerate
docker compose build backend
docker compose exec backend python -c "..."
git add frontend/openapi/Swisper_Internal_api_v1.json
git commit -m "chore: regenerate OpenAPI spec after merging main"
```

**Lesson:** OpenAPI spec is a **build artifact** that depends on ALL backend code. Treat merges like dependency changes.

---

### **Root Cause #2: Non-Unique Pydantic Model Names**

**What Happened:**
- Multiple admin routes used generic names: `SyncConfigRequest`, `UpdateConfigRequest`
- OpenAPI spec had duplicate schema names
- TypeScript generator created conflicting type exports
- **TS2308: Module has already exported member** error

**Why It Was Hard to Find:**
- Error mentioned `FactConfigSyncConfigRequest` which DIDN'T exist in our code
- It was auto-generated by the TypeScript generator
- Not obvious the problem was in Pydantic model naming

**The Fix:**
```python
# ❌ Generic names (conflicts across routers)
class SyncConfigRequest(BaseModel):
    ...

# ✅ Domain-specific names (unique)
class FactConfigSyncRequest(BaseModel):
    ...
```

**Lesson:** Always prefix Pydantic models with their domain/feature name. Generic names WILL cause conflicts as the codebase grows.

---

### **Root Cause #3: Multiple Tags on Single Router (THE SNEAKY ONE)**

**What Happened:**
- Router had TWO tags: `tags=["admin", "configuration"]`
- TypeScript generator created operations in BOTH `AdminApi.ts` AND `ConfigurationApi.ts`
- Same types exported from both files → `index.ts` re-export ambiguity
- **TS2308 error** (again, but different root cause!)

**Why It Was THE HARDEST to Find:**
- Same error message as Root Cause #2
- We'd already fixed model names and operation IDs
- Not obvious that tags controlled which API file gets the operation
- The OpenAPI spec itself was valid - the problem was in TypeScript generation logic

**The Fix:**
```python
# ❌ Multiple tags = multiple API files = duplicate exports
router = APIRouter(prefix="/admin/fact-config", tags=["admin", "configuration"])

# ✅ Single tag = single API file = no duplicates
router = APIRouter(prefix="/admin/fact-config", tags=["admin"])
```

**Lesson:** **ONE tag per router**. Multiple tags are for documentation/grouping in API docs, but they cause TypeScript generation to create duplicate code.

---

### **Meta-Lessons: How to Debug Faster Next Time**

#### **1. Understand the Full Pipeline**
```
Backend Routes (Python)
  ↓ (FastAPI)
OpenAPI Spec (JSON)
  ↓ (openapi-generator-cli)
TypeScript API Client
  ↓ (tsc)
Compiled JavaScript
```

**Each layer can fail independently.** Don't assume the error at layer N means the problem is at layer N.

#### **2. Test in Isolation**

**Backend:**
```bash
# Generate spec manually and inspect
docker compose exec backend python -c "import app.main, json; ..."
```

**TypeScript:**
```bash
# Try generation locally (needs Java)
cd frontend && npm run generate:api
```

**Key:** If you can't test locally, at least VERIFY the inputs (e.g., inspect OpenAPI spec for duplicate tags).

#### **3. Check What CI Actually Sees**

```bash
# What's in the committed spec?
git show HEAD:frontend/openapi/Swisper_Internal_api_v1.json | python3 -c "..."

# What would be generated now?
docker compose exec backend python -c "..." | python3 -c "..."
```

**Key:** Your local environment might be different from CI. Always verify what's in git.

#### **4. Pattern Recognition**

| Error | Likely Cause | Check This |
|-------|--------------|------------|
| "Files are different" (backend) | Spec out of sync with code | Did you merge main? Regenerate spec |
| "TS2308 already exported" | Duplicate model names OR multiple tags | Check Pydantic model names AND router tags |
| "TS2307 cannot find module" | Missing operation ID | Check all endpoints have unique operation IDs |
| Spec has fewer endpoints than expected | Routes not imported in main.py | Check imports in `backend/app/api/main.py` |

#### **5. Create This Guide**

**You're reading it!** 🎉

Document your debugging journey. Future you (and your team) will thank you.

---

### **Prevention Checklist (Print This)**

**Before Creating Any New Router:**
- [ ] **ONE tag only** (e.g., `tags=["admin"]`)
- [ ] **Domain-prefixed model names** (e.g., `FactConfigUpdateRequest`)
- [ ] **Unique operation IDs** (e.g., `operation_id="fact_config-update"`)

**After Merging Main:**
- [ ] **Rebuild backend** (`docker compose build backend`)
- [ ] **Regenerate OpenAPI spec** (see Fast Fix command)
- [ ] **Commit spec** (`git add frontend/openapi/*.json`)
- [ ] **Push immediately** (don't mix with feature work)

**Before Pushing Feature:**
- [ ] **Run tests** (backend and frontend)
- [ ] **Check OpenAPI diff** (if routes changed)
- [ ] **Verify TypeScript compiles** (if spec changed)

---

### **Time Saved**

- **First occurrence:** 3+ hours of debugging
- **With this guide:** 5-10 minutes (run Fast Fix command, push, done)

**ROI:** This guide pays for itself on the second occurrence. 🚀

---

### **Why This Matters**

OpenAPI spec is the **contract** between backend and frontend. When it's wrong:
- ❌ Frontend can't call new backend endpoints
- ❌ TypeScript types don't match reality
- ❌ CI blocks merges
- ❌ Developers waste hours debugging

When it's right:
- ✅ Frontend auto-generates correct API client
- ✅ Type safety catches bugs at compile time
- ✅ CI passes quickly
- ✅ Developers stay productive

---

## 📚 **Related Documentation**

- **Cursor Rule (Quick Reference):** `.cursor/rules/70-openapi-workflow.mdc`
- **OpenAPI Generation Script:** `scripts/generate-open-api-for-fe.sh`
- **CI OpenAPI Diff Check:** `.github/workflows/...` (check openapi-diff step)
- **TypeScript Generation:** `frontend/package.json` → `generate:api` script
- **Backend Routes:** `backend/app/api/main.py` (route imports)

---

## ❓ **FAQ**

### **Q: Why don't we just generate the spec in CI?**
**A:** We do! But we ALSO commit it to version control so:
- Developers can see API changes in PR diffs
- Frontend can use spec immediately without waiting for backend
- We detect accidental API changes (if spec changes unexpectedly)

### **Q: Why does TypeScript generation fail but not OpenAPI generation?**
**A:** OpenAPI generation from backend succeeds. TypeScript generation fails when:
- Spec has duplicate operation IDs
- Spec has duplicate model names
- Spec is incomplete (missing required fields)

### **Q: Can I skip regenerating if I didn't touch backend routes?**
**A:** NO! Even if YOU didn't change routes, merging `main` brings in NEW routes from others. Always regenerate after merge.

---

**Remember:** OpenAPI spec = Contract between backend and frontend. Keep it synchronized! 🔄

---

**Questions?** Contact heiko or see AGENTS.md for development workflow.

