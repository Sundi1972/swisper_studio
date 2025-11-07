# Swisper Admin Protocol (SAP) v1.2 - Specification

**Version:** v1.2  
**Last Updated:** 2025-11-07  
**Last Updated By:** heiko  
**Status:** Active

---

## Changelog

### v1.2 - 2025-11-07
- Added User Management endpoints (for per-user tracing consent)
- Added GET /api/admin/users (list users with email/name)
- Added GET /api/admin/users/{user_id} (get single user)
- Added GET /api/admin/users/search?email={email} (search by email)
- Required for Phase 5.5: Per-User Tracing Consent

### v1.1 - 2025-11-03
- Updated with all 18 Kvant models (from https://documentation.kvant.cloud/products/maas/supported_models/)
- Added temperature step=0.1 to schema example
- Clarified field.step usage for number inputs
- Added notes on dynamic model options (future v1.2)
- Updated examples with actual Kvant model names
- Documented browser vs backend URL requirements

### v1.0 - 2025-11-02
- Initial SAP specification
- Defined schema format
- Defined endpoint contracts
- Added validation rules
- Provided examples

---

## 1. Introduction

### 1.1 Purpose

The **Swisper Admin Protocol (SAP)** is a standard API protocol for managing configuration in Swisper deployments. SAP enables:

1. ✅ **Schema Introspection** - Auto-discover config tables and their fields
2. ✅ **CRUD Operations** - Create, Read, Update, Delete config records
3. ✅ **Validation** - Field-level constraints and type checking
4. ✅ **Hot-Reload** - Cache updates without application restart
5. ✅ **Git Deployment** - Generate YAML and commit to source control

### 1.2 Goals

- **Data-Driven UI**: SwisperStudio auto-generates forms from SAP schema
- **No Code Changes**: PO can modify configs via UI without developer intervention
- **Fast Feedback**: "Test Live" mode for immediate testing
- **Source of Truth**: "Deploy to Prod" commits to Git for permanence

### 1.3 Version

- **Current Version:** v1.0
- **Compatibility:** Swisper backend v1.0+
- **Breaking Changes:** None (initial release)

---

## 2. Schema Format

### 2.1 Schema Object

**Endpoint:** `GET /api/admin/config/schema`

**Response Format:**
```json
{
  "version": "1.0",
  "tables": [
    {
      "name": "string",
      "description": "string",
      "primary_key": "string",
      "fields": [
        {
          "name": "string",
          "type": "string" | "number" | "boolean" | "select" | "textarea" | "json",
          "required": boolean,
          "immutable": boolean,
          "description": "string",
          
          // Type-specific properties
          "max_length": number,        // string only
          "pattern": "string",          // string only (regex)
          "min": number,                // number only
          "max": number,                // number only
          "step": number,               // number only
          "options": ["string"],        // select only
          "default": any,               // optional default value
          
          // UI hints
          "placeholder": "string",      // optional
          "help_text": "string",        // optional
          "ui_group": "string"          // optional (for grouping fields in UI)
        }
      ]
    }
  ]
}
```

### 2.2 Field Types

| Type | Description | Validation Properties | UI Component |
|------|-------------|----------------------|--------------|
| `string` | Text field | `max_length`, `pattern`, `default` | `<Input type="text">` |
| `number` | Numeric field | `min`, `max`, `step`, `default` | `<Input type="number">` |
| `boolean` | True/False | `default` | `<Checkbox>` |
| `select` | Dropdown with predefined options | `options` (required), `default` | `<Select>` |
| `textarea` | Multi-line text | `max_length`, `default` | `<Textarea>` |
| `json` | JSON object | `default` | `<JSONEditor>` |

### 2.3 Field Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | string | ✅ Yes | Field identifier (matches database column) |
| `type` | string | ✅ Yes | Field type (see 2.2) |
| `required` | boolean | No (default: false) | Field must have value |
| `immutable` | boolean | No (default: false) | Can't be changed after creation |
| `description` | string | ✅ Yes | Human-readable description |
| `default` | any | No | Default value for new records |
| `placeholder` | string | No | Placeholder text for UI |
| `help_text` | string | No | Additional help text |
| `ui_group` | string | No | Group fields together in UI |

### 2.4 Example Schema

```json
{
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
          "required": true,
          "immutable": true,
          "max_length": 100,
          "description": "LangGraph node identifier",
          "placeholder": "e.g., global_planner",
          "help_text": "Must match node name in LangGraph definition"
        },
        {
          "name": "default_model",
          "type": "select",
          "required": true,
          "options": [
            "inference-llama4-maverick",
            "gpt-4-turbo",
            "gpt-4",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229"
          ],
          "default": "inference-llama4-maverick",
          "description": "Default LLM model for this node",
          "ui_group": "Default Settings"
        },
        {
          "name": "default_temperature",
          "type": "number",
          "required": false,
          "min": 0.0,
          "max": 2.0,
          "step": 0.1,
          "default": 0.7,
          "description": "Sampling temperature (0 = deterministic, 2 = creative)",
          "ui_group": "Default Settings"
        },
        {
          "name": "default_max_tokens",
          "type": "number",
          "required": false,
          "min": 100,
          "max": 32000,
          "step": 100,
          "default": 10000,
          "description": "Maximum tokens in response",
          "ui_group": "Default Settings"
        },
        {
          "name": "azure_model",
          "type": "select",
          "required": false,
          "options": [
            "gpt-4-turbo",
            "gpt-4",
            "gpt-35-turbo"
          ],
          "default": null,
          "description": "Azure-specific model override (NULL uses default)",
          "help_text": "Only used when Azure provider is active",
          "ui_group": "Azure Overrides"
        },
        {
          "name": "langsmith_tracing",
          "type": "boolean",
          "required": false,
          "default": true,
          "description": "Enable LangSmith tracing for this node",
          "help_text": "Disable for high-volume nodes to save costs"
        }
      ]
    }
  ]
}
```

---

## 3. API Endpoints

### 3.1 Schema Introspection

#### Get Config Schema

**Endpoint:** `GET /api/admin/config/schema`

**Description:** Returns schema for all config tables

**Request:**
```http
GET /api/admin/config/schema HTTP/1.1
Host: swisper.example.com
Authorization: Bearer {api_key}
```

**Response:** `200 OK`
```json
{
  "version": "1.0",
  "tables": [...]  // See section 2.4
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing API key
- `403 Forbidden` - User lacks admin permissions

---

### 3.2 CRUD Operations

#### List Config Records

**Endpoint:** `GET /api/admin/config/{table}`

**Description:** List all config records for a table

**Request:**
```http
GET /api/admin/config/llm_node_config HTTP/1.1
Host: swisper.example.com
Authorization: Bearer {api_key}
```

**Response:** `200 OK`
```json
{
  "table": "llm_node_config",
  "records": [
    {
      "node_name": "global_planner",
      "default_model": "gpt-4-turbo",
      "default_temperature": 0.7,
      "default_max_tokens": 4000,
      "azure_model": null,
      "langsmith_tracing": true
    },
    {
      "node_name": "intent_classification",
      "default_model": "inference-llama4-maverick",
      "default_temperature": 0.8,
      "default_max_tokens": 2000,
      "azure_model": null,
      "langsmith_tracing": false
    }
  ],
  "count": 2
}
```

**Error Responses:**
- `404 Not Found` - Table doesn't exist
- `401 Unauthorized` - Invalid API key
- `403 Forbidden` - User lacks permissions

---

#### Get Single Config Record

**Endpoint:** `GET /api/admin/config/{table}/{id}`

**Description:** Get single config record by primary key

**Request:**
```http
GET /api/admin/config/llm_node_config/global_planner HTTP/1.1
Host: swisper.example.com
Authorization: Bearer {api_key}
```

**Response:** `200 OK`
```json
{
  "node_name": "global_planner",
  "default_model": "gpt-4-turbo",
  "default_temperature": 0.7,
  "default_max_tokens": 4000,
  "azure_model": null,
  "langsmith_tracing": true
}
```

**Error Responses:**
- `404 Not Found` - Record not found
- `401 Unauthorized` - Invalid API key

---

#### Create Config Record

**Endpoint:** `POST /api/admin/config/{table}`

**Description:** Create new config record

**Request:**
```http
POST /api/admin/config/llm_node_config HTTP/1.1
Host: swisper.example.com
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "node_name": "ui_node",
  "default_model": "gpt-4-turbo",
  "default_temperature": 0.9,
  "default_max_tokens": 3000,
  "langsmith_tracing": true
}
```

**Response:** `201 Created`
```json
{
  "node_name": "ui_node",
  "default_model": "gpt-4-turbo",
  "default_temperature": 0.9,
  "default_max_tokens": 3000,
  "azure_model": null,
  "langsmith_tracing": true
}
```

**Error Responses:**
- `400 Bad Request` - Validation failed (missing required fields, invalid values)
- `409 Conflict` - Record already exists
- `401 Unauthorized` - Invalid API key

**Validation Errors Example:**
```json
{
  "error": "Validation failed",
  "details": [
    {
      "field": "node_name",
      "error": "Required field missing"
    },
    {
      "field": "default_temperature",
      "error": "Value 3.0 exceeds maximum 2.0"
    }
  ]
}
```

---

#### Update Config Record

**Endpoint:** `PUT /api/admin/config/{table}/{id}`

**Description:** Update existing config record

**Request:**
```http
PUT /api/admin/config/llm_node_config/global_planner HTTP/1.1
Host: swisper.example.com
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "default_model": "gpt-4",
  "default_temperature": 0.5
}
```

**Response:** `200 OK`
```json
{
  "node_name": "global_planner",
  "default_model": "gpt-4",
  "default_temperature": 0.5,
  "default_max_tokens": 4000,
  "azure_model": null,
  "langsmith_tracing": true
}
```

**Error Responses:**
- `404 Not Found` - Record not found
- `400 Bad Request` - Validation failed
- `409 Conflict` - Attempted to modify immutable field
- `401 Unauthorized` - Invalid API key

---

#### Delete Config Record

**Endpoint:** `DELETE /api/admin/config/{table}/{id}`

**Description:** Delete config record

**Request:**
```http
DELETE /api/admin/config/llm_node_config/ui_node HTTP/1.1
Host: swisper.example.com
Authorization: Bearer {api_key}
```

**Response:** `204 No Content`

**Error Responses:**
- `404 Not Found` - Record not found
- `401 Unauthorized` - Invalid API key
- `403 Forbidden` - User lacks delete permissions

---

### 3.3 Live Testing

#### Test Live (Cache Update)

**Endpoint:** `POST /api/admin/config/{table}/{id}/test-live`

**Description:** Update cache immediately without Git commit

**Request:**
```http
POST /api/admin/config/llm_node_config/global_planner/test-live HTTP/1.1
Host: swisper.example.com
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "default_temperature": 0.6
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Config updated in cache (immediate effect)",
  "config": {
    "node_name": "global_planner",
    "default_model": "gpt-4-turbo",
    "default_temperature": 0.6,
    "default_max_tokens": 4000,
    "azure_model": null,
    "langsmith_tracing": true
  },
  "effect": "immediate",
  "deployed_to_git": false
}
```

**Notes:**
- ✅ Updates database
- ✅ Updates in-memory cache (hot-reload)
- ✅ Immediate effect (no restart required)
- ❌ Does NOT commit to Git (temporary change)

---

### 3.4 Production Deployment

#### Deploy to Production (Git Commit)

**Endpoint:** `POST /api/admin/config/{table}/deploy`

**Description:** Generate YAML from current DB state, commit to Git

**Request:**
```http
POST /api/admin/config/llm_node_config/deploy HTTP/1.1
Host: swisper.example.com
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "commit_message": "Update LLM node config: lower temperature for global_planner"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Config deployed to production",
  "deployment": {
    "status": "committed",
    "commit_sha": "a1b2c3d4",
    "file_path": "backend/config/llm_node_config.yaml",
    "commit_message": "Update LLM node config: lower temperature for global_planner",
    "committed_at": "2025-11-02T14:30:00Z",
    "committed_by": "user@example.com"
  },
  "yaml_preview": "# LLM Node Configuration\nllm_nodes:\n  global_planner:\n    default_model: gpt-4-turbo\n    default_temperature: 0.6\n    ..."
}
```

**Error Responses:**
- `400 Bad Request` - Validation failed
- `409 Conflict` - Git has uncommitted changes
- `500 Internal Server Error` - Git operation failed
- `401 Unauthorized` - Invalid API key

**Notes:**
- ✅ Generates YAML from current database state
- ✅ Commits to Git repository
- ✅ Permanent (source of truth)
- ✅ Triggers CI/CD (optional)
- ⏳ Effect: After next deployment

---

### 3.5 User Management (SAP v1.2)

**Purpose:** Enable SwisperStudio to identify users for per-user tracing consent

**Requirements:**
- List users with email/name (for admin to select)
- Search users by email (for finding specific user)
- Get single user details (for verification)
- **NO sensitive data** (no passwords, no sessions, no PII beyond email/name)

---

#### List Users

**Endpoint:** `GET /api/admin/users`

**Description:** List all users (minimal info for user selection)

**Request:**
```http
GET /api/admin/users?limit=50&offset=0 HTTP/1.1
Host: swisper.example.com
Authorization: Bearer {api_key}
```

**Response:** `200 OK`
```json
{
  "users": [
    {
      "id": "user-uuid-123",
      "email": "john.doe@example.com",
      "display_name": "John D.",
      "created_at": "2025-01-15T10:30:00Z"
    },
    {
      "id": "user-uuid-456",
      "email": "jane.smith@example.com",
      "display_name": "Jane S.",
      "created_at": "2025-02-20T14:15:00Z"
    }
  ],
  "total": 2,
  "limit": 50,
  "offset": 0
}
```

**Query Parameters:**
- `limit` (optional): Max records to return (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Privacy:** Only returns non-sensitive data (id, email, name)

---

#### Search Users by Email

**Endpoint:** `GET /api/admin/users/search`

**Description:** Find users by email (for admin to quickly locate user)

**Request:**
```http
GET /api/admin/users/search?email=john.doe@example.com HTTP/1.1
Host: swisper.example.com
Authorization: Bearer {api_key}
```

**Response:** `200 OK`
```json
{
  "users": [
    {
      "id": "user-uuid-123",
      "email": "john.doe@example.com",
      "display_name": "John D.",
      "created_at": "2025-01-15T10:30:00Z"
    }
  ],
  "total": 1
}
```

**Query Parameters:**
- `email` (required): Email to search (partial match supported)

**Use Case:** Admin searches "john@" → finds all Johns

---

#### Get Single User

**Endpoint:** `GET /api/admin/users/{user_id}`

**Description:** Get detailed info for one user

**Request:**
```http
GET /api/admin/users/user-uuid-123 HTTP/1.1
Host: swisper.example.com
Authorization: Bearer {api_key}
```

**Response:** `200 OK`
```json
{
  "id": "user-uuid-123",
  "email": "john.doe@example.com",
  "display_name": "John D.",
  "created_at": "2025-01-15T10:30:00Z",
  "last_active": "2025-11-07T06:30:00Z"
}
```

**Error Responses:**
- `404 Not Found` - User doesn't exist
- `401 Unauthorized` - Invalid API key

---

## 4. Validation Rules

### 4.1 Field Validation

**Type Validation:**
```python
# string
if field.type == "string":
    if len(value) > field.max_length:
        raise ValidationError(f"String exceeds max_length {field.max_length}")
    if field.pattern and not re.match(field.pattern, value):
        raise ValidationError(f"String doesn't match pattern {field.pattern}")

