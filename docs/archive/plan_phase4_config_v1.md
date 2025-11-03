# Phase 4: Configuration Management - Implementation Plan v1.0

**Version:** v1.0  
**Last Updated:** 2025-11-02  
**Last Updated By:** AI Assistant  
**Status:** Active

---

## Changelog

### v1.0 - 2025-11-02
- Initial implementation plan for Phase 4
- Defined sub-phases (4a MVP, 4b Full)
- Listed files to create/modify
- Provided detailed implementation steps
- Defined success criteria

---

## Executive Summary

**Goal:** Build data-driven admin UI for managing Swisper configuration without code changes.

**Strategy:** Implement in 2 sub-phases:
- **Phase 4a (MVP)**: Single table (`llm_node_config`), Test Live mode
- **Phase 4b (Full)**: Multiple tables, Deploy to Prod mode, audit history

**Estimated Duration:**
- Phase 4a: 7-10 days
- Phase 4b: 5-7 days
- **Total**: 12-17 days

**Reference Documents:**
- Analysis: `docs/analysis/phase4_config_analysis.md`
- SAP Spec: `docs/specs/spec_sap_v1.md`

---

## Table of Contents

1. [Overview](#1-overview)
2. [Phase 4a: MVP](#2-phase-4a-mvp)
3. [Phase 4b: Full Implementation](#3-phase-4b-full-implementation)
4. [Success Criteria](#4-success-criteria)
5. [Risk Mitigation](#5-risk-mitigation)

---

## 1. Overview

### 1.1 Architecture

```
┌──────────────────────────────────────────────────────┐
│ SwisperStudio Frontend                               │
│                                                      │
│  ┌────────────────────────────────────────┐         │
│  │ Configuration UI                       │         │
│  │ - Table selector dropdown              │         │
│  │ - Auto-generated form (from schema)    │         │
│  │ - Diff viewer (before/after)           │         │
│  │ - [Test Live] [Deploy to Prod]         │         │
│  └────────────────────────────────────────┘         │
│                      ↓                               │
│  ┌────────────────────────────────────────┐         │
│  │ React Query Hooks                      │         │
│  │ - useConfigSchema()                    │         │
│  │ - useConfigData()                      │         │
│  │ - useConfigMutations()                 │         │
│  └────────────────────────────────────────┘         │
└──────────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────────┐
│ SwisperStudio Backend (Config Proxy)                 │
│                                                      │
│  ┌────────────────────────────────────────┐         │
│  │ API Routes (/api/v1/projects/...       │         │
│  │              /config)                  │         │
│  │ - GET /schema                          │         │
│  │ - GET /config/{table}                  │         │
│  │ - PUT /config/{table}/{id}             │         │
│  └────────────────────────────────────────┘         │
│                      ↓                               │
│  ┌────────────────────────────────────────┐         │
│  │ Config Service                         │         │
│  │ - Proxy to Swisper SAP endpoints       │         │
│  │ - Audit logging                        │         │
│  │ - Config history tracking              │         │
│  └────────────────────────────────────────┘         │
└──────────────────────────────────────────────────────┘
                      ↓ (HTTP)
┌──────────────────────────────────────────────────────┐
│ Swisper Backend (SAP Implementation)                 │
│                                                      │
│  ┌────────────────────────────────────────┐         │
│  │ Admin API Routes                       │         │
│  │ (/api/admin/config/...)                │         │
│  │ - GET /schema                          │         │
│  │ - GET /{table}                         │         │
│  │ - PUT /{table}/{id}                    │         │
│  │ - POST /{table}/deploy                 │         │
│  └────────────────────────────────────────┘         │
│                      ↓                               │
│  ┌────────────────────────────────────────┐         │
│  │ Config Manager                         │         │
│  │ - In-memory cache                      │         │
│  │ - Database queries                     │         │
│  │ - Hot-reload on update                 │         │
│  │ - YAML generation                      │         │
│  └────────────────────────────────────────┘         │
│                      ↓                               │
│  ┌────────────────────────────────────────┐         │
│  │ PostgreSQL (Config Tables)             │         │
│  │ - llm_node_configuration               │         │
│  │ - fact_preloading_config (future)      │         │
│  └────────────────────────────────────────┘         │
└──────────────────────────────────────────────────────┘
```

### 1.2 File Structure

**SwisperStudio Backend:**
```
backend/app/
├── api/routes/
│   └── config.py (NEW) - Config proxy endpoints
├── api/services/
│   └── config_service.py (NEW) - Config management logic
├── models/
│   └── config_history.py (NEW) - Audit trail model
└── tests/api/
    └── test_config.py (NEW) - Config API tests
```

**SwisperStudio Frontend:**
```
frontend/src/features/config/
├── components/
│   ├── config-page.tsx (MODIFY) - Replace placeholder
│   ├── config-table-selector.tsx (NEW) - Dropdown for tables
│   ├── data-driven-form.tsx (NEW) - Auto-generated forms
│   ├── field-renderer.tsx (NEW) - Dynamic field components
│   ├── config-diff-viewer.tsx (NEW) - Before/after comparison
│   └── config-history.tsx (NEW) - Audit log viewer
├── hooks/
│   ├── use-config-schema.ts (NEW) - Fetch schema
│   ├── use-config-data.ts (NEW) - Fetch/update config
│   └── use-config-history.ts (NEW) - Fetch history
└── types.ts (NEW) - TypeScript interfaces
```

**Swisper Backend (Reference - NOT in this repo):**
```
backend/app/api/routes/admin/
├── __init__.py (NEW)
└── config.py (NEW) - SAP endpoints

backend/app/core/
└── config_manager.py (NEW) - Hot-reload config manager
```

---

## 2. Phase 4a: MVP

**Goal:** Single table (`llm_node_config`), Test Live mode only, auto-generated UI

**Duration:** 7-10 days

### Sub-Phase 4a.1: Swisper Backend - SAP Endpoints (Days 1-3)

**Files to Create/Modify:**

#### 1. `backend/app/api/routes/admin/__init__.py` (NEW)
```python
"""Admin API routes"""
from fastapi import APIRouter

from app.api.routes.admin import config

router = APIRouter()
router.include_router(config.router, prefix="/config", tags=["admin"])
```

#### 2. `backend/app/api/routes/admin/config.py` (NEW)

**Purpose:** SAP-compliant endpoints for config management

**Endpoints:**
- `GET /api/admin/config/schema` - Return schema for llm_node_config
- `GET /api/admin/config/llm_node_config` - List all records
- `GET /api/admin/config/llm_node_config/{node_name}` - Get single record
- `PUT /api/admin/config/llm_node_config/{node_name}` - Update record
- `POST /api/admin/config/llm_node_config/{node_name}/test-live` - Test Live mode

**Implementation:**
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models import LLMNodeConfiguration
from app.core.db import get_session
from app.core.config_manager import config_manager
from typing import List, Dict, Any
from pydantic import BaseModel

router = APIRouter()

# Pydantic models
class ConfigSchemaField(BaseModel):
    name: str
    type: str
    required: bool
    description: str
    # Type-specific fields
    max_length: int | None = None
    min: float | None = None
    max: float | None = None
    step: float | None = None
    options: List[str] | None = None
    default: Any | None = None

class ConfigSchemaTable(BaseModel):
    name: str
    description: str
    primary_key: str
    fields: List[ConfigSchemaField]

class ConfigSchema(BaseModel):
    version: str
    tables: List[ConfigSchemaTable]

class LLMNodeConfigUpdate(BaseModel):
    default_model: str | None = None
    default_temperature: float | None = None
    default_max_tokens: int | None = None
    langsmith_tracing: bool | None = None

@router.get("/schema", response_model=ConfigSchema)
async def get_config_schema():
    """Return schema for all config tables (currently: llm_node_config)"""
    return {
        "version": "1.0",
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
                        "description": "LangGraph node identifier"
                    },
                    {
                        "name": "default_model",
                        "type": "select",
                        "required": True,
                        "options": [
                            "inference-llama4-maverick",
                            "gpt-4-turbo",
                            "gpt-4",
                            "claude-3-opus-20240229"
                        ],
                        "default": "inference-llama4-maverick",
                        "description": "Default LLM model for this node"
                    },
                    {
                        "name": "default_temperature",
                        "type": "number",
                        "required": False,
                        "min": 0.0,
                        "max": 2.0,
                        "step": 0.1,
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
                    }
                ]
            }
        ]
    }

@router.get("/llm_node_config")
async def list_llm_node_configs(
    session: Session = Depends(get_session)
):
    """List all LLM node configurations"""
    statement = select(LLMNodeConfiguration)
    results = session.exec(statement).all()
    return {
        "table": "llm_node_config",
        "records": [r.model_dump() for r in results],
        "count": len(results)
    }

@router.get("/llm_node_config/{node_name}")
async def get_llm_node_config(
    node_name: str,
    session: Session = Depends(get_session)
):
    """Get single LLM node configuration"""
    config = session.get(LLMNodeConfiguration, node_name)
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    return config.model_dump()

@router.put("/llm_node_config/{node_name}")
async def update_llm_node_config(
    node_name: str,
    data: LLMNodeConfigUpdate,
    session: Session = Depends(get_session)
):
    """Update LLM node configuration (standard update - no hot-reload)"""
    config = session.get(LLMNodeConfiguration, node_name)
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    
    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)
    
    session.add(config)
    session.commit()
    session.refresh(config)
    
    return config.model_dump()

