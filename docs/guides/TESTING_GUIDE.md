# Testing Guide

**Version:** v2.0  
**Last Updated:** 2025-10-29  
**Last Updated By:** heiko  
**Status:** Active

---

## Changelog

### v2.0 - 2025-10-29
- Complete rewrite focused on Swisper-specific testing approach
- Added Docker container testing requirements
- Added CI test selection strategy (1-2 critical tests per domain)
- Added real infrastructure testing philosophy
- Removed generic testing content
- Updated all commands to use Docker

### v1.0 - 2025-10-08
- Initial testing guide

---

## 🎯 Swisper Testing Philosophy

**Core Principle:** Use **real infrastructure** for comprehensive testing, but keep **CI minimal** for speed.

### **Key Approach:**

1. ✅ **Write comprehensive tests** with real infrastructure (DB, LLM, Redis)
2. ✅ **Mark 1-2 critical tests per domain** for CI (`@pytest.mark.ci_critical`)
3. ✅ **Skip expensive tests in CI** (LLM calls, edge cases)
4. ✅ **Run all tests locally** before PR
5. ✅ **Execute tests in Docker containers** (same environment as production)

**Goal:** Comprehensive coverage locally + Fast CI (<5 minutes)

---

## 🐳 Running Tests in Docker Containers

### **CRITICAL: Always Test in Docker**

Tests MUST run in Docker containers to use real infrastructure (database, Redis, etc.).

### **Step-by-Step:**

**1. Update Container with Latest Code:**
```bash
# Copy your changes to running container
docker compose cp backend/app/. backend:/code/app/
docker compose cp backend/tests/. backend:/code/tests/
```

**2. Execute Tests in Container:**
```bash
# Run specific test file (verbose mode)
docker compose exec backend pytest tests/api/test_my_feature.py -vv

# Run all tests
docker compose exec backend pytest -vv

# Run only CI-critical tests
docker compose exec backend pytest -m ci_critical -vv
```

**3. Watch Terminal Output:**
- See test progress in real-time
- Verify PASS/FAIL status
- Check assertion messages

---

## 🏷️ CI Test Marking Strategy

### **Mark Tests for CI Selection:**

**Only 1-2 critical tests per domain should run in CI.**

#### **CI-Critical Tests (RUN in CI):**

```python
# ✅ Mark for CI - golden path test
@pytest.mark.ci_critical
@pytest.mark.asyncio
async def test_fact_extraction_basic_flow(db, test_user):
    """CI: Verify basic fact extraction works end-to-end"""
    result = await extract_facts("I'm allergic to peanuts", test_user.id)
    
    assert len(result.facts) > 0
    assert result.facts[0].type == "Allergy"
```

**Criteria for CI tests:**
- ✅ Golden path (most important scenario)
- ✅ Fast (<5 seconds)
- ✅ No expensive LLM calls (or use mocked)
- ✅ Regression prevention (tests that caught bugs)

---

#### **Comprehensive Tests (SKIP in CI, RUN locally):**

```python
# ✅ Skip in CI - uses real LLM calls
import os

pytestmark = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="CI: Uses real LLM calls - run locally only"
)

@pytest.mark.asyncio
async def test_entity_disambiguation_comprehensive(db, test_user):
    """
    Comprehensive test with 10+ scenarios using real LLM.
    Tests edge cases, ambiguous entities, relationship filtering.
    """
    # Expensive but thorough - run locally and in nightly builds
    # Test 10+ scenarios with real LLM calls
    pass
```

**Criteria for skipping CI:**
- ❌ Uses real LLM calls (expensive)
- ❌ Tests edge case variations (not critical for every commit)
- ❌ Performance tests (run in nightly builds)
- ❌ Integration with external APIs (rate limits)

---

## 📋 pytest Configuration

**Add to `backend/pytest.ini`:**

```ini
[pytest]
markers =
    ci_critical: Critical tests that run in CI (fast, golden path)
    asyncio: Async tests
    performance: Performance/load tests (skip in CI)
    integration: Integration tests
```

**Run different test suites:**

```bash
# CI tests only (fast, critical path)
docker compose exec backend pytest -m ci_critical -vv

# All tests except CI-critical (comprehensive suite)
docker compose exec backend pytest -m "not ci_critical" -vv

# All tests (local development)
docker compose exec backend pytest -vv

# Performance tests only
docker compose exec backend pytest -m performance -vv
```

