# Swisper SAP Implementation Guide - Complete

**Version:** v1.1  
**Last Updated:** 2025-11-03  
**Last Updated By:** heiko  
**Status:** Active - Authoritative Implementation Guide

**This is the complete implementation guide for Swisper backend team to implement SAP v1.1**

---

## Changelog

### v1.1 - 2025-11-03
- Complete implementation guide created
- Added step-by-step implementation instructions
- Included code examples for all endpoints
- Documented all 18 Kvant models
- Added validation logic
- Added hot-reload cache implementation
- Included testing strategy
- Added troubleshooting guide

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Implementation Steps](#3-implementation-steps)
4. [Endpoint Implementation](#4-endpoint-implementation)
5. [Model Configuration](#5-model-configuration)
6. [Cache & Hot-Reload](#6-cache--hot-reload)
7. [Testing](#7-testing)
8. [Deployment](#8-deployment)

---

## 1. Overview

### 1.1 What is SAP?

SAP (Swisper Admin Protocol) is a REST API that enables SwisperStudio to:
- Discover Swisper's configuration schema automatically
- Display config in auto-generated UI
- Update config without code deployments
- Support multi-environment workflows (dev/staging/production)

### 1.2 Architecture

```
┌─────────────────────────────────────────┐
│ SwisperStudio Frontend (Browser)       │
│ http://localhost:3000                   │
└─────────────────────────────────────────┘
           ↓ Fetches schema & records
┌─────────────────────────────────────────┐
│ Swisper SAP Endpoints                   │
│ http://swisper:8000/api/admin/config/   │
│                                         │
│ - GET /schema                           │
│ - GET /llm_node_config                  │
│ - PUT /llm_node_config/{node_name}      │
└─────────────────────────────────────────┘
           ↓ Reads/Writes
┌─────────────────────────────────────────┐
│ PostgreSQL Database                     │
│ - llm_node_configuration table          │
└─────────────────────────────────────────┘
```

### 1.3 Estimated Effort

- **Minimum (Schema + GET endpoints):** 1 day
- **Full implementation (+ PUT, validation, cache):** 3-5 days
- **With tests:** 5-7 days

---

## 2. Prerequisites

### 2.1 Existing Swisper Setup

**Assumes you already have:**
- ✅ PostgreSQL database with `llm_node_configuration` table
- ✅ FastAPI application
- ✅ SQLModel/SQLAlchemy models
- ✅ Dependency injection (`get_session`)

### 2.2 Required Packages

```bash
# Should already be installed
pip install fastapi
pip install sqlmodel
pip install pydantic
```

### 2.3 Database Schema

**Your existing table (from screenshot):**
```sql
CREATE TABLE llm_node_configuration (
    node_name VARCHAR(100) PRIMARY KEY,
    default_temperature FLOAT8,
    default_max_tokens INT4,
    default_log_reasoning BOOL,
    default_model VARCHAR(255),
    azure_model VARCHAR(255),
    azure_temperature FLOAT8,
    azure_max_tokens INT4,
    langsmith_tracing BOOL,
    description TEXT
);
```

---

## 3. Implementation Steps

### Step 1: Create Admin Routes Module

**File:** `backend/app/api/routes/admin/__init__.py`

```python
"""Admin API routes"""
from fastapi import APIRouter

from app.api.routes.admin import config

router = APIRouter()
router.include_router(config.router, prefix="/config", tags=["admin"])
```

**File:** `backend/app/api/routes/admin/config.py`

```python
"""SAP v1.1 - Config Management Endpoints"""
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from app.core.db import get_session
from app.models import LLMNodeConfiguration

router = APIRouter()

# Continue below...
```

### Step 2: Implement Schema Endpoint

**THE MOST IMPORTANT ENDPOINT**

```python
@router.get("/schema")
async def get_config_schema():
    """
    SAP v1.1 - Return schema for all config tables.
    
    This is the critical endpoint - SwisperStudio uses this to auto-generate UI.
    MUST include all 18 Kvant models in default_model.options!
    """
    return {
        "version": "1.1",
        "tables": [
            {
                "name": "llm_node_config",
                "description": "LLM configuration per LangGraph node",
                "primary_key": "node_name",
                "fields": [
                    {
                        "name": "node_name",
                        "type": "string",
                        "required": True,
                        "immutable": True,
                        "max_length": 100,
                        "description": "LangGraph node identifier",
                        "placeholder": "e.g., global_planner"
                    },
                    {
                        "name": "default_model",
                        "type": "select",
                        "required": True,
                        "options": [
                            # ✅ ALL 18 Kvant models (CRITICAL!)
                            "inference-llama4-maverick",
                            "inference-llama4-scout-17b",
                            "inference-llama33-70b",
                            "inference-apertus-8b",
                            "inference-apertus-70b",
                            "inference-deepseekr1-70b",
                            "inference-deepseekr1-670b",
                            "inference-qwen3-8b",
                            "inference-qwq-32b",
                            "inference-qwq25-vl-72b",
                            "inference-gemma-12b-it",
                            "inference-gpt-oss-120b",
                            "inference-granite-33-8b",
                            "inference-granite-vision-2b",
                            "inference-mistral-v03-7b",
                            "inference-bge-m3",
                            "infer-bge-reranker",
                            "infer-whisper-3lt"
                        ],
                        "default": "inference-llama4-maverick",
                        "description": "Default LLM model for this node (Kvant MaaS)",
                        "help_text": "See https://documentation.kvant.cloud/products/maas/supported_models/"
                    },
                    {
                        "name": "default_temperature",
                        "type": "number",
                        "required": False,
                        "min": 0.0,
                        "max": 2.0,
                        "step": 0.1,  # ✅ CRITICAL for correct UI increments!
                        "default": 0.7,
                        "description": "Sampling temperature (0 = deterministic, 2 = creative)"
                    },
                    {
                        "name": "default_max_tokens",
                        "type": "number",
                        "required": False,
                        "min": 100,
                        "max": 32000,
                        "step": 100,
                        "default": 10000,
                        "description": "Maximum tokens in response"
                    },
                    {
                        "name": "langsmith_tracing",
                        "type": "boolean",
                        "required": False,
                        "default": True,
                        "description": "Enable LangSmith tracing for this node"
                    },
                    {
                        "name": "azure_model",
                        "type": "select",
                        "required": False,
                        "options": [
                            "gpt-4-turbo",
                            "gpt-4",
                            "gpt-4-32k",
                            "gpt-35-turbo"
                        ],
                        "default": None,
                        "description": "Azure-specific model override (NULL uses default)"
                    }
                ]
            }
        ]
    }
```

### Step 3: Implement List Endpoint

```python
@router.get("/llm_node_config")
async def list_llm_node_configs(
    session: Session = Depends(get_session)
):
    """
    SAP v1.1 - List all LLM node configurations.
    
    Returns all records in the llm_node_configuration table.
    """
    statement = select(LLMNodeConfiguration)
    results = session.exec(statement).all()
    
    return {
        "table": "llm_node_config",
        "records": [
            {
                "node_name": r.node_name,
                "default_model": r.default_model,
                "default_temperature": r.default_temperature,
                "default_max_tokens": r.default_max_tokens,
                "langsmith_tracing": r.langsmith_tracing,
                "azure_model": r.azure_model,
                # Include all fields from your table
            }
            for r in results
        ],
        "count": len(results)
    }
```

### Step 4: Implement Get Single Record

```python
@router.get("/llm_node_config/{node_name}")
async def get_llm_node_config(
    node_name: str,
    session: Session = Depends(get_session)
):
    """
    SAP v1.1 - Get single LLM node configuration.
    """
    config = session.get(LLMNodeConfiguration, node_name)
    
    if not config:
        raise HTTPException(status_code=404, detail=f"Config not found: {node_name}")
    
    return config.dict()
```

### Step 5: Implement Update Endpoint

```python
class LLMConfigUpdate(BaseModel):
    """Request model for updating LLM config"""
    default_model: str | None = Field(None)
    default_temperature: float | None = Field(None, ge=0.0, le=2.0)
    default_max_tokens: int | None = Field(None, ge=100, le=32000)
    langsmith_tracing: bool | None = None
    azure_model: str | None = None


@router.put("/llm_node_config/{node_name}")
async def update_llm_node_config(
    node_name: str,
    data: LLMConfigUpdate,
    session: Session = Depends(get_session)
):
    """
    SAP v1.1 - Update LLM node configuration.
    
    Validates input, updates database, and triggers cache hot-reload.
    """
    config = session.get(LLMNodeConfiguration, node_name)
    if not config:
        raise HTTPException(status_code=404, detail=f"Config not found: {node_name}")
    
    # Update only provided fields
    update_data = data.dict(exclude_unset=True)
    
    # Additional validation (beyond Pydantic)
    if "default_model" in update_data:
        valid_models = [
            "inference-llama4-maverick", "inference-llama4-scout-17b",
            "inference-llama33-70b", "inference-apertus-8b", "inference-apertus-70b",
            "inference-deepseekr1-70b", "inference-deepseekr1-670b",
            "inference-qwen3-8b", "inference-qwq-32b", "inference-qwq25-vl-72b",
            "inference-gemma-12b-it", "inference-gpt-oss-120b",
            "inference-granite-33-8b", "inference-granite-vision-2b",
            "inference-mistral-v03-7b", "inference-bge-m3",
            "infer-bge-reranker", "infer-whisper-3lt"
        ]
        if update_data["default_model"] not in valid_models:
            raise HTTPException(400, f"Invalid model. Must be one of: {valid_models}")
    
    # Update config
    for key, value in update_data.items():
        setattr(config, key, value)
    
    session.add(config)
    session.commit()
    session.refresh(config)
    
    # ✅ Hot-reload cache (optional but recommended)
    # config_manager.update_cache("llm_node_config", node_name, config.dict())
    
    return config.dict()
```

---

## 4. Endpoint Implementation

### 4.1 Required Endpoints (Minimum SAP Compliance)

| Endpoint | Status | Estimated Time |
|----------|--------|----------------|
| `GET /schema` | ✅ Required | 2 hours |
| `GET /llm_node_config` | ✅ Required | 1 hour |
| `GET /llm_node_config/{id}` | ✅ Required | 30 min |
| `PUT /llm_node_config/{id}` | ✅ Required | 2 hours |
| **Total** | **4 endpoints** | **5.5 hours** |

### 4.2 Optional Endpoints (Future)

| Endpoint | Status | Use Case |
|----------|--------|----------|
| `POST /llm_node_config` | Optional | Create new node configs |
| `DELETE /llm_node_config/{id}` | Optional | Remove node configs |
| `POST /llm_node_config/{id}/test-live` | Optional | Hot-reload without commit |
| `POST /llm_node_config/deploy` | Optional | Git commit (if using YAML backup) |

---

## 5. Model Configuration

### 5.1 Kvant Models (18 Total)

**Source:** https://documentation.kvant.cloud/products/maas/supported_models/

**Complete list for `default_model.options`:**

```python
KVANT_MODELS = [
    # Chat & Multimodal
    "inference-llama4-maverick",      # Default recommendation
    "inference-llama4-scout-17b",     
    "inference-llama33-70b",          
    
    # Swiss AI Models
    "inference-apertus-8b",           # Multilingual
    "inference-apertus-70b",          
    
    # Reasoning Models
    "inference-deepseekr1-70b",       
    "inference-deepseekr1-670b",      # Highest capability
    "inference-qwen3-8b",             
    "inference-qwq-32b",              
    
    # Multimodal
    "inference-qwq25-vl-72b",         # Vision-language
    "inference-gemma-12b-it",         
    "inference-granite-vision-2b",    
    
    # General Chat
    "inference-gpt-oss-120b",         
    "inference-granite-33-8b",        
    "inference-mistral-v03-7b",       
    
    # Specialized
    "inference-bge-m3",               # Embeddings
    "infer-bge-reranker",             # Reranker
    "infer-whisper-3lt"               # Speech-to-text
]
```

**Update Frequency:** Check Kvant docs quarterly for new models

### 5.2 Azure Models (Customer-Specific)

**For SAP v1.1:** Static list of common models
```python
AZURE_MODELS = [
    "gpt-4-turbo",
    "gpt-4",
    "gpt-4-32k",
    "gpt-35-turbo"
]
```

**For SAP v1.2 (Future):** Dynamic from Azure API
```python
async def get_azure_deployments():
    """Fetch customer's Azure deployments"""
    response = await httpx.get(
        f"{settings.AZURE_ENDPOINT}/openai/deployments",
        params={"api-version": "2024-10-21"},
        headers={"api-key": settings.AZURE_API_KEY}
    )
    return [d["model"] for d in response.json()["data"]]
```

---

## 6. Cache & Hot-Reload

### 6.1 Why Hot-Reload?

**Without hot-reload:**
```
Update config → Restart Swisper → 30+ seconds downtime
```

**With hot-reload:**
```
Update config → Update cache → Immediate effect (< 1 second)
```

### 6.2 Implementation

**File:** `backend/app/core/config_manager.py`

```python
"""Configuration manager with hot-reload support"""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages configuration with in-memory cache and hot-reload"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def get_config(self, table: str, key: str) -> Dict[str, Any] | None:
        """
        Get config from cache (cache-first strategy).
        
        Returns None if not in cache (caller should fetch from DB).
        """
        cache_key = f"{table}:{key}"
        return self._cache.get(cache_key)
    
    def update_cache(self, table: str, key: str, value: Dict[str, Any]):
        """
        Update cache (hot-reload).
        
        Called after database update to make changes immediate.
        """
        cache_key = f"{table}:{key}"
        self._cache[cache_key] = value
        logger.info(f"Config cache updated: {cache_key}")
    
    def flush_cache(self, table: str | None = None):
        """Flush cache (all or specific table)"""
        if table:
            keys_to_remove = [k for k in self._cache.keys() if k.startswith(f"{table}:")]
            for key in keys_to_remove:
                del self._cache[key]
            logger.info(f"Flushed cache for table: {table}")
        else:
            self._cache.clear()
            logger.info("Flushed entire config cache")


# Global instance
config_manager = ConfigManager()
```

**Usage in your nodes:**
```python
# In global_planner_node.py
from app.core.config_manager import config_manager
from app.models import LLMNodeConfiguration

async def global_planner_node(state):
    # Try cache first
    config_dict = config_manager.get_config("llm_node_config", "global_planner")
    
    if not config_dict:
        # Cache miss - load from DB
        config = db.query(LLMNodeConfiguration).get("global_planner")
        config_dict = config.dict()
        config_manager.update_cache("llm_node_config", "global_planner", config_dict)
    
    # Use config
    llm = ChatOpenAI(
        model=config_dict["default_model"],
        temperature=config_dict["default_temperature"],
        max_tokens=config_dict["default_max_tokens"]
    )
    
    # ... rest of node logic
```

**Update endpoint triggers cache update:**
```python
@router.put("/llm_node_config/{node_name}")
async def update_config(node_name: str, data: LLMConfigUpdate, session: Session):
    # ... update database ...
    
    # ✅ Hot-reload cache
    config_manager.update_cache("llm_node_config", node_name, config.dict())
    
    return config.dict()
```

---

## 7. Testing

### 7.1 Test Plan (10 tests minimum)

```python
# tests/api/admin/test_config.py

@pytest.mark.asyncio
async def test_schema_endpoint():
    """Test schema endpoint returns valid schema"""
    response = await client.get("/api/admin/config/schema")
    assert response.status_code == 200
    schema = response.json()
    assert schema["version"] == "1.1"
    assert len(schema["tables"]) >= 1

@pytest.mark.asyncio
async def test_schema_has_18_kvant_models():
    """Test schema includes all 18 Kvant models"""
    response = await client.get("/api/admin/config/schema")
    schema = response.json()
    
    model_field = next(
        f for f in schema["tables"][0]["fields"] 
        if f["name"] == "default_model"
    )
    
    assert len(model_field["options"]) == 18
    assert "inference-llama4-maverick" in model_field["options"]
    assert "inference-apertus-8b" in model_field["options"]

@pytest.mark.asyncio
async def test_list_configs():
    """Test list all configs"""
    response = await client.get("/api/admin/config/llm_node_config")
    assert response.status_code == 200
    data = response.json()
    assert "records" in data
    assert "count" in data

@pytest.mark.asyncio
async def test_get_single_config():
    """Test get single config"""
    response = await client.get("/api/admin/config/llm_node_config/global_planner")
    assert response.status_code == 200
    config = response.json()
    assert config["node_name"] == "global_planner"

@pytest.mark.asyncio
async def test_update_config():
    """Test update config"""
    response = await client.put(
        "/api/admin/config/llm_node_config/global_planner",
        json={"default_temperature": 0.5}
    )
    assert response.status_code == 200
    config = response.json()
    assert config["default_temperature"] == 0.5

@pytest.mark.asyncio
async def test_update_validation_temperature_too_high():
    """Test temperature validation (max 2.0)"""
    response = await client.put(
        "/api/admin/config/llm_node_config/global_planner",
        json={"default_temperature": 3.0}
    )
    assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_update_validation_invalid_model():
    """Test model validation"""
    response = await client.put(
        "/api/admin/config/llm_node_config/global_planner",
        json={"default_model": "invalid-model"}
    )
    assert response.status_code == 400  # Invalid model

@pytest.mark.asyncio
async def test_update_nonexistent_config():
    """Test update non-existent config returns 404"""
    response = await client.put(
        "/api/admin/config/llm_node_config/nonexistent",
        json={"default_temperature": 0.5}
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_hot_reload_cache():
    """Test cache updates on config change"""
    # Update config
    await client.put(
        "/api/admin/config/llm_node_config/global_planner",
        json={"default_temperature": 0.5}
    )
    
    # Verify cache updated
    cached = config_manager.get_config("llm_node_config", "global_planner")
    assert cached["default_temperature"] == 0.5

@pytest.mark.asyncio
async def test_config_used_by_node():
    """Integration test: Node uses updated config"""
    # Update config
    await client.put(
        "/api/admin/config/llm_node_config/global_planner",
        json={"default_temperature": 0.5}
    )
    
    # Run node
    result = await run_global_planner_node(test_state)
    
    # Verify node used new config
    # (check LLM was called with temperature=0.5)
```

---

## 8. Deployment Checklist

### 8.1 Pre-Deployment

- [ ] All 4 SAP endpoints implemented
- [ ] Schema includes 18 Kvant models
- [ ] Temperature field has `step: 0.1`
- [ ] 10+ tests passing
- [ ] CORS configured for SwisperStudio
- [ ] Cache manager implemented
- [ ] Hot-reload working

### 8.2 Integration with SwisperStudio

**Update SwisperStudio environment:**
```sql
-- Point dev environment to real Swisper
UPDATE project_environment 
SET swisper_url = 'http://swisper.dev.customer.com'
WHERE env_type = 'dev';
```

**Test in SwisperStudio:**
1. Navigate to Configuration page
2. Select LLM Node Config table
3. Verify schema loads
4. Verify 18 Kvant models in dropdown
5. Edit config and save
6. Verify update persists
7. Verify change takes effect in Swisper (next LLM call uses new config)

---

## 9. Acceptance Criteria

**SAP v1.1 is complete when:**

- ✅ `GET /schema` returns valid schema with 18 Kvant models
- ✅ `GET /llm_node_config` lists all configs
- ✅ `GET /llm_node_config/{id}` returns single config
- ✅ `PUT /llm_node_config/{id}` updates config
- ✅ Validation enforces constraints (temperature 0-2, valid models)
- ✅ 404 for non-existent configs
- ✅ 400/422 for validation errors
- ✅ Accessible from browser (CORS configured)
- ✅ 10+ tests passing
- ✅ Config changes take effect immediately (hot-reload)
- ✅ SwisperStudio can manage configs via UI

---

## 10. Reference

- **SAP Specification:** `docs/specs/spec_sap_v1_comprehensive.md`
- **Mock Implementation:** `backend/app/api/routes/mock_sap.py`
- **Kvant Models:** https://documentation.kvant.cloud/products/maas/supported_models/
- **Azure API:** https://learn.microsoft.com/en-us/azure/ai-services/openai/reference

---

**Estimated Total Effort:** 5-7 days (including tests and cache implementation)

**Next Steps:**
1. Review this document with Swisper team
2. Schedule implementation sprint
3. Use mock SAP as reference
4. Integrate and test with SwisperStudio

---

**Document Owner:** heiko  
**Last Review:** 2025-11-03  
**Status:** Ready for Swisper team implementation