@router.post("/llm_node_config/{node_name}/test-live")
async def test_live_llm_node_config(
    node_name: str,
    data: LLMNodeConfigUpdate,
    session: Session = Depends(get_session)
):
    """Update config and hot-reload cache (immediate effect)"""
    # Update database
    config = session.get(LLMNodeConfiguration, node_name)
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)
    
    session.add(config)
    session.commit()
    session.refresh(config)
    
    # Hot-reload cache (immediate effect!)
    config_manager.update_cache("llm_node_config", node_name, config.model_dump())
    
    return {
        "success": True,
        "message": "Config updated in cache (immediate effect)",
        "config": config.model_dump(),
        "effect": "immediate",
        "deployed_to_git": False
    }
```

#### 3. `backend/app/core/config_manager.py` (NEW)

**Purpose:** Cache management with hot-reload

```python
"""Configuration manager with hot-reload support"""
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages configuration with in-memory cache and hot-reload"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def get_config(self, table: str, key: str) -> Dict[str, Any] | None:
        """Get config from cache (cache-first strategy)"""
        cache_key = f"{table}:{key}"
        return self._cache.get(cache_key)
    
    def update_cache(self, table: str, key: str, value: Dict[str, Any]):
        """Update cache (hot-reload)"""
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

#### 4. `backend/tests/api/admin/test_config.py` (NEW)

