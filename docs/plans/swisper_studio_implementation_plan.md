# Swisper Prompt Studio - Implementation Plan

**Version:** 1.0  
**Status:** ✅ Approved  
**Start Date:** TBD  
**Target Completion:** 6-8 weeks  
**Last Updated:** 2025-10-09

---

## Table of Contents

1. [Current Codebase Analysis](#1-current-codebase-analysis)
2. [Architecture Overview](#2-architecture-overview)
3. [Touch Point Analysis](#3-touch-point-analysis)
4. [Implementation Phases](#4-implementation-phases)
5. [Database Schema](#5-database-schema)
6. [Testing Strategy](#6-testing-strategy)
7. [Deployment & Rollback](#7-deployment--rollback)

---

## 1. Current Codebase Analysis

### 1.1 Backend Structure Analysis

**Existing File Structure:**
```
backend/app/
├── main.py                          ← Touch point #1 (3 lines)
├── models.py                        ← Touch point #2 (1 field)
├── core/
│   ├── config.py                    ← Touch point #3 (1 setting)
│   └── db.py                        (No changes)
├── api/
│   ├── main.py                      ← Touch point #4 (1 line)
│   ├── deps.py                      ← Touch point #5 (new function)
│   ├── routes/                      (Existing routes - NO CHANGES)
│   │   ├── chats.py
│   │   ├── users.py
│   │   ├── login.py
│   │   └── ...
│   └── services/
│       ├── agents/                  (NO CHANGES to existing)
│       │   └── global_supervisor/
│       │       └── nodes/
│       │           ├── user_interface_node.py
│       │           └── prompts/*.md (Studio reads these)
│       └── prompt_studio/           ← NEW MODULE (isolated)
│           └── (All Studio code here)
```

**Key Finding:** 
- ✅ Clean separation already exists (`services/` for business logic)
- ✅ Route registration pattern well-established (`api/main.py`)
- ✅ Auth uses JWT with `User.is_superuser` (can reuse)

**What This Means for Studio:**
- ✅ Studio will follow existing patterns (not introducing new architecture)
- ✅ Can reuse `CurrentUser` dependency (already implemented)
- ✅ Can reuse `SessionDep` pattern (already implemented)

---

### 1.2 Frontend Structure Analysis

**Existing File Structure:**
```
frontend/src/
├── main.tsx                         (No changes)
├── router/
│   ├── Router.tsx                   (No changes - uses RouteDefinition)
│   └── RouteDefinition.tsx          ← Touch point #1 (add Studio route)
├── features/                        (Existing features - NO CHANGES)
│   ├── auth/
│   ├── chat/
│   ├── login/
│   ├── preferences/
│   └── sidemenu/                    ← Touch point #2 (add nav item)
│       └── components/
│           └── SideMenu.tsx
└── domain/
    └── auth/
        └── components/
            ├── AuthorizedLayout.tsx  (Can reuse for Studio)
            └── UnauthorizedLayout.tsx
```

**Key Finding:**
- ✅ Domain-driven structure (`domain/` for shared, `features/` for pages)
- ✅ Auth layouts already exist (can wrap Studio routes)
- ✅ Route registration is simple array push

**What This Means for Studio:**
- ✅ Studio goes in `features/promptStudio/` (follows pattern)
- ✅ Can wrap with `<AuthorizedLayout>` (reuse existing)
- ✅ One-line change to add route

---

### 1.3 Auth System Analysis

**Current Implementation:**

```python
# backend/app/models.py
class User(UserBase, table=True):
    id: uuid.UUID
    email: EmailStr
    hashed_password: str
    is_active: bool = False
    is_superuser: bool = False  ← EXISTING (can reuse!)
    # ... other fields ...
```

**Key Finding:**
- ✅ Already have `is_superuser` field (don't need new `is_admin`)
- ✅ JWT creation in `app/core/security.py`
- ✅ Dependency `get_current_active_superuser` exists

**What This Means for Studio:**
- ✅ Zero auth changes needed
- ✅ Just check `user.is_superuser` in frontend
- ✅ Use existing `get_current_active_superuser` dependency in backend

---

### 1.4 Testing Pattern Analysis

**Current Test Structure:**

```
backend/tests/
├── conftest.py                      (Shared fixtures)
├── integration/                     (E2E tests with real infra)
│   └── test_greeting_frequency_e2e.py
├── api/services/                    (Integration tests)
│   └── test_global_supervisor_focused.py
└── test_*.py                        (Unit tests)
```

**Pattern Observed:**
```python
# Fixture-based mocking
@pytest.fixture
def mock_llm_adapter():
    adapter = Mock(spec=LLMAdapterInterface)
    adapter.get_structured_output = AsyncMock()
    return adapter

# Integration tests use real DB
@pytest.mark.asyncio
async def test_with_real_db(db_session):
    # Uses actual database
    ...
```

**What This Means for Studio:**
- ✅ Follow same pattern (fixtures in conftest)
- ✅ Unit tests: Mock everything
- ✅ Integration tests: Real DB, mock LLM
- ✅ E2E tests: Real everything

---

## 2. Architecture Overview

### 2.1 System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│ Frontend (React + TypeScript)                                    │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  features/chat/                    ← EXISTING (untouched)        │
│  features/preferences/             ← EXISTING (untouched)        │
│  features/auth/                    ← EXISTING (untouched)        │
│                                                                   │
│  features/promptStudio/            ← NEW (isolated module)       │
│  ├── components/                                                 │
│  │   ├── FragmentLibrary.tsx       (List all prompts)           │
│  │   ├── Editor.tsx                (Monaco editor)              │
│  │   ├── PlaceholderBrowser.tsx    (Sidebar with fields)        │
│  │   ├── CompositionPreview.tsx    (Show assembled prompt)      │
│  │   ├── VersionHistory.tsx        (Version list)               │
│  │   ├── TestModeSetup.tsx         (Test configuration)         │
│  │   └── Analytics.tsx             (Metrics dashboard)          │
│  ├── api/                                                        │
│  │   └── studioApi.ts              (API client)                 │
│  ├── hooks/                                                      │
│  │   ├── useFragments.ts                                        │
│  │   ├── useVersions.ts                                         │
│  │   └── useTestMode.ts                                         │
│  └── index.tsx                     (Entry point)                │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
                              ↓ HTTP/REST
┌──────────────────────────────────────────────────────────────────┐
│ Backend (FastAPI + Python)                                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  api/routes/                       ← EXISTING (untouched)        │
│  ├── chats.py                                                    │
│  ├── users.py                                                    │
│  └── ...                                                         │
│                                                                   │
│  api/routes/prompt_studio.py      ← NEW (isolated router)       │
│  ├── GET /fragments                                              │
│  ├── GET /fragments/{id}                                         │
│  ├── POST /fragments/{id}/versions                              │
│  ├── GET /versions/{id}                                          │
│  ├── POST /versions/{id}/publish                                │
│  ├── POST /test-sessions                                         │
│  └── GET /analytics/{version_id}                                │
│                                                                   │
│  api/services/prompt_studio/       ← NEW (isolated module)       │
│  ├── middleware.py                 (File interception)          │
│  ├── state_inspector.py            (Discover placeholders)      │
│  ├── version_manager.py            (Version lifecycle)          │
│  ├── test_session_manager.py       (Test mode)                  │
│  ├── validator.py                  (Placeholder validation)     │
│  ├── renderer.py                   (Test rendering)             │
│  └── analytics.py                  (Metrics collection)         │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ Database (PostgreSQL)                                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  EXISTING TABLES (untouched):                                    │
│  ├── users                                                       │
│  ├── chats                                                       │
│  ├── messages                                                    │
│  └── ...                                                         │
│                                                                   │
│  NEW TABLES (isolated):                                          │
│  ├── prompt_fragments                                            │
│  ├── prompt_versions                                             │
│  ├── prompt_test_sessions                                        │
│  └── prompt_execution_logs                                       │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 Module Boundaries (Critical for Isolation)

**Dependency Flow:**

```
✅ ALLOWED:
- Studio → Core models (User, Session)
- Studio → Core deps (get_current_user, SessionDep)
- Studio → Config (settings)

❌ FORBIDDEN:
- Core → Studio (core should not import Studio)
- Studio → Domain agents (read only via filesystem)
- Studio → Chat routes (no coupling)

⚠️ TOUCH POINTS (Minimal):
- main.py: Register Studio middleware (if feature flag enabled)
- api/main.py: Register Studio router (if feature flag enabled)
- User model: Already has is_superuser (reuse)
```

**Enforcement:**
```python
# In Studio module __init__.py
"""
Prompt Studio - Isolated Module

DEPENDENCY RULES:
- Can import from: app.models, app.core, app.api.deps
- Cannot import from: app.api.routes.*, app.api.services.agents.*
- Must never modify: Core business logic, domain agents

If you need to integrate, use dependency injection, not direct imports.
"""
```

---

## 3. Touch Point Analysis

### 3.1 Backend Touch Points (5 files)

#### **File 1: backend/app/core/config.py**

**Current State:**
```python
class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["local", "staging", "dev", "production"] = "local"
    VOICE_ENABLED: bool = True
    TTS_ENABLED: bool = True
    # ... other settings ...
```

**Change Required:**
```python
# Add one setting (line ~45)
PROMPT_STUDIO_ENABLED: bool = False  # Feature flag - OFF by default
```

**Risk:** Minimal (adding one field)

**Test Required:**
```python
def test_prompt_studio_disabled_by_default():
    from app.core.config import settings
    assert settings.PROMPT_STUDIO_ENABLED == False
```

---

#### **File 2: backend/app/models.py**

**Current State:**
```python
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    is_active: bool = False
    is_superuser: bool = False  ← ALREADY EXISTS!
    # ...
```

**Change Required:**
```
NO CHANGES NEEDED!
```

**Reason:** We'll reuse `is_superuser` instead of adding `is_admin`.

**Test Required:**
```python
def test_superuser_flag_exists():
    """Verify User model has is_superuser field"""
    from app.models import User
    assert hasattr(User, 'is_superuser')
```

---

#### **File 3: backend/app/main.py**

**Current State:**
```python
from app.api.main import api_router
from app.core.config import settings

# ... lifespan, CORS, etc ...

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(CORSMiddleware, ...)

# Register routes
app.include_router(api_router, prefix=settings.API_V1_STR)
```

**Change Required:**
```python
# Add AFTER line 72 (after include_router)

# Prompt Studio middleware (feature-flagged)
if settings.PROMPT_STUDIO_ENABLED:
    try:
        from app.api.services.prompt_studio.middleware import enable_prompt_interception
        enable_prompt_interception()
        logger.info("✅ Prompt Studio middleware enabled")
    except Exception as e:
        logger.error(f"Failed to enable Prompt Studio: {e}")
        logger.info("Core app continues without Studio")
```

**Risk:** Low (feature flag OFF by default, try/catch wraps Studio import)

**Test Required:**
```python
def test_app_starts_without_studio():
    """Verify app starts normally when Studio disabled"""
    from app.main import app
    assert app is not None

def test_app_starts_with_studio_enabled(monkeypatch):
    """Verify app starts when Studio enabled"""
    monkeypatch.setenv("PROMPT_STUDIO_ENABLED", "true")
    from app.main import app
    assert app is not None
```

---

#### **File 4: backend/app/api/main.py**

**Current State:**
```python
from app.api.routes import chats, configuration, experiments
from fastapi import APIRouter
from app.api.routes import login, private, users, utils, feedback, email_auth, telegram, wealthos
from app.api.routers import user_facts, presentation_rules, user_preferences, people
from app.api.services.voice.voice_router import router as voice_router
from app.api.services.voice.tts_router import router as tts_router

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
# ... many includes ...

if settings.VOICE_ENABLED:
    api_router.include_router(voice_router, prefix="/voice")

if settings.TTS_ENABLED:
    api_router.include_router(tts_router, prefix="/tts", tags=["tts"])
```

**Change Required:**
```python
# Add AFTER line 43 (after metrics_router)

# Prompt Studio routes (feature-flagged)
if settings.PROMPT_STUDIO_ENABLED:
    from app.api.routes import prompt_studio
    api_router.include_router(
        prompt_studio.router, 
        prefix="/prompt-studio", 
        tags=["prompt-studio"]
    )
```

**Risk:** Low (follows existing pattern for conditional routers)

**Test Required:**
```python
def test_studio_routes_not_registered_when_disabled():
    """Verify Studio routes not in router when disabled"""
    from app.api.main import api_router
    routes = [route.path for route in api_router.routes]
    assert not any('/prompt-studio' in route for route in routes)

def test_studio_routes_registered_when_enabled(monkeypatch):
    """Verify Studio routes registered when enabled"""
    monkeypatch.setenv("PROMPT_STUDIO_ENABLED", "true")
    # Re-import to pick up env change
    import importlib
    import app.api.main as main_module
    importlib.reload(main_module)
    routes = [route.path for route in main_module.api_router.routes]
    assert any('/prompt-studio' in route for route in routes)
```

---

#### **File 5: backend/app/api/deps.py**

**Current State:**
```python
CurrentUser = Annotated[User, Depends(get_current_user)]

def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
```

**Change Required:**
```python
# Add AFTER line 92 (after get_current_active_superuser)

def get_studio_user(current_user: CurrentUser) -> User:
    """
    Dependency for Prompt Studio access.
    Requires superuser privileges.
    
    Usage:
        @router.get("/fragments")
        async def list_fragments(user: User = Depends(get_studio_user)):
            ...
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, 
            detail="Prompt Studio access requires superuser privileges"
        )
    return current_user

# Type alias for convenience
StudioUser = Annotated[User, Depends(get_studio_user)]
```

**Risk:** Minimal (adding one function, no side effects)

**Test Required:**
```python
def test_studio_user_blocks_non_superuser():
    """Verify non-superuser cannot access Studio"""
    from app.api.deps import get_studio_user
    mock_user = Mock(is_superuser=False)
    
    with pytest.raises(HTTPException) as exc:
        get_studio_user(mock_user)
    assert exc.value.status_code == 403

def test_studio_user_allows_superuser():
    """Verify superuser can access Studio"""
    from app.api.deps import get_studio_user
    mock_user = Mock(is_superuser=True, id="user-123")
    
    result = get_studio_user(mock_user)
    assert result.id == "user-123"
```

---

### 3.2 Frontend Touch Points (2 files)

#### **File 1: frontend/src/router/RouteDefinition.tsx**

**Current State:**
```typescript
export const routeDefinition: RouteDefinition[] = [
  {
    path: '/',
    exact: true,
    title: 'Swisper Landing',
    element: (
      <AuthorizedLayout>
        <ChatPage />
      </AuthorizedLayout>
    ),
  },
  // ... other routes ...
];
```

**Change Required:**
```typescript
// Add AFTER line 128 (before mocks conditional)

{
  path: '/prompt-studio/*',
  exact: false,
  title: 'Prompt Studio',
  element: (
    <AuthorizedLayout>
      <PromptStudioPage />
    </AuthorizedLayout>
  ),
},
```

**With lazy loading:**
```typescript
// At top of file
const PromptStudioPage = lazy(() => 
  import('../features/promptStudio').catch(err => {
    console.error('Failed to load Prompt Studio:', err);
    return { default: () => <div>Prompt Studio unavailable</div> };
  })
);
```

**Risk:** Low (adding one route, lazy loaded)

**Test Required:**
```typescript
describe('RouteDefinition', () => {
  it('should include prompt studio route', () => {
    const studioRoute = routeDefinition.find(r => r.path === '/prompt-studio/*');
    expect(studioRoute).toBeDefined();
  });
});
```

---

#### **File 2: frontend/src/features/sidemenu/components/SideMenu.tsx**

**Current State:**
```typescript
// frontend/src/features/account/components/account-menu/account-menu.tsx

export function AccountMenu({ anchorEl, open, onClose, ...rest }: AccountMenuProps) {
  return (
    <Menu>
      <UserPersonalityItemOption />
      <Divider />
      
      <AccountMenuItemOption
        id="settings"
        onClick={handleOptionClick}
        icon={<SettingsIcon />}
        label={'Settings'}
      />
      
      <AccountMenuItemOption
        id="logout"
        onClick={handleOptionClick}
        icon={<LogoutIcon />}
        label={'Logout'}
      />
    </Menu>
  );
}
```

**Change Required:**
```typescript
// Add new menu item AFTER "Settings", BEFORE "Logout"
// Only show for superusers

import { PaletteIcon } from '@shiu/icons';  // Or appropriate icon
import { useAuth } from '@/domain/auth/hooks';

export function AccountMenu({ anchorEl, open, onClose, ...rest }: AccountMenuProps) {
  const { user } = useAuth();
  const isSuperuser = user?.is_superuser || false;
  
  return (
    <Menu>
      <UserPersonalityItemOption />
      <Divider />
      
      <AccountMenuItemOption
        id="settings"
        onClick={handleOptionClick}
        icon={<SettingsIcon />}
        label={'Settings'}
      />
      
      {/* NEW: Prompt Studio menu item (superuser only) */}
      {isSuperuser && (
        <AccountMenuItemOption
          id="prompt-studio"
          onClick={handleOptionClick}
          icon={<PaletteIcon />}
          label={'Prompt Studio'}
        />
      )}
      
      <AccountMenuItemOption
        id="logout"
        onClick={handleOptionClick}
        icon={<LogoutIcon />}
        label={'Logout'}
      />
    </Menu>
  );
}
```

**Update hooks:**
```typescript
// frontend/src/features/account/components/account-menu/hooks.ts

export function useAccountMenu() {
  const navigate = useNavigate();
  const logout = useLogout();
  const { open: openPreferencesModal } = usePreferencesSidemenu();

  function onOptionClick(option: AccountMenuItemId) {
    switch (option) {
      case 'logout':
        logout();
        navigate('/login');
        break;

      case 'integrations':
        openPreferencesModal('integrations');
        break;
        
      case 'prompt-studio':  // NEW
        navigate('/prompt-studio');
        break;

      case 'settings':
      default:
        openPreferencesModal();
        break;
    }
  }

  return { onOptionClick };
}
```

**Update types:**
```typescript
// frontend/src/features/account/components/account-menu/types.ts

export type AccountMenuItemId = 
  | 'settings' 
  | 'integrations' 
  | 'logout'
  | 'prompt-studio';  // NEW
```

**Risk:** Low (conditional rendering, only affects superusers)

**Test Required:**
```typescript
describe('AccountMenu', () => {
  it('should show Prompt Studio for superuser', () => {
    const mockUser = { is_superuser: true };
    render(<AccountMenu />, { mockUser });
    expect(screen.getByText('Prompt Studio')).toBeInTheDocument();
  });
  
  it('should hide Prompt Studio for normal user', () => {
    const mockUser = { is_superuser: false };
    render(<AccountMenu />, { mockUser });
    expect(screen.queryByText('Prompt Studio')).not.toBeInTheDocument();
  });
});
```

---

## 4. Implementation Phases

### Phase 0: Validation (Optional - 2 weeks)

**Goal:** Prove middleware approach works without building full UI

**Purpose:** Low-risk validation before committing to 6-8 week build

---

#### Step 0.1: Backend - Minimal Middleware (Day 1-2)

**Files to Create:**
```
backend/app/api/services/prompt_studio/
├── __init__.py
└── middleware.py  (100 lines)
```

**Implementation:**

```python
# backend/app/api/services/prompt_studio/__init__.py
"""
Prompt Studio - Isolated Module

DEPENDENCY RULES:
- Can import: app.models, app.core, app.api.deps
- Cannot import: app.api.routes.*, app.api.services.agents.*
- Must not modify: Core business logic

Module can be completely removed without breaking core app.
"""
__version__ = "0.1.0"
```

```python
# backend/app/api/services/prompt_studio/middleware.py

"""
Prompt File Interception Middleware

Transparently intercepts Path.read_text() calls for .md files in prompts/ directories.
If test mode is active for current user, loads from database instead of filesystem.

Safety:
- Feature flagged (PROMPT_STUDIO_ENABLED)
- Try/catch wraps all logic
- Falls back to filesystem on any error
- Can be disabled without restart (kill switch)
"""

import pathlib
import logging
from contextvars import ContextVar
from typing import Optional

logger = logging.getLogger(__name__)

# Context var to track current test session ID for this request
# This is set by HTTP middleware per request
current_test_session_id: ContextVar[Optional[str]] = ContextVar(
    'prompt_test_session_id', 
    default=None
)

# Store original method (for fallback and disable)
_original_read_text = pathlib.Path.read_text

def _intercepted_read_text(self, *args, **kwargs):
    """
    Intercept Path.read_text() for prompt .md files.
    
    Logic:
    1. Check if this is a prompt file (*.md in prompts/)
    2. Check if test session active for current request
    3. If yes, try to load from Studio DB
    4. On any error or if not test mode, fallback to filesystem
    
    This function is called on EVERY Path.read_text() call, so must be fast.
    """
    
    # Quick check: Only intercept .md files in prompts/ directories
    path_str = str(self)
    if not (path_str.endswith('.md') and 'prompts' in path_str):
        # Not a prompt file - use original method (fast path)
        return _original_read_text(self, *args, **kwargs)
    
    # This IS a prompt file - check for test mode
    test_session_id = current_test_session_id.get()
    
    if not test_session_id:
        # No test session active - use filesystem (normal path)
        return _original_read_text(self, *args, **kwargs)
    
    # Test mode active - try to load from Studio
    try:
        fragment_id = self.stem  # Extract "core" from "core.md"
        
        # Import locally to avoid circular dependencies
        from .test_session_manager import get_test_override_content
        
        override_content = get_test_override_content(test_session_id, fragment_id)
        
        if override_content:
            logger.info(
                f"🧪 PROMPT INTERCEPTED: {fragment_id}.md loaded from Studio "
                f"(test session: {test_session_id})"
            )
            return override_content
        
        # No override for this fragment - use filesystem
        return _original_read_text(self, *args, **kwargs)
    
    except Exception as e:
        # ANY error in Studio logic? Fall back to filesystem
        logger.warning(
            f"Prompt Studio interception failed for {self}: {e}. "
            f"Falling back to filesystem."
        )
        return _original_read_text(self, *args, **kwargs)

def enable_prompt_interception():
    """
    Enable prompt file interception.
    
    Call this once at app startup (in main.py) if PROMPT_STUDIO_ENABLED=true.
    
    SAFETY: This monkey-patches pathlib.Path.read_text(), but:
    - Only affects .md files in prompts/ directories
    - Falls back to original on any error
    - Can be disabled by calling disable_prompt_interception()
    """
    pathlib.Path.read_text = _intercepted_read_text
    logger.info("✅ Prompt Studio middleware enabled - .md file interception active")

def disable_prompt_interception():
    """
    Disable prompt file interception (restore original behavior).
    
    Can be called at runtime if Studio causes issues.
    """
    pathlib.Path.read_text = _original_read_text
    logger.info("❌ Prompt Studio middleware disabled - using filesystem only")
```

**Validation Test:**
```python
# backend/tests/api/services/prompt_studio/test_middleware.py

import pytest
from pathlib import Path
from app.api.services.prompt_studio.middleware import (
    enable_prompt_interception,
    disable_prompt_interception,
    current_test_session_id
)

def test_interception_ignores_non_md_files(tmp_path):
    """Non-.md files should not be intercepted"""
    enable_prompt_interception()
    
    # Create test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello")
    
    # Read should work normally
    content = test_file.read_text()
    assert content == "Hello"
    
    disable_prompt_interception()

def test_interception_ignores_non_prompt_md_files(tmp_path):
    """*.md files outside prompts/ should not be intercepted"""
    enable_prompt_interception()
    
    # Create test .md file (not in prompts/)
    test_file = tmp_path / "readme.md"
    test_file.write_text("# README")
    
    # Read should work normally
    content = test_file.read_text()
    assert content == "# README"
    
    disable_prompt_interception()

def test_interception_fallback_on_no_test_session(tmp_path):
    """Prompt files should use filesystem when no test session"""
    enable_prompt_interception()
    
    # Create fake prompts directory
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    core_file = prompts_dir / "core.md"
    core_file.write_text("# Core Prompt")
    
    # No test session set
    current_test_session_id.set(None)
    
    # Should read from filesystem
    content = core_file.read_text()
    assert content == "# Core Prompt"
    
    disable_prompt_interception()

def test_interception_with_test_session(tmp_path, mock_db):
    """When test session active, should load from Studio"""
    enable_prompt_interception()
    
    # Create fake prompts directory
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    core_file = prompts_dir / "core.md"
    core_file.write_text("# Original Prompt")
    
    # Mock Studio returning test version
    with patch('app.api.services.prompt_studio.middleware.get_test_override_content') as mock_get:
        mock_get.return_value = "# Test Version Prompt"
        
        # Set test session
        current_test_session_id.set("test-session-123")
        
        # Should read from Studio, not filesystem
        content = core_file.read_text()
        assert content == "# Test Version Prompt"
        assert "Original" not in content
    
    disable_prompt_interception()

def test_interception_fallback_on_studio_error(tmp_path):
    """If Studio throws error, should fallback to filesystem"""
    enable_prompt_interception()
    
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    core_file = prompts_dir / "core.md"
    core_file.write_text("# Fallback Prompt")
    
    # Mock Studio throwing error
    with patch('app.api.services.prompt_studio.middleware.get_test_override_content') as mock_get:
        mock_get.side_effect = Exception("Studio DB error")
        
        current_test_session_id.set("test-session-123")
        
        # Should fallback to filesystem
        content = core_file.read_text()
        assert content == "# Fallback Prompt"
    
    disable_prompt_interception()

def test_enable_disable_interception():
    """Verify can enable and disable cleanly"""
    # Initially disabled
    assert pathlib.Path.read_text == pathlib.Path.read_text  # Original
    
    # Enable
    enable_prompt_interception()
    assert pathlib.Path.read_text != _original_read_text  # Patched
    
    # Disable
    disable_prompt_interception()
    assert pathlib.Path.read_text == _original_read_text  # Restored
```

**Success Criteria for Phase 0:**
- ✅ All middleware tests pass
- ✅ Can enable/disable without errors
- ✅ Fallback works correctly
- ✅ No performance impact when disabled

**Decision Point:** If tests pass and performance is good → Continue to Phase 1

---

### Phase 1: Backend Foundation (2 weeks)

**Goal:** Complete backend infrastructure (DB, APIs, services)

---

#### Step 1.1: Database Models (Day 1-2)

**File to Create:** `backend/app/models.py` (append to existing)

**Analysis of Existing models.py:**
- Uses SQLModel with `table=True`
- UUID primary keys
- Relationships with `Relationship()`
- Follows pattern: Base class → Create class → Update class → DB class

**New Models to Add:**

```python
# Append to backend/app/models.py (around line 200+)

# ============================================================================
# PROMPT STUDIO MODELS (Isolated - can be removed without affecting core)
# ============================================================================

from sqlalchemy import Column, Text, JSON, Integer, Float, Boolean, ForeignKey

class PromptFragment(SQLModel, table=True):
    """
    Represents a prompt fragment file (e.g., 'core', 'simple', 'greeting_voice').
    
    These map 1:1 with .md files in prompts/ directories.
    Each fragment can have multiple versions (drafts, published, archived).
    """
    __tablename__ = "prompt_fragments"
    
    # Primary key: Fragment ID (same as filename without .md)
    id: str = Field(primary_key=True, description="Fragment ID (e.g., 'core', 'greeting_voice')")
    
    # Metadata
    name: str = Field(description="Display name for UI")
    description: Optional[str] = Field(default=None, description="What this fragment does")
    category: str = Field(description="Category: 'core', 'variant', 'modality'")
    
    # File path (for reference)
    file_path: Optional[str] = Field(default=None, description="Original .md file path")
    
    # Current published version
    published_version_id: Optional[str] = Field(
        default=None, 
        foreign_key="prompt_versions.id",
        description="Currently live version ID"
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    # versions: list["PromptVersion"] = Relationship(back_populates="fragment")


class PromptVersion(SQLModel, table=True):
    """
    Version history for prompt fragments.
    
    Lifecycle: draft → testing → published → archived
    Versions are immutable once created (edit creates new version).
    """
    __tablename__ = "prompt_versions"
    
    # Primary key
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), 
        primary_key=True
    )
    
    # Parent fragment
    fragment_id: str = Field(foreign_key="prompt_fragments.id", index=True)
    
    # Version info
    version_number: int = Field(description="Sequential version number (1, 2, 3...)")
    status: str = Field(
        description="Lifecycle status: 'draft', 'testing', 'published', 'archived'"
    )
    
    # Content (the actual markdown)
    content: str = Field(sa_column=Column(Text), description="Markdown content with {{PLACEHOLDERS}}")
    
    # Validation
    validation_status: str = Field(
        default="pending",
        description="Validation state: 'pending', 'valid', 'invalid', 'warnings'"
    )
    validation_details: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Detailed validation errors/warnings"
    )
    
    # Authorship
    created_by: Optional[str] = Field(
        default=None,
        description="User ID who created this version"
    )
    change_summary: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description="What changed in this version"
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = Field(default=None)
    
    # Performance tracking (aggregated from execution logs)
    usage_count: int = Field(default=0, description="Total executions")
    error_count: int = Field(default=0, description="Total errors")
    
    # Relationships
    # fragment: PromptFragment = Relationship(back_populates="versions")


class PromptTestSession(SQLModel, table=True):
    """
    Active test sessions for users.
    
    When PO enables test mode, a session is created that:
    - Maps fragments to test version IDs
    - Optionally overrides state fields
    - Auto-expires after N hours
    """
    __tablename__ = "prompt_test_sessions"
    
    # Primary key
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), 
        primary_key=True
    )
    
    # User who created this test session
    user_id: uuid.UUID = Field(
        foreign_key="user.id",
        index=True,
        description="User this test session belongs to"
    )
    
    # Optional: Scope to specific chat
    chat_id: Optional[str] = Field(
        default=None,
        index=True,
        description="If set, only applies to this chat. If null, applies to all user's chats"
    )
    
    # Prompt overrides
    prompt_overrides: dict = Field(
        sa_column=Column(JSON),
        description="Map of fragment_id → version_id to use for testing"
    )
    # Example: {"core": "uuid-v7", "greeting_voice": "uuid-v12"}
    
    # State overrides (for scenario testing)
    state_overrides: dict = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="State fields to override during testing"
    )
    # Example: {"is_first_message": true, "last_greeting_time": "2024-10-08T00:00:00Z"}
    
    # Test scenario metadata
    scenario_name: Optional[str] = Field(
        default=None,
        description="Name of predefined scenario (e.g., 'first_time_user')"
    )
    scenario_description: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description="Description of what this test session simulates"
    )
    
    # Session lifecycle
    enabled: bool = Field(default=True, description="Is this session active?")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(description="Auto-disable after this time")
    
    # Aggregate stats (updated as tests run)
    total_requests: int = Field(default=0)
    total_tokens_input: int = Field(default=0)
    total_tokens_output: int = Field(default=0)


class PromptExecutionLog(SQLModel, table=True):
    """
    Detailed analytics for every prompt execution.
    
    Logs EVERY time a prompt is assembled and sent to LLM, with:
    - Performance metrics (time, tokens, cost)
    - Context (which version, which user, test mode or not)
    - Quality indicators (errors, unresolved placeholders)
    
    IMPORTANT: Retention policy required (delete logs > 30 days old).
    """
    __tablename__ = "prompt_execution_logs"
    
    # Primary key
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), 
        primary_key=True
    )
    
    # Context
    version_id: str = Field(
        foreign_key="prompt_versions.id",
        index=True,
        description="Which prompt version was used"
    )
    fragment_id: str = Field(
        index=True,
        description="Which fragment (for aggregation)"
    )
    user_id: uuid.UUID = Field(index=True, description="User who triggered this")
    chat_id: str = Field(index=True, description="Chat context")
    correlation_id: str = Field(description="Request correlation ID")
    
    # Test mode flags
    is_test_mode: bool = Field(
        default=False,
        index=True,
        description="Was this execution part of test session?"
    )
    
    # Prompt details
    variant: str = Field(description="simple, complex, voice, etc.")
    modality: str = Field(description="text or voice")
    
    # Performance metrics
    prompt_build_time_ms: float = Field(sa_column=Column(Float), description="Time to build prompt")
    llm_call_time_ms: float = Field(sa_column=Column(Float), description="Time for LLM response")
    total_time_ms: float = Field(sa_column=Column(Float), description="Total execution time")
    
    # Token usage
    tokens_input: int = Field(sa_column=Column(Integer), description="Input tokens to LLM")
    tokens_output: int = Field(sa_column=Column(Integer), description="Output tokens from LLM")
    tokens_total: int = Field(sa_column=Column(Integer), description="Total tokens")
    estimated_cost_usd: float = Field(
        sa_column=Column(Float), 
        description="Estimated cost (for budgeting)"
    )
    
    # Quality indicators
    had_errors: bool = Field(default=False, description="Did this execution fail?")
    error_message: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description="Error details if failed"
    )
    unresolved_placeholders: int = Field(
        default=0,
        description="Count of placeholders that couldn't be resolved"
    )
    
    # Size metrics
    prompt_length: int = Field(description="Final prompt character count")
    response_length: int = Field(description="LLM response character count")
    
    # Timestamp
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,  # Important for retention query
        description="When this execution happened"
    )


# ============================================================================
# END PROMPT STUDIO MODELS
# ============================================================================
```

**Migration Script:**

```bash
# Create Alembic migration
cd backend
alembic revision -m "add_prompt_studio_tables"
```

```python
# backend/app/alembic/versions/XXXX_add_prompt_studio_tables.py

"""add prompt studio tables

Revision ID: XXXX
Revises: YYYY
Create Date: 2025-10-09

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'XXXX'
down_revision = 'YYYY'  # Current latest migration
branch_labels = None
depends_on = None


def upgrade():
    # Create prompt_fragments table
    op.create_table(
        'prompt_fragments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=True),
        sa.Column('published_version_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_prompt_fragments_id', 'prompt_fragments', ['id'])
    
    # Create prompt_versions table
    op.create_table(
        'prompt_versions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('fragment_id', sa.String(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('validation_status', sa.String(), nullable=False),
        sa.Column('validation_details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('change_summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_count', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['fragment_id'], ['prompt_fragments.id'], ondelete='CASCADE')
    )
    op.create_index('ix_prompt_versions_fragment_id', 'prompt_versions', ['fragment_id'])
    op.create_index('ix_prompt_versions_status', 'prompt_versions', ['status'])
    
    # Create prompt_test_sessions table
    op.create_table(
        'prompt_test_sessions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('chat_id', sa.String(), nullable=True),
        sa.Column('prompt_overrides', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('state_overrides', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('scenario_name', sa.String(), nullable=True),
        sa.Column('scenario_description', sa.Text(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('total_requests', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_tokens_input', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_tokens_output', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE')
    )
    op.create_index('ix_prompt_test_sessions_user_id', 'prompt_test_sessions', ['user_id'])
    op.create_index('ix_prompt_test_sessions_enabled', 'prompt_test_sessions', ['enabled'])
    
    # Create prompt_execution_logs table
    op.create_table(
        'prompt_execution_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('version_id', sa.String(), nullable=False),
        sa.Column('fragment_id', sa.String(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('chat_id', sa.String(), nullable=False),
        sa.Column('correlation_id', sa.String(), nullable=False),
        sa.Column('is_test_mode', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('variant', sa.String(), nullable=False),
        sa.Column('modality', sa.String(), nullable=False),
        sa.Column('prompt_build_time_ms', sa.Float(), nullable=False),
        sa.Column('llm_call_time_ms', sa.Float(), nullable=False),
        sa.Column('total_time_ms', sa.Float(), nullable=False),
        sa.Column('tokens_input', sa.Integer(), nullable=False),
        sa.Column('tokens_output', sa.Integer(), nullable=False),
        sa.Column('tokens_total', sa.Integer(), nullable=False),
        sa.Column('estimated_cost_usd', sa.Float(), nullable=False),
        sa.Column('had_errors', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('unresolved_placeholders', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('prompt_length', sa.Integer(), nullable=False),
        sa.Column('response_length', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['version_id'], ['prompt_versions.id'], ondelete='CASCADE')
    )
    op.create_index('ix_prompt_execution_logs_version_id', 'prompt_execution_logs', ['version_id'])
    op.create_index('ix_prompt_execution_logs_created_at', 'prompt_execution_logs', ['created_at'])
    op.create_index('ix_prompt_execution_logs_is_test_mode', 'prompt_execution_logs', ['is_test_mode'])


def downgrade():
    # Drop tables in reverse order (respects foreign keys)
    op.drop_table('prompt_execution_logs')
    op.drop_table('prompt_test_sessions')
    op.drop_table('prompt_versions')
    op.drop_table('prompt_fragments')
```

**Test Migration:**
```python
# backend/tests/api/services/prompt_studio/test_models.py

import pytest
from sqlmodel import Session, select
from app.models import PromptFragment, PromptVersion, PromptTestSession, PromptExecutionLog
from datetime import datetime, timedelta

def test_create_fragment(db: Session):
    """Test creating a prompt fragment"""
    fragment = PromptFragment(
        id="test_core",
        name="Test Core",
        description="Test fragment",
        category="core"
    )
    db.add(fragment)
    db.commit()
    
    # Verify
    loaded = db.get(PromptFragment, "test_core")
    assert loaded is not None
    assert loaded.name == "Test Core"

def test_create_version(db: Session):
    """Test creating a version for a fragment"""
    # Create fragment first
    fragment = PromptFragment(id="test", name="Test", category="core")
    db.add(fragment)
    db.commit()
    
    # Create version
    version = PromptVersion(
        fragment_id="test",
        version_number=1,
        status="draft",
        content="# Test Prompt\n\n{{USER_MESSAGE}}",
        validation_status="valid"
    )
    db.add(version)
    db.commit()
    
    # Verify
    loaded = db.get(PromptVersion, version.id)
    assert loaded is not None
    assert loaded.fragment_id == "test"
    assert "USER_MESSAGE" in loaded.content

def test_cascade_delete_versions(db: Session):
    """Verify deleting fragment deletes its versions"""
    fragment = PromptFragment(id="test", name="Test", category="core")
    db.add(fragment)
    db.commit()
    
    version = PromptVersion(
        fragment_id="test",
        version_number=1,
        status="draft",
        content="Test"
    )
    db.add(version)
    db.commit()
    version_id = version.id
    
    # Delete fragment
    db.delete(fragment)
    db.commit()
    
    # Version should be deleted too
    assert db.get(PromptVersion, version_id) is None

def test_test_session_expires(db: Session, test_user):
    """Test that test sessions can expire"""
    session = PromptTestSession(
        user_id=test_user.id,
        prompt_overrides={"core": "version-123"},
        state_overrides={},
        expires_at=datetime.utcnow() - timedelta(hours=1)  # Expired 1h ago
    )
    db.add(session)
    db.commit()
    
    # Query active sessions
    active = db.exec(
        select(PromptTestSession)
        .where(PromptTestSession.enabled == True)
        .where(PromptTestSession.expires_at > datetime.utcnow())
    ).all()
    
    # Should not include expired session
    assert session not in active
```

**Business Test:**
```python
def test_version_lifecycle():
    """
    BUSINESS TEST: Verify complete version lifecycle
    
    Scenario:
    1. PO creates draft
    2. PO tests it (status → testing)
    3. PO publishes (status → published, fragment.published_version_id updated)
    4. PO creates new draft (old version → archived)
    """
    # Step 1: Create fragment
    fragment = PromptFragment(id="greeting", name="Greeting", category="voice")
    db.add(fragment)
    db.commit()
    
    # Step 2: Create v1 draft
    v1 = PromptVersion(
        fragment_id="greeting",
        version_number=1,
        status="draft",
        content="Hello!"
    )
    db.add(v1)
    db.commit()
    
    # Step 3: Publish v1
    v1.status = "published"
    v1.published_at = datetime.utcnow()
    fragment.published_version_id = v1.id
    db.commit()
    
    # Verify
    assert fragment.published_version_id == v1.id
    assert v1.status == "published"
    
    # Step 4: Create v2 draft
    v2 = PromptVersion(
        fragment_id="greeting",
        version_number=2,
        status="draft",
        content="Hello there!"
    )
    db.add(v2)
    db.commit()
    
    # Step 5: Publish v2 (v1 should be archived)
    v1.status = "archived"
    v2.status = "published"
    v2.published_at = datetime.utcnow()
    fragment.published_version_id = v2.id
    db.commit()
    
    # Verify
    assert fragment.published_version_id == v2.id
    assert v2.status == "published"
    assert v1.status == "archived"
```

---

#### Step 1.2: State Inspector (Day 3-4)

**File to Create:** `backend/app/api/services/prompt_studio/state_inspector.py`

**Purpose:** Auto-discover placeholders from `GlobalSupervisorState` TypedDict

```python
# backend/app/api/services/prompt_studio/state_inspector.py

"""
State Inspector - Dynamic Placeholder Discovery

Automatically discovers available placeholders by introspecting:
- GlobalSupervisorState TypedDict
- Nested Pydantic models (GlobalPlannerDecision, MemoryDomain, etc.)

This ensures placeholder catalog is always in sync with actual state structure.
No manual maintenance required.

Usage:
    inspector = StateInspector()
    placeholders = inspector.discover_placeholders()
    # Returns: {"USER_MESSAGE": PlaceholderInfo(...), "CURRENT_TIME": ...}
"""

import logging
import inspect
from typing import get_type_hints, get_origin, get_args, Any, Dict, List, Optional, Union
from pydantic import BaseModel
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PlaceholderInfo:
    """Information about a discovered placeholder"""
    key: str                    # "USER_MESSAGE"
    path: str                   # "user_message" or "memory_domain.conversation_context"
    type_hint: str              # "str", "Optional[str]", "Dict[str, Any]"
    description: str            # Plain English description
    is_optional: bool           # Can this be None?
    is_nested: bool             # Is this a nested field?
    parent_model: Optional[str] # Parent model name if nested
    example_value: Optional[str] # Example for documentation


class StateInspector:
    """
    Discovers placeholders from GlobalSupervisorState structure.
    
    This class introspects the state TypedDict and nested models to build
    a complete catalog of available placeholders.
    """
    
    def discover_placeholders(self) -> Dict[str, PlaceholderInfo]:
        """
        Discover all available placeholders from state structure.
        
        Returns:
            Dict mapping placeholder key to its metadata
            Example: {"USER_MESSAGE": PlaceholderInfo(...)}
        """
        from app.api.services.agents.global_supervisor_state import GlobalSupervisorState
        
        placeholders = {}
        
        # Get top-level TypedDict fields
        type_hints = get_type_hints(GlobalSupervisorState)
        
        for field_name, field_type in type_hints.items():
            # Convert to placeholder key: user_message → USER_MESSAGE
            placeholder_key = field_name.upper()
            
            # Extract type information
            is_optional = self._is_optional_type(field_type)
            base_type = self._extract_base_type(field_type)
            description = self._get_field_description(field_name, field_type)
            example = self._get_example_value(base_type)
            
            placeholders[placeholder_key] = PlaceholderInfo(
                key=placeholder_key,
                path=field_name,
                type_hint=str(field_type),
                description=description,
                is_optional=is_optional,
                is_nested=False,
                parent_model=None,
                example_value=example
            )
            
            # If this field is a Pydantic model, discover nested fields
            if inspect.isclass(base_type) and issubclass(base_type, BaseModel):
                nested = self._discover_nested_fields(base_type, field_name)
                placeholders.update(nested)
        
        logger.info(f"Discovered {len(placeholders)} placeholders from state")
        return placeholders
    
    def get_placeholder_value(self, state: Dict[str, Any], placeholder_path: str) -> Any:
        """
        Extract value from state dict using dot-notation path.
        
        Example:
            get_placeholder_value(state, "memory_domain.facts")
            → state["memory_domain"]["facts"]
        
        Args:
            state: State dictionary
            placeholder_path: Dot-notation path (e.g., "user_message" or "memory_domain.facts")
        
        Returns:
            Value at that path, or None if not found
        """
        keys = placeholder_path.split('.')
        value = state
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            elif hasattr(value, key):
                value = getattr(value, key)
            else:
                return None
            
            if value is None:
                return None
        
        return value
    
    def _is_optional_type(self, type_hint) -> bool:
        """Check if type is Optional[X]"""
        origin = get_origin(type_hint)
        if origin is Union:
            args = get_args(type_hint)
            return type(None) in args
        return False
    
    def _extract_base_type(self, type_hint):
        """Extract T from Optional[T] or return type as-is"""
        if self._is_optional_type(type_hint):
            args = get_args(type_hint)
            return next(arg for arg in args if arg is not type(None))
        return type_hint
    
    def _get_field_description(self, field_name: str, field_type) -> str:
        """
        Generate human-readable description for field.
        
        For MVP, use simple heuristics. Can be enhanced with manual annotations later.
        """
        # Simple descriptions based on field name
        descriptions = {
            "user_message": "The current message/question from the user",
            "user_id": "Unique identifier for the user",
            "chat_id": "Unique identifier for the conversation",
            "model": "LLM model being used (e.g., 'gpt-4o')",
            "modality": "Interaction mode: 'text' or 'voice'",
            "user_timezone": "User's timezone (e.g., 'Europe/Zurich')",
            "current_time": "Current timestamp in ISO format",
            "user_locale": "User's locale (e.g., 'de-CH')",
            "is_first_message": "Whether this is the first message in the chat",
            "avatar_name": "Name of the assistant personality",
            "filename": "Uploaded file name (if any)",
            "file_content": "Uploaded file binary content",
            "conversation_summary": "Summary of recent conversation context",
        }
        
        return descriptions.get(field_name, f"State field: {field_name}")
    
    def _get_example_value(self, type_hint) -> Optional[str]:
        """Generate example value based on type"""
        if type_hint == str:
            return "Example string"
        elif type_hint == int:
            return "42"
        elif type_hint == bool:
            return "true"
        elif type_hint == datetime:
            return "2025-10-09T14:30:00Z"
        else:
            return None
    
    def _discover_nested_fields(
        self, 
        model_class: type[BaseModel], 
        prefix: str
    ) -> Dict[str, PlaceholderInfo]:
        """
        Recursively discover fields in nested Pydantic models.
        
        Example:
            For MemoryDomain model with field 'conversation_context',
            creates placeholder: MEMORY_DOMAIN_CONVERSATION_CONTEXT
            with path: "memory_domain.conversation_context"
        """
        placeholders = {}
        
        # Introspect Pydantic model fields
        if hasattr(model_class, '__fields__'):
            for field_name, field in model_class.__fields__.items():
                # Create placeholder key
                placeholder_key = f"{prefix}_{field_name}".upper()
                path = f"{prefix}.{field_name}"
                
                # Get field info
                description = field.field_info.description or f"Nested field: {field_name}"
                is_optional = not field.required
                
                placeholders[placeholder_key] = PlaceholderInfo(
                    key=placeholder_key,
                    path=path,
                    type_hint=str(field.outer_type_),
                    description=description,
                    is_optional=is_optional,
                    is_nested=True,
                    parent_model=model_class.__name__,
                    example_value=None
                )
        
        return placeholders
```

**Test:**
```python
# backend/tests/api/services/prompt_studio/test_state_inspector.py

import pytest
from app.api.services.prompt_studio.state_inspector import StateInspector

def test_discover_placeholders():
    """Test that inspector discovers placeholders from state"""
    inspector = StateInspector()
    placeholders = inspector.discover_placeholders()
    
    # Should discover top-level fields
    assert "USER_MESSAGE" in placeholders
    assert "MODEL" in placeholders
    assert "CHAT_ID" in placeholders
    
    # Should have metadata
    user_msg = placeholders["USER_MESSAGE"]
    assert user_msg.path == "user_message"
    assert not user_msg.is_nested
    assert user_msg.description is not None

def test_discover_nested_placeholders():
    """Test discovery of nested model fields"""
    inspector = StateInspector()
    placeholders = inspector.discover_placeholders()
    
    # Should discover nested fields from MemoryDomain
    # (if MemoryDomain is a Pydantic model in state)
    nested = [p for p in placeholders.values() if p.is_nested]
    assert len(nested) > 0

def test_get_placeholder_value():
    """Test extracting values from state"""
    inspector = StateInspector()
    
    state = {
        "user_message": "Hello",
        "memory_domain": {
            "facts": {"allergies": ["peanuts"]}
        }
    }
    
    # Top-level
    assert inspector.get_placeholder_value(state, "user_message") == "Hello"
    
    # Nested
    facts = inspector.get_placeholder_value(state, "memory_domain.facts")
    assert facts == {"allergies": ["peanuts"]}
    
    # Non-existent
    assert inspector.get_placeholder_value(state, "nonexistent") is None

def test_optional_type_detection():
    """Test detecting Optional types"""
    inspector = StateInspector()
    
    from typing import Optional
    assert inspector._is_optional_type(Optional[str]) == True
    assert inspector._is_optional_type(str) == False
```

---

#### Step 1.3: Validator Service (Day 5-6)

**File to Create:** `backend/app/api/services/prompt_studio/validator.py`

**Purpose:** Validate prompt content before saving/publishing

```python
# backend/app/api/services/prompt_studio/validator.py

"""
Prompt Validator

Validates prompt content against rules:
- All placeholders are valid (exist in state)
- No syntax errors (mismatched braces)
- No dangerous patterns (potential injection)
- Prompt length reasonable

Returns structured validation result for UI display.
"""

import logging
import re
from typing import Dict, Any, List
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """Single validation error"""
    type: str          # "unknown_placeholder", "syntax_error", etc.
    message: str       # Human-readable message
    line: Optional[int] = None  # Line number if applicable
    suggestion: Optional[str] = None  # Suggested fix


@dataclass
class ValidationResult:
    """Complete validation result"""
    valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    used_placeholders: List[str]
    available_placeholders: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization"""
        return {
            "valid": self.valid,
            "errors": [asdict(e) for e in self.errors],
            "warnings": [asdict(w) for w in self.warnings],
            "used_placeholders": self.used_placeholders,
            "available_placeholders": self.available_placeholders
        }


class PromptValidator:
    """Validates prompt content"""
    
    def __init__(self):
        from .state_inspector import StateInspector
        self.inspector = StateInspector()
        self.available_placeholders = self.inspector.discover_placeholders()
    
    def validate(self, content: str) -> ValidationResult:
        """
        Run all validation checks on prompt content.
        
        Args:
            content: Markdown content with {{PLACEHOLDERS}}
        
        Returns:
            ValidationResult with errors, warnings, and metadata
        """
        errors = []
        warnings = []
        
        # Check 1: Validate placeholders
        placeholder_check = self._validate_placeholders(content)
        errors.extend(placeholder_check["errors"])
        warnings.extend(placeholder_check["warnings"])
        used_placeholders = placeholder_check["used_placeholders"]
        
        # Check 2: Syntax errors
        syntax_errors = self._validate_syntax(content)
        errors.extend(syntax_errors)
        
        # Check 3: Security concerns
        security_warnings = self._validate_security(content)
        warnings.extend(security_warnings)
        
        # Check 4: Style recommendations
        style_warnings = self._validate_style(content)
        warnings.extend(style_warnings)
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            used_placeholders=used_placeholders,
            available_placeholders=list(self.available_placeholders.keys())
        )
    
    def _validate_placeholders(self, content: str) -> Dict[str, Any]:
        """Check all {{PLACEHOLDERS}} exist in state"""
        # Extract all {{PLACEHOLDER}} patterns
        pattern = r'\{\{([A-Z_][A-Z0-9_]*)\}\}'
        found_placeholders = re.findall(pattern, content)
        found_set = set(found_placeholders)
        
        available_keys = set(self.available_placeholders.keys())
        
        errors = []
        warnings = []
        
        # Check for unknown placeholders
        unknown = found_set - available_keys
        for placeholder in unknown:
            suggestion = self._suggest_similar(placeholder, available_keys)
            errors.append(ValidationError(
                type="unknown_placeholder",
                message=f"Placeholder {{{{{{placeholder}}}}}} not found in state",
                suggestion=f"Did you mean {{{{{{suggestion}}}}}}?" if suggestion else None
            ))
        
        return {
            "errors": errors,
            "warnings": warnings,
            "used_placeholders": list(found_set)
        }
    
    def _validate_syntax(self, content: str) -> List[ValidationError]:
        """Check for syntax errors"""
        errors = []
        
        # Check for mismatched braces
        open_count = content.count('{{')
        close_count = content.count('}}')
        
        if open_count != close_count:
            errors.append(ValidationError(
                type="mismatched_braces",
                message=f"Mismatched braces: {open_count} {{ vs {close_count} }}}",
                suggestion="Check for unclosed placeholders"
            ))
        
        # Check for single braces (common mistake)
        single_open = len(re.findall(r'\{(?!\{)', content))
        single_close = len(re.findall(r'(?<!\})\}', content))
        
        if single_open > 0 or single_close > 0:
            errors.append(ValidationError(
                type="single_brace",
                message="Found single { or } - placeholders need double braces",
                suggestion="Use {{PLACEHOLDER}} not {PLACEHOLDER}"
            ))
        
        return errors
    
    def _validate_security(self, content: str) -> List[ValidationError]:
        """Check for potential security issues"""
        warnings = []
        
        # Check for potential prompt injection patterns
        dangerous_patterns = [
            (r'ignore previous instructions', "Potential prompt injection"),
            (r'forget everything', "Potential prompt injection"),
            (r'<script>', "HTML/JS injection risk"),
        ]
        
        for pattern, message in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                warnings.append(ValidationError(
                    type="security_concern",
                    message=message,
                    suggestion=f"Review content containing: {pattern}"
                ))
        
        return warnings
    
    def _validate_style(self, content: str) -> List[ValidationError]:
        """Style and best practice recommendations"""
        warnings = []
        
        # Check length
        if len(content) > 5000:
            warnings.append(ValidationError(
                type="long_prompt",
                message=f"Prompt is {len(content)} characters (very long)",
                suggestion="Consider breaking into smaller fragments"
            ))
        
        return warnings
    
    def _suggest_similar(self, placeholder: str, available: set) -> Optional[str]:
        """Suggest similar placeholder using Levenshtein distance"""
        from difflib import get_close_matches
        matches = get_close_matches(placeholder, available, n=1, cutoff=0.6)
        return matches[0] if matches else None
```

**Test:**
```python
# backend/tests/api/services/prompt_studio/test_validator.py

import pytest
from app.api.services.prompt_studio.validator import PromptValidator

def test_valid_prompt():
    """Test validation of valid prompt"""
    validator = PromptValidator()
    content = "Hello {{USER_MESSAGE}}, the time is {{CURRENT_TIME}}"
    
    result = validator.validate(content)
    
    assert result.valid == True
    assert len(result.errors) == 0
    assert "USER_MESSAGE" in result.used_placeholders
    assert "CURRENT_TIME" in result.used_placeholders

def test_unknown_placeholder():
    """Test detection of unknown placeholder"""
    validator = PromptValidator()
    content = "Hello {{INVALID_FIELD}}"
    
    result = validator.validate(content)
    
    assert result.valid == False
    assert len(result.errors) == 1
    assert result.errors[0].type == "unknown_placeholder"
    assert "INVALID_FIELD" in result.errors[0].message

def test_mismatched_braces():
    """Test detection of mismatched braces"""
    validator = PromptValidator()
    content = "Hello {{USER_MESSAGE} missing close"
    
    result = validator.validate(content)
    
    assert result.valid == False
    assert any(e.type == "mismatched_braces" for e in result.errors)

def test_single_braces():
    """Test detection of single braces"""
    validator = PromptValidator()
    content = "Hello {USER_MESSAGE}"  # Single braces (wrong)
    
    result = validator.validate(content)
    
    assert result.valid == False
    assert any(e.type == "single_brace" for e in result.errors)

def test_suggestion_for_typo():
    """Test that validator suggests similar placeholders"""
    validator = PromptValidator()
    content = "{{USER_MESAGE}}"  # Typo: MESAGE instead of MESSAGE
    
    result = validator.validate(content)
    
    assert result.valid == False
    assert result.errors[0].suggestion is not None
    assert "USER_MESSAGE" in result.errors[0].suggestion  # Should suggest correct spelling

def test_long_prompt_warning():
    """Test warning for very long prompts"""
    validator = PromptValidator()
    content = "X" * 6000  # 6000 characters
    
    result = validator.validate(content)
    
    # Should be valid but with warning
    assert result.valid == True  # No errors
    assert any(w.type == "long_prompt" for w in result.warnings)
```

---

#### Step 1.4: Version Manager (Day 7-8)

**File to Create:** `backend/app/api/services/prompt_studio/version_manager.py`

**Purpose:** Manage version lifecycle (draft → publish → rollback)

```python
# backend/app/api/services/prompt_studio/version_manager.py

"""
Version Manager

Manages the complete lifecycle of prompt versions:
- Create draft versions
- Validate before save
- Publish to production (atomic)
- Rollback to previous versions
- Archive old versions
- Export to .md files for Git tracking

All operations are database transactions - atomic and safe.
"""

import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
from sqlmodel import Session, select

from app.models import PromptFragment, PromptVersion

logger = logging.getLogger(__name__)


class VersionManager:
    """Manages prompt version lifecycle"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_draft(
        self, 
        fragment_id: str, 
        content: str, 
        created_by: str,
        change_summary: Optional[str] = None
    ) -> PromptVersion:
        """
        Create a new draft version.
        
        Workflow:
        1. Get latest version number for this fragment
        2. Increment version number
        3. Validate content
        4. Create draft version
        5. Return version object
        
        Args:
            fragment_id: Fragment to version (e.g., "core", "greeting_voice")
            content: Markdown content with {{PLACEHOLDERS}}
            created_by: User ID creating this draft
            change_summary: Optional description of changes
        
        Returns:
            Created PromptVersion with status='draft'
        """
        # Get latest version number
        statement = (
            select(PromptVersion)
            .where(PromptVersion.fragment_id == fragment_id)
            .order_by(PromptVersion.version_number.desc())
        )
        latest = self.db.exec(statement).first()
        
        next_version = (latest.version_number + 1) if latest else 1
        
        # Validate content
        from .validator import PromptValidator
        validator = PromptValidator()
        validation = validator.validate(content)
        
        # Create draft version
        version = PromptVersion(
            id=str(uuid.uuid4()),
            fragment_id=fragment_id,
            version_number=next_version,
            status="draft",
            content=content,
            validation_status="valid" if validation.valid else "invalid",
            validation_details=validation.to_dict(),
            created_by=created_by,
            change_summary=change_summary,
            created_at=datetime.utcnow()
        )
        
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        
        logger.info(
            f"Created draft v{version.version_number} for {fragment_id} "
            f"by user {created_by}"
        )
        
        return version
    
    async def publish_version(
        self, 
        version_id: str,
        export_to_file: bool = True
    ) -> PromptVersion:
        """
        Publish a version to production.
        
        Workflow:
        1. Validate version can be published (must be valid, have tests)
        2. Archive current published version (if exists)
        3. Update version status to 'published'
        4. Update fragment.published_version_id pointer
        5. Export to .md file (optional, for Git)
        6. Log publish event
        
        This is an ATOMIC operation - either all steps succeed or none.
        
        Args:
            version_id: Version to publish
            export_to_file: Whether to export to prompts/*.md file
        
        Returns:
            Published version
        
        Raises:
            ValueError: If version invalid or cannot be published
        """
        version = self.db.get(PromptVersion, version_id)
        if not version:
            raise ValueError(f"Version {version_id} not found")
        
        # Validation checks
        if version.validation_status != "valid":
            raise ValueError(
                f"Cannot publish invalid version. "
                f"Validation status: {version.validation_status}"
            )
        
        # Get fragment
        fragment = self.db.get(PromptFragment, version.fragment_id)
        if not fragment:
            raise ValueError(f"Fragment {version.fragment_id} not found")
        
        # Archive previous published version
        if fragment.published_version_id:
            old_version = self.db.get(PromptVersion, fragment.published_version_id)
            if old_version and old_version.id != version_id:
                old_version.status = "archived"
                logger.info(f"Archived previous version {old_version.version_number}")
        
        # Publish new version
        version.status = "published"
        version.published_at = datetime.utcnow()
        
        # Update fragment pointer
        fragment.published_version_id = version_id
        fragment.updated_at = datetime.utcnow()
        
        # Commit transaction (atomic)
        self.db.commit()
        self.db.refresh(version)
        
        logger.warning(
            f"🚀 PUBLISHED: {fragment.id} v{version.version_number} to PRODUCTION"
        )
        
        # Export to file (optional, best-effort)
        if export_to_file:
            try:
                await self._export_to_file(fragment.id, version.content)
            except Exception as e:
                logger.error(f"Failed to export {fragment.id}: {e}")
                # Don't fail publish if export fails
        
        return version
    
    async def rollback_to_version(self, version_id: str) -> PromptVersion:
        """
        Rollback to a previous version.
        
        This is instant - just updates the fragment.published_version_id pointer.
        No content changes, just which version is "live".
        
        Args:
            version_id: Version to rollback to
        
        Returns:
            The version now published
        """
        version = self.db.get(PromptVersion, version_id)
        if not version:
            raise ValueError(f"Version {version_id} not found")
        
        fragment = self.db.get(PromptFragment, version.fragment_id)
        if not fragment:
            raise ValueError(f"Fragment {version.fragment_id} not found")
        
        # Update pointer
        old_published_id = fragment.published_version_id
        fragment.published_version_id = version_id
        fragment.updated_at = datetime.utcnow()
        
        # Update version status if was archived
        if version.status == "archived":
            version.status = "published"
            version.published_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(version)
        
        logger.warning(
            f"⏮️ ROLLBACK: {fragment.id} from {old_published_id} to v{version.version_number}"
        )
        
        # Export to file
        try:
            await self._export_to_file(fragment.id, version.content)
        except Exception as e:
            logger.error(f"Failed to export after rollback: {e}")
        
        return version
    
    async def _export_to_file(self, fragment_id: str, content: str):
        """
        Export version to .md file for Git tracking.
        
        Creates/updates prompts/{fragment_id}.md with content.
        Adds header comment indicating Studio management.
        """
        # Find prompts directory (search from current working directory)
        prompts_dir = Path("backend/app/api/services/agents/global_supervisor/nodes/prompts")
        
        if not prompts_dir.exists():
            logger.warning(f"Prompts directory not found: {prompts_dir}")
            return
        
        file_path = prompts_dir / f"{fragment_id}.md"
        
        # Add header comment
        header = (
            f"<!-- Managed by Prompt Studio | "
            f"Last exported: {datetime.utcnow().isoformat()} | "
            f"Do not edit directly - use Studio -->\n\n"
        )
        
        file_path.write_text(header + content, encoding="utf-8")
        logger.info(f"Exported {fragment_id} to {file_path}")
```

**Test:**
```python
# backend/tests/api/services/prompt_studio/test_version_manager.py

import pytest
from app.api.services.prompt_studio.version_manager import VersionManager
from app.models import PromptFragment, PromptVersion

@pytest.mark.asyncio
async def test_create_draft(db: Session, test_user):
    """Test creating a draft version"""
    # Setup: Create fragment
    fragment = PromptFragment(id="test", name="Test", category="core")
    db.add(fragment)
    db.commit()
    
    # Create draft
    manager = VersionManager(db)
    version = await manager.create_draft(
        fragment_id="test",
        content="# Test\n\n{{USER_MESSAGE}}",
        created_by=str(test_user.id),
        change_summary="Initial version"
    )
    
    # Verify
    assert version.version_number == 1
    assert version.status == "draft"
    assert version.validation_status == "valid"
    assert "USER_MESSAGE" in version.content

@pytest.mark.asyncio
async def test_publish_version(db: Session, test_user):
    """
    BUSINESS TEST: Test publishing version to production
    
    Scenario:
    1. Create fragment
    2. Create draft version
    3. Publish it
    4. Verify fragment points to published version
    """
    # Setup
    fragment = PromptFragment(id="test", name="Test", category="core")
    db.add(fragment)
    db.commit()
    
    # Create draft
    manager = VersionManager(db)
    draft = await manager.create_draft(
        fragment_id="test",
        content="# Test\n\n{{USER_MESSAGE}}",
        created_by=str(test_user.id)
    )
    
    # Publish
    published = await manager.publish_version(draft.id, export_to_file=False)
    
    # Verify
    assert published.status == "published"
    assert published.published_at is not None
    
    # Fragment should point to this version
    db.refresh(fragment)
    assert fragment.published_version_id == published.id

@pytest.mark.asyncio
async def test_publish_archives_previous(db: Session, test_user):
    """
    BUSINESS TEST: Publishing new version archives old version
    
    Scenario:
    1. Publish v1
    2. Create and publish v2
    3. Verify v1 is archived, v2 is published
    """
    fragment = PromptFragment(id="test", name="Test", category="core")
    db.add(fragment)
    db.commit()
    
    manager = VersionManager(db)
    
    # Create and publish v1
    v1 = await manager.create_draft("test", "V1 content", str(test_user.id))
    await manager.publish_version(v1.id, export_to_file=False)
    
    # Create and publish v2
    v2 = await manager.create_draft("test", "V2 content", str(test_user.id))
    await manager.publish_version(v2.id, export_to_file=False)
    
    # Verify
    db.refresh(v1)
    db.refresh(v2)
    
    assert v1.status == "archived"  # Old version archived
    assert v2.status == "published"  # New version published
    
    db.refresh(fragment)
    assert fragment.published_version_id == v2.id  # Points to v2

@pytest.mark.asyncio
async def test_rollback(db: Session, test_user):
    """
    BUSINESS TEST: Test rollback to previous version
    
    Scenario:
    1. Have v1 published, v2 published
    2. Rollback to v1
    3. Verify v1 is now published, fragment points to it
    """
    fragment = PromptFragment(id="test", name="Test", category="core")
    db.add(fragment)
    db.commit()
    
    manager = VersionManager(db)
    
    # Create and publish v1, then v2
    v1 = await manager.create_draft("test", "V1", str(test_user.id))
    await manager.publish_version(v1.id, export_to_file=False)
    
    v2 = await manager.create_draft("test", "V2", str(test_user.id))
    await manager.publish_version(v2.id, export_to_file=False)
    
    # Rollback to v1
    rollback_version = await manager.rollback_to_version(v1.id)
    
    # Verify
    assert rollback_version.id == v1.id
    assert rollback_version.status == "published"
    
    db.refresh(fragment)
    assert fragment.published_version_id == v1.id  # Back to v1

@pytest.mark.asyncio
async def test_cannot_publish_invalid_version(db: Session, test_user):
    """Test that invalid versions cannot be published"""
    fragment = PromptFragment(id="test", name="Test", category="core")
    db.add(fragment)
    db.commit()
    
    manager = VersionManager(db)
    
    # Create draft with invalid content
    draft = await manager.create_draft(
        fragment_id="test",
        content="{{INVALID_PLACEHOLDER}}",  # Unknown placeholder
        created_by=str(test_user.id)
    )
    
    # Should have invalid validation status
    assert draft.validation_status == "invalid"
    
    # Attempt to publish should fail
    with pytest.raises(ValueError, match="Cannot publish invalid version"):
        await manager.publish_version(draft.id)
```

---

#### Step 1.5: Test Session Manager (Day 9-10)

**File to Create:** `backend/app/api/services/prompt_studio/test_session_manager.py`

**Purpose:** Manage test mode sessions (enable, get active, disable)

```python
# backend/app/api/services/prompt_studio/test_session_manager.py

"""
Test Session Manager

Manages test mode sessions for users:
- Enable test mode (create session with overrides)
- Get active session for user
- Get test override content (used by middleware)
- Disable test mode
- Apply state overrides

Test sessions allow POs to:
- Test draft prompts in production without affecting other users
- Override state fields to simulate scenarios (e.g., first-time user)
- Collect analytics on test versions
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlmodel import Session, select

from app.models import PromptTestSession, PromptVersion

logger = logging.getLogger(__name__)


class TestSessionManager:
    """Manages test mode sessions"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def enable_test_mode(
        self,
        user_id: str,
        prompt_overrides: Dict[str, str],
        state_overrides: Dict[str, Any] = None,
        chat_id: Optional[str] = None,
        scenario_name: Optional[str] = None,
        scenario_description: Optional[str] = None,
        duration_hours: int = 24
    ) -> PromptTestSession:
        """
        Enable test mode for a user.
        
        Creates a new test session. If user already has active session, disables it first.
        
        Args:
            user_id: User to enable test mode for
            prompt_overrides: Map of fragment_id → version_id to test
            state_overrides: Optional state fields to override
            chat_id: Optional - scope to specific chat only
            scenario_name: Optional - name of predefined scenario
            scenario_description: Optional - description of test scenario
            duration_hours: How long session stays active (default 24h)
        
        Returns:
            Created test session
        """
        # Disable any existing active sessions for this user
        existing = self.db.exec(
            select(PromptTestSession)
            .where(PromptTestSession.user_id == user_id)
            .where(PromptTestSession.enabled == True)
        ).all()
        
        for session in existing:
            session.enabled = False
            logger.info(f"Disabled previous test session {session.id}")
        
        # Create new session
        session = PromptTestSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            chat_id=chat_id,
            prompt_overrides=prompt_overrides,
            state_overrides=state_overrides or {},
            scenario_name=scenario_name,
            scenario_description=scenario_description,
            enabled=True,
            started_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=duration_hours)
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        logger.info(
            f"🧪 TEST MODE ENABLED: User {user_id}, overrides: {prompt_overrides}, "
            f"expires: {session.expires_at}"
        )
        
        return session
    
    async def disable_test_mode(self, user_id: str):
        """Disable test mode for user"""
        sessions = self.db.exec(
            select(PromptTestSession)
            .where(PromptTestSession.user_id == user_id)
            .where(PromptTestSession.enabled == True)
        ).all()
        
        for session in sessions:
            session.enabled = False
        
        self.db.commit()
        logger.info(f"🧪 TEST MODE DISABLED: User {user_id}")
    
    async def get_active_session(
        self, 
        user_id: str, 
        chat_id: Optional[str] = None
    ) -> Optional[PromptTestSession]:
        """
        Get active test session for user.
        
        Checks:
        1. Session is enabled
        2. Session not expired
        3. Session matches chat_id (if provided) or is global
        
        Args:
            user_id: User to check
            chat_id: Optional - filter by chat
        
        Returns:
            Active session or None
        """
        query = (
            select(PromptTestSession)
            .where(PromptTestSession.user_id == user_id)
            .where(PromptTestSession.enabled == True)
            .where(PromptTestSession.expires_at > datetime.utcnow())
        )
        
        # If chat_id provided, filter by it (or global sessions with chat_id=None)
        if chat_id:
            # This is tricky - need to match either this chat or global sessions
            sessions = self.db.exec(query).all()
            for session in sessions:
                if session.chat_id is None or session.chat_id == chat_id:
                    return session
            return None
        
        return self.db.exec(query).first()
    
    def apply_state_overrides(
        self, 
        state: Dict[str, Any], 
        test_session: PromptTestSession
    ) -> Dict[str, Any]:
        """
        Apply test session state overrides to state dict.
        
        Handles nested paths like "memory_domain.facts".
        
        Args:
            state: Original state dict
            test_session: Active test session with overrides
        
        Returns:
            Modified state dict
        """
        if not test_session or not test_session.state_overrides:
            return state
        
        # Copy state (don't modify original)
        modified = state.copy()
        
        for field_path, value in test_session.state_overrides.items():
            # Support nested paths: "memory_domain.facts"
            keys = field_path.split('.')
            target = modified
            
            # Navigate to parent
            for key in keys[:-1]:
                if key not in target:
                    target[key] = {}
                target = target[key]
            
            # Set value
            final_key = keys[-1]
            logger.info(f"🧪 STATE OVERRIDE: {field_path} = {value}")
            target[final_key] = value
        
        return modified


# Module-level function for middleware to call (avoid circular imports)
def get_test_override_content(test_session_id: str, fragment_id: str) -> Optional[str]:
    """
    Get override content for a fragment if test session has it.
    
    Called by middleware.py during file interception.
    
    Args:
        test_session_id: Active test session ID
        fragment_id: Fragment being loaded (e.g., "core")
    
    Returns:
        Override content or None
    """
    from app.core.db import engine
    
    with Session(engine) as db:
        # Get test session
        session = db.get(PromptTestSession, test_session_id)
        if not session or not session.enabled:
            return None
        
        # Check if session has override for this fragment
        version_id = session.prompt_overrides.get(fragment_id)
        if not version_id:
            return None
        
        # Load override version
        version = db.get(PromptVersion, version_id)
        if not version:
            logger.warning(f"Override version {version_id} not found")
            return None
        
        logger.debug(f"Returning test content for {fragment_id} from v{version.version_number}")
        return version.content
```

**Test:**
```python
# backend/tests/api/services/prompt_studio/test_test_session_manager.py

import pytest
from datetime import datetime, timedelta
from app.api.services.prompt_studio.test_session_manager import TestSessionManager
from app.models import PromptTestSession

@pytest.mark.asyncio
async def test_enable_test_mode(db, test_user):
    """Test enabling test mode"""
    manager = TestSessionManager(db)
    
    session = await manager.enable_test_mode(
        user_id=str(test_user.id),
        prompt_overrides={"core": "version-123"},
        state_overrides={"is_first_message": True}
    )
    
    assert session.enabled == True
    assert session.user_id == test_user.id
    assert session.prompt_overrides == {"core": "version-123"}
    assert session.state_overrides == {"is_first_message": True}

@pytest.mark.asyncio
async def test_enable_disables_previous_session(db, test_user):
    """Test that enabling new session disables previous one"""
    manager = TestSessionManager(db)
    
    # Enable first session
    session1 = await manager.enable_test_mode(
        user_id=str(test_user.id),
        prompt_overrides={"core": "v1"}
    )
    assert session1.enabled == True
    
    # Enable second session
    session2 = await manager.enable_test_mode(
        user_id=str(test_user.id),
        prompt_overrides={"core": "v2"}
    )
    assert session2.enabled == True
    
    # First session should be disabled
    db.refresh(session1)
    assert session1.enabled == False

@pytest.mark.asyncio
async def test_get_active_session(db, test_user):
    """Test retrieving active session"""
    manager = TestSessionManager(db)
    
    # No session yet
    active = await manager.get_active_session(str(test_user.id))
    assert active is None
    
    # Enable test mode
    await manager.enable_test_mode(
        user_id=str(test_user.id),
        prompt_overrides={"core": "v1"}
    )
    
    # Should find active session
    active = await manager.get_active_session(str(test_user.id))
    assert active is not None
    assert active.enabled == True

@pytest.mark.asyncio
async def test_expired_session_not_active(db, test_user):
    """Test that expired sessions are not returned as active"""
    manager = TestSessionManager(db)
    
    # Create session that expired 1 hour ago
    session = PromptTestSession(
        user_id=test_user.id,
        prompt_overrides={},
        state_overrides={},
        enabled=True,
        started_at=datetime.utcnow() - timedelta(hours=25),
        expires_at=datetime.utcnow() - timedelta(hours=1)  # Expired
    )
    db.add(session)
    db.commit()
    
    # Should not find expired session
    active = await manager.get_active_session(str(test_user.id))
    assert active is None

def test_apply_state_overrides():
    """Test applying state overrides to state dict"""
    manager = TestSessionManager(None)  # No DB needed
    
    state = {
        "user_message": "Hello",
        "is_first_message": False,
        "memory_domain": {
            "facts": {}
        }
    }
    
    session = PromptTestSession(
        user_id="user-123",
        prompt_overrides={},
        state_overrides={
            "is_first_message": True,
            "memory_domain.facts": {"allergies": ["peanuts"]}
        },
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    
    # Apply overrides
    modified = manager.apply_state_overrides(state, session)
    
    # Verify top-level override
    assert modified["is_first_message"] == True
    
    # Verify nested override
    assert modified["memory_domain"]["facts"] == {"allergies": ["peanuts"]}
    
    # Original state unchanged
    assert state["is_first_message"] == False
```

---

#### Step 1.6: REST API Router (Day 11-12)

**File to Create:** `backend/app/api/routes/prompt_studio.py`

**Purpose:** REST API endpoints for all Studio operations

**Analysis:** Follow existing pattern from `chats.py`, `users.py`
- Use `APIRouter` with prefix
- Use `StudioUser` dependency for auth
- Return Pydantic models
- Handle errors with HTTPException

```python
# backend/app/api/routes/prompt_studio.py

"""
Prompt Studio API Endpoints

Provides REST API for:
- Fragment management (CRUD)
- Version management (create, publish, rollback)
- Test session management (enable, disable, status)
- Analytics (metrics, comparisons)
- Placeholder discovery

All endpoints require superuser privileges.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel
from sqlmodel import Session, select

from app.api.deps import StudioUser, SessionDep
from app.models import PromptFragment, PromptVersion, PromptTestSession, User

router = APIRouter(prefix="/prompt-studio", tags=["prompt-studio"])


# ============================================================================
# Request/Response Models
# ============================================================================

class FragmentListResponse(BaseModel):
    """Response for listing fragments"""
    fragments: List[Dict[str, Any]]


class VersionDetailResponse(BaseModel):
    """Detailed version information"""
    id: str
    fragment_id: str
    version_number: int
    status: str
    content: str
    validation_status: str
    validation_details: Optional[Dict]
    created_by: Optional[str]
    created_at: str
    published_at: Optional[str]
    change_summary: Optional[str]


class CreateDraftRequest(BaseModel):
    """Request to create a draft version"""
    content: str
    change_summary: Optional[str] = None


class PublishRequest(BaseModel):
    """Request to publish a version"""
    export_to_file: bool = True


class EnableTestModeRequest(BaseModel):
    """Request to enable test mode"""
    prompt_overrides: Dict[str, str]  # {"core": "version-uuid"}
    state_overrides: Dict[str, Any] = {}
    chat_id: Optional[str] = None
    scenario_name: Optional[str] = None
    scenario_description: Optional[str] = None
    duration_hours: int = 24


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/placeholders")
async def get_placeholders(
    user: User = Depends(StudioUser)
) -> Dict[str, Dict[str, Any]]:
    """
    Get all available placeholders discovered from state.
    
    Returns catalog of placeholders with metadata for UI.
    """
    from app.api.services.prompt_studio.state_inspector import StateInspector
    
    inspector = StateInspector()
    placeholders = inspector.discover_placeholders()
    
    # Convert to dict for JSON
    return {
        key: {
            "key": info.key,
            "path": info.path,
            "type_hint": info.type_hint,
            "description": info.description,
            "is_optional": info.is_optional,
            "is_nested": info.is_nested,
            "example_value": info.example_value
        }
        for key, info in placeholders.items()
    }


@router.get("/fragments")
async def list_fragments(
    session: SessionDep,
    user: User = Depends(StudioUser)
) -> FragmentListResponse:
    """List all prompt fragments"""
    fragments = session.exec(select(PromptFragment)).all()
    
    return FragmentListResponse(
        fragments=[
            {
                "id": f.id,
                "name": f.name,
                "description": f.description,
                "category": f.category,
                "published_version_id": f.published_version_id,
                "updated_at": f.updated_at.isoformat()
            }
            for f in fragments
        ]
    )


@router.get("/fragments/{fragment_id}/versions")
async def list_versions(
    fragment_id: str,
    session: SessionDep,
    user: User = Depends(StudioUser)
) -> List[Dict[str, Any]]:
    """List all versions of a fragment"""
    versions = session.exec(
        select(PromptVersion)
        .where(PromptVersion.fragment_id == fragment_id)
        .order_by(PromptVersion.version_number.desc())
    ).all()
    
    return [
        {
            "id": v.id,
            "version_number": v.version_number,
            "status": v.status,
            "validation_status": v.validation_status,
            "created_at": v.created_at.isoformat(),
            "published_at": v.published_at.isoformat() if v.published_at else None,
            "change_summary": v.change_summary,
            "usage_count": v.usage_count
        }
        for v in versions
    ]


@router.get("/versions/{version_id}")
async def get_version(
    version_id: str,
    session: SessionDep,
    user: User = Depends(StudioUser)
) -> VersionDetailResponse:
    """Get detailed version info including content"""
    version = session.get(PromptVersion, version_id)
    if not version:
        raise HTTPException(404, "Version not found")
    
    return VersionDetailResponse(
        id=version.id,
        fragment_id=version.fragment_id,
        version_number=version.version_number,
        status=version.status,
        content=version.content,
        validation_status=version.validation_status,
        validation_details=version.validation_details,
        created_by=version.created_by,
        created_at=version.created_at.isoformat(),
        published_at=version.published_at.isoformat() if version.published_at else None,
        change_summary=version.change_summary
    )


@router.post("/fragments/{fragment_id}/versions")
async def create_draft(
    fragment_id: str,
    request: CreateDraftRequest,
    session: SessionDep,
    user: User = Depends(StudioUser)
) -> Dict[str, Any]:
    """Create a new draft version"""
    from app.api.services.prompt_studio.version_manager import VersionManager
    
    manager = VersionManager(session)
    version = await manager.create_draft(
        fragment_id=fragment_id,
        content=request.content,
        created_by=str(user.id),
        change_summary=request.change_summary
    )
    
    return {
        "id": version.id,
        "version_number": version.version_number,
        "status": version.status,
        "validation_status": version.validation_status,
        "validation_details": version.validation_details
    }


@router.post("/versions/{version_id}/publish")
async def publish_version(
    version_id: str,
    request: PublishRequest,
    session: SessionDep,
    user: User = Depends(StudioUser)
) -> Dict[str, Any]:
    """Publish a version to production"""
    from app.api.services.prompt_studio.version_manager import VersionManager
    
    manager = VersionManager(session)
    
    try:
        version = await manager.publish_version(
            version_id=version_id,
            export_to_file=request.export_to_file
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    
    return {
        "id": version.id,
        "version_number": version.version_number,
        "status": version.status,
        "published_at": version.published_at.isoformat()
    }


@router.post("/versions/{version_id}/rollback")
async def rollback_version(
    version_id: str,
    session: SessionDep,
    user: User = Depends(StudioUser)
) -> Dict[str, Any]:
    """Rollback to a previous version"""
    from app.api.services.prompt_studio.version_manager import VersionManager
    
    manager = VersionManager(session)
    version = await manager.rollback_to_version(version_id)
    
    return {
        "id": version.id,
        "version_number": version.version_number,
        "status": version.status,
        "message": f"Rolled back to version {version.version_number}"
    }


@router.post("/test-sessions")
async def enable_test_mode(
    request: EnableTestModeRequest,
    session: SessionDep,
    user: User = Depends(StudioUser)
) -> Dict[str, Any]:
    """Enable test mode for current user"""
    from app.api.services.prompt_studio.test_session_manager import TestSessionManager
    
    manager = TestSessionManager(session)
    test_session = await manager.enable_test_mode(
        user_id=str(user.id),
        prompt_overrides=request.prompt_overrides,
        state_overrides=request.state_overrides,
        chat_id=request.chat_id,
        scenario_name=request.scenario_name,
        scenario_description=request.scenario_description,
        duration_hours=request.duration_hours
    )
    
    return {
        "id": test_session.id,
        "enabled": test_session.enabled,
        "expires_at": test_session.expires_at.isoformat()
    }


@router.delete("/test-sessions")
async def disable_test_mode(
    session: SessionDep,
    user: User = Depends(StudioUser)
) -> Dict[str, str]:
    """Disable test mode for current user"""
    from app.api.services.prompt_studio.test_session_manager import TestSessionManager
    
    manager = TestSessionManager(session)
    await manager.disable_test_mode(str(user.id))
    
    return {"message": "Test mode disabled"}


@router.get("/test-sessions/active")
async def get_active_test_session(
    session: SessionDep,
    user: User = Depends(StudioUser)
) -> Optional[Dict[str, Any]]:
    """Get active test session for current user"""
    from app.api.services.prompt_studio.test_session_manager import TestSessionManager
    
    manager = TestSessionManager(session)
    test_session = await manager.get_active_session(str(user.id))
    
    if not test_session:
        return None
    
    return {
        "id": test_session.id,
        "prompt_overrides": test_session.prompt_overrides,
        "state_overrides": test_session.state_overrides,
        "scenario_name": test_session.scenario_name,
        "enabled": test_session.enabled,
        "expires_at": test_session.expires_at.isoformat()
    }
```

**Test:**
```python
# backend/tests/api/routes/test_prompt_studio_routes.py

import pytest
from fastapi.testclient import TestClient

def test_non_superuser_blocked(client: TestClient, normal_user_token_headers):
    """Non-superuser should get 403 on all Studio endpoints"""
    response = client.get(
        "/api/v1/prompt-studio/fragments",
        headers=normal_user_token_headers
    )
    assert response.status_code == 403

def test_superuser_can_list_fragments(client: TestClient, superuser_token_headers):
    """Superuser can access Studio endpoints"""
    response = client.get(
        "/api/v1/prompt-studio/fragments",
        headers=superuser_token_headers
    )
    assert response.status_code == 200

def test_create_draft(client: TestClient, superuser_token_headers, db):
    """
    BUSINESS TEST: Create draft version via API
    
    Scenario:
    1. Superuser creates fragment
    2. Creates draft version via API
    3. Verifies draft is saved correctly
    """
    # Setup: Create fragment
    from app.models import PromptFragment
    fragment = PromptFragment(id="test", name="Test", category="core")
    db.add(fragment)
    db.commit()
    
    # Create draft via API
    response = client.post(
        "/api/v1/prompt-studio/fragments/test/versions",
        headers=superuser_token_headers,
        json={
            "content": "# Test\n\n{{USER_MESSAGE}}",
            "change_summary": "Initial draft"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["version_number"] == 1
    assert data["status"] == "draft"
    assert data["validation_status"] == "valid"

def test_publish_draft(client: TestClient, superuser_token_headers, db):
    """
    BUSINESS TEST: Publish draft to production
    
    Scenario:
    1. Create fragment and draft
    2. Publish via API
    3. Verify fragment.published_version_id updated
    """
    from app.models import PromptFragment, PromptVersion
    
    # Setup
    fragment = PromptFragment(id="test", name="Test", category="core")
    db.add(fragment)
    db.commit()
    
    version = PromptVersion(
        fragment_id="test",
        version_number=1,
        status="draft",
        content="Test",
        validation_status="valid"
    )
    db.add(version)
    db.commit()
    
    # Publish via API
    response = client.post(
        f"/api/v1/prompt-studio/versions/{version.id}/publish",
        headers=superuser_token_headers,
        json={"export_to_file": False}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "published"
    
    # Verify fragment updated
    db.refresh(fragment)
    assert fragment.published_version_id == version.id
```

---

### Phase 2: Frontend Core (2 weeks)

**Goal:** Build UI for editing, versioning, testing

---

#### Step 2.1: Fragment Library (Day 13-14)

**Files to Create:**
```
frontend/src/features/promptStudio/
├── index.tsx                       (Entry point, lazy loaded)
├── components/
│   ├── FragmentLibrary.tsx         (List all fragments)
│   ├── FragmentCard.tsx            (Individual fragment card)
│   └── StatusBadge.tsx             (Live/Draft/Testing badge)
├── api/
│   └── studioApi.ts                (API client)
└── hooks/
    └── useFragments.ts             (Data fetching hook)
```

**Implementation:**

```typescript
// frontend/src/features/promptStudio/index.tsx

import React, { Suspense, lazy } from 'react';
import { Routes, Route } from 'react-router-dom';

// Lazy load components
const FragmentLibrary = lazy(() => import('./components/FragmentLibrary'));
const Editor = lazy(() => import('./components/Editor'));
const Analytics = lazy(() => import('./components/Analytics'));

export default function PromptStudio() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route index element={<FragmentLibrary />} />
        <Route path="edit/:fragmentId" element={<Editor />} />
        <Route path="analytics/:versionId" element={<Analytics />} />
      </Routes>
    </Suspense>
  );
}
```

```typescript
// frontend/src/features/promptStudio/api/studioApi.ts

import { ChatsApi } from '@/generated';  // Reuse generated API client pattern

const API_BASE = '/api/v1/prompt-studio';

export const studioApi = {
  async getPlaceholders() {
    const response = await fetch(`${API_BASE}/placeholders`, {
      headers: { Authorization: `Bearer ${getToken()}` }
    });
    return response.json();
  },
  
  async listFragments() {
    const response = await fetch(`${API_BASE}/fragments`, {
      headers: { Authorization: `Bearer ${getToken()}` }
    });
    return response.json();
  },
  
  async getVersion(versionId: string) {
    const response = await fetch(`${API_BASE}/versions/${versionId}`, {
      headers: { Authorization: `Bearer ${getToken()}` }
    });
    return response.json();
  },
  
  async createDraft(fragmentId: string, content: string, changeSummary?: string) {
    const response = await fetch(`${API_BASE}/fragments/${fragmentId}/versions`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${getToken()}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ content, change_summary: changeSummary })
    });
    return response.json();
  },
  
  async publish(versionId: string) {
    const response = await fetch(`${API_BASE}/versions/${versionId}/publish`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${getToken()}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ export_to_file: true })
    });
    return response.json();
  },
  
  // ... more endpoints ...
};

function getToken() {
  // Reuse existing auth pattern
  return localStorage.getItem('token');
}
```

---

## 5. Database Schema

### Schema Diagram

```
┌─────────────────────┐
│ users               │
│ ├─ id (UUID) PK     │
│ ├─ email            │
│ └─ is_superuser     │ ← EXISTING (reuse)
└─────────────────────┘
          │ 1
          │
          │ N
┌─────────────────────────┐
│ prompt_test_sessions    │ ← NEW
│ ├─ id PK                │
│ ├─ user_id FK           │
│ ├─ prompt_overrides     │
│ ├─ state_overrides      │
│ └─ expires_at           │
└─────────────────────────┘

┌─────────────────────┐
│ prompt_fragments    │ ← NEW
│ ├─ id PK            │
│ ├─ name             │
│ ├─ category         │
│ └─ published_ver_id │───┐
└─────────────────────┘   │
          │ 1             │
          │               │
          │ N             │
┌─────────────────────┐   │
│ prompt_versions     │ ← NEW
│ ├─ id PK            │◄──┘
│ ├─ fragment_id FK   │
│ ├─ version_number   │
│ ├─ status           │
│ ├─ content (TEXT)   │
│ └─ validation_...   │
└─────────────────────┘
          │ 1
          │
          │ N
┌─────────────────────┐
│ prompt_exec_logs    │ ← NEW
│ ├─ id PK            │
│ ├─ version_id FK    │
│ ├─ user_id          │
│ ├─ tokens_*         │
│ ├─ cost_usd         │
│ └─ created_at       │
└─────────────────────┘
```

**Key Points:**
- ✅ No foreign keys TO core tables (only FROM Studio tables)
- ✅ Can drop all Studio tables without affecting core
- ✅ Cascade deletes contained within Studio tables

---

## 6. Testing Strategy

### 6.1 Testing Pyramid

```
                    ▲
                   ╱ ╲
                  ╱ E2E╲         ← 5 tests (full flow)
                 ╱───────╲
                ╱Integration╲    ← 20 tests (API + DB)
               ╱─────────────╲
              ╱  Unit Tests   ╲  ← 50+ tests (isolated)
             ╱─────────────────╲
            ╱  Existing Tests   ╲ ← Regression (must not break)
           ╱─────────────────────╲
```

### 6.2 Regression Tests (CRITICAL)

**Before ANY code changes, create regression baseline:**

```python
# backend/tests/regression/test_studio_does_not_break_chat.py

"""
Regression Tests - Ensure Studio doesn't break core functionality

These tests MUST pass before and after Studio implementation.
Run with: pytest tests/regression/test_studio_does_not_break_chat.py
"""

import pytest
from app.api.services.agents.global_supervisor.global_supervisor import GlobalSupervisor

@pytest.mark.asyncio
async def test_chat_still_works_with_studio_disabled(
    mock_llm_adapter,
    mock_conversation_context_repository,
    mock_domain_agents,
    mock_db_session
):
    """
    CRITICAL: Chat must work when Studio disabled (default state)
    
    This is the baseline - if this fails after Studio added, we broke something.
    """
    supervisor = GlobalSupervisor(
        llm_adapter=mock_llm_adapter,
        domain_agents=mock_domain_agents,
        conversation_context_repository=mock_conversation_context_repository,
        max_iterations=5
    )
    
    # Mock LLM response
    mock_llm_adapter.get_streaming_completion.return_value = AsyncIterator(["Hello!"])
    
    # Run supervisor
    result = await supervisor.run(
        user_message="Hello",
        model="gpt-4o",
        messages_history=[],
        db=mock_db_session,
        chat_id="test-chat",
        user_id="test-user"
    )
    
    # Should complete successfully
    assert result is not None
    assert result.get("user_interface_response") is not None

@pytest.mark.asyncio
async def test_prompt_loading_still_works(tmp_path):
    """
    CRITICAL: Existing prompt loading must still work
    
    This tests that .md files can still be read normally.
    """
    from pathlib import Path
    from app.api.services.agents.global_supervisor.nodes.ui_components.professional_prompt_builder import (
        build_professional_prompt
    )
    
    # Should be able to call build_professional_prompt without errors
    # (This will read from actual .md files)
    prompt = build_professional_prompt(
        variant="simple",
        modality="text",
        authority_level="agent_results",
        user_preferences={},
        user_message="Hello",
        facts_block="",
        conversation_summary="",
        agent_text_summary="",
        greeting_instructions="",
        temporal_context={"current_time": "2025-10-09", "user_timezone": "UTC", "user_locale": "en"}
    )
    
    # Should have content
    assert len(prompt) > 0
    assert "Swisper" in prompt  # Should contain identity

@pytest.mark.asyncio  
async def test_ui_node_still_works(
    mock_llm_adapter,
    mock_db_session
):
    """
    CRITICAL: UI node must still work after Studio added
    
    This ensures middleware doesn't break prompt loading in UI node.
    """
    from app.api.services.agents.global_supervisor.nodes.user_interface_node import user_interface_node
    from app.api.services.agents.global_supervisor_state import GlobalSupervisorState
    
    # Mock state
    state: GlobalSupervisorState = {
        "user_message": "Hello",
        "model": "gpt-4o",
        "chat_id": "test-chat",
        "user_id": "test-user",
        "intent_route": "simple_chat",
        "modality": "text",
        "user_timezone": "UTC",
        "current_time": "2025-10-09T14:30:00Z",
        "user_locale": "en"
    }
    
    # Mock LLM response
    mock_response = Mock()
    mock_response.content = "Hello! How can I help?"
    mock_response.usage = {"prompt_tokens": 100, "completion_tokens": 20}
    mock_llm_adapter.generate_response = AsyncMock(return_value=mock_response)
    
    # Run UI node
    result = await user_interface_node(
        state=state,
        llm_adapter=mock_llm_adapter,
        correlation_id="test-correlation",
        db=mock_db_session
    )
    
    # Should complete successfully
    assert result is not None
    assert result.get("user_interface_response") is not None


# Run these tests BEFORE starting Studio work:
pytest tests/regression/test_studio_does_not_break_chat.py

# Run again AFTER each phase:
pytest tests/regression/test_studio_does_not_break_chat.py

# If any fail, STOP and fix before continuing
```

### 6.3 Integration Test (End-to-End Studio Flow)

```python
# backend/tests/integration/test_prompt_studio_e2e.py

"""
E2E Test: Complete Prompt Studio workflow

Tests the full PO journey:
1. Login as superuser
2. List fragments
3. Create draft version
4. Enable test mode
5. Chat (prompt should use draft)
6. Check analytics
7. Publish draft
8. Chat again (prompt should use published)
9. Rollback
10. Verify rollback worked
"""

import pytest
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_complete_studio_workflow(client: TestClient, superuser_token_headers, db):
    """
    BUSINESS TEST: Complete PO workflow from edit → test → publish
    
    This test simulates a real PO using Studio.
    """
    from app.models import PromptFragment, PromptVersion
    
    # Setup: Create fragment with initial version
    fragment = PromptFragment(id="greeting_voice", name="Greeting Voice", category="voice")
    db.add(fragment)
    db.commit()
    
    v1 = PromptVersion(
        fragment_id="greeting_voice",
        version_number=1,
        status="published",
        content="# Old Greeting\n\nHi!",
        validation_status="valid",
        published_at=datetime.utcnow()
    )
    db.add(v1)
    fragment.published_version_id = v1.id
    db.commit()
    
    # Step 1: PO creates new draft
    response = client.post(
        f"/api/v1/prompt-studio/fragments/greeting_voice/versions",
        headers=superuser_token_headers,
        json={
            "content": "# New Greeting\n\nHello! {{USER_MESSAGE}}",
            "change_summary": "Warmer greeting"
        }
    )
    assert response.status_code == 200
    v2_id = response.json()["id"]
    
    # Step 2: PO enables test mode
    response = client.post(
        "/api/v1/prompt-studio/test-sessions",
        headers=superuser_token_headers,
        json={
            "prompt_overrides": {"greeting_voice": v2_id},
            "state_overrides": {"is_first_message": True}
        }
    )
    assert response.status_code == 200
    
    # Step 3: PO chats (should use v2 due to test mode)
    # (This would require full chat flow test - complex)
    # For now, verify test session is active
    response = client.get(
        "/api/v1/prompt-studio/test-sessions/active",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    session = response.json()
    assert session["prompt_overrides"]["greeting_voice"] == v2_id
    
    # Step 4: PO publishes v2
    response = client.post(
        f"/api/v1/prompt-studio/versions/{v2_id}/publish",
        headers=superuser_token_headers,
        json={"export_to_file": False}
    )
    assert response.status_code == 200
    
    # Verify v2 is now published
    db.refresh(fragment)
    assert fragment.published_version_id == v2_id
    
    # Step 5: PO rollsback to v1 (if something went wrong)
    response = client.post(
        f"/api/v1/prompt-studio/versions/{v1.id}/rollback",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    
    # Verify rollback
    db.refresh(fragment)
    assert fragment.published_version_id == v1.id
```

---

## 7. Deployment & Rollback

### 7.1 Deployment Checklist

**Pre-Deployment:**
```bash
# 1. Run all tests
pytest backend/tests/

# 2. Run regression tests specifically
pytest backend/tests/regression/

# 3. Verify Studio disabled by default
grep "PROMPT_STUDIO_ENABLED" backend/app/core/config.py
# Should default to False

# 4. Backup database
pg_dump swisper_db > backup_before_studio.sql

# 5. Test migrations in staging
alembic upgrade head

# 6. Verify rollback works
alembic downgrade -1
alembic upgrade head
```

**Deployment:**
```bash
# 1. Deploy backend with Studio DISABLED
PROMPT_STUDIO_ENABLED=false docker-compose up -d

# 2. Verify core app works
curl https://api.swisper.com/api/v1/health

# 3. Enable Studio for yourself only
UPDATE users SET is_superuser = true WHERE email = 'heiko@swisper.com';

# 4. Enable Studio feature flag
kubectl set env deployment/backend PROMPT_STUDIO_ENABLED=true

# 5. Verify Studio accessible
curl https://api.swisper.com/api/v1/prompt-studio/fragments \
  -H "Authorization: Bearer YOUR_TOKEN"

# 6. Monitor metrics
# - Core chat latency (should be unchanged)
# - Error rate (should be unchanged)
# - Studio API latency
```

### 7.2 Rollback Plan

**If Studio causes issues:**

**Level 1: Disable Feature Flag (Instant)**
```bash
kubectl set env deployment/backend PROMPT_STUDIO_ENABLED=false
# Middleware disabled, Studio routes hidden
# Core app continues normally
```

**Level 2: Disable Middleware Only**
```python
# If feature flag stuck, disable middleware programmatically
from app.api.services.prompt_studio.middleware import disable_prompt_interception
disable_prompt_interception()
```

**Level 3: Rollback Database Migration**
```bash
alembic downgrade -1  # Removes Studio tables
# Core tables unaffected
```

**Level 4: Remove Code**
```bash
# Remove Studio module
rm -rf backend/app/api/services/prompt_studio/
rm backend/app/api/routes/prompt_studio.py

# Revert touch point changes
git checkout backend/app/main.py
git checkout backend/app/api/main.py
git checkout frontend/src/router/RouteDefinition.tsx

# Deploy
# Core app restored to pre-Studio state
```

---

## 8. Summary & Timeline

### Files Created (Isolated Module)

**Backend (~2,000 lines):**
```
backend/app/api/services/prompt_studio/
├── __init__.py                  (10 lines)
├── middleware.py                (100 lines)
├── state_inspector.py           (300 lines)
├── version_manager.py           (400 lines)
├── test_session_manager.py      (200 lines)
├── validator.py                 (200 lines)
├── renderer.py                  (150 lines)
└── analytics.py                 (300 lines)

backend/app/api/routes/
└── prompt_studio.py             (500 lines)
```

**Frontend (~1,500 lines):**
```
frontend/src/features/promptStudio/
├── index.tsx                    (50 lines)
├── components/
│   ├── FragmentLibrary.tsx      (200 lines)
│   ├── Editor.tsx               (300 lines)
│   ├── PlaceholderBrowser.tsx   (200 lines)
│   ├── CompositionPreview.tsx   (150 lines)
│   ├── VersionHistory.tsx       (200 lines)
│   ├── TestModeSetup.tsx        (200 lines)
│   └── Analytics.tsx            (300 lines)
├── api/
│   └── studioApi.ts             (200 lines)
└── hooks/
    ├── useFragments.ts          (100 lines)
    ├── useVersions.ts           (100 lines)
    └── useTestMode.ts           (100 lines)
```

**Tests (~1,500 lines):**
```
backend/tests/
├── regression/
│   └── test_studio_does_not_break_chat.py  (200 lines)
├── api/services/prompt_studio/
│   ├── test_middleware.py       (300 lines)
│   ├── test_state_inspector.py  (200 lines)
│   ├── test_validator.py        (200 lines)
│   ├── test_version_manager.py  (300 lines)
│   └── test_test_session_manager.py (200 lines)
├── api/routes/
│   └── test_prompt_studio_routes.py (300 lines)
└── integration/
    └── test_prompt_studio_e2e.py (300 lines)
```

**Modified Files:**
```
backend/app/core/config.py        (+1 line)
backend/app/api/deps.py           (+10 lines)
backend/app/main.py               (+3 lines)
backend/app/api/main.py           (+4 lines)
backend/app/models.py             (+200 lines for new models)

frontend/src/router/RouteDefinition.tsx (+10 lines)
frontend/src/features/account/components/account-menu/account-menu.tsx (+10 lines)
frontend/src/features/account/components/account-menu/hooks.ts (+5 lines)
frontend/src/features/account/components/account-menu/types.ts (+1 line)
```

**Total:**
- New code: ~5,000 lines (isolated)
- Modified code: ~244 lines (minimal touch points)
- Tests: ~1,500 lines

---

### Timeline

| Phase | Duration | Deliverables | Tests |
|-------|----------|--------------|-------|
| **Phase 0** | 2 weeks | Middleware validation | 10 tests |
| **Phase 1** | 2 weeks | Backend (DB, APIs, services) | 30 tests |
| **Phase 2** | 2 weeks | Frontend (editor, versioning) | 20 tests |
| **Phase 3** | 1 week | Testing & analytics features | 10 tests |
| **Phase 4** | 1 week | Polish & deploy | 5 E2E tests |
| **Phase 5** | 1 week | Production rollout | Monitoring |
| **Total** | **8-9 weeks** | Full Studio | **75+ tests** |

---

## 9. Success Criteria

### Phase Completion Criteria

**Phase 0 Complete When:**
- ✅ All middleware tests pass (10/10)
- ✅ Can enable/disable without errors
- ✅ Regression tests still pass
- ✅ Performance overhead < 2ms

**Phase 1 Complete When:**
- ✅ All unit tests pass (30/30)
- ✅ Can CRUD fragments/versions via API
- ✅ Superuser auth works, non-superuser blocked
- ✅ Regression tests still pass

**Phase 2 Complete When:**
- ✅ PO can edit greeting_voice.md in UI
- ✅ PO can see composition preview
- ✅ PO can save draft and publish
- ✅ All frontend tests pass (20/20)

**Phase 3 Complete When:**
- ✅ PO can enable test mode
- ✅ PO can override state fields
- ✅ Analytics dashboard shows metrics
- ✅ All integration tests pass (10/10)

**Phase 4 Complete When:**
- ✅ Full E2E flow works (edit → test → publish)
- ✅ All tests pass (75/75)
- ✅ Zero linter errors
- ✅ Documentation complete

**Production Rollout Complete When:**
- ✅ Zero production incidents
- ✅ PO publishes 1+ prompts successfully
- ✅ Core app metrics stable
- ✅ PO satisfaction positive

---

**This plan provides:**
- ✅ Exact file locations
- ✅ Precise code changes
- ✅ Comprehensive tests
- ✅ Clear isolation strategy
- ✅ Rollback procedures
- ✅ Junior-dev friendly guidance

**Ready to start Phase 0 or Phase 1!** 🚀

