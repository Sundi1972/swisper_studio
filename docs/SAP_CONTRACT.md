# SAP (Swisper Admin Protocol) - Contract Documents

**Version:** v1.1  
**Last Updated:** 2025-11-03  
**Last Updated By:** heiko  
**Status:** Active

**This document is the index for all SAP-related documentation.**

---

## 📋 Document Overview

SAP is the **critical contract** between two systems:
- **Swisper** (backend server) - Exposes configuration
- **SwisperStudio** (admin UI) - Manages configuration

**All architectural decisions, specifications, and implementation details are documented here.**

---

## 📚 Core Documents

### 1. **SAP Specification v1.1** (Authoritative Contract)

**File:** `docs/specs/spec_sap_v1_comprehensive.md`

**Purpose:** The complete API specification - what SAP is and how it works

**Contains:**
- Complete schema format
- All 18 Kvant models
- Field types and validation rules
- API endpoint contracts
- Architecture decisions
- Examples and troubleshooting

**Audience:** Both teams (contract document)

**Last Updated:** 2025-11-03 by heiko

---

### 2. **Swisper Implementation Guide** (For Swisper Team)

**File:** `docs/architecture/swisper_sap_implementation_guide.md`

**Purpose:** Step-by-step guide for Swisper team to implement SAP

**Contains:**
- Implementation steps (5-7 days)
- Code examples for all endpoints
- Model configuration (18 Kvant models)
- Hot-reload cache implementation
- Test plan (10+ tests)
- Deployment checklist

**Audience:** Swisper backend team

**Last Updated:** 2025-11-03 by heiko

---

### 3. **Mock SAP Reference Implementation**

**File:** `backend/app/api/routes/mock_sap.py`

**Purpose:** Working reference implementation for testing

**Contains:**
- All 4 SAP endpoints implemented
- 18 Kvant models configured
- Validation logic
- 88 tests passing against this implementation

**Audience:** Both teams (reference code)

**Live at:** http://localhost:8001/api/v1/mock-swisper/api/admin/config/schema

---

### 4. **Phase 4 Analysis** (Background Research)

**File:** `docs/analysis/phase4_config_analysis.md`

**Purpose:** Research and analysis that led to SAP design

**Contains:**
- Current Swisper config structure analysis
- Langfuse UI patterns studied
- SAP design approach
- Implementation strategy

**Audience:** Architects, historical reference

---

### 5. **Phase 4 Implementation Plan**

**File:** `docs/plans/plan_phase4_config_v1.md`

**Purpose:** How Phase 4 was implemented in SwisperStudio

**Contains:**
- Sub-phases breakdown
- Files created/modified
- Testing approach
- Success criteria

**Audience:** SwisperStudio team, historical reference

---

## 🔑 Key Architectural Decisions

### Decision 1: Static Model Options (v1.1)

**Question:** How to handle 18 Kvant models + dynamic Azure deployments?

**Decision:** Static in schema for v1.1, dynamic endpoint for v1.2

**Rationale:**
- Kvant models change infrequently (quarterly)
- Simpler implementation
- Azure will use dynamic endpoint in future

**Documented in:** `spec_sap_v1_comprehensive.md` § 2.1

---

### Decision 2: Environment-First Architecture

**Question:** How to handle dev/staging/production configs?

**Decision:** 
- Projects have 3 environments
- Config versions managed in SwisperStudio
- Deploy versions to specific environments

**Rationale:**
- Clear separation of environments
- Fast iteration (no Git/YAML)
- Easy rollback

**Documented in:** `plan_phase4_config_v1.md` § Architecture

---

### Decision 3: Browser-Accessible SAP

**Question:** Should SwisperStudio proxy SAP calls or call directly?

**Decision:** Frontend calls Swisper SAP directly (for schema/records)

**Rationale:**
- Reduces latency
- Simpler architecture
- Schema rarely changes (can cache)

**Impact:** Swisper must be accessible from browser (CORS configured)

**Documented in:** `spec_sap_v1_comprehensive.md` § 2.3

---

### Decision 4: Number Field Step

**Question:** How to specify decimal increments (0.1 for temperature)?

**Decision:** Add `step` property to schema

**Example:**
```json
{
  "name": "default_temperature",
  "type": "number",
  "step": 0.1  // ✅ Up/down arrows increment by 0.1
}
```

**Documented in:** `spec_sap_v1_comprehensive.md` § 2.2

---

## 🎯 Contract Compliance

### For Swisper (Server)

**MUST implement:**
- ✅ 4 SAP endpoints (schema, list, get, update)
- ✅ Include 18 Kvant models in schema
- ✅ Set `step: 0.1` for temperature field
- ✅ Validate all fields (min/max, options, required)
- ✅ Return proper HTTP status codes
- ✅ Accessible from browser (CORS)
- ✅ 10+ tests passing

**When complete:** SAP v1.1 certified ✅

---

### For SwisperStudio (Client)

**MUST support:**
- ✅ Fetch schema from Swisper
- ✅ Auto-generate forms from schema
- ✅ Render select fields with all 18 models
- ✅ Use `step` property for number inputs
- ✅ Display validation errors
- ✅ Handle 404/422/500 errors gracefully

**Status:** Complete ✅ (Phase 4 delivered)

---

## 📊 Implementation Status

| Component | Status | Version | Tests |
|-----------|--------|---------|-------|
| **SAP Specification** | ✅ Complete | v1.1 | N/A |
| **SwisperStudio** | ✅ Complete | Phase 4 | 88/88 passing |
| **Mock SAP** | ✅ Complete | v1.1 | 8/8 passing |
| **Swisper Backend** | ⏸️ Pending | N/A | To be implemented |

---

## 🔄 Version History

| Version | Date | Changes | Breaking |
|---------|------|---------|----------|
| v1.1 | 2025-11-03 | Added 18 Kvant models, `step` property, comprehensive docs | No |
| v1.0 | 2025-11-02 | Initial specification | N/A |

---

## 📞 Contact

**Document Owner:** heiko  
**SwisperStudio Team:** Development complete  
**Swisper Team:** Ready for implementation

**Questions?**
- Review `spec_sap_v1_comprehensive.md` for detailed specification
- Review `swisper_sap_implementation_guide.md` for implementation steps
- Check `backend/app/api/routes/mock_sap.py` for reference code

---

**This is the single source of truth for SAP contract between systems.**

**All decisions must be documented here to keep systems in sync.**