**Purpose:** Test SAP endpoints

**Tests:**
- ✅ GET /schema returns valid schema
- ✅ GET /llm_node_config lists all configs
- ✅ GET /llm_node_config/{id} returns single config
- ✅ PUT /llm_node_config/{id} updates config
- ✅ POST /llm_node_config/{id}/test-live updates cache
- ✅ Validation errors handled correctly

**Testing Approach:**
- Use real database (Docker container)
- TDD: Write tests first, verify they fail
- Execute in Docker: `docker compose exec backend pytest tests/api/admin/test_config.py -vv`

---

### Sub-Phase 4a.2: SwisperStudio Backend - Config Proxy (Days 4-6)

**Files to Create/Modify:**

#### 1. `backend/app/models/config_history.py` (NEW)

**Purpose:** Audit trail for config changes

```python
"""Config history model for audit trail"""
import uuid
from datetime import datetime
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import JSON
from typing import Dict, Any

class ConfigHistory(SQLModel, table=True):
    """Audit trail of configuration changes"""
    __tablename__ = "config_history"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="project.id", index=True)
    
    # What was changed
    table_name: str = Field(max_length=100, index=True)
    record_id: str = Field(max_length=255, index=True)
    
    # Who changed it
    user_id: str | None = Field(default=None, max_length=255)
    user_email: str | None = Field(default=None, max_length=255)
    
    # What changed
    action: str = Field(max_length=20)  # "update", "create", "delete"
    before: Dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    after: Dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    
    # Mode
    mode: str = Field(max_length=20)  # "test_live" or "deploy"
    
    # When
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # IP and metadata
    ip_address: str | None = Field(default=None, max_length=45)
```

**Migration:**
```bash
# Create migration
alembic revision --autogenerate -m "Add config_history table"
alembic upgrade head
```

#### 2. `backend/app/api/routes/config.py` (NEW)

**Purpose:** Config proxy to Swisper SAP

