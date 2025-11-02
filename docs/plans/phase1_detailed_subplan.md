# Phase 1 Detailed Sub-Plan: "Hello World"

**Phase:** Phase 1 - End-to-End Proof  
**Duration:** 2 weeks  
**Business Value:** See first trace flowing from Swisper to SwisperStudio UI  
**Status:** Ready for Approval

---

## 📚 Based On Analysis

**Reference:** `docs/analysis/phase1_langfuse_swisper_analysis.md`

**Key Decisions from Analysis:**
1. ✅ Use simplified Project model (from Langfuse pattern)
2. ✅ PostgreSQL only for MVP (ClickHouse in Phase 5+)
3. ✅ Use MUI v7 (NOT Tailwind) - Match Swisper
4. ✅ Reuse `@shiu/components` and `@shiu/icons`
5. ✅ Follow Langfuse pagination patterns
6. ✅ Follow Swisper naming conventions (kebab-case files)
7. ✅ Use TanStack Query with custom hooks

---

## 🎯 Phase 1 Goals

### End-to-End Flow
1. User opens SwisperStudio → Sees login page
2. User enters API key → Authenticated
3. User creates first project → "Production Swisper"
4. Swisper sends trace (via SDK) → SwisperStudio receives it
5. User sees trace in list → Clicks → Views details

### Success Criteria
- [ ] Login works (API key auth)
- [ ] Project created successfully
- [ ] Trace ingested and stored
- [ ] Trace visible in UI table
- [ ] Trace details viewable (JSON viewer)
- [ ] SDK integrated in test Swisper instance

---

## 📋 Backend Tasks (Week 1)

### Task 1.1: Project Model & API (Clean Architecture)

**Files to Create:**
```
backend/app/
├── models/
│   └── project.py              [CREATE] - Project model
├── api/routes/
│   └── projects.py             [CREATE] - Project CRUD endpoints  
└── tests/
    └── api/
        └── test_projects.py    [CREATE] - Project tests
```

**Implementation (following Langfuse patterns):**

```python
# app/models/project.py
import uuid
from datetime import datetime
from typing import Any
from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class Project(SQLModel, table=True):
    """
    Represents a connection to one Swisper deployment.
    
    Based on Langfuse Project model (simplified for MVP).
    Reference: langfuse/packages/shared/prisma/schema.prisma:130-186
    """
    __tablename__ = "projects"
    
    # Primary key (UUID4 instead of Langfuse's cuid)
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique project identifier"
    )
    
    # Core fields
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    swisper_url: str = Field(..., description="Swisper instance URL (e.g., https://swisper.company.com)")
    swisper_api_key: str = Field(..., description="Hashed API key for Swisper connection")
    
    # Optional fields
    description: str | None = Field(None, max_length=1000, description="Project description")
    meta: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="Additional metadata"
    )
    
    # Timestamps (Langfuse pattern)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When project was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="When project was last updated"
    )
    
    # Soft delete (Langfuse pattern)
    deleted_at: datetime | None = Field(
        None,
        description="When project was deleted (soft delete)"
    )
```

**API Endpoints:**

```python
# app/api/routes/projects.py

@router.post("/projects", response_model=ProjectResponse, status_code=201)
async def create_project(
    data: ProjectCreate,
    session: DBSession,
    api_key: APIKey
):
    """Create new project (Langfuse pattern with validation)"""
    # Hash API key before storage (security best practice)
    hashed_key = bcrypt.hashpw(
        data.swisper_api_key.encode(),
        bcrypt.gensalt()
    )
    
    project = Project(
        name=data.name,
        swisper_url=str(data.swisper_url),
        swisper_api_key=hashed_key.decode(),
        description=data.description,
        meta=data.meta
    )
    
    session.add(project)
    await session.commit()
    await session.refresh(project)
    
    return project

@router.get("/projects", response_model=ProjectListResponse)
async def list_projects(
    pagination: PaginationParams = Depends(),
    session: DBSession,
    api_key: APIKey
):
    """List all projects with pagination (Langfuse pattern)"""
    # Filter out soft-deleted
    stmt = select(Project).where(
        Project.deleted_at.is_(None)
    ).offset((pagination.page - 1) * pagination.limit).limit(pagination.limit)
    
    result = await session.execute(stmt)
    projects = result.scalars().all()
    
    # Count total
    count_stmt = select(func.count()).select_from(Project).where(
        Project.deleted_at.is_(None)
    )
    total = await session.scalar(count_stmt)
    
    return {
        "data": projects,
        "meta": {
            "page": pagination.page,
            "limit": pagination.limit,
            "total_items": total,
            "total_pages": math.ceil(total / pagination.limit)
        }
    }

@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(...):
    """Get project by ID"""
    ...

@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(...):
    """Update project"""
    ...

@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(...):
    """Soft delete project (Langfuse pattern)"""
    project.deleted_at = datetime.utcnow()
    await session.commit()
```

