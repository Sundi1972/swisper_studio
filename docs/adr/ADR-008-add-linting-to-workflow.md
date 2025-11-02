# ADR-008: Add Linting to Development Workflow

**Status:** ✅ Accepted  
**Date:** 2025-11-02  
**Deciders:** Development Team  
**Context:** Development Workflow - Catching Errors Early

---

## Context and Problem Statement

We frequently encounter import errors and type issues at runtime (when backend tries to start). These should be caught during development, not when the application crashes.

**Examples of issues caught late:**
- Missing imports (`NameError: name 'APIKey' is not defined`)
- Unused imports
- Type mismatches

**Question:** How can we catch these errors before runtime?

---

## Decision

**Add linting checks to development workflow** using `ruff` and `mypy`.

**When to run:**
1. ✅ **Before committing** - Run `./scripts/lint.sh`
2. ✅ **In CI** - Automatic linting on every PR
3. ✅ **On file save** (optional) - IDE integration

---

## Implementation

### 1. Linting Script

Created: `scripts/lint.sh`

```bash
#!/bin/bash
# Checks:
# - Unused imports (ruff F401)
# - Missing imports (ruff F821)
# - Type errors (mypy)
# - Code formatting (ruff format)
```

**Usage:**
```bash
./scripts/lint.sh
```

### 2. Ruff Checks

**Key error codes:**
- `F401` - Unused imports
- `F811` - Redefined imports
- `F821` - Undefined names (missing imports!)
- `E402` - Module level import not at top

### 3. MyPy Type Checking

Catches:
- Missing imports
- Type mismatches
- Incorrect return types

---

## Workflow Integration

### Updated Development Process

```
BEFORE (Current - Reactive):
1. Write code
2. Copy to container
3. Run code
4. ❌ CRASH - NameError!
5. Fix import
6. Repeat

AFTER (New - Proactive):
1. Write code
2. Run ./scripts/lint.sh
3. ✅ Catch import errors
4. Fix before copying
5. Copy to container
6. ✅ Code works first time!
```

### Add to Cursor Workflow

Update `.cursor/00-workflow.mdc`:

**Step 4.5: Lint Before Testing**
```
After writing code, BEFORE copying to container:
1. Run: ./scripts/lint.sh
2. Fix any import or type errors
3. THEN copy to container and run tests
```

---

## Benefits

✅ **Catch errors early** - Before runtime
✅ **Faster development** - No restart cycles
✅ **Better code quality** - Enforced standards
✅ **CI-ready** - Same checks in CI pipeline

---

## Future Enhancements

### Pre-commit Hooks

```bash
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ruff
        name: ruff
        entry: docker compose exec backend ruff check
        language: system
        pass_filenames: false
```

### IDE Integration

- VS Code: Ruff extension
- Cursor: Same as VS Code
- PyCharm: Ruff plugin

---

## Notes

**Why Not Install in Dockerfile?**
- Currently using production image (small size)
- Dev dependencies add 100MB+
- Future: Create separate dev Dockerfile with all tools

**Temporary Solution:**
- Install on-demand in lint script
- Fast with `uv` (< 5 seconds)
- Good enough for MVP

**Production:**
- Add proper dev container with all tools pre-installed
- Make linting mandatory (block commits if fails)