```python
"""Config proxy routes - forwards to Swisper SAP endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Dict, Any
import httpx
from app.core.db import get_session
from app.models.project import Project
from app.models.config_history import ConfigHistory
from pydantic import BaseModel

router = APIRouter()

class ConfigUpdateRequest(BaseModel):
    data: Dict[str, Any]

async def get_project_by_id(project_id: str, session: Session) -> Project:
    """Helper to get project"""
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.get("/{project_id}/config/schema")
async def get_config_schema(
    project_id: str,
    session: Session = Depends(get_session)
):
    """Proxy: Get config schema from Swisper"""
    project = await get_project_by_id(project_id, session)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{project.swisper_url}/api/admin/config/schema",
            headers={"Authorization": f"Bearer {project.api_key}"}
        )
        response.raise_for_status()
        return response.json()

@router.get("/{project_id}/config/{table}")
async def list_config(
    project_id: str,
    table: str,
    session: Session = Depends(get_session)
):
    """Proxy: List config records from Swisper"""
    project = await get_project_by_id(project_id, session)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{project.swisper_url}/api/admin/config/{table}",
            headers={"Authorization": f"Bearer {project.api_key}"}
        )
        response.raise_for_status()
        return response.json()

@router.get("/{project_id}/config/{table}/{record_id}")
async def get_config_record(
    project_id: str,
    table: str,
    record_id: str,
    session: Session = Depends(get_session)
):
    """Proxy: Get single config record from Swisper"""
    project = await get_project_by_id(project_id, session)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{project.swisper_url}/api/admin/config/{table}/{record_id}",
            headers={"Authorization": f"Bearer {project.api_key}"}
        )
        response.raise_for_status()
        return response.json()

@router.put("/{project_id}/config/{table}/{record_id}/test-live")
async def update_config_test_live(
    project_id: str,
    table: str,
    record_id: str,
    request: ConfigUpdateRequest,
    session: Session = Depends(get_session)
):
    """Proxy: Update config in Test Live mode (immediate effect)"""
    project = await get_project_by_id(project_id, session)
    
    # Fetch current config (for audit trail)
    async with httpx.AsyncClient(timeout=10.0) as client:
        current_response = await client.get(
            f"{project.swisper_url}/api/admin/config/{table}/{record_id}",
            headers={"Authorization": f"Bearer {project.api_key}"}
        )
        current_config = current_response.json() if current_response.status_code == 200 else None
        
        # Update config via Swisper SAP
        update_response = await client.post(
            f"{project.swisper_url}/api/admin/config/{table}/{record_id}/test-live",
            json=request.data,
            headers={"Authorization": f"Bearer {project.api_key}"}
        )
        update_response.raise_for_status()
        result = update_response.json()
    
    # Log to config history
    history = ConfigHistory(
        project_id=project_id,
        table_name=table,
        record_id=record_id,
        action="update",
        before=current_config,
        after=result.get("config"),
        mode="test_live",
        user_email="current_user@example.com",  # TODO: Get from auth
        ip_address="0.0.0.0"  # TODO: Get from request
    )
    session.add(history)
    session.commit()
    
    return result

@router.get("/{project_id}/config/history")
async def get_config_history(
    project_id: str,
    table: str | None = None,
    limit: int = 50,
    session: Session = Depends(get_session)
):
    """Get config change history"""
    from sqlmodel import select
    
    statement = select(ConfigHistory).where(
        ConfigHistory.project_id == project_id
    )
    
    if table:
        statement = statement.where(ConfigHistory.table_name == table)
    
    statement = statement.order_by(ConfigHistory.timestamp.desc()).limit(limit)
    
    results = session.exec(statement).all()
    return {
        "project_id": project_id,
        "table": table,
        "history": [h.model_dump() for h in results],
        "count": len(results)
    }
```

**Register routes in `backend/app/api/routes/__init__.py`:**
```python
from app.api.routes import config

router.include_router(config.router, prefix="/projects", tags=["config"])
```

#### 3. `backend/tests/api/test_config.py` (NEW)

**Tests:**
- ✅ GET /projects/{id}/config/schema proxies correctly
- ✅ GET /projects/{id}/config/{table} proxies correctly
- ✅ PUT /projects/{id}/config/{table}/{id}/test-live proxies and logs history
- ✅ GET /projects/{id}/config/history returns audit trail
- ✅ Error handling for invalid project ID
- ✅ Error handling for Swisper API failures

---

### Sub-Phase 4a.3: SwisperStudio Frontend - Data-Driven UI (Days 6-10)

**Files to Create/Modify:**

#### 1. `frontend/src/features/config/types.ts` (NEW)

```typescript
// SAP Schema Types
export interface ConfigSchemaField {
  name: string;
  type: "string" | "number" | "boolean" | "select" | "textarea" | "json";
  required: boolean;
  immutable?: boolean;
  description: string;
  
  // Type-specific
  max_length?: number;
  min?: number;
  max?: number;
  step?: number;
  options?: string[];
  default?: any;
  
  // UI hints
  placeholder?: string;
  help_text?: string;
  ui_group?: string;
}

export interface ConfigSchemaTable {
  name: string;
  description: string;
  primary_key: string;
  fields: ConfigSchemaField[];
}

export interface ConfigSchema {
  version: string;
  tables: ConfigSchemaTable[];
}

// Config Data
export interface ConfigRecord {
  [key: string]: any;
}

// Config History
export interface ConfigHistoryEntry {
  id: string;
  table_name: string;
  record_id: string;
  action: "create" | "update" | "delete";
  before: any;
  after: any;
  mode: "test_live" | "deploy";
  user_email: string;
  timestamp: string;
}
```

#### 2. `frontend/src/features/config/hooks/use-config-schema.ts` (NEW)

```typescript
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type { ConfigSchema } from "../types";

export function useConfigSchema(projectId: string) {
  return useQuery({
    queryKey: ["config-schema", projectId],
    queryFn: async () => {
      const response = await apiClient.get<ConfigSchema>(
        `/projects/${projectId}/config/schema`
      );
      return response.data;
    },
    enabled: !!projectId,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}
```

#### 3. `frontend/src/features/config/hooks/use-config-data.ts` (NEW)

