# Parallel Development Setup Guide

**Date:** 2025-11-01  
**Status:** Ready to Go  

---

## 🎯 Your Setup: Two Cursor Windows

```
┌─────────────────────────────────────────────────────┐
│  Window 1: Swisper (helvetiq)                       │
│  - Continue Swisper feature development             │
│  - Current workspace                                │
│  - Path: /root/projects/helvetiq                    │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Window 2: SwisperStudio (swisper_studio)           │
│  - Build observability platform                     │
│  - New workspace (fresh AI context)                 │
│  - Path: /root/projects/swisper_studio              │
└─────────────────────────────────────────────────────┘
```

---

## 📋 Step-by-Step Instructions

### **1. Stay in Current Window (Swisper)**

You're currently in: `/root/projects/helvetiq`

**This workspace will be for:**
- ✅ Swisper features
- ✅ Agent development
- ✅ Business logic
- ✅ User-facing functionality

---

### **2. Open New Cursor Window (SwisperStudio)**

**Option A: From Cursor Menu**
```
File → New Window
File → Open Folder...
Navigate to: /root/projects/swisper_studio
Click: Open
```

**Option B: From Command Line**
```bash
cursor /root/projects/swisper_studio
# Opens new Cursor window
```

**Option C: From Terminal (if cursor not in PATH)**
```bash
cd /root/projects/swisper_studio
# Then open manually in Cursor: File → Open Folder
```

---

### **3. Verify Both Windows**

**Window 1 (Swisper):**
- Status bar shows: `helvetiq`
- You see: `backend/`, `frontend/`, `docs/`
- Cursor AI context: Swisper codebase

**Window 2 (SwisperStudio):**
- Status bar shows: `swisper_studio`
- You see: `backend/`, `frontend/`, `reference/`, `docs/`
- Cursor AI context: SwisperStudio codebase

---

## 📚 Accessing Components Between Repos

### **From SwisperStudio → Swisper:**

You have access via `reference/swisper/`:

```typescript
// In swisper_studio, you can reference:
reference/swisper/frontend/src/components/     # UI components
reference/swisper/packages/icons/              # Icons
reference/swisper/frontend/src/domain/         # Domain logic
reference/swisper/frontend/src/lib/            # Utilities

// Example: Copy a component
// 1. Study: reference/swisper/frontend/src/components/Button.tsx
// 2. Adapt for SwisperStudio
// 3. Create: frontend/src/components/Button.tsx
```

### **From SwisperStudio → Langfuse:**

You also have `reference/langfuse/`:

```python
# Study Langfuse data models:
reference/langfuse/packages/shared/prisma/schema.prisma

# Study Langfuse UI:
reference/langfuse/web/src/features/traces/

# Study Langfuse API:
reference/langfuse/web/src/server/api/routers/traces.ts
```

---

## 🔄 Sharing Patterns

### **1. UI Components (Copy & Adapt)**

**Workflow:**
```bash
# In SwisperStudio window
# 1. Study Swisper component
cat reference/swisper/frontend/src/components/Button.tsx

# 2. Copy as base
cp reference/swisper/frontend/src/components/Button.tsx \
   frontend/src/components/Button.tsx

# 3. Adapt for SwisperStudio
# (different styling, different props)
```

### **2. Icons (Direct Use)**

**Workflow:**
```typescript
// SwisperStudio can import from packages/icons
// (if you set up proper npm workspace or copy)

// For MVP: Copy icons as needed
cp -r reference/swisper/packages/icons/svg/* \
      frontend/public/icons/
```

### **3. Styles/Theme (Copy & Customize)**

**Workflow:**
```bash
# Copy base Tailwind config
cp reference/swisper/frontend/tailwind.config.ts \
   frontend/tailwind.config.ts

# Customize for SwisperStudio
# (different colors, different spacing)
```

### **4. Utilities (Copy)**

**Workflow:**
```bash
# Copy useful utilities
cp reference/swisper/frontend/src/lib/date-utils.ts \
   frontend/src/lib/date-utils.ts
```

---

## ⚠️ Important Rules

### **DON'T:**
- ❌ Modify files in `reference/`
- ❌ Import directly from `reference/` (won't work at runtime)
- ❌ Create dependencies between repos
- ❌ Share databases

### **DO:**
- ✅ Study code in `reference/`
- ✅ Copy & adapt components
- ✅ Learn patterns and approaches
- ✅ Keep repos independent

---

## 🎯 Workflow Example

### **Scenario: You need a Table component in SwisperStudio**

**Step 1: Study Swisper's table**
```bash
# In SwisperStudio window
code reference/swisper/frontend/src/components/DataTable.tsx
# Study implementation, understand patterns
```

**Step 2: Check Langfuse's table**
```bash
# Also study Langfuse approach
code reference/langfuse/web/src/features/traces/components/TracesTable.tsx
```

**Step 3: Create SwisperStudio version**
```bash
# Copy best ideas from both
# Create: frontend/src/components/TraceTable.tsx
# Adapt to SwisperStudio needs
```

---

## 🧹 Delete Feature Branch (Swisper)

### **Safe to Delete:**

All documentation copied to `swisper_studio`, so safe to clean up:

```bash
# In helvetiq window
git checkout main
git branch -D feature/swisper-studio-langfuse
# Done! Branch deleted
```

**What was in branch:**
- ✅ Documentation → Copied to swisper_studio
- ✅ Analysis → Copied to swisper_studio
- ✅ Plans → Copied to swisper_studio
- ✅ Workflow improvements → Kept in main (useful)

---

## 📊 Final Repository Structure

```
/root/projects/
├── helvetiq/                              # Swisper (main product)
│   ├── backend/                           # Python/FastAPI
│   ├── frontend/                          # React
│   └── docs/                              # Swisper docs
│
├── swisper_studio/                        # SwisperStudio (observability)
│   ├── backend/                           # Python/FastAPI (new)
│   ├── frontend/                          # React (new)
│   ├── reference/
│   │   ├── langfuse/ -> ...              # Langfuse fork
│   │   └── swisper/ -> helvetiq/         # Swisper link
│   └── docs/                              # SwisperStudio docs
│
└── swisper_studio_langfuse_reference/     # Langfuse fork (unchanged)
```

---

## ✅ Ready to Go Checklist

- [ ] Open second Cursor window for swisper_studio
- [ ] Verify you see `reference/swisper/` and `reference/langfuse/`
- [ ] Review MVP plan: `docs/plans/plan_swisper_studio_mvp_v1.md`
- [ ] Delete feature branch in helvetiq (optional)
- [ ] Start Week 1 development in swisper_studio

---

## 🚀 Next Steps

### **In Swisper Window (Window 1):**
- Continue normal Swisper development
- Commit docs that are still staged
- Delete feature branch (optional)

### **In SwisperStudio Window (Window 2):**
- Review MVP plan
- Setup backend structure (Week 1)
- Study reference implementations
- Start building!

---

**You're all set for parallel development!** 🎉

**Questions?** Just ask in either window! 💪

