# Swisper Admin Protocol (SAP) v1.1 - Complete Specification

**Version:** v1.1  
**Last Updated:** 2025-11-03  
**Last Updated By:** heiko  
**Status:** Active - Contract Document

**This is the authoritative specification for the contract between SwisperStudio and Swisper.**

---

## Changelog

### v1.1 - 2025-11-03
- Added all 18 Kvant models (from https://documentation.kvant.cloud/products/maas/supported_models/)
- Added `step` property for number fields (temperature uses 0.1)
- Documented dynamic vs static model options decision
- Added architecture decisions and rationale
- Added implementation examples from mock SAP
- Clarified browser accessibility requirements
- Added field rendering guidelines for SwisperStudio
- Expanded validation rules
- Added troubleshooting section

### v1.0 - 2025-11-02
- Initial SAP specification

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Architecture Decisions](#2-architecture-decisions)
3. [Schema Format](#3-schema-format)
4. [API Endpoints](#4-api-endpoints)
5. [Validation Rules](#5-validation-rules)
6. [Model Options](#6-model-options)
7. [Error Handling](#7-error-handling)
8. [Implementation Guidelines](#8-implementation-guidelines)
9. [Examples](#9-examples)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Introduction

### 1.1 Purpose

The **Swisper Admin Protocol (SAP)** is a REST API contract between:
- **Swisper Backend** (server) - Exposes configuration via API
- **SwisperStudio Frontend** (client) - Consumes configuration via UI

SAP enables:
1. ✅ **Schema Introspection** - Auto-discover config tables and fields
2. ✅ **CRUD Operations** - Manage configuration records
3. ✅ **Field Validation** - Type checking and constraints
4. ✅ **Auto-Generated UI** - SwisperStudio builds forms from schema
5. ✅ **Hot-Reload** - Changes take effect without restart

### 1.2 Version

- **Current Version:** v1.1
- **Compatibility:** Swisper backend v1.0+, SwisperStudio v1.0+
- **Breaking Changes:** None (backward compatible with v1.0)

### 1.3 Reference Implementation

- **Mock SAP:** `backend/app/api/routes/mock_sap.py` in SwisperStudio repo
- **Live Example:** http://localhost:8001/api/v1/mock-swisper/api/admin/config/schema

---

## 2. Architecture Decisions

### 2.1 Static vs Dynamic Model Options

**Decision:** Model options are **static in schema** (SAP v1.1)

**Rationale:**
- Kvant models change infrequently (quarterly)
- Azure deployments are customer-specific (can't be in shared schema)
- Static options simplify implementation
- Future v1.2 will add `options_source` for dynamic lookups

**Implementation:**
```python
# Swisper backend hardcodes model list
"options": [
    "inference-llama4-maverick",
    "inference-apertus-8b",
    # ... all 18 Kvant models
]

# Updated quarterly when Kvant releases new models
```

**Future (SAP v1.2):**
```json
{
  "name": "azure_model",
  "type": "select",
  "options_source": "/api/admin/config/model-options?field=azure_model"
}
```

### 2.2 Number Field Step Values

**Decision:** Include `step` property in schema for decimal fields

**Rationale:**
- Temperature needs 0.1 increments (not 1.0)
- Schema must specify precision for auto-generated UI
- SwisperStudio uses `step` in `<input type="number">`

**Example:**
```json
{
  "name": "default_temperature",
  "type": "number",
  "min": 0.0,
  "max": 2.0,
  "step": 0.1,  // ✅ Increments by 0.1
  "default": 0.7
}
```

### 2.3 Browser Accessibility

**Decision:** Swisper URLs must be accessible from browser

**Context:**
- SwisperStudio backend runs in Docker (can use `backend:8000`)
- Browser runs on host machine (needs `localhost:8001` or public URL)
- Frontend directly calls Swisper SAP from browser (for schema/records)

**Implementation:**
```
Production:
- Swisper URL: https://swisper.customer.com
- Browser can access: ✅

Development (Docker):
- Swisper URL for backend tests: http://backend:8000
- Swisper URL for browser/frontend: http://localhost:8001
- Both point to same mock SAP ✅
```

---

## 3. Schema Format

### 3.1 Complete Schema Object

```json
{
  "version": "1.1",
  "tables": [
    {
      "name": "string",
      "description": "string",
      "primary_key": "string",
      "fields": [
        {
          "name": "string",
          "type": "string|number|boolean|select|textarea|json",
          "required": boolean,
          "immutable": boolean,
          "description": "string",
          
          // String-specific
          "max_length": number,
          "pattern": "regex string",
          
          // Number-specific
          "min": number,
          "max": number,
          "step": number,  // ✅ NEW in v1.1
          
          // Select-specific
          "options": ["string"],
          
          // All types
          "default": any,
          "placeholder": "string",
          "help_text": "string",
          "ui_group": "string"
        }
      ]
    }
  ]
}
```

### 3.2 Field Properties Reference

| Property | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `name` | string | ✅ Yes | Field identifier (DB column name) | `"default_model"` |
| `type` | string | ✅ Yes | Field type | `"select"` |
| `required` | boolean | No | Must have value | `true` |
| `immutable` | boolean | No | Can't change after creation | `true` |
| `description` | string | ✅ Yes | Human-readable description | `"Default LLM model"` |
| `max_length` | number | No | String max length | `255` |
| `pattern` | string | No | Regex validation | `"^[a-z_]+$"` |
| `min` | number | No | Minimum value (number) | `0.0` |
| `max` | number | No | Maximum value (number) | `2.0` |
| `step` | number | No | Increment step (number) | `0.1` |
| `options` | array | No | Allowed values (select) | `["gpt-4", "gpt-4-turbo"]` |
| `default` | any | No | Default value | `0.7` |
| `placeholder` | string | No | Input placeholder text | `"e.g., 0.7"` |
| `help_text` | string | No | Additional help | `"See docs for details"` |
| `ui_group` | string | No | Group fields in UI | `"Default Settings"` |

### 3.3 Field Type Details

#### String Fields
```json
{
  "name": "node_name",
  "type": "string",
  "required": true,
  "immutable": true,
  "max_length": 100,
  "pattern": "^[a-z_]+$",
  "description": "Node identifier",
  "placeholder": "e.g., global_planner"
}
```

**SwisperStudio renders:**
```html
<TextField 
  type="text"
  maxLength={100}
  required
  disabled={immutable}
  placeholder="e.g., global_planner"
/>
```

#### Number Fields
```json
{
  "name": "default_temperature",
  "type": "number",
  "required": false,
  "min": 0.0,
  "max": 2.0,
  "step": 0.1,  // ✅ Important for decimals!
  "default": 0.7,
  "description": "Sampling temperature"
}
```

**SwisperStudio renders:**
```html
<TextField 
  type="number"
  min={0.0}
  max={2.0}
  step={0.1}  /* Up/down arrows increment by 0.1 */
  defaultValue={0.7}
/>
```

#### Select Fields (With Static Options)
```json
{
  "name": "default_model",
  "type": "select",
  "required": true,
  "options": [
    "inference-llama4-maverick",
    "inference-apertus-8b",
    "inference-apertus-70b"
  ],
  "default": "inference-llama4-maverick",
  "description": "Default LLM model"
}
```

**SwisperStudio renders:**
```html
<Select>
  <MenuItem value="inference-llama4-maverick">inference-llama4-maverick</MenuItem>
  <MenuItem value="inference-apertus-8b">inference-apertus-8b</MenuItem>
  <MenuItem value="inference-apertus-70b">inference-apertus-70b</MenuItem>
</Select>
```

#### Boolean Fields
```json
{
  "name": "langsmith_tracing",
  "type": "boolean",
  "default": true,
  "description": "Enable LangSmith tracing"
}
```

**SwisperStudio renders:**
```html
<Checkbox checked={true} />
```

---

## 4. API Endpoints

### 4.1 Complete Endpoint List

| Endpoint | Method | Purpose | Required |
|----------|--------|---------|----------|
| `/api/admin/config/schema` | GET | Get all table schemas | ✅ Yes |
| `/api/admin/config/{table}` | GET | List all records | ✅ Yes |
| `/api/admin/config/{table}/{id}` | GET | Get single record | ✅ Yes |
| `/api/admin/config/{table}/{id}` | PUT | Update record | ✅ Yes |
| `/api/admin/config/{table}` | POST | Create record | Optional |
| `/api/admin/config/{table}/{id}` | DELETE | Delete record | Optional |

### 4.2 Schema Endpoint (Critical!)

**Endpoint:** `GET /api/admin/config/schema`

**Purpose:** Returns schema for ALL config tables

**Response Format:**
```json
{
  "version": "1.1",
  "tables": [
    {
      "name": "llm_node_config",
      "description": "LLM configuration per LangGraph node",
      "primary_key": "node_name",
      "fields": [
        // ... all fields
      ]
    }
  ]
}
```

**MUST include:**
- All config tables Swisper exposes
- All fields for each table
- Field types, validation, defaults
- Model options (18 Kvant models minimum)

**Example (Minimal llm_node_config):**
```json
{
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
          "required": true,
          "immutable": true,
          "max_length": 100,
          "description": "LangGraph node identifier"
        },
        {
          "name": "default_model",
          "type": "select",
          "required": true,
          "options": [
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
          "required": false,
          "min": 0.0,
          "max": 2.0,
          "step": 0.1,
          "default": 0.7,
          "description": "Sampling temperature (0 = deterministic, 2 = creative)"
        },
        {
          "name": "default_max_tokens",
          "type": "number",
          "required": false,
          "min": 100,
          "max": 32000,
          "step": 100,
          "default": 10000,
          "description": "Maximum tokens in response"
        },
        {
          "name": "langsmith_tracing",
          "type": "boolean",
          "required": false,
          "default": true,
          "description": "Enable LangSmith tracing for this node"
        }
      ]
    }
  ]
}
```

---

## 5. Model Options (Critical Decision)

### 5.1 Kvant Models (Static in Schema)

**All 18 models from Kvant MaaS** (as of 2025-11-03):

| Model Name | Type | Use Case |
|------------|------|----------|
| `inference-llama4-maverick` | Chat/Multimodal | Default recommendation |
| `inference-llama4-scout-17b` | Chat/Multimodal | Text and multimodal |
| `inference-llama33-70b` | Chat | Multilingual dialogue |
| `inference-apertus-8b` | Chat | Multilingual (Swiss AI) |
| `inference-apertus-70b` | Chat | Multilingual (Swiss AI) |
| `inference-deepseekr1-70b` | Reasoning | Advanced reasoning |
| `inference-deepseekr1-670b` | Reasoning | Highest capability reasoning |
| `inference-qwen3-8b` | Reasoning | Efficient reasoning |
| `inference-qwq-32b` | Reasoning | Thinking and reasoning |
| `inference-qwq25-vl-72b` | Multimodal | Vision-language |
| `inference-gemma-12b-it` | Multimodal | Text and image |
| `inference-gpt-oss-120b` | Chat | Powerful reasoning |
| `inference-granite-33-8b` | Chat | IBM Granite |
| `inference-granite-vision-2b` | Multimodal | Vision-language |
| `inference-mistral-v03-7b` | Chat | Multilingual |
| `inference-bge-m3` | Embedding | Embeddings |
| `infer-bge-reranker` | Reranker | Relevance scoring |
| `infer-whisper-3lt` | Speech-to-Text | ASR |

**Source:** https://documentation.kvant.cloud/products/maas/supported_models/

**Update Frequency:** Quarterly (when Kvant releases new models)

### 5.2 Azure Models (Future)

**For SAP v1.2:**

```json
{
  "name": "azure_model",
  "type": "select",
  "options": [],  // Empty - will use options_source
  "options_source": {
    "type": "endpoint",
    "url": "/api/admin/config/model-options",
    "params": { "field": "azure_model" }
  },
  "description": "Azure-specific model override"
}
```

**Swisper will implement:**
```python
@router.get("/api/admin/config/model-options")
async def get_model_options(field: str):
    if field == "azure_model":
        # Call Azure API
        response = await httpx.get(
            f"{settings.AZURE_ENDPOINT}/openai/deployments",
            params={"api-version": "2024-10-21"},
            headers={"api-key": settings.AZURE_API_KEY}
        )
        deployments = response.json()["data"]
        
        return {
            "options": [
                {
                    "value": d["model"],
                    "label": f"{d['id']} ({d['model']})"
                }
                for d in deployments
            ]
        }
```

---

## 6. Validation Rules

### 6.1 Field-Level Validation

**Swisper MUST validate:**

```python
def validate_field(field_schema, value):
    # Required check
    if field_schema["required"] and value is None:
        raise ValidationError(f"Field {field_schema['name']} is required")
    
    # Type validation
    if field_schema["type"] == "number":
        if not isinstance(value, (int, float)):
            raise ValidationError("Value must be a number")
        if "min" in field_schema and value < field_schema["min"]:
            raise ValidationError(f"Value must be >= {field_schema['min']}")
        if "max" in field_schema and value > field_schema["max"]:
            raise ValidationError(f"Value must be <= {field_schema['max']}")
    
    elif field_schema["type"] == "select":
        if value not in field_schema["options"]:
            raise ValidationError(f"Value must be one of: {field_schema['options']}")
    
    elif field_schema["type"] == "string":
        if "max_length" in field_schema and len(value) > field_schema["max_length"]:
            raise ValidationError(f"String exceeds max_length {field_schema['max_length']}")
        if "pattern" in field_schema and not re.match(field_schema["pattern"], value):
            raise ValidationError(f"String doesn't match pattern")
    
    elif field_schema["type"] == "boolean":
        if not isinstance(value, bool):
            raise ValidationError("Value must be true or false")
```

### 6.2 Immutable Field Protection

```python
# On UPDATE (PUT) operation
if field_schema["immutable"]:
    current_value = db.get_current_value(table, id, field_name)
    if value != current_value:
        raise ValidationError(f"Field {field_name} is immutable")
```

---

## 7. Implementation Guidelines for Swisper Team

### 7.1 Quick Start (30-minute implementation)

**Step 1: Copy Mock SAP**
```bash
# From SwisperStudio repo
cp backend/app/api/routes/mock_sap.py your_swisper_backend/app/api/routes/admin/config.py
```

**Step 2: Replace Mock Data with Real DB**
```python
# Change this:
MOCK_LLM_CONFIGS = {...}  # Mock data

# To this:
from app.models import LLMNodeConfiguration

@router.get("/llm_node_config")
async def list_configs(session: Session = Depends(get_session)):
    configs = session.query(LLMNodeConfiguration).all()
    return {
        "table": "llm_node_config",
        "records": [c.dict() for c in configs],
        "count": len(configs)
    }
```

**Step 3: Test**
```bash
curl http://localhost:8000/api/admin/config/schema
curl http://localhost:8000/api/admin/config/llm_node_config
```

### 7.2 Schema Generation (Auto-generate from SQLModel)

**Option:** Generate schema from database models

```python
def generate_schema_from_model(model_class):
    """Auto-generate SAP schema from SQLModel"""
    fields = []
    
    for field_name, field_info in model_class.__fields__.items():
        field_def = {
            "name": field_name,
            "type": infer_type(field_info.annotation),
            "required": field_info.is_required(),
            "description": field_info.description or f"{field_name} field"
        }
        
        # Add constraints
        if hasattr(field_info, 'max_length'):
            field_def["max_length"] = field_info.max_length
        
        fields.append(field_def)
    
    return {
        "name": model_class.__tablename__,
        "description": model_class.__doc__,
        "primary_key": model_class.__table__.primary_key.columns.keys()[0],
        "fields": fields
    }
```

### 7.3 URL Accessibility Requirements

**CRITICAL:** Swisper SAP endpoints must be accessible from:
1. ✅ **SwisperStudio backend** (for proxying, audit logging)
2. ✅ **End-user browser** (for direct schema/record fetching)

**Production Setup:**
```
Swisper URL: https://swisper.customer.com
- Backend can call: ✅
- Browser can call: ✅ (CORS configured)
```

**Development Setup:**
```
Swisper URL: http://localhost:8001
- Backend (Docker) calls: http://backend:8000 (internal)
- Browser calls: http://localhost:8001 (host machine)
```

**CORS Configuration Required:**
```python
# Swisper backend must allow SwisperStudio origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://swisperstudio.customer.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

---

## 8. Testing SAP Implementation

### 8.1 Validation Checklist

**Before marking SAP as complete:**

```bash
# 1. Schema endpoint returns valid JSON
curl http://swisper:8000/api/admin/config/schema | jq .

# 2. Verify 18 Kvant models in default_model options
curl http://swisper:8000/api/admin/config/schema | jq '.tables[0].fields[] | select(.name=="default_model") | .options'

# 3. List configs returns records
curl http://swisper:8000/api/admin/config/llm_node_config | jq .

# 4. Get single config works
curl http://swisper:8000/api/admin/config/llm_node_config/global_planner | jq .

# 5. Update config works
curl -X PUT http://swisper:8000/api/admin/config/llm_node_config/global_planner \
  -H "Content-Type: application/json" \
  -d '{"default_temperature": 0.5}'

# 6. Validation works
curl -X PUT http://swisper:8000/api/admin/config/llm_node_config/global_planner \
  -H "Content-Type: application/json" \
  -d '{"default_temperature": 3.0}'  # Should return 400 error
```

### 8.2 Integration Test with SwisperStudio

```bash
# 1. Update SwisperStudio project environment to point to real Swisper
# In SwisperStudio database:
UPDATE project_environment 
SET swisper_url = 'http://swisper.real.com' 
WHERE env_type = 'dev';

# 2. Test in browser
# Navigate to http://localhost:3000/projects/{id}/config
# Select environment: DEV
# Should fetch schema from real Swisper
# Should display config table
```

---

## 9. Examples

### 9.1 Complete Workflow Example

**Step 1: SwisperStudio fetches schema**
```http
GET /api/admin/config/schema HTTP/1.1
Host: swisper.customer.com
Authorization: Bearer dev_api_key_xxx
```

**Response:**
```json
{
  "version": "1.1",
  "tables": [
    {
      "name": "llm_node_config",
      "fields": [...]
    }
  ]
}
```

**Step 2: SwisperStudio auto-generates form**
- Dropdown for `default_model` with 18 Kvant models
- Number input for `default_temperature` (step=0.1)
- Checkbox for `langsmith_tracing`

**Step 3: User edits and saves**
```http
PUT /api/admin/config/llm_node_config/global_planner HTTP/1.1
Content-Type: application/json

{
  "default_temperature": 0.5
}
```

**Step 4: Swisper validates and updates**
- Validates: 0.0 ≤ 0.5 ≤ 2.0 ✅
- Updates database
- Updates in-memory cache (hot-reload)
- Returns updated config

---

## 10. Troubleshooting

### 10.1 Schema Not Loading

**Symptom:** SwisperStudio shows "Loading schema..." forever

**Causes:**
1. CORS not configured (browser blocked)
2. URL not accessible from browser
3. Swisper SAP endpoint not implemented

**Fix:**
```bash
# Check if endpoint exists
curl http://swisper:8000/api/admin/config/schema

# Check CORS headers
curl -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -X OPTIONS \
  http://swisper:8000/api/admin/config/schema
```

### 10.2 Model Options Not Showing

**Symptom:** Dropdown is empty or shows wrong models

**Cause:** `options` array missing or incorrect in schema

**Fix:**
```python
# Verify schema includes all 18 Kvant models
schema = get_schema()
model_field = next(f for f in schema['tables'][0]['fields'] if f['name'] == 'default_model')
assert len(model_field['options']) == 18
```

### 10.3 Temperature Increment Wrong

**Symptom:** Up/down arrows increment by 1.0 instead of 0.1

**Cause:** Missing `step` property in schema

**Fix:**
```json
{
  "name": "default_temperature",
  "type": "number",
  "step": 0.1  // ✅ MUST include this!
}
```

---

## 11. Future Enhancements (SAP v1.2)

### 11.1 Dynamic Model Options

**Planned for v1.2:**
```json
{
  "name": "azure_model",
  "type": "select",
  "options_source": "/api/admin/config/model-options?field=azure_model"
}
```

### 11.2 Field Dependencies

**Planned for v1.2:**
```json
{
  "name": "azure_temperature",
  "type": "number",
  "visible_when": {
    "field": "use_azure",
    "equals": true
  }
}
```

### 11.3 Validation Groups

**Planned for v1.2:**
```json
{
  "validation_groups": [
    {
      "name": "either_or",
      "rule": "at_least_one_required",
      "fields": ["default_model", "azure_model"]
    }
  ]
}
```

---

## 12. Reference Links

- **Kvant Models:** https://documentation.kvant.cloud/products/maas/supported_models/
- **Mock SAP Implementation:** `backend/app/api/routes/mock_sap.py`
- **SwisperStudio DataTable:** `frontend/src/components/data-table.tsx`
- **SAP Architecture Design:** `docs/architecture/swisper_sap_implementation_todo.md`

---

## 13. Contract Compliance

**For Swisper to be SAP v1.1 compliant:**

- ✅ Implements GET `/api/admin/config/schema`
- ✅ Returns valid JSON matching schema format
- ✅ Includes all 18 Kvant models in `default_model.options`
- ✅ Includes `step: 0.1` for `default_temperature`
- ✅ Implements GET `/api/admin/config/llm_node_config`
- ✅ Implements GET `/api/admin/config/llm_node_config/{node_name}`
- ✅ Implements PUT `/api/admin/config/llm_node_config/{node_name}`
- ✅ Validates all fields per section 6
- ✅ Returns proper HTTP status codes
- ✅ Accessible from browser (CORS configured)
- ✅ 10+ tests passing

**When all checkboxes complete → SAP v1.1 certified!** ✅

---

**Document Status:** Complete and authoritative as of 2025-11-03