```typescript
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type { ConfigRecord } from "../types";

export function useConfigRecords(projectId: string, tableName: string) {
  return useQuery({
    queryKey: ["config-records", projectId, tableName],
    queryFn: async () => {
      const response = await apiClient.get<{
        table: string;
        records: ConfigRecord[];
        count: number;
      }>(`/projects/${projectId}/config/${tableName}`);
      return response.data;
    },
    enabled: !!projectId && !!tableName,
  });
}

export function useConfigRecord(
  projectId: string,
  tableName: string,
  recordId: string
) {
  return useQuery({
    queryKey: ["config-record", projectId, tableName, recordId],
    queryFn: async () => {
      const response = await apiClient.get<ConfigRecord>(
        `/projects/${projectId}/config/${tableName}/${recordId}`
      );
      return response.data;
    },
    enabled: !!projectId && !!tableName && !!recordId,
  });
}

export function useUpdateConfigTestLive(projectId: string) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({
      tableName,
      recordId,
      data,
    }: {
      tableName: string;
      recordId: string;
      data: Partial<ConfigRecord>;
    }) => {
      const response = await apiClient.put(
        `/projects/${projectId}/config/${tableName}/${recordId}/test-live`,
        { data }
      );
      return response.data;
    },
    onSuccess: (_, { tableName, recordId }) => {
      // Invalidate cache to refetch
      queryClient.invalidateQueries({
        queryKey: ["config-records", projectId, tableName],
      });
      queryClient.invalidateQueries({
        queryKey: ["config-record", projectId, tableName, recordId],
      });
    },
  });
}
```

#### 4. `frontend/src/features/config/components/field-renderer.tsx` (NEW)

```typescript
import React from "react";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import type { ConfigSchemaField } from "../types";
import { FormControl, FormDescription, FormItem, FormLabel, FormMessage } from "@/components/ui/form";

interface FieldRendererProps {
  field: ConfigSchemaField;
  value: any;
  onChange: (value: any) => void;
  disabled?: boolean;
}

export function FieldRenderer({ field, value, onChange, disabled }: FieldRendererProps) {
  const renderInput = () => {
    switch (field.type) {
      case "string":
        return (
          <Input
            type="text"
            value={value || ""}
            onChange={(e) => onChange(e.target.value)}
            placeholder={field.placeholder}
            maxLength={field.max_length}
            disabled={disabled || field.immutable}
          />
        );
      
      case "number":
        return (
          <Input
            type="number"
            value={value ?? field.default ?? ""}
            onChange={(e) => onChange(parseFloat(e.target.value))}
            min={field.min}
            max={field.max}
            step={field.step}
            disabled={disabled}
          />
        );
      
      case "boolean":
        return (
          <Checkbox
            checked={value ?? field.default ?? false}
            onCheckedChange={onChange}
            disabled={disabled}
          />
        );
      
      case "select":
        return (
          <Select
            value={value || field.default}
            onValueChange={onChange}
            disabled={disabled}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select..." />
            </SelectTrigger>
            <SelectContent>
              {field.options?.map((option) => (
                <SelectItem key={option} value={option}>
                  {option}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        );
      
      case "textarea":
        return (
          <Textarea
            value={value || ""}
            onChange={(e) => onChange(e.target.value)}
            placeholder={field.placeholder}
            maxLength={field.max_length}
            disabled={disabled}
            rows={5}
          />
        );
      
      default:
        return (
          <Input
            type="text"
            value={value || ""}
            onChange={(e) => onChange(e.target.value)}
            disabled={disabled}
          />
        );
    }
  };

  return (
    <FormItem>
      <FormLabel>
        {field.name}
        {field.required && <span className="text-red-500 ml-1">*</span>}
      </FormLabel>
      <FormControl>{renderInput()}</FormControl>
      {field.description && <FormDescription>{field.description}</FormDescription>}
      {field.help_text && <FormDescription className="text-muted-foreground">{field.help_text}</FormDescription>}
      <FormMessage />
    </FormItem>
  );
}
```

#### 5. `frontend/src/features/config/components/data-driven-form.tsx` (NEW)

