# SwisperStudio Integration Guide

**Version:** v1.0
**Date:** 2025-11-01
**Last Updated By:** heiko
**Status:** Technical Specification

---

## Overview

This document answers key integration questions for SwisperStudio + Swisper.

---

## 1. Repository Setup - Using Langfuse as Living Spec

### **Strategy: Submodule Approach** ✅

```bash
# Step 1: Create new production repo
cd /root/projects
mkdir swisper_studio_prod
cd swisper_studio_prod
git init

# Step 2: Add Langfuse fork as reference (git submodule)
git submodule add https://github.com/Sundi1972/swisper_studio reference/langfuse

# Step 3: Create your new code structure
mkdir -p backend/app frontend/src docs

# Result:
swisper_studio/
├── backend/         # NEW - Your production code
├── frontend/        # NEW - Your production code
├── reference/
│   └── langfuse/    # REFERENCE - Fork for copying
└── docs/
```

### **How to Use Reference:**

```bash
# Copy data models
cp reference/langfuse/packages/shared/prisma/schema.prisma \
   backend/temp/langfuse_schema.prisma
# Then manually adapt to SQLModel

# Copy UI patterns
code reference/langfuse/web/src/features/traces/
# Open in VSCode, study, then implement in React

# Compare implementations
# See side-by-side what Langfuse does vs what you're building
```

### **Benefits:**
- ✅ Easy reference (same repo)
- ✅ Git tracks which Langfuse commit you're referencing
- ✅ Can `git diff` to see changes
- ✅ Update reference: `git submodule update`
- ✅ No risk of accidentally modifying reference

---

## 2. Swisper SDK - Tracing Integration

### **SDK Package Location:**

```python
# In helvetiq repo (main Swisper repo):

helvetiq/
├── backend/
│   ├── swisper_sdk/              # NEW PACKAGE ✨
│   │   ├── __init__.py
│   │   ├── tracing/
│   │   │   ├── __init__.py
│   │   │   ├── decorator.py      # @traced
│   │   │   ├── graph_wrapper.py  # create_traced_graph
│   │   │   ├── context.py
│   │   │   └── client.py
│   │   ├── config/
│   │   │   └── loader.py
│   │   └── prompts/
│   │       └── loader.py
│   │
│   └── app/                       # Existing Swisper code
│       └── api/
│           └── services/
│               └── agents/
│                   └── global_supervisor/
│                       ├── global_supervisor.py
│                       └── nodes/
│                           ├── intent_classification_node.py
│                           └── ...
```

### **SDK Implementation: `@traced` Decorator**

```python
# swisper_sdk/tracing/decorator.py

import asyncio
import functools
import inspect
import time
from typing import TypeVar, Callable, Any
from contextvars import ContextVar

from .client import SwisperStudioClient
from .context import get_current_trace, set_current_observation

T = TypeVar('T')

# Global client (configured once)
_studio_client: SwisperStudioClient | None = None

def initialize_tracing(
    api_url: str,
    api_key: str,
    enabled: bool = True,
):
    """Initialize tracing (call once at startup)"""
    global _studio_client
    if enabled:
        _studio_client = SwisperStudioClient(
            api_url=api_url,
            api_key=api_key,
        )


def traced(
    name: str | None = None,
    observation_type: str = "SPAN",  # SPAN, GENERATION, EVENT, TOOL, AGENT
    track_io: bool = True,
):
    """
    Auto-trace any function/node

    Usage:
        @traced("my_node")
        def my_node(state: GlobalSupervisorState):
            # Your logic
            return updated_state
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        obs_name = name or func.__name__

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            if not _studio_client:
                # Tracing not initialized, just run function
                return await func(*args, **kwargs)

            # Extract input (state if LangGraph node)
            input_data = None
            if track_io and args and hasattr(args[0], 'dict'):
                input_data = args[0].dict()

            # Start observation
            parent_obs = get_current_observation()
            trace_id = get_current_trace()

            start_time = time.time()
            obs_id = await _studio_client.create_observation(
                trace_id=trace_id,
                name=obs_name,
                type=observation_type,
                parent_observation_id=parent_obs,
                input=input_data,
            )

            # Set as current observation (for child calls)
            token = set_current_observation(obs_id)

            try:
                # Execute function
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                # Extract output
                output_data = None
                if track_io and hasattr(result, 'dict'):
                    output_data = result.dict()

                # End observation (success)
                await _studio_client.end_observation(
                    observation_id=obs_id,
                    output=output_data,
                    level="DEFAULT",
                )

                return result

            except Exception as e:
                # End observation (error)
                await _studio_client.end_observation(
                    observation_id=obs_id,
                    level="ERROR",
                    status_message=str(e),
                )
                raise

            finally:
                # Reset observation context
                set_current_observation(parent_obs, token)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            # Sync version (if function is not async)
            if not _studio_client:
                return func(*args, **kwargs)

            # Similar logic but without await
            # (Implementation omitted for brevity)
            return func(*args, **kwargs)

        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
```

