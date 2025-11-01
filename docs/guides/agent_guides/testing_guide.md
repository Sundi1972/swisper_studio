# Testing Guide for AI Agents

**Version:** v1.0  
**Last Updated:** 2025-10-29  
**Last Updated By:** heiko  
**Status:** Active

**Audience:** AI Assistants (Cursor, Claude)  
**Purpose:** How to write, mark, and execute tests following Swisper's TDD workflow

---

## Changelog

### v1.0 - 2025-10-29
- Initial creation for AI agents
- Docker container testing workflow
- CI test marking strategy
- Test templates and examples
- Quick reference checklist

---

## 🎯 Core Philosophy

**Write comprehensive tests with real infrastructure, mark only critical tests for CI.**

### **The Rules:**
1. ✅ Use **real infrastructure** (database, Redis, LLM)
2. ✅ Mock ONLY when: cost prohibitive, unstable, or rate-limited
3. ✅ Mark **1-2 critical tests per domain** for CI
4. ✅ **Execute in Docker containers** (not locally)
5. ✅ Always run in **verbose mode** (`-vv`)
6. ✅ **Watch terminal output** to verify status

---

## 🐳 Docker Container Testing Workflow

### **Mandatory 3-Step Process:**

**Every time you write or modify tests:**

```bash
# Step 1: UPDATE container with latest code
docker compose cp backend/app/. backend:/code/app/
docker compose cp backend/tests/. backend:/code/tests/

# Step 2: EXECUTE tests in verbose mode
docker compose exec backend pytest tests/api/test_my_feature.py -vv

# Step 3: WATCH terminal output and VERIFY status
# TDD Red: Tests should FAIL
# TDD Green: Tests should PASS
```

**NEVER run tests locally with `poetry run pytest` - always use Docker!**

---

## 🏷️ CI Test Marking

### **Mark CI-Critical Tests:**

**Only 1-2 tests per domain run in CI to keep CI fast (<5 minutes).**

```python
# ✅ CI-Critical Test (runs in CI)
@pytest.mark.ci_critical
@pytest.mark.asyncio
async def test_fact_extraction_basic_flow(db, test_user):
    """CI: Basic fact extraction works"""
    result = await extract_facts("I'm allergic to peanuts", test_user.id)
    
    assert len(result.facts) > 0
    assert result.facts[0].type == "Allergy"
```

**Criteria for CI-critical:**
- ✅ Golden path (most important scenario)
- ✅ Fast (<5 seconds)
- ✅ No expensive LLM calls (or mocked)
- ✅ Regression prevention

---

### **Mark Comprehensive Tests to Skip CI:**

**Tests with real LLM calls or many scenarios should skip CI.**

```python
# ✅ Comprehensive Test (skip in CI, run locally)
import os

pytestmark = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="CI: Uses real LLM calls - run locally only"
)

@pytest.mark.asyncio
async def test_entity_disambiguation_comprehensive(db, test_user):
    """
    Comprehensive: 10+ scenarios with real LLM.
    Tests edge cases, ambiguous entities, relationship filtering.
    """
    # Expensive but thorough - run locally and nightly
    # Test scenario 1
    # Test scenario 2
    # ... 10+ scenarios
    pass
```

**Mark to skip CI if:**
- ❌ Uses real LLM calls (expensive)
- ❌ Tests many edge case variations (not critical for every commit)
- ❌ Performance tests (run in nightly)
- ❌ External API integration (rate limits)

---

## 📋 Test Templates

### **Template 1: Business Value Test**

```python
@pytest.mark.asyncio
async def test_{feature}_{business_scenario}(db, test_user_with_avatar):
    """
    Business case: [Describe user scenario in plain English]
    Expected: [What should happen]
    """
    user_id, avatar_id, workspace_id = test_user_with_avatar
    service = MyService()
    
    input_data = MyInput(
        user_message="[Realistic user message]",
        user_id=str(user_id),
        avatar_id=str(avatar_id),
        workspace_id=str(workspace_id)
    )
    
    result = await service.execute(input_data, db=db)
    
    # Assert business outcome
    assert len(result.entities_created) == 1, \
        f"Should create 1 entity, got {len(result.entities_created)}"
```

