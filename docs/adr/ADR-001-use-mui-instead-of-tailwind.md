# ADR-001: Use MUI Instead of Tailwind for Frontend

**Status:** ✅ Accepted  
**Date:** 2025-11-01  
**Deciders:** Development Team  
**Context:** Phase 1 - Frontend Technology Selection

---

## Context and Problem Statement

SwisperStudio needs a UI framework for the frontend. The initial plan mentioned Tailwind CSS (commonly used with Shadcn/ui), but our analysis of the Swisper reference codebase revealed it uses Material-UI (MUI) v7.

**Question:** Should we use Tailwind CSS or MUI for SwisperStudio's frontend?

---

## Decision Drivers

* **Visual consistency** with existing Swisper product
* **Component reusability** from Swisper codebase
* **Development speed** (leverage existing patterns vs. learning new framework)
* **Maintenance burden** (keeping two different UI systems in sync)
* **Designer/developer familiarity** with the chosen framework

---

## Considered Options

1. **Tailwind CSS + Shadcn/ui** (originally planned, matches Langfuse)
2. **MUI v7 + @shiu/components** (matches Swisper)
3. **Mix both** (use Tailwind in SwisperStudio, but import some Swisper components)

---

## Decision Outcome

**Chosen option:** "MUI v7 + @shiu/components"

**Rationale:**

SwisperStudio is a **companion product** to Swisper, not a standalone application. Users will switch between Swisper and SwisperStudio frequently, so they should feel like **the same product family**.

Using MUI provides:
1. **Instant visual consistency** with Swisper
2. **Direct component reuse** (`@shiu/components`, `@shiu/icons`)
3. **No designer work needed** (reuse Swisper's theme)
4. **Familiar patterns** for developers (same as Swisper codebase)
5. **Easier to copy/paste code** from Swisper reference

### Positive Consequences

* ✅ SwisperStudio looks and feels like Swisper (unified product experience)
* ✅ Can directly reuse `@shiu/components` package (buttons, cards, dialogs, etc.)
* ✅ Can directly reuse `@shiu/icons` package (consistent iconography)
* ✅ Developers familiar with Swisper can immediately contribute
* ✅ No need to maintain two separate design systems
* ✅ Theme changes in Swisper automatically apply to SwisperStudio (if we share the theme)

### Negative Consequences

* ❌ Langfuse reference uses Tailwind (can't copy Langfuse frontend code directly)
* ❌ MUI is heavier than Tailwind (larger bundle size)
* ❌ Committed to MUI ecosystem (harder to change later)

---

## Pros and Cons of the Options

### Option 1: Tailwind CSS + Shadcn/ui

**Pros:**
* Smaller bundle size
* Matches Langfuse reference (easier to copy UI patterns)
* Modern, popular framework
* Utility-first CSS (fast prototyping)

**Cons:**
* ❌ **Different look from Swisper** (users see inconsistency)
* ❌ **Cannot reuse Swisper components** (incompatible systems)
* ❌ **Need to recreate all UI patterns** (buttons, forms, etc.)
* ❌ **Need designer to create new theme** (extra work)
* ❌ **Two design systems to maintain** (Swisper + SwisperStudio)

### Option 2: MUI v7 + @shiu/components ✅ CHOSEN

**Pros:**
* ✅ **Perfect visual consistency** with Swisper
* ✅ **Direct component reuse** (instant UI library)
* ✅ **No design work needed** (reuse Swisper theme)
* ✅ **Single design system** (easier maintenance)
* ✅ **Familiar to team** (same as Swisper patterns)

**Cons:**
* ❌ Larger bundle size than Tailwind
* ❌ Can't directly copy Langfuse frontend code

### Option 3: Mix Both

**Pros:**
* Flexibility to use both systems

**Cons:**
* ❌ **Worst of both worlds** (two CSS systems = complexity)
* ❌ **Bundle size bloat** (shipping both MUI + Tailwind)
* ❌ **Inconsistent styling** (some components Tailwind, some MUI)
* ❌ **Confusion for developers** (which system to use?)

---

## Implementation Details

### Dependencies to Add

```json
{
  "dependencies": {
    "@mui/material": "^7.0.2",
    "@mui/icons-material": "^7.0.2",
    "@emotion/react": "^11.11.1",
    "@emotion/styled": "^11.11.0"
  }
}
```

### Reusing Swisper Packages

```json
{
  "dependencies": {
    "@shiu/components": "workspace:*",
    "@shiu/icons": "workspace:*"
  }
}
```

### Styling Pattern

```typescript
// Follow Swisper pattern - styled components
import { styled } from '@mui/material/styles';
import Box from '@mui/material/Box';

const Container = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  backgroundColor: theme.palette.background.paper,
}));
```

---

## Links

* **Analysis:** [Phase 1 Langfuse/Swisper Analysis](../analysis/phase1_langfuse_swisper_analysis.md)
* **Swisper Components:** `reference/swisper/packages/components/`
* **Swisper Icons:** `reference/swisper/packages/icons/`
* **Cursor Rules:** `reference/swisper/.cursor/rules/styling.mdc`

---

## Validation

**Success Metrics:**
- SwisperStudio UI looks consistent with Swisper (same colors, fonts, spacing)
- Can reuse at least 80% of UI components from `@shiu/components`
- Developers report no confusion when switching between codebases
- No need for separate design system documentation

**Review Date:** After Phase 1 completion (2 weeks)

---

## Notes

**Langfuse UX Still Valuable:**
- While we can't copy Langfuse's Tailwind code directly, we can still:
  - Copy their **UX patterns** (page layouts, information architecture)
  - Copy their **data flow** (how data is structured and displayed)
  - Reference their **component structure** (which components exist)
  - Then implement in MUI following Swisper patterns

**Cost of Reversal:**
- **High** - Changing UI framework after Phase 1 would require complete frontend rewrite
- Better to decide now and commit
- If MUI proves problematic, reassess after Phase 1

---

**Decision Made By:** Development Team  
**Approved By:** Product Owner (pending)  
**Date:** 2025-11-01