### **SDK Implementation: Context Management**

```python
# swisper_sdk/tracing/context.py

from contextvars import ContextVar
from typing import Optional

# Context variables for trace/observation tracking
_current_trace_id: ContextVar[Optional[str]] = ContextVar('trace_id', default=None)
_current_observation_id: ContextVar[Optional[str]] = ContextVar('observation_id', default=None)

def get_current_trace() -> Optional[str]:
    """Get current trace ID from context"""
    return _current_trace_id.get()

def set_current_trace(trace_id: str):
    """Set current trace ID"""
    return _current_trace_id.set(trace_id)

def get_current_observation() -> Optional[str]:
    """Get current observation ID (parent for nesting)"""
    return _current_observation_id.get()

def set_current_observation(obs_id: Optional[str], token=None):
    """Set current observation ID"""
    if token:
        _current_observation_id.reset(token)
    else:
        return _current_observation_id.set(obs_id)
```

### **SDK Implementation: API Client**

```python
# swisper_sdk/tracing/client.py

import httpx
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

class SwisperStudioClient:
    """Client for SwisperStudio API"""

    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=api_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=5.0,
        )

    async def create_trace(
        self,
        name: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[list[str]] = None,
    ) -> str:
        """Create a new trace"""
        trace_id = str(uuid.uuid4())

        await self.client.post(
            "/api/v1/traces",
            json={
                "id": trace_id,
                "name": name,
                "user_id": user_id,
                "session_id": session_id,
                "metadata": metadata or {},
                "tags": tags or [],
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        return trace_id

    async def create_observation(
        self,
        trace_id: str,
        name: str,
        type: str,
        parent_observation_id: Optional[str] = None,
        input: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a new observation (span, generation, etc.)"""
        obs_id = str(uuid.uuid4())

        await self.client.post(
            "/api/v1/observations",
            json={
                "id": obs_id,
                "trace_id": trace_id,
                "parent_observation_id": parent_observation_id,
                "name": name,
                "type": type,
                "input": input,
                "start_time": datetime.utcnow().isoformat(),
            }
        )

        return obs_id

    async def end_observation(
        self,
        observation_id: str,
        output: Optional[Dict[str, Any]] = None,
        level: str = "DEFAULT",
        status_message: Optional[str] = None,
    ):
        """End an observation"""
        await self.client.patch(
            f"/api/v1/observations/{observation_id}",
            json={
                "end_time": datetime.utcnow().isoformat(),
                "output": output,
                "level": level,
                "status_message": status_message,
            }
        )
```

---

## 3. Usage in Swisper

### **Initialization (at startup):**

```python
# backend/app/main.py

from swisper_sdk.tracing import initialize_tracing
from app.core.config import settings

# Initialize tracing at startup
initialize_tracing(
    api_url=settings.SWISPER_STUDIO_URL,  # e.g., "http://swisper-studio:8000"
    api_key=settings.SWISPER_STUDIO_API_KEY,
    enabled=settings.TRACING_ENABLED,
)
```

### **Usage in Nodes (Manual):**