# number
if field.type == "number":
    if value < field.min or value > field.max:
        raise ValidationError(f"Number must be between {field.min} and {field.max}")

# select
if field.type == "select":
    if value not in field.options:
        raise ValidationError(f"Value must be one of: {field.options}")

# boolean
if field.type == "boolean":
    if not isinstance(value, bool):
        raise ValidationError("Value must be true or false")
```

**Required Fields:**
```python
if field.required and value is None:
    raise ValidationError(f"Field {field.name} is required")
```

**Immutable Fields:**
```python
if field.immutable and is_update_operation:
    if value != current_value:
        raise ValidationError(f"Field {field.name} is immutable")
```

### 4.2 Table Validation

**Primary Key Uniqueness:**
```python
if is_create_operation:
    existing = db.query(table).filter_by(primary_key=value).first()
    if existing:
        raise ConflictError(f"Record with {primary_key}={value} already exists")
```

**Foreign Key Constraints:**
```python
# If schema defines foreign_keys
for fk in table_schema.foreign_keys:
    referenced_record = db.query(fk.table).filter_by(id=value).first()
    if not referenced_record:
        raise ValidationError(f"Referenced {fk.table} record not found")
```

---

## 5. Cache Management

### 5.1 Cache Strategy

**Two-Tier Caching:**
1. **In-Memory Cache** (Primary) - Fast, per-instance
2. **Redis Cache** (Optional) - Shared across instances

**Cache Read Flow:**
```
1. Check in-memory cache → Return if found
2. Check Redis cache → Return if found
3. Query database → Cache result → Return
```

**Cache Write Flow:**
```
1. Update database (source of truth)
2. Update in-memory cache (immediate effect)
3. Publish to Redis (notify other instances)
```

### 5.2 Cache Invalidation

**On Config Update:**
```python
def update_config(table: str, id: str, data: dict):
    # Update database
    db.update(table, id, data)
    
    # Update cache (hot-reload)
    cache_key = f"{table}:{id}"
    cache.set(cache_key, data)
    
    # Notify other instances (Redis pub/sub)
    redis.publish(f"config:update", {"table": table, "id": id})