---

### **Template 2: Edge Case Test**

```python
@pytest.mark.asyncio
async def test_{feature}_handles_{edge_case}(db, test_user):
    """Edge case: [Describe boundary condition]"""
    result = await function_under_test(
        edge_case_input,
        user_id=test_user.id
    )
    
    assert result.is_valid()
    # Or assert proper error handling
```

---

### **Template 3: Error Case Test**

```python
@pytest.mark.asyncio
async def test_{feature}_returns_error_for_{invalid_input}(db):
    """Error case: [Invalid input] should raise [specific error]"""
    with pytest.raises(ValueError, match="Expected error message"):
        await function_under_test(invalid_input, user_id="invalid")
```

---

## 🎯 TDD Workflow for Agents

### **Step 2: TDD (Red) - Write Tests**

**Actions:**
1. ✅ Write 3-5 comprehensive business tests
2. ✅ Write 2-3 edge case tests
3. ✅ Write 1-2 error case tests
4. ✅ Mark **1-2 as CI-critical** with `@pytest.mark.ci_critical`
5. ✅ Mark **expensive LLM tests** with `skipif(CI)`
6. 🔄 **UPDATE container:**
   ```bash
   docker compose cp backend/app/. backend:/code/app/
   docker compose cp backend/tests/. backend:/code/tests/
   ```
7. ⚡ **EXECUTE:**
   ```bash
   docker compose exec backend pytest tests/api/test_my_feature.py -vv
   ```
8. 👁️ **WATCH** terminal output
9. ✅ **VERIFY:** Tests FAIL (red)

---

### **Step 5: Implement (Green) - After Implementation**

**Actions:**
1. 🔄 **UPDATE container:**
   ```bash
   docker compose cp backend/app/. backend:/code/app/
   ```
2. ⚡ **EXECUTE:**
   ```bash
   docker compose exec backend pytest tests/api/test_my_feature.py -vv
   ```
3. 👁️ **WATCH** terminal output
4. ✅ **VERIFY:** Tests PASS (green)

---

### **Step 6: Refactor - After Code Quality Improvements**

**Actions:**
1. 🔄 **UPDATE container:**
   ```bash
   docker compose cp backend/app/. backend:/code/app/
   ```
2. ⚡ **EXECUTE:**
   ```bash
   docker compose exec backend pytest tests/api/test_my_feature.py -vv
   ```
3. 👁️ **WATCH** terminal output
4. ✅ **VERIFY:** Tests STILL PASS

---

## 📊 CI Allocation Per Domain

**Goal:** CI in <5 minutes total

| Domain | CI Tests | Local Tests | Example CI Test |
|--------|----------|-------------|-----------------|
| Fact Extraction | 2 | 10+ | Basic extraction, allergy facts |
| Entity Disambiguation | 2 | 8+ | Colleague vs public figure |
| Intent Classification | 1 | 5+ | Simple chat detection |
| Preference Extraction | 1 | 6+ | Basic preference detection |
| API Endpoints | 1 each | Many | Chat creation, message send |

**Total CI:** 10-15 tests (~60-90 seconds)  
**Total Comprehensive:** 50-100+ tests (run locally)

---

## ✅ Test Writing Checklist

**Before writing tests:**
- [ ] Read `docs/plans/plan_{feature}_v{version}.md` for test scenarios
- [ ] Identify business-critical scenarios (1-2 for CI)
- [ ] Identify edge cases and error cases (skip CI)

**While writing tests:**
- [ ] Use real infrastructure (DB, Redis, LLM when needed)
- [ ] Write descriptive docstrings (business case + expected outcome)
- [ ] Use realistic test data (not "test" or "foo")
- [ ] Mark 1-2 as `@pytest.mark.ci_critical`
- [ ] Mark expensive LLM tests with `skipif(CI)`

