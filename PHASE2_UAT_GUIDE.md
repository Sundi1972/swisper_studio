# Phase 2 UAT Guide - Rich Tracing

**Date:** November 2, 2025  
**Phase:** Phase 2 MVP  
**Status:** Ready for UAT ✅

---

## 🚀 System Status

**Services:**
- ✅ Backend: http://localhost:8001 (FastAPI)
- ✅ Frontend: http://localhost:3000 (React + MUI)
- ✅ Database: PostgreSQL on port 5433
- ✅ API Docs: http://localhost:8001/api/v1/docs

**Credentials:**
```
SwisperStudio API Key: dev-api-key-change-in-production
```

**Test Data:** ✅ Created for "Production Swisper" project

---

## 📋 UAT Test Scenarios

### **Test 1: New Project Workspace Navigation** ⭐ PHASE 2

**What Changed:** Projects now open to an Overview page with sidebar navigation (not directly to tracing).

**Steps:**
1. Open http://localhost:3000
2. Login with API key: `dev-api-key-change-in-production`
3. Find **"Production Swisper"** project card
4. Click **"Open Project"** button

**✅ Verify:**
- [ ] Navigates to **Project Overview** page
- [ ] **Sidebar visible** on left with menu items:
  - 📊 Overview (highlighted/active)
  - 🔍 Tracing
  - 📈 Analytics (grayed out with "Coming soon")
  - 🌐 Graphs (grayed out with "Coming soon")
  - ⚙️ Configuration
- [ ] **Header shows:**
  - Breadcrumb: "Projects > Production Swisper"
  - Project name: "Production Swisper"
  - Description chip (if present)
- [ ] **Content shows:**
  - Project details (name, URL)
  - **Quick Actions** section with 2 cards:
    - "View Traces" card with "Go to Tracing" button
    - "Configuration" card with "View Config" button
  - Placeholder: "Key metrics dashboard coming in future phases"

---

### **Test 2: Sidebar Navigation**

**Steps:**
1. From Project Overview, click **"Tracing"** in sidebar
2. Wait for page to load
3. Click **"Configuration"** in sidebar
4. Click **"Overview"** in sidebar

**✅ Verify:**
- [ ] Each click changes main content (right side)
- [ ] **Sidebar stays visible** (persistent)
- [ ] **Active menu item highlighted** (blue background)
- [ ] **Breadcrumb updates:**
  - Overview: "Projects > Production Swisper"
  - Tracing: "Projects > Production Swisper > Tracing"
  - Config: "Projects > Production Swisper > Configuration"
- [ ] **No page reload** (SPA navigation)
- [ ] **SwisperStudio logo** stays in sidebar

---

### **Test 3: Observation Tree with Costs** ⭐ PHASE 2 CORE

**What Changed:** Trace detail now shows nested observation tree with costs, tokens, and model info.

**Steps:**
1. From Overview, click **"Go to Tracing"** button (or click "Tracing" in sidebar)
2. Wait for trace list to load
3. Find trace: **"User Request: What's my next meeting?"**
4. **Click on the trace row** (entire row is clickable)

**✅ Verify Trace Detail Page:**
- [ ] **Header section shows:**
  - Trace name: "User Request: What's my next meeting?"
  - User: "user_123"
  - Session: "session_456"
  - Time: (timestamp)
  - **Total Cost: $0.005400** ⭐ NEW!

- [ ] **Tabs present:**
  - "Tree View" (active) ✅
  - "Timeline" (disabled - future)
  - "JSON" (disabled - future)

**✅ Verify Observation Tree:**

Should show **6 observations** in nested structure:

```
📍 global_supervisor [AGENT - purple badge]
   ├─ 📍 intent_classification [GENERATION - blue badge]
   │     • Model: gpt-4-turbo
   │     • Tokens: 200 tokens
   │     • Cost: $0.003000 ⭐
   │     • Duration: ~1000ms
   │
   ├─ 📍 memory_node [SPAN - gray badge]
   │     • Duration: ~500ms
   │
   ├─ 📍 productivity_agent [AGENT - purple badge]
   │     ├─ 📍 get_calendar_events [TOOL - green badge]
   │     │     • Duration: ~500ms
   │     │
   │     └─ 📍 generate_response [GENERATION - blue badge]
   │           • Model: claude-3-sonnet-20240229
   │           • Tokens: 400 tokens
   │           • Cost: $0.002400 ⭐
   │           • Duration: ~1000ms
   │
   └─ 📍 failed_llm_call [GENERATION - blue badge]
         • Model: gpt-4
         • ERROR badge (red) ⭐
         • Duration: 0ms
```

