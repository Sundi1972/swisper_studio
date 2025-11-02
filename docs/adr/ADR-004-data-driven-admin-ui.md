# ADR-004: Data-Driven Admin UI via SAP

**Status:** ✅ Accepted  
**Date:** 2025-11-01  
**Deciders:** Development Team, Product Owner  
**Context:** Phase 4 - Configuration Management

---

## Context and Problem Statement

Swisper has multiple configuration tables (`llm_node_config`, `llm_route`, `fact_preloading_config`, etc.) and may add more in the future. SwisperStudio needs to provide a UI for editing these configs.

**Question:** Should we hardcode UI forms for each config table, or create a data-driven system that auto-adapts to new tables?

---

## Decision Drivers

* **Extensibility** - Easy to add new config tables
* **Maintenance burden** - Changes in Swisper shouldn't require SwisperStudio code changes
* **Development speed** - Avoid creating custom UI for every table
* **Type safety** - Ensure correct field types and validation
* **User experience** - Auto-generated UI should still be good UX

---

## Considered Options

1. **Hardcoded UI forms** - Create custom form for each config table
2. **Data-driven UI via schema API** - SwisperStudio auto-generates UI from Swisper schema
3. **Admin framework** (like Django Admin or Rails Admin)

---

## Decision Outcome

**Chosen option:** "Data-driven UI via schema API"

**Rationale:**

We want SwisperStudio to be **future-proof**. When Swisper adds a new config table, SwisperStudio should "just work" without code changes.

### How It Works

**Step 1:** Swisper exposes config schema via **SAP (Swisper Admin Protocol)**

```python
# Swisper Backend
@app.get("/api/admin/config/schema")
async def get_config_schema():
    """
    Returns schema for ALL config tables.
    SAP v1.0 compliant.
    """
    return {
        "version": "1.0",
        "tables": [
            {
                "name": "llm_node_config",
                "display_name": "LLM Node Configuration",
                "description": "Configure which LLM each node uses",
                "fields": [
                    {
                        "name": "node_name",
                        "type": "select",
                        "label": "Node Name",
                        "required": True,
                        "options": ["intent_classification", "memory", "planner"]
                    },
                    {
                        "name": "model",
                        "type": "select",
                        "label": "LLM Model",
                        "options": ["gpt-4", "gpt-4-turbo", "claude-3-opus"],
                        "default": "gpt-4"
                    },
                    {
                        "name": "temperature",
                        "type": "number",
                        "label": "Temperature",
                        "min": 0.0,
                        "max": 2.0,
                        "step": 0.1,
                        "default": 0.7
                    }
                ]
            }
            // ... more tables ...
        ]
    }
```

**Step 2:** SwisperStudio auto-generates UI

```typescript
// SwisperStudio Frontend
function ConfigManager({ projectId }: Props) {
  const { data: schema } = useConfigSchemaQuery(projectId);
  
  return (
    <div>
      {schema.tables.map(table => (
        <ConfigTableEditor 
          key={table.name}
          table={table}
          // Auto-renders form based on field types!
        />
      ))}
    </div>
  );
}

function ConfigTableEditor({ table }: Props) {
  return (
    <Card>
      <Typography variant="h6">{table.display_name}</Typography>
      <Typography variant="body2">{table.description}</Typography>
      
      {table.fields.map(field => (
        <FieldRenderer 
          key={field.name}
          field={field}
          // Auto-selects component based on field.type:
          // - "select" → MUI Select
          // - "number" → MUI Slider or TextField
          // - "boolean" → MUI Switch
          // - "text" → MUI TextField
        />
      ))}
    </Card>
  );
}
```

**Step 3:** Add new table in Swisper → UI auto-updates!

```sql
-- Developer adds new table in Swisper
CREATE TABLE email_config (
    smtp_host VARCHAR(255),
    smtp_port INTEGER,
    enabled BOOLEAN
);
```

```python
# Update schema endpoint to include email_config
# SwisperStudio UI automatically shows "Email Configuration" section!
# ZERO code changes in SwisperStudio!
```

### Positive Consequences

