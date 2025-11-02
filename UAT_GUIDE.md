# SwisperStudio Phase 1 UAT Guide

**Date:** November 2, 2025  
**Version:** Phase 1 - "Hello World"  
**Tester:** Product Owner / Development Team

---

## 🎯 What We're Testing

**Phase 1 Scope:**
- ✅ Login to SwisperStudio
- ✅ Create and view projects
- ✅ View trace list (will be empty until Swisper integration)
- ✅ Backend API endpoints
- ✅ Swisper branding (dark mode, logo, colors)

**Out of Scope for Phase 1:**
- ❌ Actual Swisper integration (Phase 2)
- ❌ Rich trace details (Phase 2)
- ❌ Graph visualization (Phase 3)
- ❌ Configuration management (Phase 4)

---

## 🚀 System Access

### Backend API
- **URL:** http://localhost:8001
- **API Docs:** http://localhost:8001/api/v1/docs (Swagger UI)
- **Health Check:** http://localhost:8001/health

### Frontend UI
- **URL:** http://localhost:3000
- **Login Required:** Yes (API key authentication)

### Database
- **Host:** localhost:5433
- **User:** studio_user
- **Database:** swisper_studio

---

## 🔑 Login Credentials

**IMPORTANT: What "API Key" Means**

There are TWO types of API keys in the system:

1. **SwisperStudio API Key** (what login asks for)
   - **Purpose:** Authenticates YOU to SwisperStudio
   - **Location:** docker-compose.yml → API_KEY variable
   - **Dev Value:** `dev-api-key-change-in-production`
   - **Use:** Login to SwisperStudio UI

2. **Swisper Instance API Key** (per project)
   - **Purpose:** SwisperStudio connects to Swisper instance
   - **Location:** Stored in projects table
   - **Use:** When creating a project (connection to Swisper)

**To Login:**
```
API Key: dev-api-key-change-in-production
```

---

## 📋 UAT Test Scenarios

### ✅ Test 1: Visual Check - Swisper Branding

**Steps:**
1. Open http://localhost:3000
2. Observe the login page

