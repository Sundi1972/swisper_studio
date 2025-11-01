# SwisperStudio Setup - Ready to Implement

**Date:** 2025-11-01
**Status:** ✅ Ready for Implementation
**Estimated Time:** 3.5-4 hours

---

## 🎯 What We're Building

**SwisperStudio** - Swisper's integrated observability platform built on Langfuse

### Architecture:
```
Infrastructure:
  ✅ ClickHouse (analytics database)
  ✅ Langfuse Web (UI at localhost:3000)
  ✅ Langfuse Worker (background processing)
  ✅ Shared PostgreSQL (separate langfuse_db database)

Backend Integration:
  ✅ backend/swisper_studio/ (consolidated module)
  ✅ Clean imports: from backend.swisper_studio import get_studio_service
  ✅ Minimal code changes (3 files modified)
```

---

## 📁 File Structure

### **New Folder:** `backend/swisper_studio/`
```
backend/swisper_studio/
├── README.md                    # What is SwisperStudio
├── __init__.py                  # Exports: get_studio_service()
├── service.py                   # Main SwisperStudioService class
├── config.py                    # Configuration from env vars
├── decorators.py                # Optional: @trace helpers
└── admin/
    ├── __init__.py
    └── routes.py                # Test/status endpoints
```

### **Modified Files:**
```
1. docker-compose.yml            # ADD 3 services (clickhouse, langfuse-web, langfuse-worker)
2. .env                          # ADD SwisperStudio config section
3. backend/pyproject.toml        # ADD langfuse dependency
4. backend/app/main.py           # Import SwisperStudio admin routes (2 lines)
```

---

## 📋 Implementation Checklist

### **Phase 1: Infrastructure Setup (3.5-4 hours)**

- [ ] **Step 1: Generate Secrets (10 min)**
  ```bash
  openssl rand -base64 32  # NEXTAUTH_SECRET
  openssl rand -base64 32  # SALT
  openssl rand -base64 16  # CLICKHOUSE_PASSWORD
  ```

- [ ] **Step 2: Update .env (15 min)**
  - Add SwisperStudio configuration section
  - Paste generated secrets

- [ ] **Step 3: Update docker-compose.yml (45 min)**
  - Add clickhouse service
  - Add langfuse-web service
  - Add langfuse-worker service
  - Add volumes

- [ ] **Step 4: Create Database (5 min)**
  - Run `scripts/init-langfuse-db.sh`

- [ ] **Step 5: Create MinIO Bucket (5 min)**
  - Run `scripts/init-langfuse-minio.sh`

- [ ] **Step 6: Start Services (15 min)**
  - Pull images
  - Start ClickHouse
  - Start Langfuse services
  - Check logs

- [ ] **Step 7: Access UI (5 min)**
  - Open http://localhost:3000
  - Create account
  - Get API keys
  - Update .env with real keys

- [ ] **Step 8: Install Python SDK (10 min)**
  ```bash
  cd backend
  poetry add langfuse
  ```

- [ ] **Step 9: Create SwisperStudio Module (20 min)**
  - Create `backend/swisper_studio/` folder
  - Create all module files (7 files)

- [ ] **Step 10: Register Routes (5 min)**
  - Update `backend/app/main.py`
  - Import and register admin routes

- [ ] **Step 11: Test Integration (15 min)**
  ```bash
  curl http://localhost:8000/api/admin/studio/status
  curl -X POST http://localhost:8000/api/admin/studio/test-trace
  ```

- [ ] **Step 12: Verify in UI (10 min)**
  - Open http://localhost:3000/traces
  - Confirm test trace appears

---

## 📚 Documentation Available

### **Implementation Guide:**
- **Main Plan:** `docs/plans/plan_langfuse_self_hosting_v1.md`
- **Quick Summary:** `SWISPER_STUDIO_SETUP.md` (this file)