```

**Cache TTL:**
- In-memory: No TTL (updated on-demand)
- Redis: 5 minute TTL (fallback to DB if expired)

**Manual Flush:**
```http
POST /api/admin/config/cache/flush HTTP/1.1
```

---

## 6. Error Handling

### 6.1 Error Response Format

**Standard Error Response:**
```json
{
  "error": "string",
  "code": "string",
  "details": {},
  "timestamp": "ISO8601"
}
```

**Example - Validation Error:**
```json
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": {
    "fields": [
      {
        "field": "default_temperature",
        "error": "Value 3.0 exceeds maximum 2.0",
        "constraint": {"min": 0.0, "max": 2.0}
      }
    ]
  },
  "timestamp": "2025-11-02T14:30:00Z"
}
```

### 6.2 HTTP Status Codes

| Status Code | Meaning | Use Case |
|-------------|---------|----------|
| `200 OK` | Success | GET, PUT requests |
| `201 Created` | Resource created | POST requests |
| `204 No Content` | Success, no body | DELETE requests |
| `400 Bad Request` | Validation error | Invalid input |
| `401 Unauthorized` | Authentication failed | Missing/invalid API key |
| `403 Forbidden` | Authorization failed | User lacks permissions |
| `404 Not Found` | Resource not found | Table/record doesn't exist |
| `409 Conflict` | Conflict error | Duplicate primary key, immutable field change |
| `500 Internal Server Error` | Server error | Unexpected error |

---

## 7. Security

### 7.1 Authentication

**API Key Authentication:**
```http
Authorization: Bearer {api_key}
```

**Key Requirements:**
- ✅ Must be valid API key for Swisper project
- ✅ Must have `admin` scope
- ✅ Validated on every request

### 7.2 Authorization

**Required Permissions:**

| Endpoint | Permission Required |
|----------|---------------------|
| `GET /api/admin/config/schema` | `config:read` |
| `GET /api/admin/config/{table}` | `config:read` |
| `GET /api/admin/config/{table}/{id}` | `config:read` |
| `POST /api/admin/config/{table}` | `config:create` |
| `PUT /api/admin/config/{table}/{id}` | `config:update` |
| `DELETE /api/admin/config/{table}/{id}` | `config:delete` |
| `POST /api/admin/config/{table}/{id}/test-live` | `config:update` |
| `POST /api/admin/config/{table}/deploy` | `config:deploy` |

### 7.3 Audit Logging

**All config operations must be logged:**

```python
{
  "timestamp": "2025-11-02T14:30:00Z",
  "user_id": "user@example.com",
  "action": "update",
  "table": "llm_node_config",
  "record_id": "global_planner",
  "before": {"default_temperature": 0.7},
  "after": {"default_temperature": 0.6},
  "mode": "test_live",  # or "deploy"
  "ip_address": "192.168.1.100"
}
```

---

## 8. Versioning

### 8.1 Version Format

**Semantic Versioning:** `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (incompatible API changes)
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