**Expected:**
- ✅ Dark mode background (#141923)
- ✅ Swisper logo displayed with "Studio" subtitle
- ✅ Swisper cyan blue color (#00A9DD) for buttons
- ✅ Clean, professional design
- ✅ Label says "SwisperStudio API Key" (not just "API Key")
- ✅ Helper text explains where to find the key

**What You Should See:**
```
╔═══════════════════════════════════════╗
║         [Swisper Logo]                ║
║              STUDIO                   ║
║                                       ║
║  AI Observability & Development       ║
║           Platform                    ║
║                                       ║
║  ┌─────────────────────────────────┐ ║
║  │ SwisperStudio API Key           │ ║
║  │ [password input]                │ ║
║  │ Enter your SwisperStudio API... │ ║
║  └─────────────────────────────────┘ ║
║                                       ║
║  [        Login Button        ]       ║
╚═══════════════════════════════════════╝
```

---

### ✅ Test 2: Login Flow

**Steps:**
1. Enter API key: `dev-api-key-change-in-production`
2. Click "Login"

**Expected:**
- ✅ Button shows "Logging in..." (loading state)
- ✅ Redirects to /projects
- ✅ Shows project list page

**If Login Fails:**
- Check backend is running: `docker compose ps`
- Check CORS: Should see no CORS errors in browser console

---

### ✅ Test 3: Create Project

**Steps:**
1. Click "New Project" button
2. Fill in form:
   - **Name:** "My First Swisper Instance"
   - **Swisper URL:** "https://swisper.mycompany.com"
   - **Swisper API Key:** "swisper-key-123" (this is the Swisper instance key)
   - **Description:** "Production Swisper deployment"
3. Click "Create Project"

**Expected:**
- ✅ Dialog closes
- ✅ New project appears in grid
- ✅ Shows all project details (name, URL, description)
- ✅ "View Traces" button visible

**What You Should See:**
```
╔═══════════════════════════════════════╗
║  Projects                  [+ New]    ║
║                                       ║
║  ┌─────────────────────────────────┐ ║
║  │ My First Swisper Instance       │ ║
║  │ https://swisper.mycompany.com   │ ║
║  │ Production Swisper deployment   │ ║
║  │                                 │ ║
║  │ [View Traces]                   │ ║
║  └─────────────────────────────────┘ ║
╚═══════════════════════════════════════╝
```

---

### ✅ Test 4: View Trace List

**Steps:**
1. Click "View Traces" on any project
2. Observe the trace list page

**Expected:**
- ✅ Shows "Traces" header
- ✅ "Back to Projects" button works
- ✅ DataGrid renders (may be empty)
- ✅ Shows "No traces yet" message if empty
- ✅ Dark mode styling consistent

**Note:** Traces will be empty until Swisper SDK integration (Phase 2)

---

### ✅ Test 5: Hot Reload - Backend

**Steps:**
1. Edit `backend/app/main.py`
2. Change version in health response:
   ```python
   return {"status": "healthy", "version": "0.1.0-uat-test"}
   ```
3. Save file
4. Wait 2 seconds
5. Call health endpoint

**Expected:**
- ✅ Uvicorn logs show "Detected file change"
- ✅ Auto-reloads
- ✅ Health endpoint returns new version
- ✅ No manual restart needed

**Verify:**
```bash
curl http://localhost:8001/health
# Should show: "version": "0.1.0-uat-test"
```

---

### ✅ Test 6: Hot Reload - Frontend

**Steps:**
1. Edit `frontend/src/features/auth/components/login-page.tsx`
2. Change subtitle:
   ```typescript
   AI Observability & Development Platform (UAT TEST)
   ```
3. Save file
4. Check browser (don't refresh!)

**Expected:**
- ✅ Page updates instantly (Vite HMR)
- ✅ No page reload
- ✅ Changes visible immediately
- ✅ Console shows "hmr update"

---

### ✅ Test 7: API Direct Test (Backend)

**Run these curl commands to verify backend:**

```bash
# 1. Create project
curl -X POST http://localhost:8001/api/v1/projects \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key-change-in-production" \
  -d '{
    "name": "UAT Test Project",
    "swisper_url": "https://swisper-uat.example.com",
    "swisper_api_key": "uat-key-123",
    "description": "Created via curl during UAT"
  }'

# 2. List projects
curl -s http://localhost:8001/api/v1/projects \
  -H "X-API-Key: dev-api-key-change-in-production" | python3 -m json.tool

# 3. Create trace
# (Get project_id from step 2 first)
curl -X POST http://localhost:8001/api/v1/traces \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key-change-in-production" \
  -d '{
    "id": "uat-trace-001",
    "project_id": "YOUR-PROJECT-ID-HERE",
    "name": "UAT Test Trace",
    "user_id": "uat-user",
    "session_id": "uat-session"
  }'
```

---

## ✅ UAT Checklist

Mark each item as you test:

**Backend:**
- [ ] Health endpoint responds
- [ ] Create project works (API)
- [ ] List projects works with pagination
- [ ] Create trace works with valid project
- [ ] Invalid project rejected
- [ ] Missing API key rejected
- [ ] Hot reload works

**Frontend:**
- [ ] Login page loads with Swisper branding
- [ ] Dark mode active (#141923 background)
- [ ] Swisper logo displays
- [ ] Login with correct API key works
- [ ] Create project dialog works
- [ ] Project list displays
- [ ] View traces navigation works
- [ ] Hot reload (HMR) works

**Integration:**
- [ ] Frontend can call backend APIs
- [ ] No CORS errors in browser console
- [ ] Authentication headers work
- [ ] Data displays correctly in UI

---

## 🐛 Common Issues & Solutions

### Issue: "Login failed" or "Invalid API key"

**Solution:** Use the correct key from docker-compose.yml:
```
API Key: dev-api-key-change-in-production
```

### Issue: "CORS error" in browser console

**Solution:** Verify backend CORS config includes localhost:3000:
```bash
docker compose exec backend printenv CORS_ORIGINS
# Should show: ["http://localhost:3000","http://localhost:5173"]
```

### Issue: Frontend doesn't load

**Solution:**
```bash
# Check if Vite is running
ps aux | grep vite

# Check Vite logs
cat /tmp/vite-uat.log

# Restart if needed
cd frontend && npm run dev
```

### Issue: Backend not responding

**Solution:**
```bash
# Check container status
docker compose ps

# Restart if needed
docker compose restart backend

# Check logs
docker compose logs backend --tail=50
```

---

## 📊 Expected State After UAT

**Database should have:**
- At least 1 project created via UI
- At least 1 project created via API (if tested)
- Possibly 1-2 traces (if manually created via API)

**Browser localStorage should have:**
- `swisper_studio_api_key` stored

**You should have verified:**
- ✅ System works end-to-end
- ✅ Swisper branding looks good
- ✅ Hot reload works (saves development time!)
- ✅ Ready for Phase 2 (Swisper SDK integration)

---

## 🎉 UAT Sign-Off

**Tested by:** ___________  
**Date:** ___________  
**Status:** [ ] PASS [ ] FAIL (with issues noted)  
**Ready for Phase 2:** [ ] YES [ ] NO

**Issues Found:**
- _________________
- _________________

**Notes:**
- _________________
- _________________

---

**Frontend:** http://localhost:3000  
**Backend:** http://localhost:8001  
**API Docs:** http://localhost:8001/api/v1/docs