```typescript
import React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Form } from "@/components/ui/form";
import { Button } from "@/components/ui/button";
import { FieldRenderer } from "./field-renderer";
import type { ConfigSchemaTable, ConfigRecord } from "../types";

// Auto-generate Zod schema from SAP schema
function schemaToZod(table: ConfigSchemaTable): z.ZodObject<any> {
  const shape: Record<string, z.ZodTypeAny> = {};
  
  for (const field of table.fields) {
    let fieldSchema: z.ZodTypeAny;
    
    switch (field.type) {
      case "string":
        fieldSchema = z.string();
        if (field.max_length) {
          fieldSchema = fieldSchema.max(field.max_length);
        }
        break;
      
      case "number":
        fieldSchema = z.number();
        if (field.min !== undefined) {
          fieldSchema = fieldSchema.min(field.min);
        }
        if (field.max !== undefined) {
          fieldSchema = fieldSchema.max(field.max);
        }
        break;
      
      case "boolean":
        fieldSchema = z.boolean();
        break;
      
      case "select":
        if (field.options) {
          fieldSchema = z.enum(field.options as [string, ...string[]]);
        } else {
          fieldSchema = z.string();
        }
        break;
      
      default:
        fieldSchema = z.any();
    }
    
    if (!field.required) {
      fieldSchema = fieldSchema.optional();
    }
    
    shape[field.name] = fieldSchema;
  }
  
  return z.object(shape);
}

interface DataDrivenFormProps {
  schema: ConfigSchemaTable;
  data: ConfigRecord;
  onSubmit: (data: ConfigRecord) => void;
  disabled?: boolean;
}

export function DataDrivenForm({ schema, data, onSubmit, disabled }: DataDrivenFormProps) {
  const formSchema = schemaToZod(schema);
  const form = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: data,
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        {schema.fields.map((field) => (
          <FieldRenderer
            key={field.name}
            field={field}
            value={form.watch(field.name)}
            onChange={(value) => form.setValue(field.name, value)}
            disabled={disabled}
          />
        ))}
        
        <div className="flex gap-4">
          <Button type="submit" disabled={disabled}>
            Test Live
          </Button>
          <Button type="button" variant="outline" disabled>
            Deploy to Prod (Coming in Phase 4b)
          </Button>
        </div>
      </form>
    </Form>
  );
}
```

#### 6. `frontend/src/features/config/components/config-page.tsx` (MODIFY)

Replace placeholder with actual implementation:

```typescript
import React, { useState } from "react";
import { useParams } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useConfigSchema, useConfigRecords, useUpdateConfigTestLive } from "../hooks";
import { DataDrivenForm } from "./data-driven-form";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { CheckCircle2 } from "lucide-react";

export function ConfigPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const [selectedTable, setSelectedTable] = useState<string>("");
  const [selectedRecord, setSelectedRecord] = useState<string>("");

  const { data: schema, isLoading: schemaLoading } = useConfigSchema(projectId!);
  const { data: records, isLoading: recordsLoading } = useConfigRecords(
    projectId!,
    selectedTable
  );
  const updateMutation = useUpdateConfigTestLive(projectId!);

  const handleSubmit = async (data: any) => {
    if (!selectedTable || !selectedRecord) return;
    
    await updateMutation.mutateAsync({
      tableName: selectedTable,
      recordId: selectedRecord,
      data,
    });
  };

  if (schemaLoading) {
    return <div>Loading schema...</div>;
  }

  const selectedTableSchema = schema?.tables.find((t) => t.name === selectedTable);
  const currentRecord = records?.records.find(
    (r) => r[selectedTableSchema?.primary_key || "id"] === selectedRecord
  );

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Configuration Management</CardTitle>
          <CardDescription>
            Manage Swisper configuration with live testing and production deployment
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Table Selector */}
          <div>
            <label className="text-sm font-medium mb-2 block">Config Table</label>
            <Select value={selectedTable} onValueChange={setSelectedTable}>
              <SelectTrigger>
                <SelectValue placeholder="Select a configuration table..." />
              </SelectTrigger>
              <SelectContent>
                {schema?.tables.map((table) => (
                  <SelectItem key={table.name} value={table.name}>
                    {table.description || table.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Record Selector */}
          {selectedTable && records && (
            <div>
              <label className="text-sm font-medium mb-2 block">Record</label>
              <Select value={selectedRecord} onValueChange={setSelectedRecord}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a record to edit..." />
                </SelectTrigger>
                <SelectContent>
                  {records.records.map((record) => {
                    const key = record[selectedTableSchema?.primary_key || "id"];
                    return (
                      <SelectItem key={key} value={key}>
                        {key}
                      </SelectItem>
                    );
                  })}
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Success Message */}
          {updateMutation.isSuccess && (
            <Alert>
              <CheckCircle2 className="h-4 w-4" />
              <AlertDescription>
                Config updated successfully! Changes are live immediately.
              </AlertDescription>
            </Alert>
          )}

          {/* Form */}
          {selectedTableSchema && currentRecord && (
            <DataDrivenForm
              schema={selectedTableSchema}
              data={currentRecord}
              onSubmit={handleSubmit}
              disabled={updateMutation.isPending}
            />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
```

---

### Phase 4a Testing & Validation (Day 10)

**End-to-End Test:**
1. Start Docker containers (`docker compose up -d`)
2. Navigate to SwisperStudio → Project → Configuration
3. Select "LLM Node Config" table
4. Select "global_planner" record
5. Change temperature from 0.7 to 0.5
6. Click "Test Live"
7. Verify success message
8. Verify config updated in Swisper database
9. Verify config history logged
10. Send message to Swisper → Verify planner uses temp=0.5

**Success Criteria:**
- ✅ Schema auto-discovery works
- ✅ Form auto-generated from schema
- ✅ "Test Live" updates config immediately
- ✅ Config history tracked
- ✅ All tests passing (backend: 15+ tests, frontend: builds)

---

## 3. Phase 4b: Full Implementation