### **Architecture Docs:**
- **Database Strategy:** `docs/specs/langfuse_database_strategy.md`
- **ClickHouse Analysis:** `docs/specs/langfuse_clickhouse_analysis.md`
- **vs LangGraph Studio:** `docs/specs/langgraph_studio_vs_langfuse.md`

### **Decision Records:**
- **Setup Decision:** `LANGFUSE_SETUP_DECISION.md`
- **SwisperStudio Branding:** This session's decision

---

## 🔑 Key Environment Variables

```bash
# SwisperStudio Configuration
SWISPER_STUDIO_ENABLED=true
SWISPER_STUDIO_HOST=http://langfuse-web:3000
SWISPER_STUDIO_PUBLIC_KEY=pk_...  # Get from UI after setup
SWISPER_STUDIO_SECRET_KEY=sk_...  # Get from UI after setup

# Langfuse Internal
NEXTAUTH_SECRET=<generated>
NEXTAUTH_URL=http://localhost:3000
SALT=<generated>
LANGFUSE_DATABASE_URL=postgresql://postgres:password@db:5432/langfuse_db

# ClickHouse
CLICKHOUSE_USER=langfuse
CLICKHOUSE_PASSWORD=<generated>
CLICKHOUSE_URL=http://clickhouse:8123
```

---

## 🎯 Success Criteria

After implementation, you should have:

- ✅ SwisperStudio UI accessible at http://localhost:3000
- ✅ ClickHouse running and healthy
- ✅ `backend/swisper_studio/` module created
- ✅ Backend can send test traces
- ✅ Test trace visible in UI
- ✅ All services healthy in `docker compose ps`
- ✅ Status endpoint returns enabled=true
- ✅ No errors in logs

---

## 💡 Quick Commands Reference

```bash
# Generate secrets
openssl rand -base64 32

# Start services
docker compose up -d clickhouse langfuse-web langfuse-worker

# Check status
docker compose ps
docker compose logs -f langfuse-web

# Create database
docker compose exec db psql -U postgres -c "CREATE DATABASE langfuse_db;"

# Test backend integration
curl http://localhost:8000/api/admin/studio/status | jq
curl -X POST http://localhost:8000/api/admin/studio/test-trace | jq

# Access UI
open http://localhost:3000
```

---

## 🚀 Resources Needed

- **RAM:** +2.5GB (total: ~6.5GB)
- **Disk:** +10GB
- **Time:** 3.5-4 hours
- **Ports:** 3000 (UI), 8123 (ClickHouse HTTP), 9000 (ClickHouse native)

---

## 🛡️ Safety Features

- **Feature flag:** `SWISPER_STUDIO_ENABLED=false` to disable
- **Circuit breaker:** Built-in to handle failures gracefully
- **Non-blocking:** Async SDK with < 1ms overhead
- **Standalone:** Can remove completely in 5 minutes if needed

---

## 📖 Next Steps After Setup

### **Immediate (Optional):**
Add basic tracing to `orchestration_service.py`:
```python
from backend.swisper_studio import get_studio_service

studio = get_studio_service()
trace = studio.create_trace(name="chat", user_id=user_id)
```

### **Week 2 (Optional):**
Trace key operations:
- Global Supervisor nodes
- Fact preloading (validate your priority system!)
- Domain agents

---

## ❓ Questions?

- **Documentation:** See `docs/plans/plan_langfuse_self_hosting_v1.md`
- **Architecture:** See `docs/specs/langfuse_database_strategy.md`
- **Comparison:** See `docs/specs/langgraph_studio_vs_langfuse.md`

---

## ✅ Ready to Implement!

**All documentation created and saved.**
**Structure designed and approved.**
**Implementation plan ready.**

**Start in new session with:**
1. Open `SWISPER_STUDIO_SETUP.md` (this file)
2. Follow checklist step by step
3. Reference detailed plan as needed

---

**SwisperStudio** - Built with Langfuse, designed for Swisper 🚀

**Estimated completion:** 3.5-4 hours
**Risk:** Low
**Reversibility:** Complete
**Value:** High (production observability from day 1)


