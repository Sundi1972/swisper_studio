# Specification: Privacy-First Per-User Tracing with Consent

**Version:** 1.0  
**Date:** 2025-11-07  
**Status:** Draft - Awaiting Approval  
**Priority:** HIGH (Privacy & Compliance)  
**Phase:** 5.5 - Before Production  
**Estimated Effort:** 5-7 days (both teams)

---

## 📋 Table of Contents

1. [Problem Statement](#problem-statement)
2. [Goals & Requirements](#goals--requirements)
3. [Architecture](#architecture)
4. [User Workflows](#user-workflows)
5. [Technical Implementation](#technical-implementation)
6. [Tracing Indicator](#tracing-indicator)
7. [Privacy & Compliance](#privacy--compliance)
8. [Testing Strategy](#testing-strategy)
9. [Timeline & Effort](#timeline--effort)

---

## 🎯 Problem Statement

### **Current State (Privacy Risk)**

**What happens now:**
```
User sends message: "My credit card is 1234-5678-9012-3456"
  ↓
SDK captures EVERYTHING (full prompt, state, responses)
  ↓
Stores in SwisperStudio PostgreSQL
  ↓
Admin can see: "My credit card is 1234-5678-9012-3456"
```

**Issues:**
- ❌ **PII Exposure:** Captures passwords, credit cards, health data, personal info
- ❌ **GDPR Violation:** No user consent for data collection
- ❌ **Production Risk:** All users traced = massive data exposure
- ❌ **Compliance Risk:** Violates privacy regulations (GDPR, CCPA, HIPAA)
- ❌ **User Trust:** Users don't know they're being monitored
- ❌ **Cost:** Tracing everyone = expensive observability costs

### **Current Tracing Levels**

**Only:** Project-level toggle (ON/OFF for entire project)
- Turn ON → ALL users traced ❌
- Turn OFF → NO users traced ❌
- **No granularity** for selective debugging

---

## ✅ Goals & Requirements

### **Primary Goals**

1. **Privacy-First:** Only trace with explicit user consent
2. **GDPR Compliant:** User opts in, data expires automatically
3. **Selective Debugging:** Trace problematic user, not everyone
4. **Production Safe:** Default = NO tracing in production
5. **User Transparency:** Clear communication about data collection

### **Functional Requirements**

**FR1: Per-User Consent Management**
- Admin can request tracing consent for specific user
- User sees consent dialog with clear explanation
- User can accept or decline
- Consent auto-expires after 24 hours

**FR2: Hierarchical Toggle System**
```
Level 1: Project Default (ON/OFF for all users)
Level 2: User Override (per-user consent)

Logic:
- If user has consent = "granted" → Trace (regardless of project default)
- If user has consent = "denied" → Don't trace (regardless of project default)
- If user has no consent record → Use project default
```

**FR3: User Identity via SAP**
- Swisper exposes user list via SAP (GET /api/admin/users)
- SwisperStudio syncs minimal user data (id, email, name)
- Admin searches by email, selects user
- No sensitive data synced

**FR4: Tracing Health Indicator**
```
🟢 Green  = Tracing ON + SDK publishing heartbeats (<30s)
🟡 Orange = Tracing ON + SDK stale (heartbeat >30s or missing)
⚪ Gray   = Tracing OFF (or no consent)
```

**FR5: SDK Heartbeat (Already Implemented)**
- SDK publishes heartbeat every 10 seconds when tracing active
- Includes project_id, sdk_version, timestamp
- Swisper monitors to show green indicator

---

## 🏗️ Architecture

### **System Components**

```
┌─────────────────────────────────────────────────────────────┐
│                    SwisperStudio                            │
│                                                             │
│  ┌──────────────────┐  ┌────────────────────────────────┐ │
│  │  Admin UI        │  │  Backend                       │ │
│  │                  │  │                                │ │
│  │  1. Search user  │  │  ┌──────────────────────────┐ │ │
│  │     by email     │──┼─►│ SAP Proxy: GET /users    │ │ │
│  │                  │  │  │ Calls Swisper API        │ │ │
│  │  2. Request      │  │  └──────────────────────────┘ │ │
│  │     consent      │  │                                │ │
│  │                  │  │  ┌──────────────────────────┐ │ │
│  │  3. View traces  │  │  │ Consent Management       │ │ │
│  │     (if granted) │  │  │ - Create consent request │ │ │
│  │                  │  │  │ - Check consent status   │ │ │
│  └──────────────────┘  │  │ - Auto-expire (24h)      │ │ │
│                         │  └──────────────────────────┘ │ │
│  ┌──────────────────┐  │                                │ │
│  │  Database        │  │  ┌──────────────────────────┐ │ │
│  │                  │  │  │ Redis Cache              │ │ │
│  │  - user_registry │  │  │                          │ │ │
│  │  - tracing_      │  │  │ tracing:{project}:       │ │ │
│  │    consent       │  │  │   user:{user}:consent    │ │ │
│  └──────────────────┘  │  │ = granted/denied/expired │ │ │
│                         │  └──────────────────────────┘ │ │
└─────────────────────────────────────────────────────────────┘
                                    ▲
                                    │ SAP /api/admin/users
                                    │ Consent checks
                                    ▼
┌─────────────────────────────────────────────────────────────┐
│                       Swisper                               │
│                                                             │
│  ┌──────────────────┐  ┌────────────────────────────────┐ │
│  │  Frontend UI     │  │  Backend                       │ │
│  │                  │  │                                │ │
│  │  Consent Dialog  │  │  ┌──────────────────────────┐ │ │
│  │  ┌────────────┐  │  │  │ SAP User Endpoints       │ │ │
│  │  │ Help Debug?│  │  │  │ GET /api/admin/users     │ │ │
│  │  │ [Yes] [No] │  │  │  │ GET /api/admin/users/{id}│ │ │
│  │  └────────────┘  │  │  │ GET /api/admin/users/    │ │ │
│  │                  │  │  │     search?email=...     │ │ │
│  │  Indicator:      │  │  └──────────────────────────┘ │ │
│  │  🟢 Tracing ON   │  │                                │ │
│  └──────────────────┘  │  ┌──────────────────────────┐ │ │
│                         │  │ Consent Check Logic      │ │ │
│                         │  │ - Check Redis cache      │ │ │
│                         │  │ - Show dialog if pending │ │ │
│                         │  │ - Update cache on accept │ │ │
│                         │  └──────────────────────────┘ │ │
│  ┌──────────────────┐  │                                │ │
│  │  Database        │  │  ┌──────────────────────────┐ │ │
│  │  - users table   │  │  │ SDK (in-process)         │ │ │
│  │    (source of    │  │  │ - Check consent before   │ │ │
│  │     truth)       │  │  │   creating trace         │ │ │
│  └──────────────────┘  │  │ - Publish heartbeat      │ │ │
│                         │  │ - Monitor Redis stream   │ │ │
│                         │  └──────────────────────────┘ │ │
└─────────────────────────────────────────────────────────────┘
```

---

### **Data Models**

#### **SwisperStudio Database**

```sql
-- Minimal user registry (synced from Swisper via SAP)
CREATE TABLE user_registry (
    project_id UUID,
    user_id VARCHAR,           -- From Swisper users.id
    email VARCHAR,             -- From Swisper (for display/search)
    display_name VARCHAR,      -- From Swisper (for display)
    first_seen TIMESTAMP,      -- Auto-populated from first trace
    last_seen TIMESTAMP,       -- Updated from traces
    synced_at TIMESTAMP,       -- Last sync from Swisper API
    PRIMARY KEY (project_id, user_id)
);

-- Tracing consent records
CREATE TABLE tracing_consent (
    project_id UUID,
    user_id VARCHAR,
    consent_status VARCHAR,    -- 'pending', 'granted', 'denied', 'expired'
    requested_by_admin_id UUID,-- Admin who requested consent
    requested_at TIMESTAMP,
    request_reason TEXT,       -- Why tracing is needed
    consent_given_at TIMESTAMP NULL,
    expires_at TIMESTAMP NULL, -- 24h after granted
    notes TEXT,                -- Admin notes
    PRIMARY KEY (project_id, user_id)
);

-- Audit log for consent operations
CREATE TABLE consent_audit_log (
    id UUID PRIMARY KEY,
    project_id UUID,
    user_id VARCHAR,
    action VARCHAR,            -- 'requested', 'granted', 'denied', 'expired'
    performed_by VARCHAR,      -- Admin or user email
    performed_at TIMESTAMP,
    details JSONB
);
```

#### **Redis Cache Keys**

```python
# Project-level toggle (existing)
"tracing:{project_id}:enabled" = "true" | "false"
TTL: 300 seconds (5 minutes)

# User-level consent (new)
"tracing:{project_id}:user:{user_id}:consent" = "granted" | "denied" | "pending" | "expired"
TTL: 86400 seconds (24 hours)

# Last heartbeat timestamp (for indicator)
"heartbeat:{project_id}:last" = "2025-11-07T07:30:15Z"
TTL: 60 seconds (updated on each heartbeat)
```

---

## 🔄 User Workflows

### **Workflow 1: Admin Requests Consent**

```
1. User reports issue:
   "I can't book meetings, please help!"

2. Admin opens SwisperStudio:
   → Navigate to Tracing → Consent Management
   → Click "Request Consent"

3. Admin searches for user:
   → Enter email: john.doe@example.com
   → SwisperStudio calls: GET /api/admin/users/search?email=john.doe
   → Shows: John D. (user-uuid-123)
   → Admin selects user

4. Admin fills form:
   → User: John D. (john.doe@example.com)
   → Reason: "Debugging meeting booking issue"
   → Duration: 24 hours
   → Click "Request Consent"

5. SwisperStudio creates consent record:
   → INSERT INTO tracing_consent (status='pending', reason='...')
   → Redis: SET tracing:{project}:user:{user_id}:consent = "pending" EX 86400
   → Shows in admin UI: "Consent pending for John D."

6. Admin notifies user:
   → "Please log into Swisper, you'll see a consent request"
```

---

### **Workflow 2: User Grants Consent**

```
1. User logs into Swisper:
   → Opens Swisper frontend

2. Swisper checks consent status:
   → Backend reads: GET tracing:{project}:user:{user_id}:consent
   → Returns: "pending"
   → Frontend shows consent dialog

3. Consent Dialog:
   ┌───────────────────────────────────────────────┐
   │  Help Us Debug Your Issue                     │
   ├───────────────────────────────────────────────┤
   │                                               │
   │  We'd like to trace your session to help fix  │
   │  the issue you're experiencing.               │
   │                                               │
   │  What we'll capture:                          │
   │  • Your messages and system responses         │
   │  • System state during execution              │
   │  • Timing and cost information                │
   │                                               │
   │  Your data will be:                           │
   │  • Stored securely in SwisperStudio           │
   │  • Viewed only by authorized support staff    │
   │  • Automatically deleted after 24 hours       │
   │                                               │
   │  Reason: Debugging meeting booking issue      │
   │                                               │
   │  [No Thanks]         [Yes, Help Me Debug]     │
   └───────────────────────────────────────────────┘

4. User clicks "Yes, Help Me Debug":
   → POST /api/consent/grant {user_id, project_id}
   → Swisper updates: SET tracing:{project}:user:{user_id}:consent = "granted" EX 86400
   → Swisper calls SwisperStudio: POST /api/v1/consent/granted
   → SwisperStudio updates DB: consent_status = 'granted', consent_given_at = now()

5. Dialog closes:
   → User continues using Swisper normally
   → Small green indicator shows: "🟢 Tracing Active"
```

---

### **Workflow 3: SDK Traces User Session**

```
1. User sends message: "Book meeting with Alice tomorrow"

2. SDK checks consent (in graph_wrapper.py):
   → project_id = get_project_id()
   → user_id = extract_user_id(input_state)
   → should_trace = await check_user_consent(project_id, user_id)

3. Consent check logic:
   → Redis GET: tracing:{project}:user:{user_id}:consent
   → Result: "granted"
   → SDK proceeds with tracing ✅

4. Trace created:
   → Full state, prompts, responses captured
   → Published to Redis Stream
   → SwisperStudio stores in database
   → Admin can debug!

5. Other users (no consent):
   → SDK checks consent for user-456
   → Redis GET: tracing:{project}:user:456:consent → NULL
   → Fallback to project default → "false" (production)
   → SDK skips tracing ✅ (privacy protected!)
```

---

### **Workflow 4: Auto-Expiry**

```
After 24 hours:
  → Redis TTL expires
  → tracing:{project}:user:{user_id}:consent → NULL
  → SDK fallback to project default → OFF
  → User no longer traced
  → SwisperStudio background job: UPDATE consent_status = 'expired'
  → Admin notified: "Consent expired for John D."
  → Existing traces remain (for historical analysis)
```

---

### **Workflow 5: User Declines Consent**

```
User clicks "No Thanks":
  → POST /api/consent/deny
  → Redis: SET tracing:{project}:user:{user_id}:consent = "denied" EX 86400
  → SwisperStudio: UPDATE consent_status = 'denied'
  → Admin sees: "John D. declined consent"
  → Admin must debug another way (logs, support call)
```

---

## 🔧 Technical Implementation

### **Phase 1: SAP User Endpoints (Swisper Team - 3 hours)**

**Add to SAP v1.2:**

```python
# backend/app/api/routes/admin/users.py

@router.get("/api/admin/users")
async def list_users(
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(get_db)
):
    """List all users (minimal info for consent management)"""
    users = session.query(User).limit(limit).offset(offset).all()
    total = session.query(User).count()
    
    return {
        "users": [
            {
                "id": str(user.id),
                "email": user.email,
                "display_name": user.name or user.email.split('@')[0],
                "created_at": user.created_at.isoformat(),
            }
            for user in users
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }

@router.get("/api/admin/users/search")
async def search_users(
    email: str,
    session: Session = Depends(get_db)
):
    """Search users by email (partial match)"""
    users = session.query(User).filter(
        User.email.ilike(f"%{email}%")
    ).all()
    
    return {
        "users": [/* same format */],
        "total": len(users)
    }

@router.get("/api/admin/users/{user_id}")
async def get_user(user_id: str, session: Session = Depends(get_db)):
    """Get single user details"""
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    return {
        "id": str(user.id),
        "email": user.email,
        "display_name": user.name or user.email.split('@')[0],
        "created_at": user.created_at.isoformat(),
        "last_active": user.last_login.isoformat() if user.last_login else None
    }
```

**Effort:** 3 hours  
**Testing:** Add 3-5 tests for user endpoints

---

### **Phase 2: SwisperStudio Consent Management (SwisperStudio Team - 2 days)**

#### **Backend (1 day)**

**Database Models:**
```python
# backend/app/models/user_registry.py
class UserRegistry(SQLModel, table=True):
    """Minimal user data synced from Swisper (via SAP)"""
    __tablename__ = "user_registry"
    
    project_id: str = Field(foreign_key="projects.id")
    user_id: str  # From Swisper
    email: str
    display_name: str
    first_seen: datetime
    last_seen: datetime
    synced_at: datetime
    
    __table_args__ = (
        PrimaryKeyConstraint("project_id", "user_id"),
    )

class TracingConsent(SQLModel, table=True):
    """Per-user tracing consent records"""
    __tablename__ = "tracing_consent"
    
    project_id: str = Field(foreign_key="projects.id")
    user_id: str
    consent_status: str  # 'pending', 'granted', 'denied', 'expired'
    requested_by_admin_id: str = Field(foreign_key="users.id")
    requested_at: datetime
    request_reason: str
    consent_given_at: datetime | None
    expires_at: datetime | None
    notes: str | None
    
    __table_args__ = (
        PrimaryKeyConstraint("project_id", "user_id"),
    )
```

**API Endpoints:**
```python
# POST /api/v1/projects/{project_id}/consent/request
# GET /api/v1/projects/{project_id}/consent
# POST /api/v1/consent/{consent_id}/cancel
# GET /api/v1/users/search?project_id=...&email=...
```

**Services:**
```python
# app/services/consent_service.py
async def request_consent(project_id, user_id, admin_id, reason):
    # 1. Sync user from Swisper (if not in registry)
    # 2. Create consent record (status='pending')
    # 3. Set Redis cache with 24h TTL
    # 4. Return consent record

async def grant_consent(project_id, user_id):
    # 1. Update consent_status = 'granted'
    # 2. Set consent_given_at, expires_at (now + 24h)
    # 3. Update Redis cache
    # 4. Return updated record

async def check_user_consent(project_id, user_id) -> bool:
    # 1. Check Redis cache first
    # 2. If cache miss, check database
    # 3. Return True/False
```

#### **Frontend (1 day)**

**Admin UI Pages:**
```tsx
// frontend/src/features/tracing/components/consent-management-page.tsx
// - Search user by email (calls Swisper SAP)
// - Request consent button
// - List active consents
// - View consent history
// - Cancel consent button

// frontend/src/features/tracing/components/request-consent-dialog.tsx
// - User search/select
// - Reason textarea
// - Duration selector (24h default)
// - Submit button
```

---

### **Phase 3: Swisper Consent Dialog (Swisper Team - 1 day)**

#### **Backend Consent Endpoints:**

```python
# POST /api/consent/grant
async def grant_consent(user_id: str):
    # Update Redis cache
    redis.setex(
        f"tracing:{project_id}:user:{user_id}:consent",
        86400,  # 24 hours
        "granted"
    )
    
    # Notify SwisperStudio
    await httpx.post(
        f"{swisperstudio_url}/api/v1/consent/granted",
        json={"project_id": project_id, "user_id": user_id}
    )
    
    return {"status": "granted"}

# POST /api/consent/deny
async def deny_consent(user_id: str):
    redis.setex(
        f"tracing:{project_id}:user:{user_id}:consent",
        86400,
        "denied"
    )
    # Notify SwisperStudio
    return {"status": "denied"}
```

#### **Frontend Dialog:**

```tsx
// Check consent on app load
useEffect(() => {
    const checkConsent = async () => {
        const status = await api.get('/consent/status');
        if (status === 'pending') {
            setShowConsentDialog(true);
        }
    };
    checkConsent();
}, []);

// Consent Dialog Component
<Dialog open={showConsentDialog}>
    <DialogTitle>Help Us Debug Your Issue</DialogTitle>
    <DialogContent>
        <Typography>
            We'd like to trace your session to help fix the issue
            you're experiencing.
        </Typography>
        
        <Box sx={{ my: 2, p: 2, bgcolor: 'info.light' }}>
            <Typography variant="body2">
                <strong>What we'll capture:</strong>
            </Typography>
            <ul>
                <li>Your messages and system responses</li>
                <li>System state during execution</li>
                <li>Timing and cost information</li>
            </ul>
        </Box>
        
        <Box sx={{ my: 2, p: 2, bgcolor: 'success.light' }}>
            <Typography variant="body2">
                <strong>Your data will be:</strong>
            </Typography>
            <ul>
                <li>Stored securely in SwisperStudio</li>
                <li>Viewed only by authorized support staff</li>
                <li>Automatically deleted after 24 hours</li>
            </ul>
        </Box>
        
        <Typography variant="body2" color="text.secondary">
            <strong>Reason:</strong> {consentReason}
        </Typography>
    </DialogContent>
    <DialogActions>
        <Button onClick={handleDecline}>
            No Thanks
        </Button>
        <Button onClick={handleAccept} variant="contained">
            Yes, Help Me Debug
        </Button>
    </DialogActions>
</Dialog>
```

---

### **Phase 4: SDK Consent Check (SwisperStudio Team - 2 hours)**

**Update graph_wrapper.py:**

```python
async def should_create_trace_for_user(project_id: str, user_id: str | None) -> bool:
    """
    Check if we should create trace for this user.
    
    Hierarchy:
    1. User-level consent (overrides project default)
    2. Project-level toggle (default)
    
    Returns:
        True if should trace, False otherwise
    """
    # No user_id → fallback to project default
    if not user_id:
        return await is_tracing_enabled_for_project(project_id)
    
    # Check user-level consent (Redis cache)
    redis_client = get_redis_client()
    if redis_client:
        try:
            consent_key = f"tracing:{project_id}:user:{user_id}:consent"
            consent = await redis_client.get(consent_key)
            
            if consent == b"granted":
                logger.info(f"✅ User {user_id[:8]}... granted consent - tracing")
                return True
            if consent == b"denied":
                logger.info(f"⏸️ User {user_id[:8]}... denied consent - skipping")
                return False
            if consent == b"expired":
                logger.info(f"⏰ User {user_id[:8]}... consent expired - skipping")
                return False
            # consent == NULL or "pending" → fallback to project default
        except Exception as e:
            logger.warning(f"Failed to check user consent: {e}")
    
    # Fallback to project-level toggle
    return await is_tracing_enabled_for_project(project_id)


# In traced_ainvoke():
user_id = input_state.get("user_id") if isinstance(input_state, dict) else None
project_id = get_project_id()

if project_id:
    should_trace = await should_create_trace_for_user(project_id, user_id)
    if not should_trace:
        logger.info(f"⏸️ Tracing disabled, skipping trace")
        return await original_ainvoke(input_state, config, **invoke_kwargs)
```

---

### **Phase 5: Tracing Indicator (Swisper Team - 1 day)**

#### **Backend - Check Status**

```python
@router.get("/api/tracing/status")
async def get_tracing_status(current_user: User = Depends(get_current_user)):
    """Get tracing status for current user (for sidebar indicator)"""
    redis_client = get_redis_client()
    project_id = settings.SWISPER_STUDIO_PROJECT_ID
    user_id = str(current_user.id)
    
    # 1. Check user-level consent
    consent = await redis_client.get(f"tracing:{project_id}:user:{user_id}:consent")
    if consent in [b"denied", b"expired"]:
        return {"status": "gray", "message": "Tracing disabled"}
    
    tracing_on = consent == b"granted"
    if not tracing_on:
        # Check project default
        project_enabled = await redis_client.get(f"tracing:{project_id}:enabled")
        tracing_on = project_enabled == b"true"
    
    if not tracing_on:
        return {"status": "gray", "message": "Tracing off"}
    
    # 2. Check heartbeat (SDK health)
    messages = await redis_client.xrevrange("observability:events", count=20)
    last_heartbeat = None
    
    for msg_id, msg_data in messages:
        if msg_data.get(b'event_type') == b'heartbeat':
            data = json.loads(msg_data[b'data'])
            last_heartbeat = data['timestamp']
            break
    
    if not last_heartbeat:
        return {"status": "orange", "message": "SDK not responding"}
    
    # 3. Calculate heartbeat age
    heartbeat_time = datetime.fromisoformat(last_heartbeat)
    age = (datetime.utcnow() - heartbeat_time).total_seconds()
    
    if age < 30:
        return {"status": "green", "message": f"Active ({int(age)}s ago)"}
    else:
        return {"status": "orange", "message": f"Stale ({int(age)}s ago)"}
```

#### **Frontend - Sidebar Indicator**

```tsx
// Poll every 30 seconds
const { data } = useQuery({
    queryKey: ['tracing-status'],
    queryFn: () => api.get('/tracing/status'),
    refetchInterval: 30000,
});

// Indicator component
function TracingIndicator({ status }: { status: string }) {
    const colors = {
        green: '#4caf50',
        orange: '#ff9800',
        gray: '#9e9e9e',
    };
    
    return (
        <Box 
            sx={{
                position: 'absolute',
                top: -2,
                right: -2,
                width: 8,
                height: 8,
                borderRadius: '50%',
                bgcolor: colors[status] || colors.gray,
                border: '1px solid #fff',
                boxShadow: 1,
            }}
            title={data?.message}
        />
    );
}

// In sidebar (next to Overview or logo)
<Box sx={{ position: 'relative' }}>
    <OverviewIcon />
    {data?.status && <TracingIndicator status={data.status} />}
</Box>
```

---

## 🔒 Privacy & Compliance

### **GDPR Compliance**

✅ **Lawful Basis:** Explicit consent (GDPR Article 6.1.a)  
✅ **Purpose Limitation:** Only for debugging (specified purpose)  
✅ **Data Minimization:** Only traces consenting users  
✅ **Storage Limitation:** Auto-delete after 24 hours  
✅ **Transparency:** Clear consent dialog explaining data collection  
✅ **Right to Withdraw:** User can decline or revoke  
✅ **Data Security:** Encrypted in transit and at rest

### **Consent Requirements**

**Must Include:**
- ✅ What data is collected
- ✅ Why it's needed (debugging purpose)
- ✅ How long it's stored (24 hours)
- ✅ Who can access it (support team)
- ✅ How to decline

**Cannot:**
- ❌ Force consent (must be optional)
- ❌ Hide data collection
- ❌ Keep data longer than stated
- ❌ Use for other purposes

---

## 🧪 Testing Strategy

### **Test Scenarios**

**Test 1: Consent Request Flow**
```
1. Admin requests consent for user
2. Verify pending status in Redis
3. User sees consent dialog
4. User accepts
5. Verify granted status
6. Verify trace created on next request
```

**Test 2: Consent Denial**
```
1. Admin requests consent
2. User declines
3. Verify denied status
4. Send request
5. Verify NO trace created
```

**Test 3: Auto-Expiry**
```
1. User grants consent
2. Mock time advance 25 hours
3. Verify consent expired
4. Send request
5. Verify NO trace created
```

**Test 4: Hierarchical Logic**
```
Project: OFF, User consent: granted → Trace ✅
Project: ON, User consent: denied → Don't trace ✅
Project: ON, User consent: NULL → Trace ✅
Project: OFF, User consent: NULL → Don't trace ✅
```

**Test 5: Indicator States**
```
Toggle OFF → Gray bubble
Toggle ON + Heartbeat fresh → Green bubble
Toggle ON + Heartbeat stale → Orange bubble
Toggle ON + No heartbeat → Orange bubble
```

---

## ⏱️ Timeline & Effort

### **Implementation Breakdown**

| Phase | Team | Duration | Tasks |
|-------|------|----------|-------|
| **Phase 1** | Swisper | 3h | SAP user endpoints |
| **Phase 2** | SwisperStudio | 2d | Consent management (backend + frontend) |
| **Phase 3** | Swisper | 1d | Consent dialog UI |
| **Phase 4** | SwisperStudio | 2h | SDK consent check logic |
| **Phase 5** | Swisper | 1d | Tracing indicator |
| **Testing** | Both | 4h | Integration testing |
| **TOTAL** | Both | **5-6 days** | Full privacy-first tracing |

### **Parallel Work**

**Week 1 (Swisper + SwisperStudio parallel):**
- Swisper: Implement SAP user endpoints (3h)
- SwisperStudio: Build consent management backend (1d)

**Week 2 (Sequential):**
- SwisperStudio: Consent management frontend (1d)
- Swisper: Consent dialog UI (1d)
- SwisperStudio: SDK integration (2h)
- Swisper: Tracing indicator (1d)
- Both: Integration testing (4h)

**Total Calendar Time:** ~7-10 days (with parallel work)

---

## ✅ Success Criteria

**Must Have:**
- ✅ Admin can request consent for specific user by email
- ✅ User sees clear consent dialog with privacy info
- ✅ User can accept or decline
- ✅ Only consenting users are traced
- ✅ Consent auto-expires after 24 hours
- ✅ Tracing indicator shows 3 states (green/orange/gray)
- ✅ SDK respects user-level consent
- ✅ No traces created for users without consent in production

**Should Have:**
- ✅ Audit log of all consent operations
- ✅ Admin can view consent history
- ✅ Admin can cancel consent early
- ✅ Email notification when consent requested

**Nice to Have:**
- ⏸️ User can revoke consent mid-session
- ⏸️ Consent export for compliance
- ⏸️ Anonymization option (hash user_id in traces)

---

## 🚀 Rollout Strategy

### **Phase 5.5: Per-User Tracing (Before Production)**

**Priority:** HIGH (privacy & compliance requirement)

**When:** After Phase 5.3 (User Auth) and Phase 5.4 (SDK Publishing)

**Why Before Production:**
- Legal requirement (can't trace all users without consent)
- Privacy-first approach
- Competitive advantage

**Production Default:**
```
Project-level tracing: OFF
Per-user consent: Required for debugging
Result: Zero tracing unless user opts in
```

---

## 📝 Open Questions

**Q1: Consent Duration**
- 24 hours (as spec'd)?
- Or configurable per request?
- **Recommendation:** 24h default, allow admin to extend

**Q2: Consent Notification**
- Email user when consent requested?
- Or just show dialog on next login?
- **Recommendation:** Both (email + dialog)

**Q3: Existing Traces**
- Keep after consent expires?
- Or auto-delete with consent?
- **Recommendation:** Keep (historical value) but mark as expired

**Q4: Multi-Session**
- User has multiple sessions - trace all?
- Or specific session only?
- **Recommendation:** All sessions for that user_id within 24h

---

**Version:** 1.0  
**Status:** Draft - Awaiting Approval  
**Next:** Create implementation plan (plan_per_user_tracing_v1.md)