**Tests (TDD - Write First!):**

```python
# tests/api/test_projects.py

@pytest.mark.ci_critical
@pytest.mark.asyncio
async def test_create_project_success(client, api_headers):
    """CI: Golden path - project creation works"""
    response = await client.post(
        "/api/v1/projects",
        json={
            "name": "Test Project",
            "swisper_url": "https://swisper.example.com",
            "swisper_api_key": "test-api-key"
        },
        headers=api_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert "swisper_api_key" not in data  # Never return hashed key

@pytest.mark.asyncio
async def test_list_projects_pagination(client, api_headers):
    """Test pagination works correctly"""
    # Create 15 projects
    for i in range(15):
        await create_test_project(f"Project {i}")
    
    # Get first page
    response = await client.get(
        "/api/v1/projects?page=1&limit=10",
        headers=api_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 10
    assert data["meta"]["total_items"] == 15
    assert data["meta"]["total_pages"] == 2

@pytest.mark.asyncio
async def test_soft_delete_project(client, api_headers):
    """Test soft delete doesn't actually remove from DB"""
    # Implementation test...
```

**Clean Architecture Principles:**
- ✅ Separate models, routes, tests
- ✅ Use dependency injection (`DBSession`, `APIKey`)
- ✅ Validate with Pydantic
- ✅ Hash sensitive data (API keys)
- ✅ Soft deletes for audit trail
- ✅ Comprehensive tests (golden path + edge cases)

---

### Task 1.2: Enhanced Trace Ingestion

**Files to Modify:**
```
backend/app/
├── models/
│   └── trace.py                [MODIFY] - Add project_id foreign key
├── api/routes/
│   └── traces.py               [MODIFY] - Add project validation
└── tests/
    └── api/
        └── test_traces.py      [MODIFY] - Add project-based tests
```

**Changes:**

```python
# app/models/trace.py

class Trace(SQLModel, table=True):
    # ... existing fields ...
    
    # Add project relationship
    project_id: str = Field(
        sa_column=Column(ForeignKey("projects.id", ondelete="CASCADE"), index=True),
        description="Project this trace belongs to"
    )
```

**API Enhancement:**

```python
# app/api/routes/traces.py

@router.post("/traces", response_model=TraceResponse, status_code=202)
async def create_trace(
    trace_data: TraceCreate,
    session: DBSession,
    api_key: APIKey
):
    """
    Ingest trace (Langfuse pattern - return 202 Accepted for async processing)
    """
    # Validate project exists
    project = await session.get(Project, trace_data.project_id)
    if not project:
        raise HTTPException(
            status_code=404,
            detail=f"Project {trace_data.project_id} not found"
        )
    
    # Idempotency check (Langfuse pattern)
    existing = await session.scalar(
        select(Trace).where(
            Trace.id == trace_data.id,
            Trace.project_id == trace_data.project_id
        )
    )
    
    if existing:
        return existing  # Return existing (idempotent)
    
    # Create trace
    trace = Trace(**trace_data.model_dump())
    session.add(trace)
    await session.commit()
    await session.refresh(trace)
    
    return trace

@router.get("/traces", response_model=TraceListResponse)
async def list_traces(
    project_id: str,
    pagination: PaginationParams = Depends(),
    filters: TraceFilters = Depends(),
    session: DBSession,
    api_key: APIKey
):
    """
    List traces for a project (Langfuse pagination pattern)
    """
    # Build query with filters
    stmt = select(Trace).where(Trace.project_id == project_id)
    
    # Apply filters
    if filters.user_id:
        stmt = stmt.where(Trace.user_id == filters.user_id)
    if filters.session_id:
        stmt = stmt.where(Trace.session_id == filters.session_id)
    if filters.start_date:
        stmt = stmt.where(Trace.timestamp >= filters.start_date)
    if filters.end_date:
        stmt = stmt.where(Trace.timestamp <= filters.end_date)
    
    # Pagination
    offset = (pagination.page - 1) * pagination.limit
    stmt = stmt.offset(offset).limit(pagination.limit).order_by(Trace.timestamp.desc())
    
    result = await session.execute(stmt)
    traces = result.scalars().all()
    
    # Count total
    count_stmt = select(func.count()).select_from(Trace).where(
        Trace.project_id == project_id
    )
    total = await session.scalar(count_stmt)
    
    return {
        "data": traces,
        "meta": {
            "page": pagination.page,
            "limit": pagination.limit,
            "total_items": total,
            "total_pages": math.ceil(total / pagination.limit)
        }
    }
```

