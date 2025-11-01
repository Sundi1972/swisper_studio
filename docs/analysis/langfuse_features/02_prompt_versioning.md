# Feature Analysis: Prompt Versioning & Management

**Priority:** P0 (Must-Have)
**Version:** v1.0
**Date:** 2025-11-01
**Status:** Complete Analysis

---

## 1. What It Does

**Purpose:** Version control for LLM prompts with Git-like semantics

**Core Capabilities:**
- ✅ Store prompts with versions (v1, v2, v3...)
- ✅ Track prompt changes over time
- ✅ See which version was used in each trace
- ✅ Compare versions (diffs)
- ✅ Label versions (e.g., "production", "staging", "experimental")
- ✅ Roll back to previous versions
- ✅ A/B test different prompt versions
- ✅ Track prompt dependencies (nested prompts)
- ✅ Test prompts in playground
- ✅ Track prompt performance (via linked traces)

**User Experience:**
1. Create prompt in UI or via API
2. Edit prompt → creates new version
3. Label version as "production"
4. SDK pulls "production" version at runtime
5. Trace shows which prompt version was used
6. Analyze performance by prompt version

---

## 2. How It Works (Architecture)

### Data Model

#### **Prompt** Model
```prisma
model Prompt {
  id        String   @id
  createdAt DateTime
  updatedAt DateTime

  projectId String
  createdBy String  # User who created version

  # Prompt Content
  prompt        Json   # Actual prompt content
  name          String # Prompt name (e.g., "intent_classification")
  version       Int    # Version number (1, 2, 3...)
  type          String # "text" or "chat"
  config        Json   # Model config (temperature, max_tokens, etc.)

  # Metadata
  tags          String[]  # Searchable tags
  labels        String[]  # Lifecycle labels (production, staging, etc.)
  commitMessage String?   # Version description

  # Relations
  PromptDependency PromptDependency[]  # Child prompts

  @@unique([projectId, name, version])
}
```

**Key Fields:**
- `name` + `version` - Unique identifier for prompt version
- `prompt` - JSON containing actual prompt content
- `labels` - Lifecycle management (production, staging, etc.)
- `config` - LLM configuration (model, temperature, etc.)
- `commitMessage` - Why this version was created

---

#### **Prompt JSON Structure**

**For Text Prompts:**
```json
{
  "type": "text",
  "prompt": "Classify the user's intent:\n\nUser: {{user_message}}\n\nIntent:"
}
```

**For Chat Prompts:**
```json
{
  "type": "chat",
  "prompt": [
    {
      "role": "system",
      "content": "You are a helpful assistant that classifies user intents."
    },
    {
      "role": "user",
      "content": "{{user_message}}"
    }
  ]
}
```

**Config JSON:**
```json
{
  "model": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 150,
  "top_p": 1.0
}
```

---

#### **Prompt Dependency** Model
```prisma
model PromptDependency {
  id String @id

  projectId String

  # Parent prompt
  parentId String
  parent   Prompt

  # Child prompt reference
  childName    String   # Name of child prompt
  childLabel   String?  # Label to use (e.g., "production")
  childVersion Int?     # Specific version (or null for label-based)

  @@index([projectId, parentId])
  @@index([projectId, childName])
}
```

**Use Case:** Nested/composed prompts
```
Prompt: "agent_workflow" (v5)
├── depends on: "intent_classification" (label: production)
├── depends on: "fact_extraction" (version: 3)
└── depends on: "response_generation" (label: production)
```

---

#### **Protected Labels** Model
```prisma
model PromptProtectedLabels {
  id        String
  projectId String
  label     String  # e.g., "production"

  @@unique([projectId, label])
}
```

**Purpose:** Prevent accidental deletion/modification of critical labels

---

### API Endpoints

#### **Prompt Management API**

**Create Prompt:**
```typescript
POST /api/public/v2/prompts
{
  "name": "intent_classification",
  "prompt": "Classify the user's intent: {{user_message}}",
  "config": {
    "model": "gpt-4",
    "temperature": 0.7
  },
  "labels": ["staging"],
  "tags": ["intent", "classification"]
}
```

**Get Prompt by Label:**
```typescript
GET /api/public/v2/prompts/:name?label=production
```

**Get Prompt by Version:**
```typescript
GET /api/public/v2/prompts/:name?version=5
```

**List Prompts:**
```typescript
GET /api/public/prompts
```

**Update Prompt (creates new version):**
```typescript
POST /api/public/v2/prompts
{
  "name": "intent_classification",  # Same name
  "prompt": "Updated prompt...",    # New content → new version
  "labels": ["production"],         # Move production label to this version
  "commitMessage": "Improved accuracy for edge cases"
}
```

