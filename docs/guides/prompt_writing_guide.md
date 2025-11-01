# Prompt Writing Guide

**Audience:** Developers, Product Owners, Prompt Engineers  
**Last Updated:** October 29, 2025  
**Status:** Production Standard

---

## 🎯 Core Philosophy

**Write prompts as if you're onboarding a smart new joiner fresh from school.**

They're intelligent and capable, but they need clear, unambiguous instructions.

---

## 📋 The Template Structure

Use this proven structure from our unified extraction prompt (`backend/app/api/services/prompts/unified_extraction.md`):

```markdown
[ROLE]
Clear job description - who they are and what they do

[TASK 1: Primary Task Name]
What they need to accomplish

CONCEPTS & PRINCIPLES:
Core concepts they need to understand

CHAIN-OF-THOUGHT ALGORITHM:
Step-by-step decision process (Q1, Q2, Q3...)

EXAMPLES:
Concrete examples showing the reasoning

RULES SUMMARY:
Quick reference of critical rules

[TASK 2: Secondary Task Name]
...repeat structure...

[OUTPUT SCHEMA]
Exact JSON/format expected
```

---

## 1. [ROLE] - Job Description

**Goal:** Define who the LLM is and what their overall purpose is.

**Template:**
```markdown
[ROLE]
You are a [JOB_TITLE] for [SYSTEM/PURPOSE].
[Brief description of responsibilities]
```

**Example:**
```markdown
[ROLE]
You are a comprehensive EXTRACTION engine for a personal assistant.
Extract facts, resolve entity ambiguities, and identify conversation topics in ONE analysis.
```

**Why This Works:**
- ✅ Gives the LLM a clear identity and purpose
- ✅ Sets context for all subsequent instructions
- ✅ Like telling a new employee their job title and department

---

## 2. [TASK X] - Break Down the Job

**Goal:** Divide the complex job into discrete, manageable tasks.

**Template:**
```markdown
[TASK 1: SPECIFIC_TASK_NAME]

Brief task description

CRITICAL CONCEPTS:
- Key concept 1
- Key concept 2

RULES:
1. Specific rule
2. Specific rule
```

**Example:**
```markdown
[TASK 1: FACT EXTRACTION]

Extract verifiable, atomic facts from the user message.

CRITICAL CONCEPT: Extract ONLY PERSISTENT facts, NOT transient actions/queries

THE KEY QUESTION: "Is this something worth remembering BEYOND this conversation moment?"

RULES:
1. Every fact MUST be complete sentence with clear subject
2. Use "User" prefix for first-person (I, me, my)
3. Named entities start with their name
```

**Why This Works:**
- ✅ Clear boundaries for each task
- ✅ LLM knows what to focus on in each section
- ✅ Like giving a new joiner their specific responsibilities

---

## 3. CONCEPTS & PRINCIPLES - The "Why"

**Goal:** Teach underlying concepts before giving instructions.

**Template:**
```markdown
**THE KEY CONCEPT:** [Central idea]

**UNDERSTANDING THE DISTINCTION:**

✅ **Category A (DO THIS):**
Things that meet criteria X:
- Example 1
- Example 2

❌ **Category B (AVOID THIS):**
Things that meet criteria Y:
- Example 1
- Example 2
```

**Example:**
```markdown
**CRITICAL CONCEPT: Extract ONLY PERSISTENT facts, NOT transient actions/queries**

**THE KEY QUESTION:** "Is this something worth remembering BEYOND this conversation moment?"

**PERSISTENT Facts (EXTRACT these):**

Things that are TRUE OVER TIME - would still be relevant next week/month:

✅ **Identity & Attributes:**
   - "I'm allergic to peanuts", "I'm vegetarian"
   - "I work at Microsoft", "I'm a software engineer"

❌ **TRANSIENT Actions/Queries (SKIP these):**

Things happening RIGHT NOW in this moment - not worth remembering:

❌ **Immediate action requests:**
   - "I want to check my emails" → Action RIGHT NOW
   - "Can you search the documentation?" → Query RIGHT NOW
```

**Why This Works:**
- ✅ LLM understands the reasoning, not just following rules blindly
- ✅ Can generalize to novel situations
- ✅ Like explaining the company's philosophy to a new joiner

---

## 4. CHAIN-OF-THOUGHT (COT) ALGORITHMS

**Goal:** Provide step-by-step decision processes that are deterministic and unambiguous.

**Template:**
```markdown
**CHAIN-OF-THOUGHT DECISION PROCESS:**

For EACH [item], ask yourself these questions IN ORDER:

**Q1: [First decision point]**
   - Indicator A
   - Indicator B
   - If YES → [action/next step]
   - If NO → Go to Q2

**Q2: [Second decision point]**
   - Indicator C
   - Indicator D
   - If YES → [action/next step]
   - If NO → Go to Q3

**Q3: [Third decision point]**
   - If YES → [final action]
   - If NO → [alternative action]

**THE FINAL TEST:**
"[Simple yes/no question to validate]"
- YES → [action]
- NO → [action]
```