---

## 🎯 CI Allocation Guidelines

**Goal:** CI completes in **<5 minutes** total

**Per Domain Allocation:**

| Domain | CI Tests | Examples |
|--------|----------|----------|
| **Fact Extraction** | 2 tests | Basic extraction, allergy handling |
| **Intent Classification** | 1 test | Simple chat detection |
| **Preference Extraction** | 1 test | Basic preference detection |
| **Entity Disambiguation** | 2 tests | Existing vs new, relationship filtering |
| **API Endpoints** | 1 per major endpoint | Chat creation, message send |

**Total:** ~10-15 critical tests across all domains

**Everything else:** Run locally and in nightly builds

---

## ✅ Test Categories

### **1. Business Value Tests (High Priority)**

Test real business scenarios with real infrastructure:

```python
@pytest.mark.asyncio
async def test_colleague_creates_person_record(db, test_user):
    """
    Business case: "My colleague Leo got promoted"
    Expected: Leo should be created as Person with role=colleague
    """
    service = FactAndEntityExtractionService()
    
    result = await service.extract_and_store(
        input_data=ExtractionInput(
            user_message="My colleague Leo just got promoted to COO",
            user_id=test_user.id,
            entity_names=["Leo"]
        ),
        db=db,
        source_msg_id=str(uuid.uuid4())
    )
    
    assert len(result.entities_created) == 1
    # Verify business logic worked
```

---

### **2. Edge Cases**

```python
@pytest.mark.asyncio
async def test_empty_message_handling(db, test_user):
    """Edge case: Empty message should not crash"""
    result = await extract_entities(message="", user_id=test_user.id)
    assert result.entities_created == []
```

---

### **3. Error Cases**

```python
@pytest.mark.asyncio
async def test_invalid_user_id_returns_proper_error(db):
    """Error case: Invalid user should raise ValueError"""
    with pytest.raises(ValueError, match="User not found"):
        await extract_entities(message="test", user_id="invalid-id")
```

---

## 🔧 Test Structure (AAA Pattern)

```python
@pytest.mark.asyncio
async def test_feature_name_does_something(db, test_user):
    """
    Clear description of what this test verifies.
    Business case or edge case being tested.
    """
    # ARRANGE: Set up test data
    input_data = create_test_input()
    
    # ACT: Execute the function
    result = await function_under_test(input_data)
    
    # ASSERT: Verify expected outcome
    assert result.success == True
    assert result.value == expected_value
```

---

## 🚀 Quick Reference

### **Before Writing Tests:**
1. Check if similar tests exist
2. Read `docs/plans/plan_{feature}_v{version}.md` for test scenarios
3. Identify 1-2 critical tests for CI

### **While Writing Tests:**
1. Use real infrastructure (DB, Redis)
2. Write comprehensive scenarios
3. Mark CI-critical tests with `@pytest.mark.ci_critical`
4. Mark expensive LLM tests with `skipif(CI)`

### **After Writing Tests:**
1. Update container: `docker compose cp backend/...`
2. Execute in Docker: `docker compose exec backend pytest ... -vv`
3. Watch terminal output
4. Verify tests fail (TDD Red phase)

### **After Implementation:**
1. Update container: `docker compose cp backend/...`
2. Execute in Docker: `docker compose exec backend pytest ... -vv`
3. Watch terminal output
4. Verify tests pass (TDD Green phase)

---

## 📚 Related Documentation

- **Workflow Rules:** `.cursor/rules/00-workflow.mdc` - Complete TDD workflow
- **Development SOP:** `.cursor/rules/development-sop.mdc` - Testing requirements
- **Common Mistakes:** `.cursor/rules/35-implementation-common-mistakes.mdc` - Test marking examples
- **Architecture:** `docs/Documentation/SWISPER_ARCHITECTURE.md`

---

## ❓ Questions?

**"What tests should run in CI?"**
→ Only 1-2 golden path tests per domain with `@pytest.mark.ci_critical`

**"How do I run tests?"**
→ Update container, then `docker compose exec backend pytest <file> -vv`

**"Should I use real LLM or mock?"**
→ Use real LLM but mark with `skipif(CI)` - run locally, skip in CI

**"How do I mark tests?"**
→ See `.cursor/rules/35-implementation-common-mistakes.mdc` for examples

---

**Remember:** Comprehensive tests locally + Minimal CI = Best of both worlds! 🎯