**Migration:**
```bash
# Create migration for project_id foreign key
alembic revision --autogenerate -m "Add project relationship to traces"
```

**Tests:**

```python
@pytest.mark.ci_critical
@pytest.mark.asyncio
async def test_trace_requires_valid_project(client, api_headers):
    """CI: Trace creation requires valid project"""
    response = await client.post(
        "/api/v1/traces",
        json={
            "id": str(uuid.uuid4()),
            "project_id": "non-existent",
            "name": "Test Trace"
        },
        headers=api_headers
    )
    
    assert response.status_code == 404
    assert "Project" in response.json()["detail"]

@pytest.mark.asyncio
async def test_list_traces_pagination(client, project, api_headers):
    """Test trace listing with pagination"""
    # Create 25 traces
    for i in range(25):
        await create_test_trace(project.id, f"Trace {i}")
    
    # Get first page
    response = await client.get(
        f"/api/v1/traces?project_id={project.id}&page=1&limit=10",
        headers=api_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 10
    assert data["meta"]["total_items"] == 25
```

---

## 📱 Frontend Tasks (Week 2)

### Task 2.1: Frontend Setup (MUI + Vite)

**Files to Create:**
```
frontend/
├── package.json                [CREATE] - Dependencies (Vite, React, MUI, TanStack Query)
├── vite.config.ts              [CREATE] - Vite configuration
├── tsconfig.json               [CREATE] - TypeScript configuration
├── index.html                  [CREATE] - HTML entry
└── src/
    ├── main.tsx                [CREATE] - React entry point
    ├── app.tsx                 [CREATE] - Root component with routing
    └── vite-env.d.ts           [CREATE] - Vite types
```

**Dependencies (based on Swisper stack):**

```json
{
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-router-dom": "^6.20.0",
    "@mui/material": "^7.0.2",
    "@mui/icons-material": "^7.0.2",
    "@emotion/react": "^11.11.1",
    "@emotion/styled": "^11.11.0",
    "@tanstack/react-query": "^5.14.0",
    "@tanstack/react-query-devtools": "^5.14.0",
    "zod": "^4.1.12",
    "react-hook-form": "^7.65.0",
    "@hookform/resolvers": "^5.2.1"
  },
  "devDependencies": {
    "vite": "^5.0.8",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "@types/react": "^18.2.45",
    "@types/react-dom": "^18.2.18"
  }
}
```

**Vite Config:**

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
    },
  },
});
```

**No TDD needed** (infrastructure setup)

---

### Task 2.2: Login Page (Simple API Key Auth)

**Files to Create:**
```
frontend/src/
├── features/
│   └── auth/
│       ├── components/
│       │   └── login-page.tsx       [CREATE] - Login UI
│       ├── hooks/
│       │   ├── use-login-mutation.ts [CREATE] - Login mutation
│       │   └── use-auth-state.ts    [CREATE] - Auth state
│       └── utils/
│           └── auth-storage.ts      [CREATE] - localStorage API key
```

**Implementation (following Swisper patterns):**

```typescript
// features/auth/components/login-page.tsx

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import { styled } from '@mui/material/styles';