**Example:**
```markdown
**CHAIN-OF-THOUGHT DECISION PROCESS:**

For EACH potential fact, ask yourself these questions IN ORDER:

**Q1: Is this an ACTION REQUEST or QUERY?**
   - "Can you X?", "Please Y", "I want to Z"
   - If YES → Check Q2
   - If NO → Go to Q3

**Q2: Does the action/query reveal a PERSISTENT plan or preference?**
   - "Can you book a flight to London?" → YES, reveals travel plan → EXTRACT the plan
   - "Can you check my emails?" → NO, just an immediate request → SKIP
   - If YES → EXTRACT
   - If NO → SKIP

**Q3: Is this describing a CURRENT MOMENT activity?**
   - Indicators: "I'm [verb]-ing", "right now", "currently"
   - If YES → SKIP (not persistent)
   - If NO → Go to Q4

**Q4: Is this a PERSISTENT truth about the user?**
   - Identity, relationships, preferences, allergies
   - If YES → EXTRACT
   - If NO → SKIP

**THE FINAL TEST:**
"Would the user want me to remember this NEXT WEEK?"
- YES → EXTRACT
- NO → SKIP
```

**Why This Works:**
- ✅ Eliminates ambiguity - clear decision tree
- ✅ LLM follows the same logic every time (consistency)
- ✅ Debuggable - you can trace where it went wrong
- ✅ Like giving a new joiner a flowchart for common decisions

---

## 5. EXAMPLES - Show, Don't Just Tell

**Goal:** Demonstrate the COT algorithm in action with diverse scenarios.

**Template:**
```markdown
**EXAMPLES:**

Example 1: [Scenario type] ([Expected outcome])
Input: "[example input]"
REASONING:
Q1: [answer] → [next step]
Q2: [answer] → [decision]
OUTPUT: [what to extract/do]

Example 2: [Different scenario] ([Different outcome])
Input: "[example input]"
REASONING:
Q1: [answer] → [next step]
Q3: [answer] → [decision]
OUTPUT: [what to extract/do]
```

**Example:**
```markdown
Example 1 - PERSISTENT (Extract):
Message: "I'm allergic to peanuts and I love Italian restaurants"
✅ Extract: "User is allergic to peanuts" (Allergy, CRITICAL)
✅ Extract: "User loves Italian restaurants" (Preference, NORMAL)

Example 2 - TRANSIENT (Skip):
Message: "Can you check my emails from today?"
❌ Extract: NONE (immediate action request, not worth remembering)

Example 3 - ACTION REQUEST revealing PLAN (Extract the plan):
Message: "Can you book a flight to London for next week?"
REASONING:
Q1: Action request? YES → Check Q2
Q2: Reveals persistent plan? YES - user IS planning to travel to London
✅ Extract: "User is planning to travel to London next week" (Travel)
```

**Why This Works:**
- ✅ Shows the COT algorithm in practice
- ✅ Covers edge cases and common scenarios
- ✅ LLM learns from examples (few-shot learning)
- ✅ Like showing a new joiner how previous employees handled similar cases

---

## 6. RULES SUMMARY - Quick Reference

**Goal:** Provide a condensed checklist for quick validation.

**Template:**
```markdown
**KEY RULES SUMMARY:**

1. ✅ [Rule for what TO do]
2. ✅ [Another rule for what TO do]
3. ❌ [Rule for what NOT to do]
4. ❌ [Another rule for what NOT to do]
5. **Default if unclear → [safe fallback]**
```

**Example:**
```markdown
**KEY RULES SUMMARY:**

1. ✅ Possessive from user (my/our) → PERSONAL
2. ✅ Possessive chain (my X's Y) → PERSONAL (indirect)
3. ✅ Interaction with user → PERSONAL
4. ❌ Knowledge query about them → REFERENCE
5. ❌ Public figure with no personal context → REFERENCE
6. **Default if unclear → REFERENCE** (safer)
```

**Why This Works:**
- ✅ Easy to scan and validate
- ✅ Reinforces most important rules
- ✅ Like a one-page cheat sheet for a new joiner

---

## 7. [OUTPUT SCHEMA] - Clear Expectations

**Goal:** Define exactly what format the output should be.

**Template:**
```markdown
[OUTPUT SCHEMA]

Return ONLY this JSON structure (no markdown, no extra text):

{
  "field1": "value type and constraints",
  "field2": ["array", "of", "valid", "values"],
  "field3": {
    "nested": "object structure"
  }
}

CRITICAL FIELD MAPPINGS:

**field1** (purpose and valid values):
  - "value1" → meaning
  - "value2" → meaning
  
**CRITICAL RULES:**
- If X → System will do Y
- If Z → System will do W
```