**After writing tests (TDD Red):**
- [ ] Update container: `docker compose cp backend/app/. backend:/code/app/`
- [ ] Update container: `docker compose cp backend/tests/. backend:/code/tests/`
- [ ] Execute: `docker compose exec backend pytest <file> -vv`
- [ ] Watch terminal output
- [ ] Verify tests FAIL (red)

**After implementing (TDD Green):**
- [ ] Update container: `docker compose cp backend/app/. backend:/code/app/`
- [ ] Execute: `docker compose exec backend pytest <file> -vv`
- [ ] Watch terminal output
- [ ] Verify tests PASS (green)

**After refactoring:**
- [ ] Update container: `docker compose cp backend/app/. backend:/code/app/`
- [ ] Execute: `docker compose exec backend pytest <file> -vv`
- [ ] Watch terminal output
- [ ] Verify tests STILL PASS

---

## 🚫 Common Mistakes

### ❌ DON'T:

```python
# ❌ Running tests locally (not in Docker)
poetry run pytest tests/api/test_my_feature.py

# ❌ Not marking CI tests
@pytest.mark.asyncio  # Missing ci_critical marker!
async def test_critical_flow(db):
    pass

# ❌ Not skipping expensive tests in CI
@pytest.mark.asyncio  # Should have skipif(CI)!
async def test_comprehensive_llm_scenarios(db):
    # Uses real LLM - should skip CI!
    pass

# ❌ Not updating container before running tests
docker compose exec backend pytest ...  # Missing docker compose cp step!
```

### ✅ DO:

```python
# ✅ Mark CI-critical tests
@pytest.mark.ci_critical
@pytest.mark.asyncio
async def test_critical_flow(db):
    pass

# ✅ Skip expensive tests in CI
import os

pytestmark = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="CI: Uses real LLM calls"
)

@pytest.mark.asyncio
async def test_comprehensive_scenarios(db):
    pass

# ✅ Update container before executing tests
# In terminal/commands:
docker compose cp backend/app/. backend:/code/app/
docker compose cp backend/tests/. backend:/code/tests/
docker compose exec backend pytest tests/api/test_my_feature.py -vv
```

---

## 📚 pytest Configuration

**Ensure `backend/pytest.ini` has:**

```ini
[pytest]
markers =
    ci_critical: Critical tests that run in CI (fast, golden path)
    asyncio: Async tests
    performance: Performance/load tests (skip in CI)
```

**Run different test suites:**

```bash
# CI tests only (what runs in CI)
docker compose exec backend pytest -m ci_critical -vv

# All tests (comprehensive local testing)
docker compose exec backend pytest -vv

# Skip CI tests (run comprehensive only)
docker compose exec backend pytest -m "not ci_critical" -vv
```

---

## 🔍 Quick Command Reference

```bash
# ====================
# BEFORE Running Tests
# ====================
# Always update container first!
docker compose cp backend/app/. backend:/code/app/
docker compose cp backend/tests/. backend:/code/tests/

# ====================
# EXECUTE Tests
# ====================
# Specific test file
docker compose exec backend pytest tests/api/test_my_feature.py -vv

# Specific test function
docker compose exec backend pytest tests/api/test_my_feature.py::test_function_name -vv

# All tests
docker compose exec backend pytest -vv

# CI-critical tests only
docker compose exec backend pytest -m ci_critical -vv

# ====================
# VERIFY Status
# ====================
# Watch terminal for:
# - PASSED (green) ✅
# - FAILED (red) ❌
# - Test names and progress
# - Assertion messages
```

---

## 📖 Related Documentation

- **Workflow Rules:** `.cursor/rules/00-workflow.mdc` - Complete TDD workflow
- **Development SOP:** `.cursor/rules/development-sop.mdc` - Testing in workflow
- **Common Mistakes:** `.cursor/rules/35-implementation-common-mistakes.mdc` - CI marking examples
- **Testing Guide (Developers):** `docs/guides/TESTING_GUIDE.md` - Conceptual overview

---

**Remember:** Real infrastructure + Docker containers + CI selection = Quality + Speed! 🎯