---

### Versioning Workflow

#### **Scenario: Updating a Production Prompt**

**Step 1: Create new version in staging**
```python
langfuse.create_prompt(
    name="intent_classification",
    prompt="New improved prompt...",
    labels=["staging"],
    commit_message="Testing new few-shot examples"
)
# Creates v6 with "staging" label
```

**Step 2: Test in staging**
```python
# SDK pulls staging version
prompt = langfuse.get_prompt(
    name="intent_classification",
    label="staging"
)
# Returns v6
```

**Step 3: Promote to production**
```python
langfuse.update_prompt_labels(
    name="intent_classification",
    version=6,
    labels=["production"]  # Moves "production" label from v5 → v6
)
```

**Step 4: Production uses new version**
```python
# All production calls now use v6
prompt = langfuse.get_prompt(
    name="intent_classification",
    label="production"
)
```

---

### Linking Prompts to Traces

#### **In Observation Model:**
```prisma
model LegacyPrismaObservation {
  # ... other fields ...
  promptId String?  # Links to Prompt.id
}
```

**When creating a generation:**
```python
langfuse.generation(
    name="intent_classification",
    prompt_id="prompt_abc123_v6",  # Which version was used
    input={"user_message": "Hello"},
    output={"intent": "greeting"}
)
```

**Result:** UI shows which prompt version was used for each LLM call

---

### UI Components

#### **1. Prompt Library View**
**Location:** `web/src/features/prompts/`

**Features:**
- List all prompts
- Search by name/tag
- Filter by label
- See version count per prompt
- Quick actions (test, edit, delete)

**Table Columns:**
- Name
- Latest Version
- Labels (production, staging, etc.)
- Tags
- Last Updated
- Created By

---

#### **2. Prompt Detail View**
**Location:** Prompt detail page

**Features:**
- Version history (all versions)
- Current prompt content
- Config (model, temperature, etc.)
- Labels and tags
- Version comparison (diff view)
- Performance metrics (linked traces)
- Dependency graph

**Version Timeline:**
```
v6 (production) - 2 hours ago - "Improved accuracy" by @heiko
v5 (archived)   - 1 day ago   - "Added few-shot examples" by @heiko
v4 (archived)   - 3 days ago  - "Fixed typo" by @sarah
v3 (archived)   - 1 week ago  - "Initial version" by @heiko
```

---

#### **3. Prompt Editor**
**Features:**
- Text editor with syntax highlighting
- Variable interpolation ({{variable_name}})
- Model config editor
- Live preview
- Test with sample inputs

**Example:**
```
System Prompt:
┌────────────────────────────────────────┐
│ You are an intent classifier.         │
│                                        │
│ User input: {{user_message}}          │
│                                        │
│ Classify into one of:                 │
│ - search_documents                     │
│ - manage_calendar                      │
│ - general_chat                         │
└────────────────────────────────────────┘

Config:
┌────────────────────────────────────────┐
│ Model: gpt-4                           │
│ Temperature: 0.7                       │
│ Max Tokens: 150                        │
└────────────────────────────────────────┘

[Test]  [Save as v7]  [Save as Draft]
```

---

#### **4. Prompt Playground**
**Location:** `web/src/features/playground/`

**Features:**
- Test prompt with real LLM
- Try different model configs
- See token usage and cost
- Compare multiple versions side-by-side
- Save as new version

**Workflow:**
1. Select prompt version
2. Enter test input
3. Click "Run"
4. See LLM response
5. Adjust and iterate
6. Save as new version

---

#### **5. Prompt Comparison View**
**Features:**
- Side-by-side diff
- Highlight changes
- Config differences
- Performance comparison (traces/scores)

**Example:**
```
Version 5              │  Version 6
─────────────────────────────────────────
You are an assistant   │  You are a helpful assistant
                       │  specialized in intent
                       │  classification.
                       │
Classify: {{message}}  │  User input: {{user_message}}
```

---

#### **6. Prompt Performance Metrics**
**Features:**
- Traces using this prompt version
- Average latency
- Average cost
- Success rate (via scores)
- Error rate
- User feedback

**Example:**
```
Prompt: intent_classification (v6)
─────────────────────────────────
Traces: 1,245
Avg Latency: 850ms
Avg Cost: $0.0012
Success Rate: 94.2% (based on scores)
Errors: 8 (0.6%)
```

---

## 3. Relevance to Swisper SDK

### Priority: **P0 (Must-Have)**

