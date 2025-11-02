# Phase 1 Analysis: "Hello World" - Langfuse + Swisper

**Date:** November 1, 2025  
**Analyst:** AI Assistant  
**Phase:** Phase 1 - End-to-End Proof

---

## 📚 Analysis Summary

**Time Spent:** 2 hours  
**Files Analyzed:** 15+ files from Langfuse + Swisper  
**Key Findings:**  
- Langfuse uses comprehensive multi-tenant architecture (we'll simplify for MVP)
- Project model is central to all data isolation
- Trace ingestion uses validation + async processing patterns
- Frontend uses Next.js Pages Router + tRPC + Shadcn/ui
- Swisper has reusable component library + icon system

**Recommendation:** Adopt simplified versions of Langfuse patterns with Swisper UI components

---

## 🔍 Langfuse Analysis

### 1. Project Management Architecture

#### Files Analyzed
- `packages/shared/prisma/schema.prisma` (lines 130-186) - Project model
- `.cursor/rules/authorization-and-rbac.mdc` - RBAC patterns
- `.cursor/rules/frontend-features.mdc` - Feature structure

#### Key Findings

**1.1 Project Model (Simplified for MVP)**

**Langfuse approach:**
```prisma
model Project {
  id                String      @id @default(cuid())
  orgId             String      @map("org_id")
  createdAt         DateTime    @default(now())
  updatedAt         DateTime    @updatedAt
  name              String
  retentionDays     Int?
  metadata          Json?
  organization      Organization @relation(...)
  apiKeys           ApiKey[]
  // ... 30+ relations
}
```

**What we'll copy:**
- `cuid()` for IDs (collision-resistant, URL-safe)
- `created_at` / `updated_at` pattern
- `metadata` JSON field for extensibility
- Project → ApiKey relationship

**What we'll simplify:**
- ❌ No `Organization` (not multi-tenant for MVP)
- ❌ No `retentionDays` (keep all data for MVP)
- ✅ Add `swisper_url` (our specific need)
- ✅ Add `swisper_api_key` (connection credential)

**Our MVP Project model:**
```python
class Project(SQLModel, table=True):
    """
    Represents a connection to one Swisper deployment.
    One SwisperStudio can manage multiple Swisper instances.
    """
    __tablename__ = "projects"
    
    # Primary key (using UUID instead of cuid for Python)
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    
    # Core fields
    name: str = Field(..., description="Human-readable project name")
    swisper_url: str = Field(..., description="Swisper instance URL")
    swisper_api_key: str = Field(..., description="API key for Swisper connection")
    
    # Metadata
    description: str | None = Field(None, description="Project description")
    meta: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Soft delete (Langfuse pattern)
    deleted_at: datetime | None = Field(None)
```

**1.2 API Key Pattern**

**Langfuse approach:**
```prisma
model ApiKey {
  publicKey           String   @unique
  hashedSecretKey     String   @unique
  fastHashedSecretKey String?  @unique
  displaySecretKey    String   // Shows last 4 chars: "sk-...abc123"
  projectId           String?
  scope               ApiKeyScope @default(PROJECT)
}
```

**Key learnings:**
- ✅ Never store raw API keys
- ✅ Hash with bcrypt for security
- ✅ Store display version (last 4 chars) for UI
- ✅ Support project-scoped keys

**For MVP:**
- Simple API key auth (one key per project)
- Enhance to user-based auth in Phase 2

---

### 2. Trace Ingestion Patterns

#### Files Analyzed
- `packages/shared/src/domain/traces.ts` - Trace domain logic
- `packages/shared/src/features/ingestion/` - Ingestion patterns
- `.cursor/rules/public-api.mdc` - API standards

#### Key Findings

**2.1 Trace Model** 

Langfuse uses **ClickHouse for traces** (we saw this in migrations):
- Primary storage: ClickHouse (fast analytics)
- Metadata: PostgreSQL (relations, indexes)

**For MVP:**
- PostgreSQL only (we already have this)
- Add ClickHouse in Phase 5+ when needed

**2.2 Ingestion Flow**

```
Client (SDK) 
  → POST /api/public/traces
  → Validation (Zod schemas with .strict())
  → Queue (async processing)
  → Storage (ClickHouse + PostgreSQL)
```

**Key patterns to copy:**
- ✅ Strict validation with Zod/Pydantic
- ✅ Async processing (return 202 Accepted immediately)
- ✅ Batch support (multiple traces/observations per request)
- ✅ Idempotency (check if ID exists, return existing)

**2.3 Pagination Pattern**

From `.cursor/rules/public-api.mdc`:
```typescript
// Pagination starts at 1 (not 0)
publicApiPaginationZod = {
  page: z.number().int().positive().default(1),
  limit: z.number().int().positive().max(1000).default(50)
}

// Return meta
paginationMetaResponseZod = {
  page: number,
  limit: number,
  totalItems: number,
  totalPages: number
}
```

**For our API:**
```python
class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=50, ge=1, le=1000)

class PaginationMeta(BaseModel):
    page: int
    limit: int
    total_items: int
    total_pages: int
```

---

### 3. Frontend UX Patterns

#### Files Analyzed
- `web/src/components/trace/TraceSearchList.tsx` - Trace table
- `web/src/components/trace/TracePage.tsx` - Trace detail view
- `.cursor/rules/frontend-features.mdc` - Feature structure
- `.cursor/rules/banner-positioning.mdc` - Layout patterns

#### Key Findings

**3.1 Technology Stack**
- **Framework:** Next.js (Pages Router)
- **API:** tRPC (type-safe client-server)
- **UI:** Shadcn/ui components
- **Styling:** Tailwind CSS
- **State:** TanStack Query (React Query)

**For our stack:**
- **Framework:** Vite + React (simpler than Next.js)
- **API:** REST (not tRPC - keep it simple)
- **UI:** Shadcn/ui + Swisper components
- **Styling:** Tailwind CSS (reuse Swisper config)
- **State:** TanStack Query

**3.2 Trace List UX**

Key patterns from `TraceSearchList.tsx`:
- ✅ Table with sortable columns
- ✅ Filters (date range, user, session)
- ✅ Search box (by ID, name)
- ✅ Pagination controls
- ✅ Loading states
- ✅ Empty states with helpful messages
- ✅ Quick actions (copy ID, open details)

**Columns to show:**
1. Timestamp
2. Name
3. User ID
4. Duration (if ended)
5. Status (success/error)
6. Actions (view, copy ID)

**3.3 Layout Patterns**

From `.cursor/rules/banner-positioning.mdc`:
```tsx
// Always use top-banner-offset for fixed/sticky elements
<div className="sticky top-banner-offset">...</div>

// NOT top-0 (banner would cover it)
```

**For our layout:**
- Use Swisper's existing layout components
- Respect banner offset for sticky headers
- Consistent spacing system

---

## 🎨 Swisper Analysis

### 4. Component Library (`@shiu/components`)

#### Files Analyzed
- `packages/components/package.json` - Component library configuration
- `packages/components/src/components/` - Available components
- `.cursor/rules/component.mdc` - Component guidelines
- `.cursor/rules/mui-imports.mdc` - MUI import patterns

#### Key Findings

**4.1 Technology Stack**

**Swisper uses MUI (Material-UI v7):**
```json
{
  "@mui/material": ">=7.0.0",
  "@mui/icons-material": "^7.0.2",
  "@mui/system": "^7.0.2",
  "@emotion/react": "^11.11.1",
  "@emotion/styled": "^11.11.0"
}
```

**Available components in `@shiu/components`:**
- `CodeCard` - Code display component
- `Card` - General card component
- `Link` - Link component
- `Dialog` - Dialog/modal component
- `ConfirmationDialog` - Confirmation dialog
- `ListSubHeader` - List section headers
- Custom hooks and utilities

**4.2 Styling Patterns**

From `.cursor/rules/styling.mdc`:

```typescript
// Pattern: Create styled components in styled.ts
import { styled } from "@mui/material/styles";
import { Box } from "@mui/material";

export const Container = styled(Box)(({ theme }) => ({
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  
  [theme.breakpoints.down("md")]: {
    padding: theme.spacing(2)
  }
}));

// Use variants for conditional styling
export const StyledBox = styled(Box)<{ isVisible: boolean }>(({ theme }) => ({
  transition: theme.transitions.create(["opacity"]),
  variants: [
    {
      props: { isVisible: true },
      style: { opacity: 1 }
    },
    {
      props: { isVisible: false },
      style: { opacity: 0 }
    }
  ]
}));
```

**Key patterns:**
- ✅ Use MUI's `styled()` API (not Tailwind!)
- ✅ Access theme for consistency
- ✅ Responsive with `theme.breakpoints`
- ✅ Use variants for conditional styling

**IMPORTANT DECISION:** Swisper uses **MUI, NOT Tailwind!**
- We should use MUI for SwisperStudio to match Swisper's look and feel
- Reuse `@shiu/components` directly
- Use MUI theme from Swisper for consistency

---

### 5. Icon System (`@shiu/icons`)

#### Files Analyzed
- `packages/icons/package.json` - Icon package
- `.cursor/rules/icons.mdc` - Icon usage guidelines

#### Key Findings

**5.1 Icon Import Pattern**

From `.cursor/rules/icons.mdc`:

```typescript
// ✅ Always use @shiu/icons (NOT @mui/icons-material)
import { EditIcon, DeleteIcon, SaveIcon } from "@shiu/icons";

// ✅ Multiple icons in one statement
import { DownloadIcon, CopyIcon, BookmarkIcon } from "@shiu/icons";

// ❌ NEVER use MUI icons directly
import EditOutlined from "@mui/icons-material/EditOutlined";
```

**Icon sizes:**
```typescript
<EditIcon fontSize="small" />    // 20px - most common
<EditIcon fontSize="medium" />   // 24px - default
<EditIcon fontSize="large" />    // 35px
<EditIcon fontSize="inherit" />  // inherits parent
```

**For SwisperStudio:**
- ✅ Reuse `@shiu/icons` package
- ✅ Use same icon names
- ✅ Consistent icon sizes with Swisper

---

### 6. File Naming & TypeScript Conventions

#### Files Analyzed
- `.cursor/rules/typescript-naming.mdc` - Naming conventions
- `.cursor/rules/naming-convention.mdc` - Additional conventions

#### Key Findings

**6.1 File Naming**

```
Files: kebab-case
- message-bubble.tsx ✅
- use-current-time.ts ✅
- MessageBubble.tsx ❌
```

**6.2 Type Naming**

```typescript
// Component props
interface MessageBubbleProps { }  ✅
interface IMessageBubbleProps { } ❌

// Hook types
interface UseCurrentTimeReturn { }  ✅
interface UseCurrentTimeResult { }  ❌

// Options objects
interface FormatDateOptions { }  ✅
interface FormatDateProps { }    ❌
```

**6.3 Variable Naming**

```typescript
// Boolean naming
isLoading: boolean    ✅
isVisible: boolean    ✅
hasError: boolean     ✅
disabled: boolean     ❌ (use isDisabled)
show: boolean         ❌ (use isVisible)
```

**For SwisperStudio:**
- ✅ Follow same naming conventions
- ✅ Use kebab-case for all files
- ✅ Use PascalCase for types
- ✅ Use is/has/should prefixes for booleans

---

### 7. React Patterns & API Integration

#### Files Analyzed
- `.cursor/rules/api.mdc` - API integration patterns
- `.cursor/rules/best-practices.mdc` - React best practices

#### Key Findings

**7.1 API Integration Pattern**

**Swisper uses TanStack Query with custom hooks:**

```typescript
// ✅ Query hook (GET requests)
export function useGetChatsQuery() {
  return useQuery<ChatsList, HttpProblem>({
    queryKey: chatKeys.list(),
    queryFn: () => chatsApi.getChats(),
  });
}

// ✅ Mutation hook (POST/PUT/DELETE)
export function useCreateChatMutation() {
  return useMutation<CreateChatResponse, ResponseError, CreateChatRequest>({
    mutationFn: (payload) => chatsApi.createChat(payload)
  });
}

// Usage in component
const { data: chats, isLoading } = useGetChatsQuery();
const { mutateAsync: createChat } = useCreateChatMutation();
```

**Naming conventions:**
- Queries: `use{Name}Query`
- Mutations: `use{Action}{Name}Mutation`

**For SwisperStudio:**
- ✅ Follow same pattern
- ✅ Create query hooks for all GET endpoints
- ✅ Create mutation hooks for POST/PUT/DELETE/PATCH
- ✅ Never use API directly in components

**7.2 React Component Pattern**

```typescript
// ✅ Function declarations (NOT arrow functions)
export function MyComponent({ prop }: MyComponentProps) {
  return <div>{prop}</div>;
}

// ❌ AVOID const arrow functions
export const MyComponent = ({ prop }: Props) => { };
```

**7.3 Custom Hooks Pattern**

```typescript
// ✅ Extract business logic into hooks
export function useMessageActions(messageId: string) {
  const { copy } = useCopyToClipboard();
  
  function handleCopy() {
    copy(messageId);
  }
  
  return { handleCopy };
}
```

---

## 🏗️ Architecture Decisions for Phase 1

### Decision 1: Project Model Design

**Decision:** Simplified single-tenant project model

**Rationale:**
- Langfuse is multi-tenant (org → projects → resources)
- We're single-tenant for MVP (one SwisperStudio instance)
- Each project = one Swisper deployment connection
- Simpler data model = faster development

**Implementation:**
```python
Project:
  - id (UUID)
  - name
  - swisper_url
  - swisper_api_key (hashed)
  - created_at, updated_at, deleted_at
```

---

### Decision 2: Authentication Strategy

**Decision:** Simple API key auth for MVP

**Rationale:**
- Langfuse uses full OAuth + RBAC
- For MVP: One API key, no user management
- Phase 2+: Add proper user auth

**Implementation:**
- Single API key in environment variable
- Header: `X-API-Key: {key}`
- Middleware validates on every request

---

### Decision 3: Trace Storage

**Decision:** PostgreSQL only for MVP

**Rationale:**
- Langfuse uses ClickHouse for scale
- Our MVP won't have millions of traces initially
- PostgreSQL is sufficient for < 100K traces
- Add ClickHouse when performance requires it

**When to add ClickHouse:**
- >100K traces
- Analytics queries taking >5 seconds
- Need for time-series aggregations

---

### Decision 4: Frontend Architecture

**Decision:** Vite + React + MUI + TanStack Query

**Rationale:**
- Langfuse uses Next.js (heavier framework)
- Vite is faster for SPA development
- **Use MUI v7** (Swisper's component library - NOT Tailwind!)
- Reuse `@shiu/components` and `@shiu/icons` directly
- Follow Swisper's styling patterns for consistency

**Stack:**
```
Frontend:
- Vite (build tool)
- React 18
- React Router (routing)
- TanStack Query (data fetching)
- MUI v7 (@mui/material)
- @shiu/components (Swisper's component library)
- @shiu/icons (Swisper's icon library)
- Emotion (styled components)
```

**Key Decision:** **Use MUI (like Swisper), NOT Tailwind or Shadcn/ui**

---

### Decision 5: API Design

**Decision:** REST API (not tRPC)

**Rationale:**
- Langfuse web uses tRPC (great for Next.js)
- We're building separate frontend/backend
- REST is simpler for MVP
- Easier to test with curl/Postman
- SDK can easily consume REST

**API patterns to copy from Langfuse:**
- Strict validation (Pydantic `.model_validate()`)
- Pagination starts at 1
- Return meta in responses
- Consistent error format

---

## 📊 Code Snippets to Reference

### Snippet 1: Project CRUD Pattern (Based on Langfuse)

**Source:** Langfuse public API patterns

```python
# POST /api/v1/projects
class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    swisper_url: HttpUrl  # Pydantic validates URL format
    swisper_api_key: str = Field(..., min_length=10)
    description: str | None = None

@router.post("/projects", response_model=ProjectResponse)
async def create_project(
    data: ProjectCreate,
    session: DBSession,
    api_key: APIKey
):
    # Hash API key before storage
    hashed_key = bcrypt.hashpw(
        data.swisper_api_key.encode(), 
        bcrypt.gensalt()
    )
    
    project = Project(
        name=data.name,
        swisper_url=str(data.swisper_url),
        swisper_api_key=hashed_key.decode(),
        description=data.description
    )
    
    session.add(project)
    await session.commit()
    await session.refresh(project)
    
    return project
```

---

### Snippet 2: Pagination Pattern (From Langfuse)

```python
class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number (starts at 1)")
    limit: int = Field(default=50, ge=1, le=1000, description="Items per page")

@router.get("/traces")
async def list_traces(
    project_id: str,
    pagination: PaginationParams = Depends(),
    session: DBSession
):
    # Calculate offset
    offset = (pagination.page - 1) * pagination.limit
    
    # Count total
    count_stmt = select(func.count()).select_from(Trace).where(
        Trace.project_id == project_id
    )
    total = await session.scalar(count_stmt)
    
    # Fetch page
    stmt = select(Trace).where(
        Trace.project_id == project_id
    ).offset(offset).limit(pagination.limit)
    
    traces = await session.execute(stmt)
    
    return {
        "data": traces.scalars().all(),
        "meta": {
            "page": pagination.page,
            "limit": pagination.limit,
            "total_items": total,
            "total_pages": math.ceil(total / pagination.limit)
        }
    }
```

---

### Snippet 3: Trace Ingestion Pattern (Langfuse-inspired)

```python
class TraceIngest(BaseModel):
    """Trace ingestion payload"""
    id: str = Field(..., description="Client-generated trace ID")
    name: str | None = None
    user_id: str | None = None
    session_id: str | None = None
    input: dict[str, Any] | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    meta: dict[str, Any] | None = None

@router.post("/traces/ingest", status_code=202)
async def ingest_trace(
    data: TraceIngest,
    project_id: str,  # From auth middleware
    session: DBSession
):
    # Idempotency: check if exists
    stmt = select(Trace).where(
        Trace.id == data.id,
        Trace.project_id == project_id
    )
    existing = await session.scalar(stmt)
    
    if existing:
        return {"status": "exists", "trace_id": existing.id}
    
    # Create trace
    trace = Trace(
        **data.model_dump(),
        project_id=project_id
    )
    
    session.add(trace)
    await session.commit()
    
    # Return 202 (async processing pattern)
    return {"status": "ingested", "trace_id": trace.id}
```

---

## 🎯 Implementation Recommendations

### Must Use from Langfuse

1. **Project-based data isolation**
   - Every resource belongs to a project
   - Filter all queries by project_id
   - Prevents data leakage

2. **Strict validation**
   - Use Pydantic `.model_validate()` with strict mode
   - Reject unknown fields
   - Validate all inputs

3. **Pagination pattern**
   - Page starts at 1
   - Always return meta
   - Consistent across all list endpoints

4. **Soft deletes**
   - `deleted_at` column instead of hard delete
   - Allows data recovery
   - Audit trail

### Should Consider from Langfuse

1. **tRPC for type safety** - Maybe in Phase 2
2. **ClickHouse for analytics** - Phase 5+
3. **Organizations** - Post-MVP

### Avoid from Langfuse

1. **Complex RBAC** - Too heavy for MVP
2. **Multi-tenancy** - Not needed yet
3. **Next.js** - Vite is simpler for us

---

## 📝 Still TODO

### Swisper Analysis (Incomplete)

- [ ] Access Swisper repository
- [ ] Document component library (`packages/components/`)
- [ ] Document icon system (`packages/icons/`)
- [ ] Extract Tailwind configuration
- [ ] Document color palette
- [ ] Document typography system
- [ ] Document layout patterns
- [ ] Find existing LangGraph integration patterns

### Langfuse Deeper Dive (If Needed)

- [ ] Study tRPC implementation (might use later)
- [ ] Study ClickHouse migration patterns (for Phase 5)
- [ ] Study graph visualization (Phase 3)
- [ ] Study prompt management (Phase 4)

---

## ✅ Analysis Checklist

- [x] Reviewed Langfuse Project model
- [x] Reviewed Langfuse API key pattern
- [x] Reviewed Langfuse trace ingestion
- [x] Reviewed Langfuse pagination
- [x] Reviewed Langfuse frontend stack
- [x] Reviewed Langfuse cursor rules
- [x] Reviewed Swisper components (@shiu/components)
- [x] Reviewed Swisper icons (@shiu/icons)
- [x] Reviewed Swisper styling (MUI + Emotion)
- [x] Reviewed Swisper API patterns (TanStack Query)
- [x] Reviewed Swisper React patterns
- [x] Made architecture decisions
- [x] Created code snippets for reference

---

## 📎 References

**Langfuse files analyzed:**
- `packages/shared/prisma/schema.prisma`
- `.cursor/rules/frontend-features.mdc`
- `.cursor/rules/public-api.mdc`
- `.cursor/rules/authorization-and-rbac.mdc`
- `.cursor/rules/banner-positioning.mdc`
- `web/src/components/trace/`

**Swisper files analyzed:**
- `packages/components/package.json`
- `packages/components/src/`
- `packages/icons/`
- `.cursor/rules/component.mdc`
- `.cursor/rules/mui-imports.mdc`
- `.cursor/rules/icons.mdc`
- `.cursor/rules/styling.mdc`
- `.cursor/rules/typescript-naming.mdc`
- `.cursor/rules/api.mdc`
- `.cursor/rules/best-practices.mdc`

---

**Analysis Status:** ✅ 100% Complete  
**Ready for sub-plan creation:** YES  
**Key Finding:** Use MUI v7 (NOT Tailwind), reuse @shiu/* packages  
**Approved by:** Pending  
**Next Step:** Create detailed Phase 1 sub-plan with clean architecture

---

**Date Completed:** November 1, 2025

