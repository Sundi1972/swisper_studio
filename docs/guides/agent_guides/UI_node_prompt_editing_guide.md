# Prompt Editing Guide

**Purpose:** How to safely edit UI Node prompts  
**Audience:** Developers, Product Owners, QA  
**Last Updated:** October 8, 2025

---

## 📖 Table of Contents

1. [Quick Start](#quick-start)
2. [Prompt Architecture](#prompt-architecture)
3. [Editing Workflow](#editing-workflow)
4. [Common Changes](#common-changes)
5. [Testing Changes](#testing-changes)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Where Are the Prompts?

```
backend/app/api/services/agents/global_supervisor/nodes/prompts/
├── core.md      ← Core identity, principles (used in ALL variants)
├── simple.md    ← Simple chat mode (quick queries)
├── complex.md   ← Complex chat mode (agent synthesis)
└── voice.md     ← Voice mode (TTS optimized)
```

### Before You Edit

1. ✅ Read this guide
2. ✅ Understand [UI_NODE_SYSTEM](../Documentation/UI_NODE_SYSTEM.md)
3. ✅ Have tests running locally
4. ✅ Create a feature branch

---

## Prompt Architecture

### How Prompts Are Built

```
┌─────────────┐
│  core.md    │  ← Always loaded (identity + principles)
└──────┬──────┘
       │
       ├─────────────────────────────────┐
       │                                 │
┌──────▼──────┐  ┌──────▼──────┐  ┌────▼──────┐
│ simple.md   │  │ complex.md  │  │ voice.md  │
│ (OR)        │  │ (OR)        │  │ (OR)      │
└──────┬──────┘  └──────┬──────┘  └────┬──────┘
       │                │               │
       └────────┬───────┴───────────────┘
                │
         ┌──────▼──────┐
         │ Placeholder │  ← {{FACTS_BLOCK}}, {{USER_MESSAGE}}, etc.
         │  Injection  │
         └──────┬──────┘
                │
         ┌──────▼──────┐
         │   Final     │
         │   Prompt    │  → Sent to LLM
         └─────────────┘
```

### Fragment Roles

| File | When Used | Purpose |
|------|-----------|---------|
| `core.md` | **Always** | Core identity, principles, language rules |
| `simple.md` | Simple queries (no agent work) | Task instructions for direct Q&A |
| `complex.md` | Complex queries (with agent results) | Agent synthesis guidance |
| `voice.md` | Voice interactions (STT/TTS) | TTS optimization rules |

### Available Placeholders

Use these in any `.md` file to inject dynamic content:

| Placeholder | Example | When to Use |
|-------------|---------|-------------|
| `{{CURRENT_TIME}}` | `2025-10-08T14:30:00Z` | Time-sensitive responses |
| `{{USER_TIMEZONE}}` | `Europe/Zurich` | Timezone awareness |
| `{{USER_LOCALE}}` | `de-CH` | Language/formatting |
| `{{LOCALE_FORMATTING_RULES}}` | `Swiss German: Use ä, ö, ü...` | Locale-specific rules |
| `{{PRESENTATION_POLICY}}` | `Verbosity: concise. Tone: friendly.` | User preferences |
| `{{FACTS_BLOCK}}` | `- name: Heiko\n- location: Zurich` | User personalization |
| `{{USER_MESSAGE}}` | `What's the weather?` | Current query |
| `{{CONTEXT_SUMMARY}}` | `User asked about Paris earlier...` | Conversation history |
| `{{AGENT_TEXT_SUMMARY}}` | `Weather Agent: Sunny, 22°C...` | Agent results (complex only) |

---

## Editing Workflow

### Step 1: Identify What to Change

**Use Case → File to Edit:**

| I want to change... | Edit this file |
|---------------------|----------------|
| Swisper's personality or tone | `core.md` |
| How Swisper uses facts | `core.md` (Fact Integration section) |
| How Swisper handles context | `core.md` (Context Usage section) |
| Language matching rules | `core.md` (Language Detection section) |
| Simple chat task instructions | `simple.md` |
| Agent synthesis guidance | `complex.md` |
| Voice/TTS optimization rules | `voice.md` |

### Step 2: Make Your Changes

**Location:**
```bash
cd backend/app/api/services/agents/global_supervisor/nodes/prompts/
```

**Edit the file:**
```bash
# Use your favorite editor
code core.md
# or
vim core.md
```

**Example Change (core.md):**
```markdown
# BEFORE
You are Swisper, a knowledgeable AI coordinator.

# AFTER
You are Swisper, a friendly and empathetic AI assistant.
```

### Step 3: Test Your Changes

**Run UI Node tests:**
```bash
cd backend
uv run pytest tests/test_ui_node_integration_simple.py -v
```

**All tests should pass:**
```
✅ test_intro_flow_works PASSED
✅ test_greeting_flow_personalized PASSED
✅ test_simple_chat_flow_works PASSED
✅ test_complex_chat_flow_works PASSED
```

### Step 4: Manual Testing (Optional but Recommended)

**Start backend:**
```bash
cd backend
uv run uvicorn app.main:app --reload
```

**Test in frontend:**
1. Open Swisper UI
2. Start new chat
3. Test affected flow (intro, greeting, simple, or complex)
4. Verify response quality

### Step 5: Commit Your Changes

```bash
git add backend/app/api/services/agents/global_supervisor/nodes/prompts/
git commit -m "feat(prompts): Update Swisper personality to be more empathetic"
```

---

## Common Changes

### Change Swisper's Personality

**File:** `core.md`  
**Section:** `# SWISPER IDENTITY`

**Example:**
```markdown
# BEFORE
**Personality:** Professional and efficient

# AFTER
**Personality:** Warm, empathetic, and supportive
```

**Test Impact:**
- Intro flow should reflect new personality
- All responses should feel more empathetic

---

### Update Fact Usage Guidance

**File:** `core.md`  
**Section:** `## FACT INTEGRATION`

**Example:**
```markdown
# BEFORE
Use facts when relevant.

# AFTER
Use facts to show deep understanding of the user's context.
Prioritize safety-critical facts (allergies, health conditions).
```

**Test Impact:**
- Facts should be used more thoughtfully
- Safety concerns should be highlighted

---

### Change Context Usage Rules

**File:** `core.md`  
**Section:** `## CONTEXT USAGE INTELLIGENCE`

**Example:**
```markdown
# BEFORE
Use context when available.

# AFTER
ALWAYS check context for:
- Unresolved questions from previous turns
- User frustrations that need addressing
- Continuity opportunities
```

**Test Impact:**
- Context should be used more proactively
- Conversations should feel more coherent

---

### Update Agent Synthesis Guidance

**File:** `complex.md`  
**Section:** `## AGENT RESULTS SYNTHESIS`

**Example:**
```markdown
# BEFORE
Synthesize agent results faithfully.

# AFTER
Synthesize agent results with these priorities:
1. SAFETY: Highlight any warnings or cautions first
2. CLARITY: Explain what agents did in plain language
3. ACTION: Tell user what they can do next
```

**Test Impact:**
- Complex responses should be more actionable
- Safety information should be prominent

---

### Adjust Voice/TTS Rules

**File:** `voice.md`  
**Section:** `## TTS OPTIMIZATION`

**Example:**
```markdown
# BEFORE
No markdown formatting.

# AFTER
CRITICAL TTS RULES:
- No markdown (**, *, #, etc.)
- No emojis
- No bullet points
- Use spoken transitions: "first", "then", "finally"
- Keep sentences under 20 words for natural pacing
```

**Test Impact:**
- Voice responses should sound more natural
- TTS output should have better pacing

---

## Testing Changes

### Automated Tests

**Run all UI Node tests:**
```bash
cd backend
uv run pytest tests/test_ui_node* -v
```

**Expected output:**
```
tests/test_ui_node_integration_simple.py::TestUINodeCoreFlows
  ✅ test_intro_flow_works PASSED
  ✅ test_greeting_flow_personalized PASSED
  ✅ test_simple_chat_flow_works PASSED
  ✅ test_complex_chat_flow_works PASSED

tests/test_ui_node_prompt_defaults_tdd.py
  ✅ test_swisper_defaults_exist PASSED
  ✅ test_preference_merging_respects_priority PASSED
  [... more tests ...]

tests/test_greeting_frequency_logic.py
  ✅ test_first_time_user_always_gets_intro PASSED
  ✅ test_not_first_message_never_gets_greeting PASSED
  [... more tests ...]
```

### Manual Test Scenarios

**Test 1: Intro Flow**
```
1. Create new user account
2. Send first message: "Hello"
3. Verify: Comprehensive intro with updated personality
```

**Test 2: Greeting Flow**
```
1. Use existing user (has_seen_intro=True)
2. Start new chat after 24 hours
3. Verify: Personalized greeting with updated tone
```

**Test 3: Simple Chat**
```
1. Ask simple question: "What is AI?"
2. Verify: Answer reflects updated guidance
```

**Test 4: Complex Chat**
```
1. Ask complex question: "Book flight to Paris and check weather"
2. Verify: Agent synthesis follows new rules
```

**Test 5: Voice Mode**
```
1. Enable voice input/output
2. Ask any question
3. Verify: Response has no markdown, sounds natural
```

---

## Best Practices

### ✅ DO

1. **Edit `.md` files directly** (not Python code)
2. **Test after every change** (run pytest)
3. **Use placeholders** for dynamic content (`{{FACTS_BLOCK}}`)
4. **Keep sections clear** (use markdown headers: `#`, `##`, `###`)
5. **Write for the LLM** (clear, explicit instructions)
6. **Be principle-based** (teach concepts, not hardcoded cases)
7. **Commit prompt changes separately** (easier to review/rollback)

### ❌ DON'T

1. **Don't hardcode user data** (use placeholders instead)
2. **Don't add brittle heuristics** (e.g., "if German, say...")
3. **Don't make prompts too long** (LLM attention degrades)
4. **Don't remove placeholders** ({{FACTS_BLOCK}} etc. are required)
5. **Don't skip testing** (prompt changes can break flows)
6. **Don't mix concerns** (keep identity in `core.md`, tasks in variant files)

---

## Troubleshooting

### Problem: Tests Failing After Prompt Change

**Symptom:**
```
AssertionError: Expected greeting, got clarification question
```

**Likely Cause:** Prompt change altered LLM behavior unexpectedly

**Fix:**
1. **Revert change:** `git checkout -- prompts/core.md`
2. **Test again:** `uv run pytest tests/test_ui_node_integration_simple.py -v`
3. **Make smaller change:** Edit only one section at a time
4. **Test incrementally:** Run tests after each small edit

---

### Problem: Placeholder Not Being Replaced

**Symptom:**
```
Response contains: "{{FACTS_BLOCK}}" (literal text)
```

**Likely Cause:** Typo in placeholder name

**Fix:**
1. **Check spelling:** `{{FACTS_BLOCK}}` (case-sensitive)
2. **Check location:** Placeholder must be in `.md` file (not Python)
3. **Check Python:** Ensure `build_professional_prompt()` replaces it

**Available placeholders:** See [Available Placeholders](#available-placeholders) section

---

### Problem: Prompt Too Long, LLM Ignores Instructions

**Symptom:** LLM only follows first few instructions, ignores later ones

**Likely Cause:** Prompt exceeds LLM's attention span

**Fix:**
1. **Shorten prompt:** Remove verbose explanations
2. **Use numbered lists:** Makes instructions easier to scan
3. **Bold key points:** `**CRITICAL:**`, `**DO NOT:**`
4. **Move context to end:** Put `{{CONTEXT_SUMMARY}}` after main instructions

**Good structure:**
```markdown
# IDENTITY (brief)
# KEY PRINCIPLES (numbered list)
# TASK (specific)
# CONTEXT (at end)
```

---

### Problem: Changes Not Reflected in Production

**Symptom:** Edited prompt, but responses unchanged

**Likely Cause:** 
1. Backend not restarted
2. Wrong file edited
3. Cache issue

**Fix:**
```bash
# 1. Verify file location
cd backend/app/api/services/agents/global_supervisor/nodes/prompts/
ls -la

# 2. Check file content
cat core.md | grep "your change text"

# 3. Restart backend
# (If running locally)
# Ctrl+C to stop, then restart

# 4. Clear any caches
# (If running in Docker)
docker-compose restart backend
```

---

## Advanced: Adding New Placeholders

**When Needed:** You want to inject new dynamic content into prompts

**Example:** Add current weather to prompt

### Step 1: Add to Python

**File:** `backend/app/api/services/agents/global_supervisor/nodes/ui_components/professional_prompt_builder.py`

```python
def build_professional_prompt(...):
    # ... existing code ...
    
    # Fetch current weather
    current_weather = get_current_weather(user_location)  # Your function
    
    # Inject placeholder
    complete_prompt = complete_prompt.replace(
        "{{CURRENT_WEATHER}}", 
        current_weather
    )
    
    return complete_prompt
```

### Step 2: Use in Markdown

**File:** `prompts/core.md`

```markdown
## CURRENT CONTEXT

Current Weather: {{CURRENT_WEATHER}}

Use this to provide contextually relevant suggestions.
```

### Step 3: Test

```bash
uv run pytest tests/test_ui_node_integration_simple.py -v
```

---

## Related Documentation

- **UI Node System:** [UI_NODE_SYSTEM](../Documentation/UI_NODE_SYSTEM.md)
- **Architecture:** [SWISPER_ARCHITECTURE](../Documentation/SWISPER_ARCHITECTURE.md)
- **Testing Guide:** [TESTING_GUIDE](TESTING_GUIDE.md)

---

## Questions?

- **Not sure which file to edit?** → Check [Fragment Roles](#fragment-roles)
- **Test failing?** → See [Troubleshooting](#troubleshooting)
- **Want to understand prompts better?** → Read [UI_NODE_SYSTEM](../Documentation/UI_NODE_SYSTEM.md)
- **Still stuck?** → Ask the team / create an issue

