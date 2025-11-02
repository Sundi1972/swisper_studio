# Architecture Decision Records (ADR)

**Purpose:** Document significant architectural decisions for SwisperStudio

**Format:** [MADR](https://adr.github.io/madr/) (Markdown Architecture Decision Records)

---

## What is an ADR?

An Architecture Decision Record (ADR) captures an important architectural decision made along with its context and consequences.

### When to Write an ADR

Create an ADR when you:
- Choose between multiple technical approaches
- Make a decision that affects the entire system
- Select a major library or framework
- Define data models or API contracts
- Establish development patterns or standards
- Make security or performance trade-offs

### When NOT to Write an ADR

Skip ADRs for:
- Implementation details (those go in code comments)
- Temporary decisions
- Obvious choices with no alternatives
- Decisions easily reversed

---

## ADR Numbering

Use sequential numbering: `001`, `002`, `003`, etc.

Format: `ADR-XXX-short-title.md`

**Examples:**
- `ADR-001-use-mui-instead-of-tailwind.md`
- `ADR-002-database-separation-strategy.md`
- `ADR-003-two-mode-configuration-system.md`

---

## Index of ADRs

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [001](ADR-001-use-mui-instead-of-tailwind.md) | Use MUI Instead of Tailwind for Frontend | ✅ Accepted | 2025-11-01 |
| [002](ADR-002-database-separation-strategy.md) | Database Separation Strategy | ✅ Accepted | 2025-11-01 |
| [003](ADR-003-two-mode-configuration-system.md) | Two-Mode Configuration System | ✅ Accepted | 2025-11-01 |
| [004](ADR-004-data-driven-admin-ui.md) | Data-Driven Admin UI via SAP | ✅ Accepted | 2025-11-01 |
| [005](ADR-005-graph-level-auto-instrumentation.md) | Graph-Level Auto-Instrumentation | ✅ Accepted | 2025-11-01 |
| [006](ADR-006-build-from-scratch-vs-fork.md) | Build from Scratch vs Fork Langfuse | ✅ Accepted | 2025-11-01 |
| [007](ADR-007-pragmatic-async-testing-strategy.md) | Pragmatic Async Testing Strategy for MVP | ✅ Accepted | 2025-11-02 |

---

## ADR Status Values

- **Proposed** - Under discussion
- **Accepted** - Approved and implemented
- **Deprecated** - No longer valid
- **Superseded** - Replaced by another ADR

---

## Template

See [ADR-TEMPLATE.md](ADR-TEMPLATE.md) for the standard template.