**Current Version:** v1.0.0

### 8.2 Version Detection

**Schema includes version:**
```json
{
  "version": "1.0"
}
```

**SwisperStudio checks version compatibility:**
```typescript
const MIN_SAP_VERSION = "1.0";
const MAX_SAP_VERSION = "1.9";

if (schemaVersion < MIN_SAP_VERSION || schemaVersion > MAX_SAP_VERSION) {
  throw new Error("Incompatible SAP version");
}
```

### 8.3 Backward Compatibility

**Guaranteed for:**
- ✅ Minor version updates (1.0 → 1.1)
- ✅ Patch version updates (1.0.0 → 1.0.1)

**Breaking changes require:**
- ❌ Major version bump (1.0 → 2.0)
- ❌ Migration guide
- ❌ Deprecation notice (1 minor version before removal)

---

## 9. Examples

### 9.1 Complete Workflow Example

**Step 1: Fetch Schema**
```http
GET /api/admin/config/schema
→ Returns schema for llm_node_config
```

**Step 2: List Current Config**
```http
GET /api/admin/config/llm_node_config
→ Returns all llm_node_config records
```

**Step 3: Update Config (Test Live)**
```http
PUT /api/admin/config/llm_node_config/global_planner
{
  "default_temperature": 0.5
}
→ Updates database + cache (immediate effect)
```