import { useLoginMutation } from '../hooks/use-login-mutation';

// Swisper styling pattern - styled components
const Container = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: '100vh',
  padding: theme.spacing(3),
}));

const LoginForm = styled(Box)(({ theme }) => ({
  width: '100%',
  maxWidth: '400px',
  padding: theme.spacing(4),
  borderRadius: theme.spacing(1),
  backgroundColor: theme.palette.background.paper,
  boxShadow: theme.shadows[3],
}));

export function LoginPage() {
  const [apiKey, setApiKey] = useState('');
  const navigate = useNavigate();
  const { mutateAsync: login, isPending } = useLoginMutation();
  
  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    
    try {
      await login({ apiKey });
      navigate('/projects');
    } catch (error) {
      // Error handled by mutation hook
    }
  }
  
  return (
    <Container data-testid="login-page">
      <LoginForm component="form" onSubmit={handleSubmit}>
        <Typography variant="h4" component="h1" gutterBottom>
          SwisperStudio
        </Typography>
        
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Enter your API key to continue
        </Typography>
        
        <TextField
          fullWidth
          type="password"
          label="API Key"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          required
          sx={{ mb: 2 }}
        />
        
        <Button
          fullWidth
          type="submit"
          variant="contained"
          disabled={isPending || !apiKey}
        >
          {isPending ? 'Logging in...' : 'Login'}
        </Button>
      </LoginForm>
    </Container>
  );
}
```

```typescript
// features/auth/hooks/use-login-mutation.ts

import { useMutation } from '@tanstack/react-query';
import { storeApiKey } from '../utils/auth-storage';

interface LoginPayload {
  apiKey: string;
}

export function useLoginMutation() {
  return useMutation<void, Error, LoginPayload>({
    mutationFn: async ({ apiKey }) => {
      // Validate API key by calling backend
      const response = await fetch('/api/health', {
        headers: { 'X-API-Key': apiKey }
      });
      
      if (!response.ok) {
        throw new Error('Invalid API key');
      }
      
      // Store in localStorage
      storeApiKey(apiKey);
    },
  });
}
```

**Follows Swisper patterns:**
- ✅ Function declarations (not arrow functions)
- ✅ MUI components
- ✅ Styled components with theme
- ✅ TanStack Query mutation
- ✅ kebab-case filenames
- ✅ data-testid on root element

---

### Task 2.3: Project Setup Page

**Files to Create:**
```
frontend/src/
├── features/
│   └── projects/
│       ├── components/
│       │   ├── project-list-page.tsx        [CREATE] - List projects
│       │   ├── project-create-dialog.tsx    [CREATE] - Create project form
│       │   └── project-card.tsx             [CREATE] - Project display
│       └── hooks/
│           ├── use-projects-query.ts        [CREATE] - GET projects
│           └── use-create-project-mutation.ts [CREATE] - POST project
```

**Implementation:**

```typescript
// features/projects/components/project-list-page.tsx

import { useState } from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import { styled } from '@mui/material/styles';
import { AddIcon } from '@shiu/icons';  // Swisper icon

import { useProjectsQuery } from '../hooks/use-projects-query';
import { ProjectCreateDialog } from './project-create-dialog';
import { ProjectCard } from './project-card';

const Container = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
}));

export function ProjectListPage() {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const { data, isLoading } = useProjectsQuery();
  
  if (isLoading) {
    return <Typography>Loading projects...</Typography>;
  }
  
  return (
    <Container data-testid="project-list-page">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Projects</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setIsCreateDialogOpen(true)}
        >
          New Project
        </Button>
      </Box>
      
      <Box sx={{ display: 'grid', gap: 2, gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))' }}>
        {data?.data.map((project) => (
          <ProjectCard key={project.id} project={project} />
        ))}
      </Box>
      
      <ProjectCreateDialog
        isOpen={isCreateDialogOpen}
        onClose={() => setIsCreateDialogOpen(false)}
      />
    </Container>
  );
}
```

---

### Task 2.4: Trace List View

**Files to Create:**
```
frontend/src/
├── features/
│   └── traces/
│       ├── components/
│       │   ├── trace-list-page.tsx    [CREATE] - Main trace table
│       │   └── trace-row.tsx          [CREATE] - Table row component
│       └── hooks/
│           └── use-traces-query.ts    [CREATE] - GET traces with pagination
```

**Implementation (following Langfuse UX patterns):**

```typescript
// features/traces/components/trace-list-page.tsx