**Example:**
```markdown
[OUTPUT SCHEMA]

Return ONLY this JSON structure (no markdown, no extra text):

{
  "facts": [
    {
      "type": "FactType enum value",
      "text": "Complete fact sentence",
      "confidence": 0.95
    }
  ]
}

CRITICAL FIELD MAPPINGS:

**type** (ONLY use these FactType enum values):
  - "Allergy" → allergies, medical restrictions
  - "Preference" → likes, dislikes, habits
  - "Relationship" → family, friends, colleagues
  
CRITICAL RULES:
- NEVER use: "Promotion", "Career", "Job" (not valid enum values)
- Every fact MUST be a complete sentence
```

**Why This Works:**
- ✅ No ambiguity about output format
- ✅ Prevents common errors (invalid enum values, wrong structure)
- ✅ Like giving a new joiner the exact template to fill out

---

## Complete Prompt Template

Here's the full structure to follow:

```markdown
[ROLE]
You are a [JOB_TITLE] for [PURPOSE].
[1-2 sentence job description]

[TASK 1: PRIMARY_TASK]

[What to accomplish]

**CRITICAL CONCEPT:** [Core principle]

**THE KEY QUESTION:** "[Guiding question]"

**UNDERSTANDING THE DISTINCTION:**

✅ **Category A (DO THIS):**
- Example
- Example

❌ **Category B (AVOID THIS):**
- Example
- Example

---

**CHAIN-OF-THOUGHT DECISION PROCESS:**

For EACH [item], ask yourself IN ORDER:

**Q1: [Decision point]**
   - If YES → [action]
   - If NO → Q2

**Q2: [Decision point]**
   - If YES → [action]
   - If NO → Q3

**THE FINAL TEST:**
"[Validation question]"
- YES → [action]
- NO → [action]

---

**EXAMPLES:**

Example 1: [Scenario] ([Outcome])
Message: "[input]"
REASONING:
Q1: [step]
Q2: [step]
OUTPUT: [result]

Example 2: [Different scenario] ([Different outcome])
[... same structure ...]

---

**KEY RULES SUMMARY:**

1. ✅ [DO this]
2. ✅ [DO this]
3. ❌ [DON'T do this]
4. **Default → [safe fallback]**

---

[TASK 2: SECONDARY_TASK]

[Repeat structure above]

---

[OUTPUT SCHEMA]

Return ONLY this JSON:

{
  "field": "type and constraints"
}

CRITICAL FIELD MAPPINGS:
[Explain valid values and mappings]
```

---

## ✅ Prompt Writing Checklist

Before finalizing your prompt, check:

### **Structure:**
- ✅ **[ROLE]** defined?
- ✅ Tasks broken down clearly?
- ✅ Each task has CONCEPTS section?
- ✅ Each task has COT algorithm?
- ✅ Each task has EXAMPLES?
- ✅ Rules summary included?
- ✅ Output schema defined?

### **Clarity:**
- ✅ Can a smart high school graduate follow this?
- ✅ Are decision trees unambiguous (clear if/then)?
- ✅ Are examples diverse (cover edge cases)?
- ✅ Are concepts explained with examples?

### **Completeness:**
- ✅ Edge cases covered in examples?
- ✅ Common errors explicitly warned against?
- ✅ Default/fallback behavior specified?
- ✅ Valid enum values listed exhaustively?

### **Quality:**
- ✅ Uses ✅ and ❌ for clarity?
- ✅ Bold for **critical concepts**?
- ✅ Numbered questions (Q1, Q2, Q3)?
- ✅ "THE KEY QUESTION" highlighted?

---

## 📚 Reference Examples

### **Unified Extraction Prompt (GOLD STANDARD)**
**Location:** `backend/app/api/services/prompts/unified_extraction.md`

Perfect example of:
- Role → Tasks → Concepts → COT → Examples → Rules → Schema
- Used for fact extraction, entity disambiguation, topic extraction, preference detection

### **UI Node Prompts**
**Location:** `backend/app/api/services/agents/global_supervisor/nodes/ui_node_helpers/`

- Uses `professional_prompt_builder.py`
- Has `prompts/core.md`, `prompts/simple.md`, `prompts/complex.md`, etc.

### **Intent Classification Prompt**
**Location:** `backend/app/api/services/agents/global_supervisor/nodes/intent_classification_helpers/`

- Uses `prompt_builder.py`
- Has `prompts/intent_classification.md`

---

## 📖 Related Documentation

- **Prompt Asset Management Pattern:** `docs/Documentation/prompt_asset_management_pattern.md`
- **AGENTS.md:** Project-wide architecture guide
- **PROMPT_EDITING_GUIDE.md:** How to edit existing prompts

---

**Questions?** Refer to the gold standard example or ask the development team! 🚀

