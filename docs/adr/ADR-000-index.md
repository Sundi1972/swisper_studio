# SwisperStudio - Architecture Decision Records

**Last Updated:** 2025-11-01  
**Total ADRs:** 6

---

## Quick Reference

| # | Decision | Impact | Phase |
|---|----------|--------|-------|
| [001](ADR-001-use-mui-instead-of-tailwind.md) | Use MUI Instead of Tailwind | 🟢 Frontend | Phase 1 |
| [002](ADR-002-database-separation-strategy.md) | Database Separation Strategy | 🔴 Architecture | Overall |
| [003](ADR-003-two-mode-configuration-system.md) | Two-Mode Configuration System | 🟡 Backend | Phase 4 |
| [004](ADR-004-data-driven-admin-ui.md) | Data-Driven Admin UI via SAP | 🟡 Full Stack | Phase 4 |
| [005](ADR-005-graph-level-auto-instrumentation.md) | Graph-Level Auto-Instrumentation | 🟢 SDK | Phase 1 |
| [006](ADR-006-build-from-scratch-vs-fork.md) | Build from Scratch vs Fork | 🔴 Strategy | Overall |

**Legend:**
- 🔴 Critical (affects entire system)
- 🟡 Significant (affects major feature)
- 🟢 Tactical (affects specific component)

---

## By Category

### Infrastructure & Data
- [ADR-002: Database Separation Strategy](ADR-002-database-separation-strategy.md)

### Frontend
- [ADR-001: Use MUI Instead of Tailwind](ADR-001-use-mui-instead-of-tailwind.md)

### Backend
- [ADR-003: Two-Mode Configuration System](ADR-003-two-mode-configuration-system.md)
- [ADR-004: Data-Driven Admin UI](ADR-004-data-driven-admin-ui.md)

### SDK & Integration
- [ADR-005: Graph-Level Auto-Instrumentation](ADR-005-graph-level-auto-instrumentation.md)

### Strategy
- [ADR-006: Build from Scratch vs Fork](ADR-006-build-from-scratch-vs-fork.md)

---

## Timeline

```
Nov 1, 2025
├── ADR-001: MUI vs Tailwind
├── ADR-002: Database Separation
├── ADR-003: Two-Mode Config
├── ADR-004: Data-Driven UI
├── ADR-005: Auto-Instrumentation
└── ADR-006: Build vs Fork
```

---

## Future ADRs (Planned)

Decisions we'll make later:
- **Phase 2:** State diff algorithm choice
- **Phase 2:** LLM telemetry capture method
- **Phase 3:** Graph layout algorithm
- **Phase 4:** SAP versioning strategy
- **Phase 5:** ClickHouse migration approach

---

## How to Use ADRs

### Before Starting a Phase
1. Read relevant ADRs
2. Understand context and rationale
3. Follow implementation notes
4. Validate decision is still correct

### When Making New Decisions
1. Check if ADR exists
2. If yes, follow it
3. If no, create new ADR
4. Get approval before implementation

### When Revisiting Decisions
1. Review ADR
2. Check validation metrics
3. Update status if superseded
4. Create new ADR if changing approach

---

**Created By:** Development Team  
**Maintained By:** Lead Architect