* ✅ **Zero maintenance** - New Swisper tables automatically get UI
* ✅ **Type safety** - Schema defines validation rules
* ✅ **Consistent UX** - All config tables look similar
* ✅ **Fast development** - No custom forms needed
* ✅ **Self-documenting** - Schema describes what each field does
* ✅ **Versioned protocol** - SAP v1.0, v2.0, etc.

### Negative Consequences

* ❌ Auto-generated UI may not be optimal for complex use cases
* ❌ Need to implement SAP in Swisper (additional work)
* ❌ Limited customization for specific tables
* ❌ Need fallback for non-compliant tables

---

## Pros and Cons of the Options

### Option 1: Hardcoded UI forms

**Pros:**
* Complete control over UI/UX
* Can optimize each form
* No schema protocol needed

**Cons:**
* ❌ **Maintenance nightmare** (one form per table)
* ❌ **Swisper changes break SwisperStudio** (tight coupling)
* ❌ **Slow to add new tables** (requires SwisperStudio code changes)
* ❌ **Code duplication** (similar forms for each table)

### Option 2: Data-driven UI via schema API ✅ CHOSEN

**Pros:**
* ✅ Extensible (new tables = zero work)
* ✅ Low maintenance
* ✅ Decoupled (Swisper owns schema)
* ✅ Fast to implement

**Cons:**
* Generic UI (not optimized for each table)
* Requires SAP implementation

### Option 3: Admin framework

**Pros:**
* Proven solution (Django Admin, Rails Admin)
* Feature-rich

**Cons:**
* ❌ **Framework lock-in** (requires specific backend framework)
* ❌ **Not API-driven** (designed for monoliths)
* ❌ **Hard to customize** (modify framework's UI)

---

## SAP (Swisper Admin Protocol) v1.0

**Specification to be created in Phase 4**

### Supported Field Types

```typescript
type FieldType = 
  | "string"      // Text input
  | "text"        // Textarea
  | "number"      // Number input or slider
  | "boolean"     // Switch/checkbox
  | "select"      // Dropdown
  | "multiselect" // Multiple choice
  | "date"        // Date picker
  | "datetime"    // Date + time picker
  | "json"        // JSON editor
  | "email"       // Email with validation
  | "url"         // URL with validation
  | "color"       // Color picker
  | "password"    // Password input (masked)
  | "reference";  // Foreign key
```

### Required Endpoints

```yaml
GET  /api/admin/config/schema           # Get schema for all tables
GET  /api/admin/config/{table}          # List records
GET  /api/admin/config/{table}/{id}     # Get single record
POST /api/admin/config/{table}          # Create record
PUT  /api/admin/config/{table}/{id}     # Update record
DELETE /api/admin/config/{table}/{id}   # Delete record (optional)
```

---

## Links

* **Related:** [ADR-003: Two-Mode Configuration](ADR-003-two-mode-configuration-system.md)
* **Related:** [ADR-002: Database Separation](ADR-002-database-separation-strategy.md)
* **Implementation:** Phase 4 - Configuration Management
* **SAP Spec:** To be created in Phase 4

---

## Validation

**Success Metrics:**
- ✅ Add new config table in Swisper → SwisperStudio UI updates automatically (zero code)
- ✅ Schema validation prevents invalid data entry
- ✅ Auto-generated UI is usable (PO can navigate without help)
- ✅ All field types render correctly
- ✅ At least 3 different config tables managed via same UI

**Review Date:** After Phase 4 implementation

---

## Notes

**Example: Adding Email Config**

1. Developer adds `email_config` table in Swisper
2. Developer updates SAP schema endpoint to include email_config
3. SwisperStudio automatically shows "Email Configuration" in UI
4. PO can immediately configure SMTP settings
5. No SwisperStudio deployment needed!

**Fallback for Complex Tables:**
- If a table needs custom UI (too complex for auto-generation), we can:
  - Add `custom_component: true` in schema
  - SwisperStudio renders custom component for that table
  - Still uses SAP for CRUD operations

**Inspiration:**
- Django Admin (Python)
- Rails Admin (Ruby)
- Strapi CMS (Node.js)
- Directus (Node.js)
- All use schema-driven UI generation