**Step 4: Test in Swisper**
```
User: "Plan my day"
→ Swisper uses temperature=0.5 for global_planner
→ Observe more deterministic planning
```

**Step 5: Deploy to Production**
```http
POST /api/admin/config/llm_node_config/deploy
{
  "commit_message": "Lower temperature for more deterministic planning"
}
→ Generates YAML, commits to Git
```

### 9.2 Error Handling Example

**Invalid Temperature:**
```http
PUT /api/admin/config/llm_node_config/global_planner
{
  "default_temperature": 3.0
}

→ 400 Bad Request
{
  "error": "Validation failed",
  "details": {
    "fields": [
      {
        "field": "default_temperature",
        "error": "Value 3.0 exceeds maximum 2.0",
        "constraint": {"min": 0.0, "max": 2.0}
      }
    ]
  }
}
```

---

## 10. Implementation Checklist

**SAP Compliance Checklist for Swisper Backend:**

- [ ] **Schema Endpoint**
  - [ ] Returns schema for all config tables
  - [ ] Includes field types, constraints, descriptions
  - [ ] Version number included

- [ ] **CRUD Endpoints**
  - [ ] GET /api/admin/config/{table} - List records
  - [ ] GET /api/admin/config/{table}/{id} - Get single record
  - [ ] POST /api/admin/config/{table} - Create record
  - [ ] PUT /api/admin/config/{table}/{id} - Update record
  - [ ] DELETE /api/admin/config/{table}/{id} - Delete record