**Specific Checks:**
- [ ] **3 levels of nesting visible** (supervisor → productivity → calendar/response)
- [ ] **Type badges color-coded:**
  - GENERATION = Blue
  - AGENT = Purple  
  - SPAN = Gray
  - TOOL = Green
- [ ] **Model names displayed** on GENERATION observations
- [ ] **Token counts shown** (e.g., "200 tokens")
- [ ] **Cost badges green** with 6 decimal places (e.g., "$0.003000")
- [ ] **Duration badges** show milliseconds
- [ ] **ERROR badge** red on failed_llm_call observation
- [ ] **Tree is expandable/collapsible** (click arrows)
- [ ] **Tree defaults to expanded** (all nodes visible)

---

### **Test 4: Cost Calculation Accuracy** ⭐ PHASE 2

**Goal:** Verify costs calculated correctly using DB pricing

**Steps:**
1. On trace detail page, examine the 2 LLM observations:
   - `intent_classification` (gpt-4-turbo)
   - `generate_response` (claude-3-sonnet)

**✅ Verify Calculations:**

**Intent Classification (gpt-4-turbo):**
- Tokens: 150 input + 50 output = 200 total ✓
- Pricing: $10/1M input, $30/1M output (default from migration)
- Calculation:
  - Input: (150 / 1,000,000) × $10 = $0.001500
  - Output: (50 / 1,000,000) × $30 = $0.001500
  - **Total: $0.003000** ⭐
- [ ] Cost badge shows: **$0.003000**

**Response Generation (claude-3-sonnet):**
- Tokens: 300 input + 100 output = 400 total ✓
- Pricing: $3/1M input, $15/1M output (default from migration)
- Calculation:
  - Input: (300 / 1,000,000) × $3 = $0.000900
  - Output: (100 / 1,000,000) × $15 = $0.001500
  - **Total: $0.002400** ⭐
- [ ] Cost badge shows: **$0.002400**

**Trace Total:**
- [ ] Header shows: **Total Cost: $0.005400** (sum of both)

---

### **Test 5: Configuration Page**

**Steps:**
1. Click **"Configuration"** in sidebar

**✅ Verify:**
- [ ] Page loads
- [ ] Shows project ID
- [ ] Blue info alert: "Full configuration UI coming in Phase 4"
- [ ] Mentions model pricing is in database
- [ ] Mentions Phase 4 will add UI

---

### **Test 6: Breadcrumb Navigation**

**Steps:**
1. From Trace Detail page (deep in hierarchy)
2. Breadcrumb should show: **Projects > Production Swisper > Tracing > [Trace ID]**
3. Click **"Production Swisper"** in breadcrumb
4. Should go to Project Overview
5. Click **"Projects"** in breadcrumb
6. Should go to Projects List

**✅ Verify:**
- [ ] Breadcrumb shows full path
- [ ] Each segment clickable
- [ ] Navigation works correctly
- [ ] No page reloads

---

### **Test 7: Multiple Observation Types**

**Goal:** Verify all observation types display correctly

**On the trace detail tree, verify:**
- [ ] **AGENT** observations (global_supervisor, productivity_agent) - Purple badge
- [ ] **GENERATION** observations (intent_classification, generate_response, failed_llm_call) - Blue badge
- [ ] **SPAN** observation (memory_node) - Gray badge
- [ ] **TOOL** observation (get_calendar_events) - Green badge

---

### **Test 8: Error Observation**

**Steps:**
1. Find `failed_llm_call` observation in tree (at same level as intent/memory/productivity)

**✅ Verify:**
- [ ] Shows **ERROR badge** (red)
- [ ] Type badge still blue (GENERATION)
- [ ] Model shows "gpt-4"
- [ ] No cost badge (0 tokens)
- [ ] Duration: 0ms

---

### **Test 9: Model Pricing API** ⭐ PHASE 2

**Goal:** Verify pricing API works (for future config UI)

**Steps:**
1. Open new tab: http://localhost:8001/api/v1/docs
2. Find **GET /api/v1/model-pricing/defaults**
3. Click "Try it out" → "Execute"