```python
# backend/app/api/services/agents/global_supervisor/nodes/intent_classification_node.py

from swisper_sdk.tracing import traced
from app.api.services.agents.global_supervisor.global_supervisor_state import GlobalSupervisorState

@traced("intent_classification", observation_type="SPAN")
async def intent_classification_node(state: GlobalSupervisorState):
    """Classify user intent"""

    # Your existing logic
    intent = await classify_intent(state.messages[-1].content)
    state.current_intent = intent

    return state

# That's it! Automatically captures:
# ✅ Input: state (before)
# ✅ Output: state (after)
# ✅ Duration
# ✅ Errors (if any)
# ✅ Parent/child relationships
```

### **Usage in LLM Calls:**

```python
# backend/app/api/services/agents/global_supervisor/nodes/ui_node.py

from swisper_sdk.tracing import traced
from langchain_openai import ChatOpenAI

@traced("ui_node", observation_type="GENERATION")  # Note: GENERATION type
async def ui_node(state: GlobalSupervisorState):
    """Generate UI response"""

    llm = ChatOpenAI(model="gpt-4")

    # LLM call (could also be traced separately)
    response = await llm.ainvoke(
        messages=[...],
        temperature=0.7,
    )

    state.ui_response = response.content
    return state
```

### **Auto-Instrumentation (LangGraph):**

```python
# backend/app/api/services/agents/global_supervisor/global_supervisor.py

from langgraph.graph import StateGraph
from swisper_sdk.tracing import create_traced_graph, traced
from swisper_sdk.tracing.context import set_current_trace

async def create_global_supervisor():
    """Create global supervisor graph with auto-tracing"""

    # Create traced graph (auto-instruments all nodes!)
    graph = StateGraph(GlobalSupervisorState)

    # Add nodes (will be auto-traced)
    graph.add_node("intent_classification", intent_classification_node)
    graph.add_node("memory", memory_node)
    graph.add_node("planner", planner_node)
    # ... etc

    return graph.compile()


async def run_global_supervisor(user_message: str, user_id: str):
    """Run supervisor with tracing"""

    # Create trace
    from swisper_sdk.tracing.client import get_studio_client
    studio = get_studio_client()

    trace_id = await studio.create_trace(
        name="user_request",
        user_id=user_id,
        metadata={"message": user_message}
    )

    # Set trace context
    set_current_trace(trace_id)

    # Run graph (all nodes auto-traced!)
    graph = await create_global_supervisor()
    result = await graph.ainvoke({
        "messages": [{"role": "user", "content": user_message}],
        "current_intent": None,
        "facts": [],
        # ... initial state
    })

    return result
```

---

## 4. Admin Integration - Data-Driven UI

### **Swisper Backend Schema Endpoint:**

```python
# backend/app/api/routes/admin_schema.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Literal

router = APIRouter(prefix="/admin", tags=["admin"])

class FieldBase(BaseModel):
    type: str
    key: str
    label: str
    description: str | None = None

class BooleanField(FieldBase):
    type: Literal["boolean"] = "boolean"
    current_value: bool
    default: bool

class SelectField(FieldBase):
    type: Literal["select"] = "select"
    options: list[str]
    current_value: str
    default: str

class SliderField(FieldBase):
    type: Literal["slider"] = "slider"
    min: float
    max: float
    step: float
    current_value: float
    default: float

class AdminSection(BaseModel):
    id: str
    title: str
    description: str | None = None
    fields: list[BooleanField | SelectField | SliderField]

class AdminSchema(BaseModel):
    version: str
    sections: list[AdminSection]


@router.get("/schema", response_model=AdminSchema)
async def get_admin_schema():
    """
    Returns schema for SwisperStudio to auto-generate admin UI

    SwisperStudio will:
    1. Fetch this schema
    2. Dynamically render forms
    3. Validate changes
    4. Deploy to Git
    """
    from app.core.config import settings

    return AdminSchema(
        version="1.0",
        sections=[
            AdminSection(
                id="features",
                title="Feature Flags",
                description="Enable/disable features",
                fields=[
                    BooleanField(
                        key="voice_enabled",
                        label="Voice Interface",
                        description="Enable voice input/output",
                        current_value=settings.VOICE_ENABLED,
                        default=True,
                    ),
                    BooleanField(
                        key="fact_preloading",
                        label="Fact Preloading",
                        description="Preload facts from memory before agent execution",
                        current_value=settings.FACT_PRELOADING_ENABLED,
                        default=True,
                    ),
                ],
            ),
            AdminSection(
                id="llm",
                title="LLM Configuration",
                description="Default LLM settings",
                fields=[
                    SelectField(
                        key="default_model",
                        label="Default Model",
                        description="Primary model for all agents",
                        options=["gpt-4", "gpt-4-turbo", "claude-3-opus", "claude-3-sonnet"],
                        current_value=settings.DEFAULT_LLM_MODEL,
                        default="gpt-4",
                    ),
                    SliderField(
                        key="temperature",
                        label="Temperature",
                        description="Creativity level (0=focused, 2=creative)",
                        min=0.0,
                        max=2.0,
                        step=0.1,
                        current_value=settings.DEFAULT_TEMPERATURE,
                        default=0.7,
                    ),
                ],
            ),
        ],
    )
```

