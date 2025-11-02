# 📋 SwisperStudio Quick Reference

**Essential documents for starting implementation:**

---

## 🎯 **Must Read (Before Coding)**

### **1. Implementation Plan** ⭐⭐⭐
```
docs/plans/plan_swisper_studio_mvp_v1.md
```
- 12-week MVP roadmap
- Week-by-week tasks
- Tech stack & architecture
- Data models

### **2. Integration Guide** ⭐⭐⭐
```
docs/guides/swisper_studio_integration_guide.md
```
- How to integrate with Helvetiq
- `@traced` decorator design
- Two-database architecture
- API communication

### **3. Handover Document** ⭐⭐
```
HANDOVER.md
```
- Complete context for new agent
- Week 1 checklist
- Quick start commands

---

## 📚 **Supporting Documents**

### **Analysis (Why we built this way)**
```
docs/analysis/ANALYSIS_COMPLETE.md
docs/analysis/swisper_studio_fork_vs_build.md
```

### **Langfuse Feature Analysis**
```
docs/analysis/langfuse_features/01_tracing_core.md
docs/analysis/langfuse_features/02_prompt_versioning.md
docs/analysis/langfuse_features/03_state_tracking.md
```

### **Development Rules**
```
.cursor/rules/00-workflow.mdc           (TDD workflow)
.cursor/rules/development-sop.mdc       (Development process)
.cursor/rules/40-db-policy.mdc          (Database policy)
```

---

## 🚀 **Quick Start**

```bash
# 1. Read the plan
less docs/plans/plan_swisper_studio_mvp_v1.md

# 2. Read integration guide
less docs/guides/swisper_studio_integration_guide.md

# 3. Read handover
less HANDOVER.md

# 4. Start Week 1 (Backend scaffolding)
```

---

## 🎯 **Week 1 Focus**

From `docs/plans/plan_swisper_studio_mvp_v1.md`:
- Backend: FastAPI + SQLModel + PostgreSQL + ClickHouse
- Trace ingestion API
- `@traced` decorator
- Basic storage

---

**Everything else is reference material!**