import { useParams } from 'react-router-dom';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

import { useTracesQuery } from '../hooks/use-traces-query';

const columns: GridColDef[] = [
  {
    field: 'timestamp',
    headerName: 'Time',
    width: 180,
    valueFormatter: (params) => formatDateTimeLocal(params.value)
  },
  {
    field: 'name',
    headerName: 'Name',
    width: 250
  },
  {
    field: 'user_id',
    headerName: 'User',
    width: 200
  },
  {
    field: 'session_id',
    headerName: 'Session',
    width: 200
  }
];

export function TraceListPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const [page, setPage] = useState(1);
  const { data, isLoading } = useTracesQuery(projectId!, page);
  
  return (
    <Box data-testid="trace-list-page" sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3 }}>Traces</Typography>
      
      <DataGrid
        rows={data?.data || []}
        columns={columns}
        loading={isLoading}
        paginationMode="server"
        rowCount={data?.meta.total_items || 0}
        page={page - 1}  // MUI DataGrid uses 0-based
        pageSize={50}
        onPageChange={(newPage) => setPage(newPage + 1)}
        autoHeight
      />
    </Box>
  );
}
```

**Follows:**
- ✅ Langfuse UX (table layout, columns)
- ✅ Swisper styling (MUI components)
- ✅ TanStack Query for data fetching
- ✅ Kebab-case filenames

---

## 🔧 SDK Tasks (Week 2)

**Location:** Create new package `swisper-studio-sdk/`

**Files to Create:**
```
swisper-studio-sdk/
├── pyproject.toml              [CREATE] - SDK dependencies
├── swisper_studio_sdk/
│   ├── __init__.py             [CREATE] - Public API
│   ├── tracing/
│   │   ├── __init__.py         [CREATE]
│   │   ├── decorator.py        [CREATE] - @traced
│   │   ├── graph_wrapper.py    [CREATE] - create_traced_graph()
│   │   ├── context.py          [CREATE] - Context vars (trace_id, observation_id)
│   │   └── client.py           [CREATE] - SwisperStudio API client
│   └── config.py               [CREATE] - SDK configuration
└── tests/
    └── test_decorator.py       [CREATE] - SDK tests
```

### Task 3.1: `create_traced_graph()` Wrapper

**The Key Integration Feature!**

```python
# swisper_studio_sdk/tracing/graph_wrapper.py

from langgraph.graph import StateGraph
from typing import TypeVar, Type
from .decorator import traced

TState = TypeVar('TState')

def create_traced_graph(
    state_class: Type[TState],
    trace_name: str,
    auto_trace_all_nodes: bool = True
) -> StateGraph:
    """
    Create a StateGraph with automatic tracing.
    
    This is the ONE-LINE CHANGE integration method:
    
    Before:
        graph = StateGraph(GlobalSupervisorState)
    
    After:
        graph = create_traced_graph(GlobalSupervisorState, trace_name="supervisor")
    
    All nodes added to this graph will be automatically traced!
    
    Args:
        state_class: The LangGraph state class
        trace_name: Name for the trace
        auto_trace_all_nodes: If True, wraps all nodes with @traced
    
    Returns:
        StateGraph instance with tracing enabled
    """
    graph = StateGraph(state_class)
    
    if auto_trace_all_nodes:
        # Monkey-patch add_node to auto-wrap with @traced
        original_add_node = graph.add_node
        
        def traced_add_node(name: str, func):
            # Automatically wrap node function with tracing
            wrapped_func = traced(
                name=name,
                observation_type="SPAN"
            )(func)
            return original_add_node(name, wrapped_func)
        
        graph.add_node = traced_add_node
    
    return graph
```

**Test:**

```python
# tests/test_graph_wrapper.py