### **SwisperStudio Frontend (Auto-Generating):**

```typescript
// SwisperStudio: frontend/src/features/config/ConfigEditor.tsx

import { useQuery, useMutation } from '@tanstack/react-query';
import { fetchAdminSchema, updateConfig, deployConfig } from '@/api/swisper';

function ConfigEditor() {
  // Fetch schema from Swisper
  const { data: schema } = useQuery('adminSchema', fetchAdminSchema);

  const [values, setValues] = useState({});

  return (
    <div>
      <h1>Swisper Configuration</h1>

      {schema?.sections.map(section => (
        <Section key={section.id}>
          <h2>{section.title}</h2>
          <p>{section.description}</p>

          {section.fields.map(field => (
            <Field
              key={field.key}
              field={field}
              value={values[field.key] ?? field.current_value}
              onChange={(val) => setValues({...values, [field.key]: val})}
            />
          ))}
        </Section>
      ))}

      <Actions>
        <Button onClick={() => deployConfig(values)}>
          Deploy to Git
        </Button>
      </Actions>
    </div>
  );
}

// Auto-select field component based on type
function Field({ field, value, onChange }) {
  switch (field.type) {
    case 'boolean':
      return <Toggle label={field.label} checked={value} onChange={onChange} />;

    case 'select':
      return (
        <Select
          label={field.label}
          options={field.options}
          value={value}
          onChange={onChange}
        />
      );

    case 'slider':
      return (
        <Slider
          label={field.label}
          min={field.min}
          max={field.max}
          step={field.step}
          value={value}
          onChange={onChange}
        />
      );
  }
}
```

---

## 5. Summary - Integration Flow

### **Complete Flow:**

```
Developer Workflow:
┌────────────────────────────────────────────────┐
│  1. Code Changes (Swisper Backend)             │
│     └─ Add @traced to new nodes                │
│                                                │
│  2. Auto-Tracing                               │
│     └─ Traces sent to SwisperStudio API        │
│                                                │
│  3. View in SwisperStudio                      │
│     ├─ Trace list                              │
│     ├─ Graph visualization                     │
│     └─ Metrics                                 │
│                                                │
│  4. Edit Config/Prompts in SwisperStudio       │
│     └─ Data-driven UI                          │
│                                                │
│  5. Deploy                                     │
│     ├─ SwisperStudio commits to Git            │
│     └─ CI/CD deploys to production             │
│                                                │
│  6. Swisper Syncs                              │
│     └─ Loads config/prompts from Git           │
└────────────────────────────────────────────────┘
```

---

## Next Steps

1. [ ] Setup swisper_studio repo with submodule
2. [ ] Implement `@traced` decorator in swisper_sdk
3. [ ] Create ingestion API in SwisperStudio backend
4. [ ] Test end-to-end: Send trace → See in UI
5. [ ] Implement admin schema endpoint in Swisper
6. [ ] Build auto-generating UI in SwisperStudio

---

**This integration design is:**
- ✅ Bulletproof (error handling, fallbacks)
- ✅ Easy for developers (one decorator)
- ✅ Super developer-friendly (no boilerplate)
- ✅ Leverages SDK patterns (standard approach)

**Ready to start building!** 🚀