**Why Essential:**
1. ✅ **Prompt Visibility** - Your requirement: "see the real prompts that were given"
2. ✅ **Version Control** - Track prompt changes over time
3. ✅ **A/B Testing** - Test new prompts without breaking production
4. ✅ **Rollback** - Quickly revert bad prompt changes
5. ✅ **Performance Tracking** - See which prompt versions perform better
6. ✅ **Collaboration** - Team can manage prompts together

---

### Swisper-Specific Use Cases

#### **Use Case 1: Intent Classification Prompt Evolution**
```
v1: Basic template (80% accuracy)
v2: Added few-shot examples (85% accuracy)
v3: Improved edge case handling (90% accuracy)  ← Production
v4: Experimental (testing)                      ← Staging
```

**Benefit:** Track prompt improvements over time

---

#### **Use Case 2: Node-Specific Prompts**
```
Prompts for each node:
├── intent_classification (v5, production)
├── fact_extraction (v8, production)
├── memory_retrieval (v3, production)
├── response_generation_simple (v12, production)
└── response_generation_complex (v7, production)
```

**Benefit:** Manage prompts for each node independently

---

#### **Use Case 3: A/B Testing**
```
Production split:
├── 80% users → response_generation (v10, production)
└── 20% users → response_generation (v11, experimental)

After 1 week:
- v10: 92% satisfaction (1,000 traces)
- v11: 95% satisfaction (250 traces)

Decision: Promote v11 to production
```

**Benefit:** Data-driven prompt optimization

---

#### **Use Case 4: Trace Debugging**
```
User reports bad response
→ Check trace
→ See which prompt version was used
→ View exact prompt content
→ Reproduce issue
→ Fix prompt
→ Deploy new version
```

**Benefit:** Fast debugging with prompt visibility

---

#### **Use Case 5: Composed Prompts**
```
ui_node_prompt (v5)
├── depends on: core.md (v2)
├── depends on: context_builder (v4)
└── depends on: fact_formatter (v1)
```

**Benefit:** Track dependencies (similar to your .md prompt pattern)

---

## 4. Complexity Assessment

### Build Effort (From Scratch)

**Prompt Management System:**
- Data model: 1 week
- Versioning logic: 1 week
- API endpoints: 1 week
- Label management: 3 days
- **Subtotal:** 3.5 weeks

**UI Components:**
- Prompt library: 1 week
- Prompt editor: 1 week
- Version comparison: 1 week
- Playground: 2 weeks
- **Subtotal:** 5 weeks

**Integration:**
- SDK pull prompts: 1 week
- Link prompts to traces: 3 days
- Performance metrics: 1 week
- **Subtotal:** 2.5 weeks

**Testing & Polish:**
- Unit tests: 1 week
- Integration tests: 1 week
- Bug fixes: 1 week
- **Subtotal:** 3 weeks

**TOTAL BUILD EFFORT:** **14 weeks** (3.5 months)

---

### Fork Effort

**Using Langfuse:**
- Prompt versioning: ✅ Built-in
- UI: ✅ Complete
- API: ✅ Complete
- Playground: ✅ Complete
- Integration: 2 days
- **Subtotal:** 2 days

**Swisper-Specific:**
- Map .md files to Langfuse prompts: 2 days
- Sync prompt changes: 1 day
- Custom UI views (optional): 3 days
- **Subtotal:** 6 days

**TOTAL FORK EFFORT:** **1.5 weeks**

**Savings:** 12.5 weeks (~3 months)

---

## 5. Build vs Fork Recommendation

### ✅ **FORK** (Strongly Recommended)

**Reasons:**
1. **Complete System** - Git-like versioning, labels, playground
2. **Production-Ready** - Used by thousands of teams
3. **Time Savings** - 3 months → 1.5 weeks
4. **Rich UI** - Diff view, playground, metrics
5. **API Mature** - Well-documented, SDKs available

**What You Get:**
- ✅ Version control
- ✅ Label management (production, staging, etc.)
- ✅ Prompt editor with preview
- ✅ Playground for testing
- ✅ Version comparison (diff)
- ✅ Performance metrics per version
- ✅ Prompt dependencies
- ✅ Link prompts to traces

**What You Need to Adapt:**
- 🔧 Map .md files to Langfuse (optional)
- 🔧 Custom UI for Swisper-specific workflows (optional)

---

### Integration with Your Current Pattern

**Your Current Pattern:**
```
ui_node_helpers/
├── prompts/
│   ├── core.md
│   ├── simple.md
│   ├── complex.md
│   └── voice.md
└── prompt_builder.py  # Loads .md files
```