**Goal:** Deploy to Prod mode, Config diff viewer, Multiple tables, YAML generation

**Duration:** 5-7 days

### Sub-Phase 4b.1: Deploy to Production (Days 1-3)

**Files to Create/Modify:**

#### 1. `backend/app/api/services/git_service.py` (NEW)

```python
"""Git service for deploying config to production"""
import subprocess
import yaml
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class GitService:
    """Handles Git operations for config deployment"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
    
    def generate_yaml(self, table_name: str, records: list[Dict[str, Any]]) -> str:
        """Generate YAML from config records"""
        if table_name == "llm_node_config":
            config = {
                "llm_nodes": {
                    record["node_name"]: {
                        "default_model": record["default_model"],
                        "default_temperature": record["default_temperature"],
                        "default_max_tokens": record["default_max_tokens"],
                        "langsmith_tracing": record.get("langsmith_tracing", True),
                    }
                    for record in records
                }
            }
            return yaml.dump(config, default_flow_style=False)
        
        raise ValueError(f"Unknown table: {table_name}")
    
    def commit_and_push(
        self,
        file_path: str,
        content: str,
        commit_message: str
    ) -> Dict[str, Any]:
        """Commit config file to Git and push"""
        full_path = self.repo_path / file_path
        
        # Write file
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)
        
        # Git add
        subprocess.run(
            ["git", "add", str(full_path)],
            cwd=self.repo_path,
            check=True
        )
        
        # Git commit
        result = subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Git commit failed: {result.stderr}")
            raise RuntimeError(f"Git commit failed: {result.stderr}")
        
        # Git push
        subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=self.repo_path,
            check=True
        )
        
        # Get commit SHA
        sha_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        return {
            "commit_sha": sha_result.stdout.strip(),
            "file_path": str(file_path),
            "commit_message": commit_message,
        }
```

#### 2. Add Deploy Endpoint in Swisper `backend/app/api/routes/admin/config.py`

```python
@router.post("/llm_node_config/deploy")
async def deploy_llm_node_config(
    commit_message: str,
    session: Session = Depends(get_session)
):
    """Deploy config to production (Git commit)"""
    from app.api.services.git_service import GitService
    from app.core.config import settings
    
    # Fetch all records
    statement = select(LLMNodeConfiguration)
    records = session.exec(statement).all()
    
    # Generate YAML
    git_service = GitService(settings.SWISPER_REPO_PATH)
    yaml_content = git_service.generate_yaml(
        "llm_node_config",
        [r.model_dump() for r in records]
    )
    
    # Commit to Git
    deployment = git_service.commit_and_push(
        "backend/config/llm_node_config.yaml",
        yaml_content,
        commit_message or "Update LLM node configuration"
    )
    
    return {
        "success": True,
        "message": "Config deployed to production",
        "deployment": deployment,
        "yaml_preview": yaml_content[:500] + "..." if len(yaml_content) > 500 else yaml_content
    }
```

#### 3. Add Deploy in SwisperStudio `backend/app/api/routes/config.py`

```python
@router.post("/{project_id}/config/{table}/deploy")
async def deploy_config(
    project_id: str,
    table: str,
    commit_message: str,
    session: Session = Depends(get_session)
):
    """Proxy: Deploy config to production"""
    project = await get_project_by_id(project_id, session)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{project.swisper_url}/api/admin/config/{table}/deploy",
            params={"commit_message": commit_message},
            headers={"Authorization": f"Bearer {project.api_key}"}
        )
        response.raise_for_status()
        result = response.json()
    
    # Log deployment
    history = ConfigHistory(
        project_id=project_id,
        table_name=table,
        record_id="*",  # All records
        action="deploy",
        mode="deploy",
        user_email="current_user@example.com",
        timestamp=datetime.utcnow()
    )
    session.add(history)
    session.commit()
    
    return result
```

#### 4. Update Frontend - Add Deploy Button

In `data-driven-form.tsx`:
```typescript
const deployMutation = useDeployConfig(projectId!);

const handleDeploy = async () => {
  const commitMessage = prompt("Enter commit message:");
  if (!commitMessage) return;
  
  await deployMutation.mutateAsync({
    tableName: schema.name,
    commitMessage,
  });
};

// In form:
<Button
  type="button"
  variant="secondary"
  onClick={handleDeploy}
  disabled={deployMutation.isPending}
>
  Deploy to Production
</Button>
```

---

### Sub-Phase 4b.2: Config Diff Viewer (Days 4-5)

#### 1. `frontend/src/features/config/components/config-diff-viewer.tsx` (NEW)

