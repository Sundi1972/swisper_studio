# Swisper SAP Implementation Guide

**Version:** v1.1  
**Last Updated:** 2025-11-03  
**Last Updated By:** heiko  
**Status:** Active - Ready for Implementation

---

## Changelog

### v1.1 - 2025-11-03
- Added complete model options (18 Kvant models)
- Added architecture decisions from Phase 4 implementation
- Documented dynamic vs static model options approach
- Added reference to mock SAP implementation
- Updated acceptance criteria
- Added notes on browser accessibility (localhost vs Docker hostnames)

### v1.0 - 2025-11-03
- Initial TODO created

---

## Purpose

This document is the **authoritative implementation guide** for SAP (Swisper Admin Protocol) in the Swisper backend.

**Context:** 
- SwisperStudio Phase 4 complete - using mock SAP for testing
- All architectural decisions documented here
- Reference implementation: `backend/app/api/routes/mock_sap.py`
- This is the **contract** between SwisperStudio and Swisper

---

## Reference Documents

- **SAP Specification**: `docs/specs/spec_sap_v1.md` - Complete API specification
- **Swisper Config Analysis**: `docs/analysis/phase4_config_analysis.md` - Current config structure
- **Mock Implementation**: `backend/app/api/routes/mock_sap.py` - Reference implementation

---

## Required Implementation

### **1. SAP Endpoints (5 endpoints minimum)**

```python
# backend/app/api/routes/admin/config.py

GET  /api/admin/config/schema
     → Returns schema for all config tables (llm_node_config, etc.)

GET  /api/admin/config/llm_node_config
     → List all LLM node configurations

GET  /api/admin/config/llm_node_config/{node_name}
     → Get single LLM node configuration

PUT  /api/admin/config/llm_node_config/{node_name}
     → Update LLM node configuration

POST /api/admin/config/llm_node_config/{node_name}/test-live (optional)
     → Update config with hot-reload (cache update)
```

### **2. Cache Hot-Reload (optional but recommended)**

```python
# backend/app/core/config_manager.py

class ConfigManager:
    """Manages config with cache and hot-reload"""
    
    def get_config(self, table: str, key: str):
        """Cache-first read"""
        # Try cache, fallback to DB
    
    def update_cache(self, table: str, key: str, value: dict):
        """Update cache on config change (hot-reload)"""
```

### **3. Schema Introspection**

The schema endpoint must return accurate field types, constraints, and options:
- Field types: string, number, boolean, select
- Validation rules: min, max, required, options
- UI hints: description, placeholder, help_text

---

## Acceptance Criteria

- ✅ All SAP endpoints implemented and tested
- ✅ Schema endpoint returns correct schema for llm_node_config table
- ✅ CRUD operations work (list, get, update)
- ✅ Validation enforced (temperature 0.0-2.0, etc.)
- ✅ Hot-reload cache updates on config change (optional)
- ✅ 10+ tests passing

---

## Estimated Effort

**Total:** 5-7 days

- Schema endpoint: 1 day
- CRUD endpoints: 2 days
- Cache manager: 1-2 days
- Tests: 1-2 days

---

## Notes

- SwisperStudio is currently using mock SAP at: `http://backend:8000/api/v1/mock-swisper`
- When Swisper SAP is ready, update project environments to point to real Swisper URLs
- Existing migration supports this - just update environment.swisper_url

---

**Status:** Pending Swisper team implementation