**Option 1: Keep .md Files** (Recommended)
- Keep .md files as source of truth
- Sync to Langfuse via script
- Version control in Git
- View in Langfuse UI
- Link to traces in Langfuse

**Sync Script:**
```python
# sync_prompts.py
import glob
from langfuse import Langfuse

langfuse = Langfuse()

for md_file in glob.glob("**/prompts/*.md"):
    with open(md_file, 'r') as f:
        content = f.read()

    name = md_file.replace("/", "_").replace(".md", "")

    langfuse.create_prompt(
        name=name,
        prompt=content,
        tags=["auto-synced"],
        commit_message=f"Synced from {md_file}"
    )
```

**Option 2: Migrate to Langfuse** (Future)
- Store prompts in Langfuse
- Pull at runtime
- Manage in Langfuse UI
- Better for non-technical team members

---

## 6. Integration Plan (If Forking)

### Phase 1: Use Langfuse for New Prompts (1 week)
1. Create prompts in Langfuse UI
2. Pull prompts via SDK
3. Link to traces
4. Test versioning workflow

### Phase 2: Sync Existing .md Files (1 week)
1. Write sync script
2. Upload all .md files as prompts
3. Version in Langfuse
4. Keep .md files or migrate (TBD)

### Phase 3: Advanced Features (2 weeks)
1. A/B testing setup
2. Performance tracking per prompt
3. Custom UI views (if needed)

**Total:** 4 weeks to fully integrated

---

## 7. How It Solves Your Requirements

### Your Requirement: "See the real prompts that were given"

**Langfuse Solution:**
1. ✅ Each trace shows which prompt version was used
2. ✅ Click prompt → see exact content
3. ✅ View input variables + final rendered prompt
4. ✅ Compare different versions
5. ✅ Track prompt changes over time

**Example Trace View:**
```
Trace: user_request_12345
└── GENERATION: intent_classification
    ├── Prompt: intent_classification (v6)  ← Click to view
    ├── Input: {"user_message": "Schedule meeting"}
    ├── Rendered Prompt: "Classify: Schedule meeting"
    └── Output: {"intent": "manage_calendar"}
```

**Click "intent_classification (v6)" →**
```
Prompt: intent_classification
Version: 6 (production)
Created: 2025-11-01 by heiko
Commit: "Improved calendar intent detection"

Content:
─────────────────────────────────────────
Classify the user's intent:

User: {{user_message}}

Possible intents:
- search_documents
- manage_calendar
- general_chat
─────────────────────────────────────────

Config:
- Model: gpt-4
- Temperature: 0.7
- Max Tokens: 150
```

**✅ Fully Satisfies Your Requirement**

---

## 8. Key Files in Langfuse

**Data Models:**
- `packages/shared/prisma/schema.prisma` (lines 751-809)

**API Endpoints:**
- `web/src/pages/api/public/v2/prompts/[promptName].ts`
- `web/src/pages/api/public/prompts/index.ts`

**UI Components:**
- `web/src/features/prompts/` (prompt library)
- `web/src/features/playground/` (prompt testing)
- `web/src/pages/project/[projectId]/prompts/` (prompt pages)

**SDK Integration:**
- `packages/shared/src/server/prompts.ts` (query logic)
- Python SDK: `langfuse.get_prompt()`, `langfuse.create_prompt()`

---

## 9. Swisper-Specific Enhancements (Optional)

### Enhancement 1: Markdown Support
**Add:** Rich markdown preview for .md-based prompts

### Enhancement 2: Prompt Templates
**Add:** Reusable templates for common patterns

### Enhancement 3: Bulk Import
**Add:** Import multiple .md files at once

### Enhancement 4: Git Integration
**Add:** Sync Langfuse ↔ Git repository

---

## 10. Summary

### What Langfuse Provides:
✅ Complete prompt versioning (14 weeks of work)
✅ Label-based deployment (production, staging)
✅ Prompt editor & playground
✅ Version comparison (diffs)
✅ Link prompts to traces
✅ Performance tracking per version
✅ Prompt dependencies

### What You Need to Add:
🔧 Sync .md files to Langfuse (optional, 1 week)
🔧 Custom UI enhancements (optional, 1-2 weeks)

### Recommendation:
**Fork Langfuse** - Saves 3 months, proven system, full-featured

### Your Requirement Status:
✅ **"See the real prompts that were given"** - FULLY SUPPORTED

---

**Next:** Analyze State Tracking (your requirement #3) - which Langfuse DOESN'T have

