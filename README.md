# SwisperStudio

**Observability & Configuration Management Platform for Swisper SDK**

---

## Overview

SwisperStudio is a custom-built platform for:
- **Traceability** - View LLM traces, agent execution flows, costs
- **Prompt Management** - Version, test, and deploy prompts
- **Configuration Management** - Manage Swisper config with UI
- **Admin Interface** - User management, API keys, settings

---

## Tech Stack

- **Backend:** Python/FastAPI
- **Frontend:** React/Vite
- **Database:** PostgreSQL + ClickHouse
- **Cache/Queue:** Redis

---

## Project Structure

```
swisper_studio/
├── backend/           # Python/FastAPI backend
│   └── app/
├── frontend/          # React/Vite frontend
│   └── src/
├── reference/         # Reference implementations
│   └── langfuse/      # Langfuse fork (living spec)
├── docs/              # Documentation
│   ├── analysis/      # Feature analysis
│   ├── plans/         # Implementation plans
│   └── guides/        # Integration guides
└── .cursor/           # Cursor AI rules
    └── rules/
```

---

## Documentation

**Start Here:**
- 📋 `docs/plans/plan_swisper_studio_mvp_v1.md` - MVP implementation plan
- 🔗 `docs/guides/swisper_studio_integration_guide.md` - Integration with Swisper
- 📊 `docs/analysis/swisper_studio_fork_vs_build.md` - Build vs fork decision

**Status:**
- `SWISPER_STUDIO_STATUS.md` - Current status
- `SWISPER_STUDIO_QUICK_STATUS.md` - Quick summary

---

## Development

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker + Docker Compose
- PostgreSQL
- Redis

### Setup

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Frontend
cd frontend
npm install

# Start services
docker compose up -d
```

---

## Architecture

**Build Approach:** Custom build using Langfuse as architectural reference

**Why Build:**
- Git-first prompt workflow
- Python-native development tools (agent builder)
- Data-driven admin UI
- Full control for platform features

**Using Langfuse as:**
- Living spec (data models, patterns)
- UI inspiration
- Architecture reference

---

## Timeline

**MVP:** 12 weeks
- Phase 1: Traceability (4 weeks)
- Phase 2: Agent Visualizer (2 weeks)
- Phase 3: Prompt Editor (3 weeks)
- Phase 4: Admin UI (3 weeks)

---

## Related Repositories

- **Swisper Backend:** [github.com/Fintama/helvetiq](https://github.com/Fintama/helvetiq)
- **Langfuse Reference:** `reference/langfuse/` (Langfuse fork for reference)

---

## License

Proprietary - Fintama AG

---

**Questions?** See `docs/` for detailed documentation.