**✅ Verify Response:**
- [ ] Returns array of pricing objects
- [ ] Each has: `hosting_provider`, `model_name`, `input_price_per_million`, `output_price_per_million`
- [ ] Includes:
  - OpenAI: gpt-4-turbo, gpt-4, gpt-3.5-turbo, gpt-4o
  - Anthropic: claude-3-opus, claude-3-sonnet, claude-3-haiku
  - Azure: gpt-4-turbo, gpt-4

---

### **Test 10: Observation Tree API** ⭐ PHASE 2

**Goal:** Verify tree API returns nested structure

**Steps:**
1. In API docs: http://localhost:8001/api/v1/docs
2. Find **GET /api/v1/traces/{trace_id}/tree**
3. Enter trace ID: `trace-1762068477` (from test data output)
4. Add API key header: `dev-api-key-change-in-production`
5. Execute

**✅ Verify Response:**
- [ ] Returns array with 1 root node
- [ ] Root node has `children` array with 4 items
- [ ] `productivity_agent` has `children` array with 2 items
- [ ] Each node has:
  - `id`, `type`, `name`
  - `latency_ms` (calculated)
  - `calculated_total_cost` (if LLM)
  - `total_cost` (aggregated from children)
  - `model`, `prompt_tokens`, `completion_tokens` (if GENERATION)

---

## ✅ Phase 2 Features Verification

**Check off as you verify:**

**Backend:**
- [ ] Database has `model_pricing` table (check via API or DB)
- [ ] Observation model extended (check via API response)
- [ ] Costs auto-calculated on observation creation
- [ ] Tree API returns nested structure
- [ ] Enhanced filtering works (can test via API docs)

**Frontend:**
- [ ] Sidebar navigation working
- [ ] Project overview as landing page
- [ ] Breadcrumbs functional
- [ ] Trace detail page loads
- [ ] Observation tree displays correctly
- [ ] Costs visible in UI
- [ ] Model names visible
- [ ] Token counts visible
- [ ] Type badges color-coded
- [ ] ERROR observations highlighted
- [ ] Click trace row → navigates to detail

**Critical Phase 2 Features:**
- [ ] **Project-level model pricing** (DB table exists, API works)
- [ ] **Automatic cost calculation** (costs appear on observations with tokens)
- [ ] **Observation tree visualization** (nested structure visible)
- [ ] **Rich telemetry** (model, tokens, params captured)
- [ ] **Professional navigation** (sidebar, breadcrumbs, nested routes)

---

## 🐛 Known Limitations (Expected)

These are **deferred to Phase 2.5** (Enhancement phase):

- ❌ No separate state viewer panel (info in tree node for now)
- ❌ Timeline tab disabled (future)
- ❌ JSON view tab disabled (future)  
- ❌ No search/filter UI controls (backend ready, UI in Phase 2.5)
- ❌ Can't click observation to see details (future)
- ❌ No model parameters display (stored in DB, not in UI yet)

**These are EXPECTED and ACCEPTABLE for MVP!**

---

## 🔧 If Issues Found

**Backend Issues:**
- Check logs: `docker compose logs backend`
- Check tests: `docker compose exec backend pytest tests/ -v`
- Check health: `curl http://localhost:8001/health`

**Frontend Issues:**
- Check console: Open browser DevTools
- Check network: See API requests in Network tab
- Rebuild: `cd frontend && npm run build`

**Database Issues:**
- Check migration: `docker compose exec backend alembic current`
- Check tables: `docker compose exec postgres psql -U swisper_studio -d swisper_studio -c "\dt"`

---

## 📸 Screenshots to Capture (for documentation)

1. **Project Overview** - Sidebar + Quick Actions
2. **Trace List** - With clickable rows
3. **Trace Detail** - Observation tree with costs
4. **Observation Tree** - Showing all 6 observations nested
5. **Cost Badges** - Close-up of cost calculations
6. **Error Observation** - ERROR badge visible
7. **Configuration Page** - Placeholder message

---

## ✅ UAT Sign-Off Checklist

**I have verified:**
- [ ] All 10 test scenarios pass
- [ ] All critical Phase 2 features work
- [ ] No blocking bugs found
- [ ] Performance acceptable (pages load < 2 seconds)
- [ ] UI looks professional (MUI theming consistent)

**Phase 2 UAT Status:** ________________ (PASS / NEEDS WORK)

**Issues Found:** ________________

**Sign-off:** ________________  
**Date:** ________________

---

**Ready to test! Start at http://localhost:3000** 🚀