@pytest.mark.asyncio
async def test_create_traced_graph_auto_wraps_nodes():
    """Verify all nodes are automatically traced"""
    graph = create_traced_graph(TestState, trace_name="test")
    
    # Add nodes (should be auto-wrapped)
    graph.add_node("node1", node1_func)
    graph.add_node("node2", node2_func)
    
    # Execute graph
    app = graph.compile()
    result = await app.ainvoke({"value": 0})
    
    # Verify traces were sent to SwisperStudio
    assert_trace_sent("test")
    assert_observation_sent("node1")
    assert_observation_sent("node2")
```

---

### Task 3.2: `@traced` Decorator

```python
# swisper_studio_sdk/tracing/decorator.py

import asyncio
import functools
import time
from typing import TypeVar, Callable
from contextvars import ContextVar

from .client import get_studio_client
from .context import get_current_trace, set_current_observation

T = TypeVar('T')

def traced(
    name: str | None = None,
    observation_type: str = "SPAN",
):
    """
    Auto-trace any function/node.
    
    Usage:
        @traced("my_node")
        async def my_node(state):
            return state
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        obs_name = name or func.__name__
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            client = get_studio_client()
            if not client:
                # Tracing not initialized
                return await func(*args, **kwargs)
            
            # Get current trace context
            trace_id = get_current_trace()
            if not trace_id:
                # No active trace, skip tracing
                return await func(*args, **kwargs)
            
            # Capture input (if LangGraph state)
            input_data = None
            if args and hasattr(args[0], 'dict'):
                input_data = args[0].dict()
            
            # Create observation
            start_time = time.time()
            obs_id = await client.create_observation(
                trace_id=trace_id,
                name=obs_name,
                type=observation_type,
                input=input_data
            )
            
            # Set as current (for nested calls)
            token = set_current_observation(obs_id)
            
            try:
                # Execute function
                result = await func(*args, **kwargs)
                
                # Capture output
                output_data = None
                if hasattr(result, 'dict'):
                    output_data = result.dict()
                
                # End observation (success)
                await client.end_observation(
                    observation_id=obs_id,
                    output=output_data,
                    level="DEFAULT"
                )
                
                return result
                
            except Exception as e:
                # End observation (error)
                await client.end_observation(
                    observation_id=obs_id,
                    level="ERROR",
                    status_message=str(e)
                )
                raise
                
            finally:
                # Reset context
                set_current_observation(None, token)
        
        return async_wrapper
    
    return decorator
```

**Test:**

```python
@pytest.mark.asyncio
async def test_traced_decorator_captures_state():
    """Verify decorator captures input/output state"""
    # ... implementation
```

---

## 📊 Database Migration

**Task 4.1: Project Table Migration**

```bash
# Generate migration
docker compose exec backend alembic revision --autogenerate -m "Add projects table"

# Apply migration
docker compose exec backend alembic upgrade head
```

**Expected migration:**
- Create `projects` table
- Add indexes on `created_at`, `deleted_at`
- Add foreign key from `traces.project_id` to `projects.id`

**Following Alembic policy:**
- ✅ One migration per PR
- ✅ Single head
- ✅ Test up and down
- ✅ Meaningful downgrade

---

## 🧪 End-to-End Integration Test

**Task 5.1: Complete Flow Test**

**Test scenario:**
1. Start SwisperStudio (backend + frontend)
2. Login with API key
3. Create project "Test Swisper"
4. Run Swisper with SDK configured
5. Send test request to Swisper
6. Verify trace appears in SwisperStudio UI

**Implementation:**

```python
# tests/integration/test_phase1_e2e.py

@pytest.mark.integration
@pytest.mark.asyncio
async def test_phase1_end_to_end_flow():
    """
    Phase 1 complete integration test:
    - Create project
    - Send trace from SDK
    - Retrieve trace via API
    - Verify all data captured
    """
    # 1. Create project
    project = await create_project_via_api(
        name="Test Project",
        swisper_url="http://localhost:8000"
    )
    
    # 2. Initialize SDK
    from swisper_studio_sdk import initialize_tracing
    initialize_tracing(
        api_url="http://localhost:8001",
        api_key="test-api-key",
        project_id=project.id
    )
    
    # 3. Send trace using SDK
    from swisper_studio_sdk import create_traced_graph
    
    graph = create_traced_graph(TestState, trace_name="test_flow")
    graph.add_node("node1", test_node_func)
    
    app = graph.compile()
    result = await app.ainvoke({"value": 0})
    
    # 4. Retrieve trace from API
    traces = await get_traces_via_api(project.id)
    
    # 5. Verify
    assert len(traces.data) == 1
    assert traces.data[0].name == "test_flow"
```

---

## 📋 Implementation Sequence (TDD Workflow)

Following `.cursor/00-workflow.mdc`:

### Week 1: Backend

**Day 1-2:** Analysis ✅ COMPLETE

**Day 3-4:** Project API
1. **TDD Red**: Write tests for Project CRUD
2. **Execute**: Run tests in Docker, verify FAIL
3. **Implement**: Create Project model and routes
4. **Execute**: Run tests in Docker, verify PASS
5. **Refactor**: Apply clean code principles
6. **Execute**: Verify tests still PASS

**Day 5:** Enhanced Trace Ingestion
1. **TDD Red**: Write tests for project-based traces
2. **Execute**: Verify FAIL
3. **Implement**: Add project_id to Trace, validation
4. **Execute**: Verify PASS
5. **Refactor**: Clean up
6. **Execute**: Verify still PASS

### Week 2: Frontend + SDK

**Day 6-7:** Frontend Setup
1. Create Vite + React + MUI project (no TDD - infrastructure)
2. Verify: `npm run dev` works
3. Build login page
4. Build project list page
5. Manual testing

**Day 8-9:** Trace List View
1. Build trace list component
2. Integrate with backend API
3. Test pagination
4. Test filters

**Day 10:** SDK
1. **TDD**: Write SDK tests
2. **Implement**: create_traced_graph() and @traced
3. **Test**: Verify in test Swisper instance

---

## 🎯 Success Criteria

Phase 1 is complete when:

- [ ] ✅ **Backend:**
  - All Project API tests pass (in Docker with -vv)
  - All Trace API tests pass
  - Project → Trace relationship works
  - Pagination works correctly
  - Soft delete works

- [ ] ✅ **Frontend:**
  - Login page works (API key validation)
  - Project list page shows all projects
  - Can create new project
  - Trace list page shows traces from project
  - Pagination works
  - Uses Swisper components (@shiu/*)

- [ ] ✅ **SDK:**
  - create_traced_graph() auto-wraps nodes
  - @traced decorator captures state
  - Traces sent to SwisperStudio
  - No errors in SDK

- [ ] ✅ **Integration:**
  - End-to-end test passes
  - Can see trace in UI after sending from Swisper
  - All data correctly displayed

- [ ] ✅ **Quality:**
  - All linters pass (mypy, ruff, tsc, eslint)
  - No technical debt
  - Clean architecture
  - No hardcoded values
  - Comprehensive tests

---

## ⚠️ Risks & Mitigation

| Risk | Mitigation |
|------|------------|
| MUI integration complexity | Use Swisper theme directly, copy their patterns |
| SDK graph wrapping breaks LangGraph | Thorough testing with real Swisper instance |
| Performance issues with state capture | Async serialization, optimize in Phase 2 if needed |
| API key security | Hash before storage, never log or return raw keys |

---

## 🔗 References to Consult During Implementation

### Langfuse Code
- Project model: `packages/shared/prisma/schema.prisma:130-186`
- Trace ingestion: `packages/shared/src/server/ingestion/`
- Pagination: `.cursor/rules/public-api.mdc`
- Trace list UX: `web/src/components/trace/TraceSearchList.tsx`

### Swisper Code
- Components: `packages/components/src/`
- Icons: `packages/icons/src/`
- Styling patterns: `.cursor/rules/styling.mdc`
- API patterns: `.cursor/rules/api.mdc`
- React patterns: `.cursor/rules/best-practices.mdc`

---

## 📝 Documentation Updates

After Phase 1 implementation:
- [ ] Update `swisper_studio_implementation_plan.md` (mark Phase 1 complete)
- [ ] Create API documentation (OpenAPI spec)
- [ ] Create SDK usage guide
- [ ] Update README with setup instructions

---

**Ready for Implementation:** YES  
**Approved by:** ___________  
**Date:** ___________  

---

**Next Step:** Get user approval, then start TDD workflow! 🚀

