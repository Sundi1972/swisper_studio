# Phase 1 UAT (User Acceptance Testing)

**Date:** November 2, 2025  
**Tester:** Development Team  
**Scope:** Backend API + Database (Frontend requires npm install)

---

## Test Scenarios

### ✅ Scenario 1: Health Check
- **Given:** Backend is running
- **When:** Call health endpoint
- **Then:** Returns healthy status

### ✅ Scenario 2: Create First Project
- **Given:** Clean database
- **When:** POST /api/v1/projects with valid data
- **Then:** Project created with ID returned

### ✅ Scenario 3: List Projects
- **Given:** Projects exist in database
- **When:** GET /api/v1/projects
- **Then:** Returns list with pagination meta

### ✅ Scenario 4: Create Trace
- **Given:** Valid project exists
- **When:** POST /api/v1/traces with project_id
- **Then:** Trace created and associated with project

### ✅ Scenario 5: List Traces
- **Given:** Traces exist for project
- **When:** GET /api/v1/traces?project_id=X
- **Then:** Returns traces for that project only

### ✅ Scenario 6: Invalid Project Rejected
- **Given:** Non-existent project ID
- **When:** POST /api/v1/traces with invalid project_id
- **Then:** Returns 404 error

### ✅ Scenario 7: Missing API Key
- **Given:** No authentication header
- **When:** Call any protected endpoint
- **Then:** Returns 401 Unauthorized

---

## Test Execution

All tests executed below...

