# Quick UAT Reference Card - Phase 2

**Start here:** http://localhost:3000

---

## 🔑 Login
```
API Key: dev-api-key-change-in-production
```

---

## 🎯 What to Test

### **1. New Navigation (2 min)**
✅ Click "Production Swisper" → "Open Project"  
✅ Verify **sidebar** visible with: Overview, Tracing, Config  
✅ Click through sidebar items  
✅ Verify breadcrumbs work  

### **2. Observation Tree (3 min)** ⭐ MAIN FEATURE
✅ Click "Go to Tracing" → Click trace "What's my next meeting?"  
✅ See **nested tree** with 7 observations  
✅ Verify **cost badges**: $0.003000, $0.002400  
✅ Verify **token badges**: 200 tokens, 400 tokens  
✅ Verify **model names**: gpt-4-turbo, claude-3-sonnet  
✅ Verify **ERROR badge** (red) on failed observation  
✅ Verify **type badges** color-coded (blue, purple, gray, green)  

### **3. Cost Accuracy (1 min)**
✅ Header shows **Total Cost: $0.005400**  
✅ Intent observation: **$0.003000** (150+50 tokens, gpt-4-turbo)  
✅ Response observation: **$0.002400** (300+100 tokens, claude-3-sonnet)  

---

## 🌳 Expected Observation Tree

```
📍 global_supervisor [AGENT - purple]
   ├─ intent_classification [GENERATION - blue] 
   │     Model: gpt-4-turbo | 200 tokens | $0.003000
   ├─ memory_node [SPAN - gray]
   │     Duration: ~500ms
   ├─ productivity_agent [AGENT - purple]
   │     ├─ get_calendar_events [TOOL - green]
   │     │     Duration: ~800ms
   │     └─ generate_user_response [GENERATION - blue]
   │           Model: claude-3-sonnet | 400 tokens | $0.002400
   └─ backup_llm_attempt [GENERATION - blue + ERROR badge]
         Model: gpt-4 | Status: Rate limit exceeded
```

---

## ✅ Quick Checklist

- [ ] Sidebar navigation works
- [ ] Breadcrumbs functional
- [ ] Observation tree displays (3 levels deep)
- [ ] Costs show: $0.003000 + $0.002400 = $0.005400
- [ ] Type badges color-coded
- [ ] ERROR badge visible (red)
- [ ] Can click trace row to view detail
- [ ] Config page accessible

---

## 🐛 Expected Limitations (Phase 2.5)

These are **deferred** and ACCEPTABLE:
- ❌ Timeline/JSON tabs disabled
- ❌ No separate state viewer panel
- ❌ No search/filter UI (backend ready)
- ❌ Can't click tree node for details

**This is the MVP - core features work!**

---

**Full Guide:** `PHASE2_UAT_GUIDE.md` (10 detailed scenarios)  
**Test Data:** Created with 1 trace, 7 observations, costs calculated  
**Status:** ✅ READY FOR UAT

---

**🚀 Go to http://localhost:3000 and start testing!**