- [ ] **Validation**
  - [ ] Type validation (string, number, boolean, select)
  - [ ] Required field validation
  - [ ] Immutable field protection
  - [ ] Min/max constraints
  - [ ] Pattern matching (regex)

- [ ] **Cache Management**
  - [ ] In-memory cache implementation
  - [ ] Cache update on config change (hot-reload)
  - [ ] Redis pub/sub (optional, for distributed systems)

- [ ] **Live Testing**
  - [ ] POST /api/admin/config/{table}/{id}/test-live
  - [ ] Updates cache immediately
  - [ ] No Git commit

- [ ] **Production Deployment**
  - [ ] POST /api/admin/config/{table}/deploy
  - [ ] Generates YAML from database
  - [ ] Commits to Git repository
  - [ ] Returns deployment status

- [ ] **Security**
  - [ ] API key authentication
  - [ ] Permission checks
  - [ ] Audit logging

- [ ] **Error Handling**
  - [ ] Standard error response format
  - [ ] Appropriate HTTP status codes
  - [ ] Detailed validation errors

---

## 11. Related Documentation

- **Analysis**: `docs/analysis/phase4_config_analysis.md`
- **Implementation Plan**: `docs/plans/plan_phase4_config_v1.md`
- **Swisper Models**: `reference/swisper/backend/app/models.py`

---

**SAP v1.0 Specification Complete!** ✅

**Next:** Create detailed implementation plan for Phase 4.