```typescript
import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ConfigRecord } from "../types";

interface ConfigDiffViewerProps {
  before: ConfigRecord;
  after: ConfigRecord;
}

export function ConfigDiffViewer({ before, after }: ConfigDiffViewerProps) {
  const changes: Array<{ key: string; before: any; after: any }> = [];
  
  // Find changed fields
  for (const key in after) {
    if (before[key] !== after[key]) {
      changes.push({ key, before: before[key], after: after[key] });
    }
  }
  
  if (changes.length === 0) {
    return <div className="text-muted-foreground">No changes</div>;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Changes Preview</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {changes.map(({ key, before, after }) => (
            <div key={key} className="flex items-center gap-2">
              <span className="font-medium">{key}:</span>
              <span className="line-through text-red-500">{String(before)}</span>
              <span>→</span>
              <span className="text-green-500">{String(after)}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
```

---

### Sub-Phase 4b.3: Config History Viewer (Days 6-7)

#### 1. `frontend/src/features/config/components/config-history.tsx` (NEW)

```typescript
import React from "react";
import { useConfigHistory } from "../hooks/use-config-history";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { formatDistanceToNow } from "date-fns";

interface ConfigHistoryProps {
  projectId: string;
  tableName?: string;
}

export function ConfigHistory({ projectId, tableName }: ConfigHistoryProps) {
  const { data, isLoading } = useConfigHistory(projectId, tableName);

  if (isLoading) {
    return <div>Loading history...</div>;
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Timestamp</TableHead>
          <TableHead>Table</TableHead>
          <TableHead>Record</TableHead>
          <TableHead>Action</TableHead>
          <TableHead>Mode</TableHead>
          <TableHead>User</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {data?.history.map((entry) => (
          <TableRow key={entry.id}>
            <TableCell>
              {formatDistanceToNow(new Date(entry.timestamp), { addSuffix: true })}
            </TableCell>
            <TableCell>{entry.table_name}</TableCell>
            <TableCell>{entry.record_id}</TableCell>
            <TableCell>
              <Badge variant={entry.action === "update" ? "default" : "secondary"}>
                {entry.action}
              </Badge>
            </TableCell>
            <TableCell>
              <Badge variant={entry.mode === "test_live" ? "outline" : "default"}>
                {entry.mode}
              </Badge>
            </TableCell>
            <TableCell>{entry.user_email}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
```

---

## 4. Success Criteria

**Phase 4 is successful when:**

### 4.1 SAP Specification
- ✅ v1.0 documented in `docs/specs/spec_sap_v1.md`
- ✅ Schema format defined
- ✅ Endpoint contracts specified
- ✅ Validation rules documented
- ✅ Examples provided

### 4.2 Swisper Backend
- ✅ SAP endpoints implemented
- ✅ Schema introspection works
- ✅ CRUD operations functional
- ✅ Cache hot-reload working
- ✅ Git deployment working
- ✅ 15+ tests passing

### 4.3 SwisperStudio Backend
- ✅ Config proxy API implemented
- ✅ Config history model created
- ✅ Audit logging functional
- ✅ 8+ tests passing

### 4.4 SwisperStudio Frontend
- ✅ Schema fetch working
- ✅ Data-driven form generation working
- ✅ Field renderer supports all types
- ✅ Test Live updates config immediately
- ✅ Deploy to Prod commits to Git
- ✅ Diff viewer shows changes
- ✅ Config history displays audit trail
- ✅ TypeScript compiles
- ✅ Builds successfully

### 4.5 End-to-End
- ✅ User can edit `llm_node_config` via UI
- ✅ "Test Live" takes effect in Swisper (no restart)
- ✅ "Deploy to Prod" commits YAML to Git
- ✅ Changes tracked in audit history
- ✅ No manual YAML editing needed

---

## 5. Risk Mitigation

### Risk 1: Git Operations Fail

**Mitigations:**
- ✅ Test Git service in isolation
- ✅ Add retry logic
- ✅ Graceful error handling
- ✅ Show detailed error messages to user

### Risk 2: Cache Inconsistency

**Mitigations:**
- ✅ DB is source of truth
- ✅ Manual cache flush endpoint
- ✅ Cache TTL (fallback to DB)

### Risk 3: Invalid Config

**Mitigations:**
- ✅ Schema validation before save
- ✅ Zod validation in frontend
- ✅ FastAPI validation in backend
- ✅ "Test Live" mode for safe testing

### Risk 4: Complex Forms

**Mitigations:**
- ✅ Start with simple table (`llm_node_config`)
- ✅ Add field types incrementally
- ✅ Comprehensive UI testing

---

## 6. Follow-Up (Future Enhancements)

**Post-Phase 4:**
- [ ] Add more config tables (fact_preloading, feature_flags)
- [ ] Rollback button (restore previous config)
- [ ] Dry-run validation (test YAML generation without commit)
- [ ] Config comparison (production vs test)
- [ ] Bulk edit (update multiple records at once)
- [ ] Export/import (JSON/YAML download/upload)

---

**Implementation Plan Complete!** ✅

**Next:** Present to user for approval, then begin implementation.

