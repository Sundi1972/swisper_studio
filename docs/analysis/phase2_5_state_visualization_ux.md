# Phase 2.5 Analysis: State Visualization & Prompt Display UX

**Date:** November 3, 2025  
**Status:** Analysis & Design Phase  
**Goal:** Design UX for displaying state transitions, prompts, and LLM outputs in trace views

---

## 🔑 Key Design Principle

**ALL observations modify state. The UI must show:**

1. **State Transition (for ALL types):** What changed from input → output
2. **Type-Specific Details:**
   - **GENERATION:** + LLM prompt & response
   - **TOOL:** + Tool arguments & results
   - **SPAN/AGENT/EVENT:** State only

**Layout Structure:**
```
Input/Output Tab (for ANY observation type):

┌─────────────────────────────────────────┐
│ 1. STATE TRANSITION (always shown)      │
│    - State before                       │
│    - State after                        │
│    - Diff (what changed)                │
├─────────────────────────────────────────┤
│ 2. TYPE-SPECIFIC SECTION (if applicable)│
│                                         │
│    If GENERATION:                       │
│    - LLM Prompt                         │
│    - LLM Response                       │
│    - Model parameters                   │
│                                         │
│    If TOOL:                             │
│    - Tool call arguments                │
│    - Tool response                      │
│    - Execution time                     │
│                                         │
│    If SPAN/AGENT/EVENT:                 │
│    - (No additional section)            │
└─────────────────────────────────────────┘
```

This ensures developers can always trace state flow through the graph, regardless of node type.

---

## 📋 Table of Contents

1. [Problem Statement](#problem-statement)
2. [Current State Analysis](#current-state-analysis)
3. [User Stories & Requirements](#user-stories--requirements)
4. [Reference Analysis (Langfuse)](#reference-analysis-langfuse)
5. [UX Design Options](#ux-design-options)
6. [Recommended Design](#recommended-design)
7. [Technical Implementation](#technical-implementation)
8. [Success Criteria](#success-criteria)

---

## Problem Statement

### What's Missing?

**Backend:** We capture complete execution context
- ✅ State before/after each node (in `observation.input`/`observation.output`)
- ✅ LLM prompts and responses (in GENERATION observations)
- ✅ Model parameters (temperature, max_tokens)
- ✅ Tool arguments and results

**Frontend:** We only show summary metrics
- ❌ Cannot see state at each step
- ❌ Cannot see state transitions (what changed)
- ❌ Cannot see prompts sent to LLMs
- ❌ Cannot see LLM responses
- ❌ Cannot see tool arguments/results

### Impact

**PO cannot:**
- Debug why an agent made a decision (can't see LLM prompt)
- Understand state changes (can't see what changed between nodes)
- Inspect tool calls (can't see arguments passed)
- Validate LLM behavior (can't see model parameters used)

**Developer cannot:**
- Trace data flow through the graph
- Identify where state corruption occurs
- Compare expected vs actual prompts
- Verify tool outputs

---

## Current State Analysis

### Backend Data Structure

From `backend/app/models/observation.py`:

```python
class Observation(SQLModel, table=True):
    # Identity
    id: str
    name: str | None
    type: ObservationType  # SPAN, GENERATION, EVENT, TOOL, AGENT
    
    # Content (THIS IS WHAT WE NEED TO DISPLAY)
    input: dict[str, Any] | None      # ← State BEFORE execution
    output: dict[str, Any] | None     # ← State AFTER execution
    meta: dict[str, Any] | None       # ← Additional metadata
    
    # LLM Details (FOR GENERATION TYPE)
    model: str | None                 # ← "gpt-4-turbo"
    model_parameters: dict | None     # ← {"temperature": 0.7, "max_tokens": 2000}
    prompt_tokens: int | None
    completion_tokens: int | None
    calculated_total_cost: Decimal | None
    
    # Status
    level: str                        # ← DEFAULT, WARNING, ERROR
    status_message: str | None        # ← Error details
```

### **CRITICAL INSIGHT: All Nodes Can Modify State!** 🔑

**Important:** `input` and `output` represent **state before/after** for ALL observation types:
- SPAN nodes can modify state
- GENERATION nodes can modify state (LLM adds intent, reasoning, etc.)
- TOOL nodes can modify state (tool response gets added to state)
- AGENT nodes can modify state
- EVENT nodes can modify state

**Data model by observation type:**

#### GENERATION (LLM calls):
```json
{
  "type": "GENERATION",
  "input": {
    "state": { "messages": [...], "current_intent": null },
    "prompt": "You are a helpful assistant...",  // ← LLM PROMPT
    "messages": [...]                             // ← LLM MESSAGES
  },
  "output": {
    "state": { "messages": [...], "current_intent": "calendar_query", "confidence": 0.95 },
    "llm_response": { "intent": "calendar_query", "reasoning": "..." }  // ← LLM RESPONSE
  },
  "model": "gpt-4-turbo",
  "model_parameters": { "temperature": 0.7 }
}
```
**Must show:**
1. State transition (state before → state after)
2. LLM prompt (what we asked)
3. LLM response (what it answered)
4. Model parameters

#### TOOL (Function/API calls):
```json
{
  "type": "TOOL",
  "name": "search_calendar",
  "input": {
    "state": { "current_intent": "calendar_query", "user_input": "next meeting" },
    "tool_call": {                                 // ← HOW WE CALLED THE TOOL
      "function": "search_calendar",
      "arguments": { "query": "next meeting", "max_results": 5 }
    }
  },
  "output": {
    "state": { "current_intent": "calendar_query", "calendar_results": [...] },
    "tool_response": {                             // ← WHAT THE TOOL RETURNED
      "results": [{ "title": "Team Standup", "time": "10:00 AM" }]
    }
  }
}
```
**Must show:**
1. State transition (state before → state after)
2. Tool call arguments (how we invoked it)
3. Tool response (what it returned)

#### SPAN/AGENT/EVENT (Generic nodes):
```json
{
  "type": "SPAN",
  "name": "planner",
  "input": {
    "state": { "current_intent": "calendar_query", "calendar_results": [...] }
  },
  "output": {
    "state": { "current_intent": "calendar_query", "calendar_results": [...], "plan": "Show next meeting" }
  }
}
```
**Must show:**
1. State transition (state before → state after)

### Current Frontend Components

**ObservationTree** (`frontend/src/features/traces/components/observation-tree.tsx`):
- Shows type, name, duration, tokens, cost
- Displays as collapsible tree
- **Does NOT show:** input, output, prompts, responses

**TraceDetailPage** (`frontend/src/features/traces/components/trace-detail-page.tsx`):
- Has 4 tabs: Tree View, Graph View, Timeline (disabled), JSON (disabled)
- **Does NOT have:** Details panel for selected observation

### API Available

**GET /api/v1/traces/{trace_id}/tree:**
```json
{
  "id": "obs-123",
  "type": "GENERATION",
  "name": "intent_classification",
  "input": {
    "messages": [...],
    "prompt": "You are a helpful assistant..."  // ← NOT DISPLAYED
  },
  "output": {
    "intent": "calendar_query",
    "confidence": 0.95,
    "reasoning": "User asked about meetings"    // ← NOT DISPLAYED
  },
  "model": "gpt-4-turbo",
  "model_parameters": {
    "temperature": 0.7,                         // ← NOT DISPLAYED
    "max_tokens": 2000
  },
  "children": [...]
}
```

**The API returns this data, but the frontend doesn't display it!**

---

## User Stories & Requirements

### US1: View State Transitions for ALL Nodes
**As a** developer  
**I want to** see state before and after for every node (SPAN, GENERATION, TOOL, AGENT, EVENT)  
**So that** I can trace data flow through the entire graph

**Acceptance Criteria:**
- Click on ANY observation → see state before/after
- State displayed as formatted JSON with syntax highlighting
- Large states should be collapsible/expandable
- Works for all observation types (not just SPAN)

---

### US2: See State Diffs
**As a** PO  
**I want to** see what changed in state between input and output  
**So that** I can understand what each node does without reading code

**Acceptance Criteria:**
- Diff view: highlight added fields (green), removed (red), changed (yellow)
- Side-by-side view: state before | state after
- Toggle between diff and side-by-side
- Option to hide unchanged fields
- Works for ALL observation types

---

### US3: View LLM Prompts & Responses (GENERATION)
**As a** developer  
**I want to** see the exact prompt sent to the LLM AND the response AND the state change  
**So that** I can debug why the agent made a decision

**Acceptance Criteria:**
- For GENERATION observations:
  - Show state transition (what changed in state)
  - Show LLM prompt (what we asked)
  - Show LLM response (what it answered)
  - Show model parameters (temperature, max_tokens)
  - All three sections visible simultaneously
- Copy buttons for prompt and response
- Display system message, user message separately

---

### US4: View Tool Calls & Responses (TOOL)
**As a** developer  
**I want to** see tool arguments AND tool results AND state changes  
**So that** I can debug tool integrations

**Acceptance Criteria:**
- For TOOL observations:
  - Show state transition (how state changed)
  - Show tool call arguments (how we invoked it)
  - Show tool response (what it returned)
  - Show execution time
  - All three sections visible simultaneously
- Function name prominently displayed
- Arguments formatted as JSON
- Results formatted as JSON
- Copy buttons for arguments and response

---

### US5: View Generic Node Execution (SPAN/AGENT/EVENT)
**As a** developer  
**I want to** see state transitions for generic nodes  
**So that** I can understand control flow

**Acceptance Criteria:**
- For SPAN/AGENT/EVENT observations:
  - Show state before
  - Show state after
  - Highlight what changed
- No extra sections (just state)
- Same diff/side-by-side toggle as other types

---

### US6: View Errors
**As a** developer  
**I want to** see error details and stack traces  
**So that** I can fix production bugs

**Acceptance Criteria:**
- ERROR-level observations highlighted in red
- Show error message prominently
- Show stack trace if available (in metadata)
- Show state when error occurred

---

## Reference Analysis (Langfuse)

### Langfuse Trace Detail UX

Let me analyze Langfuse's approach to displaying observation details...

**Key Patterns from Langfuse:**

1. **IOView Component** (`web/src/components/trace/IOView.tsx`)
   - Displays input/output side-by-side
   - JSON syntax highlighting
   - Collapsible sections
   - Copy to clipboard

2. **ObservationDetail Panel** (`web/src/features/traces/components/ObservationDetail.tsx`)
   - Shows when observation selected
   - Tabs: Overview | I/O | Metadata | Scores
   - Overview: Model, tokens, cost, timing
   - I/O: Input and output with diff viewer
   - Metadata: All other fields

3. **Three-Panel Layout:**
   ```
   ┌─────────────────────────────────────────────┐
   │ Trace Header (name, user, time, cost)       │
   ├─────────────┬───────────────────────────────┤
   │             │                               │
   │ Observation │  Observation Detail Panel     │
   │ Tree        │                               │
   │ (Left 40%)  │  - Overview tab               │
   │             │  - Input/Output tab           │
   │             │  - Metadata tab               │
   │             │                               │
   │             │  (Right 60%)                  │
   │             │                               │
   └─────────────┴───────────────────────────────┘
   ```

4. **State Diff Viewer:**
   - Uses `react-diff-viewer` library
   - Side-by-side comparison
   - Syntax highlighting
   - Line numbers
   - Expand/collapse sections

5. **Prompt/Response Display:**
   - For GENERATION type:
     - Input shows as "Prompt"
     - Output shows as "Completion"
   - Markdown rendering for formatted text
   - Code blocks syntax highlighted

---

## UX Design Options

### Option A: Modal Dialog (Simple)

**Pros:**
- Easy to implement
- Works on mobile
- Focused view (no distractions)

**Cons:**
- Context switching (lose sight of tree)
- Can't compare multiple observations
- Modal fatigue

**Design:**
```
Tree View → Click observation → Modal opens
┌──────────────────────────────────────┐
│ ✕  intent_classification (GENERATION)│
├──────────────────────────────────────┤
│ Tabs: Overview | Input | Output | ... │
├──────────────────────────────────────┤
│                                       │
│   [Content based on tab]              │
│                                       │
│                                       │
└──────────────────────────────────────┘
```

---

### Option B: Side Panel (Langfuse Style) ⭐ RECOMMENDED

**Pros:**
- See tree + details simultaneously
- Natural workflow (select → view)
- Can navigate tree while viewing details
- Professional appearance

**Cons:**
- More complex to implement
- Requires responsive design
- Less space on small screens

**Design:**
```
┌─────────────┬────────────────────────────┐
│ Tree View   │ Observation Details        │
│ (Left 40%)  │ (Right 60%)                │
│             │                            │
│ ☑ SPAN      │ ┌────────────────────────┐ │
│   ├─ GEN ✓  │ │ Tabs: Overview | I/O   │ │
│   ├─ TOOL   │ │       Metadata | ...   │ │
│   └─ SPAN   │ └────────────────────────┘ │
│             │                            │
│             │ [Content based on tab]     │
│             │                            │
│             │                            │
└─────────────┴────────────────────────────┘
```

---

### Option C: Expandable Rows (Accordion)

**Pros:**
- No context switching
- Simple interaction (click to expand)
- All in one view

**Cons:**
- Long scrolling
- Hard to see overview
- Messy with many observations

**Design:**
```
Tree View:
☑ SPAN: supervisor (100ms)
  ├─ GENERATION: intent_classification (50ms) ▼
  │  ┌─────────────────────────────────────────┐
  │  │ Input: {...}                            │
  │  │ Output: {...}                           │
  │  │ Model: gpt-4-turbo                      │
  │  └─────────────────────────────────────────┘
  ├─ TOOL: search_calendar (20ms)
  └─ SPAN: ui_node (30ms)
```

---

### Option D: Tabs with Details in Each Tab

**Pros:**
- Familiar tab pattern
- Clear separation of concerns

**Cons:**
- Which observation's details to show?
- Confusing navigation

**Not Recommended**

---

## Recommended Design

### **Option B: Side Panel (Langfuse Pattern)** ⭐

**Layout:**
```
┌───────────────────────────────────────────────────────────────┐
│ Trace Header                                                  │
│ supervisor-trace-2024-11-03 | User: alice | Cost: $0.0054    │
├─────────────────────┬─────────────────────────────────────────┤
│ Observation Tree    │ Observation Details                     │
│ (40% width)         │ (60% width)                             │
│                     │                                         │
│ ☑ SPAN: supervisor  │ ┌─────────────────────────────────────┐ │
│   100ms             │ │ GENERATION: intent_classification   │ │
│                     │ │ gpt-4-turbo | 50ms | $0.0015        │ │
│   ├─ GENERATION ✓   │ └─────────────────────────────────────┘ │
│   │  intent_class   │                                         │
│   │  50ms           │ Tabs: Overview | Input/Output | Raw    │
│   │                 │ ─────────────────────────────────────── │
│   ├─ TOOL           │                                         │
│   │  search_cal     │ [Tab Content - see below]               │
│   │  20ms           │                                         │
│   │                 │                                         │
│   └─ SPAN           │                                         │
│      ui_node        │                                         │
│      30ms           │                                         │
│                     │                                         │
└─────────────────────┴─────────────────────────────────────────┘
```

### Tab 1: Overview

**For ALL observation types:**
```
┌─────────────────────────────────────────────────────┐
│ Overview                                            │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Type:       GENERATION                              │
│ Name:       intent_classification                   │
│ Status:     ✓ Success                               │
│ Duration:   50ms                                    │
│                                                     │
│ ─── LLM Details ───                                 │
│ Model:      gpt-4-turbo                             │
│ Tokens:     150 prompt + 50 completion = 200 total  │
│ Cost:       $0.0015 ($0.001 input + $0.0005 output) │
│                                                     │
│ ─── Parameters ───                                  │
│ temperature:  0.7                                   │
│ max_tokens:   2000                                  │
│ top_p:        1.0                                   │
│                                                     │
│ ─── Timing ───                                      │
│ Start:      2024-11-03 14:32:01.123                 │
│ End:        2024-11-03 14:32:01.173                 │
│ Latency:    50ms                                    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**For GENERATION (additional):**
- Show model parameters prominently
- Show token breakdown
- Show cost breakdown

**For TOOL (additional):**
- Show tool name
- Show execution time

**For ERROR level:**
- Show error message in red box
- Show stack trace if available

---

### Tab 2: Input/Output

**This tab adapts based on observation type!**

---

#### For ALL Types: State Transition (Always Shown First)

**Default View: State Diff**
```
┌─────────────────────────────────────────────────────┐
│ State Transition              [View: Diff ▼]        │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ─── What Changed ───                                │
│                                                     │
│ {                                                   │
│   "messages": [...],                    (unchanged) │
│ - "current_intent": null,               (removed)   │
│ + "current_intent": "calendar_query",   (added)     │
│ + "confidence": 0.95,                   (added)     │
│ + "reasoning": "User asked about..."    (added)     │
│   "user_input": "What's my next..."     (unchanged) │
│ }                                                   │
│                                                     │
│ [View: Side-by-Side] [Show Unchanged] [Copy]        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Alternative View: Side-by-Side State**
```
┌─────────────────────────────────────────────────────┐
│ State Transition          [View: Side-by-Side ▼]    │
├──────────────────────┬──────────────────────────────┤
│ State Before         │ State After                  │
├──────────────────────┼──────────────────────────────┤
│                      │                              │
│ {                    │ {                            │
│   "messages": [...], │   "messages": [...],         │
│   "current_intent":  │   "current_intent":          │
│     null,            │     "calendar_query",        │
│   "user_input":      │   "confidence": 0.95,        │
│     "What's my..."   │   "reasoning": "...",        │
│ }                    │   "user_input": "..."        │
│                      │ }                            │
│ [Copy]               │ [Copy]                       │
│                      │                              │
└──────────────────────┴──────────────────────────────┘
```

---

#### Additional for GENERATION: Prompt & Response

**Below the state transition, show:**

```
┌─────────────────────────────────────────────────────┐
│ ─── LLM Interaction ───                             │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Prompt Sent to LLM:                                 │
│ ┌─────────────────────────────────────────────────┐ │
│ │ System: You are a helpful assistant that        │ │
│ │ classifies user intents...                      │ │
│ │                                                 │ │
│ │ User: What's my next meeting?                   │ │
│ │                                                 │ │
│ │ Context: Available intents: calendar_query,     │ │
│ │ task_create, ...                                │ │
│ └─────────────────────────────────────────────────┘ │
│ [Copy Prompt] [View Raw JSON]                       │
│                                                     │
│ LLM Response:                                       │
│ ┌─────────────────────────────────────────────────┐ │
│ │ {                                               │ │
│ │   "intent": "calendar_query",                   │ │
│ │   "confidence": 0.95,                           │ │
│ │   "reasoning": "User is asking about their      │ │
│ │                 next scheduled meeting"         │ │
│ │ }                                               │ │
│ └─────────────────────────────────────────────────┘ │
│ [Copy Response] [View Raw JSON]                     │
│                                                     │
│ Model: gpt-4-turbo | Temperature: 0.7 | Tokens: 200 │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

#### Additional for TOOL: Tool Call & Response

**Below the state transition, show:**

```
┌─────────────────────────────────────────────────────┐
│ ─── Tool Execution ───                              │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Tool Called:                                        │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Function: search_calendar                       │ │
│ │                                                 │ │
│ │ Arguments:                                      │ │
│ │ {                                               │ │
│ │   "query": "next meeting",                      │ │
│ │   "max_results": 5,                             │ │
│ │   "start_date": "2024-11-03"                    │ │
│ │ }                                               │ │
│ └─────────────────────────────────────────────────┘ │
│ [Copy Arguments]                                    │
│                                                     │
│ Tool Response:                                      │
│ ┌─────────────────────────────────────────────────┐ │
│ │ {                                               │ │
│ │   "status": "success",                          │ │
│ │   "results": [                                  │ │
│ │     {                                           │ │
│ │       "title": "Team Standup",                  │ │
│ │       "time": "2024-11-03 10:00:00",            │ │
│ │       "attendees": ["alice", "bob"]             │ │
│ │     }                                           │ │
│ │   ]                                             │ │
│ │ }                                               │ │
│ └─────────────────────────────────────────────────┘ │
│ [Copy Response]                                     │
│                                                     │
│ Execution Time: 145ms                               │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

#### For SPAN/AGENT/EVENT: State Only

**Just show the state transition (no additional sections)**

```
┌─────────────────────────────────────────────────────┐
│ State Transition              [View: Diff ▼]        │
├─────────────────────────────────────────────────────┤
│                                                     │
│ {                                                   │
│   "current_intent": "calendar_query",   (unchanged) │
│   "calendar_results": [...],            (unchanged) │
│ + "plan": "Show next meeting to user",  (added)     │
│ + "next_step": "ui_node"                (added)     │
│ }                                                   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Alternative View: Diff Mode**
```
┌─────────────────────────────────────────────────────┐
│ Input/Output                        [View: Diff ▼]  │
├─────────────────────────────────────────────────────┤
│                                                     │
│ {                                                   │
│   "messages": [...],                                │
│ - "current_intent": null,              (removed)    │
│ + "current_intent": "calendar_query",  (added)      │
│ + "confidence": 0.95,                  (added)      │
│ + "reasoning": "User asked about..."   (added)      │
│   "user_input": "What's my next meeting?"           │
│ }                                                   │
│                                                     │
│ [Copy] [Show Full] [Toggle Unchanged]               │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**For GENERATION observations specifically:**

Show prompts in readable format:
```
┌─────────────────────────────────────────────────────┐
│ Prompt                                              │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ─── System Message ───                              │
│ You are a helpful assistant that classifies user    │
│ intents for a calendar application.                 │
│                                                     │
│ ─── User Message ───                                │
│ What's my next meeting?                             │
│                                                     │
│ ─── Context ───                                     │
│ Available intents: calendar_query, task_create,     │
│ reminder_set, ...                                   │
│                                                     │
│ [Copy Prompt]                                       │
│                                                     │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Response                                            │
├─────────────────────────────────────────────────────┤
│                                                     │
│ {                                                   │
│   "intent": "calendar_query",                       │
│   "confidence": 0.95,                               │
│   "reasoning": "User is asking about their next     │
│                 scheduled meeting, which is a       │
│                 calendar query."                    │
│ }                                                   │
│                                                     │
│ [Copy Response]                                     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

### Tab 3: Metadata

**Show all other fields:**
```
┌─────────────────────────────────────────────────────┐
│ Metadata                                            │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ID:              obs-abc-123-def-456                │
│ Trace ID:        trace-xyz-789                      │
│ Parent ID:       obs-parent-123                     │
│                                                     │
│ ─── Custom Metadata ───                             │
│ {                                                   │
│   "environment": "production",                      │
│   "version": "1.2.3",                               │
│   "user_tier": "premium"                            │
│ }                                                   │
│                                                     │
│ ─── Timestamps ───                                  │
│ Start Time:           2024-11-03 14:32:01.123       │
│ Completion Started:   2024-11-03 14:32:01.145       │
│ End Time:             2024-11-03 14:32:01.173       │
│ TTFT:                 22ms                          │
│ Total Latency:        50ms                          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

### Empty States

**When no observation selected:**
```
┌─────────────────────────────────────────────┐
│                                             │
│                                             │
│           📊                                │
│                                             │
│    Select an observation from the tree      │
│    to view its details                      │
│                                             │
│                                             │
└─────────────────────────────────────────────┘
```

**When observation has no input:**
```
┌─────────────────────────────────────────────┐
│ Input                                       │
├─────────────────────────────────────────────┤
│                                             │
│   No input data available                   │
│                                             │
└─────────────────────────────────────────────┘
```

---

### Responsive Design

**Desktop (>1200px):**
- Side-by-side: Tree (40%) | Details (60%)

**Tablet (768px - 1200px):**
- Side-by-side: Tree (35%) | Details (65%)
- Scrollable

**Mobile (<768px):**
- Stack vertically: Tree on top, details below
- OR: Full-screen modal on click

---

## Technical Implementation

### New Frontend Components

**1. `ObservationDetailsPanel` (NEW)**
- Location: `frontend/src/features/traces/components/observation-details-panel.tsx`
- Props:
  - `observation: ObservationNode | null`
  - `onClose?: () => void`
- State: `currentTab: 'overview' | 'io' | 'metadata'`

**2. `ObservationOverviewTab` (NEW)**
- Shows summary (type, name, duration, model, tokens, cost)
- Shows model parameters
- Shows error details if level === 'ERROR'

**3. `ObservationIOTab` (NEW)**
- Shows input/output side-by-side or diff
- JSON syntax highlighting (use `react-json-view` or `@uiw/react-json-view`)
- Copy to clipboard buttons
- Expandable/collapsible sections

**4. `StateViewer` (NEW - Reusable)**
- Props: `data: any, title: string`
- JSON syntax highlighting
- Copy button
- Expand/collapse
- Search in JSON

**5. `DiffViewer` (NEW - Reusable)**
- Props: `before: any, after: any`
- Side-by-side or unified diff
- Color highlighting (red = removed, green = added, yellow = changed)
- Uses `react-diff-viewer-continued` library

**6. `PromptViewer` (NEW)**
- For GENERATION observations
- Parse input to extract system/user/assistant messages
- Format nicely
- Syntax highlighting for code in prompts

**7. Update `TraceDetailPage`:**
- Add state: `selectedObservationId: string | null`
- Pass to `ObservationTree`: `onSelectObservation(id)`
- Render `ObservationDetailsPanel` in right panel

**8. Update `ObservationTree`:**
- Add `onSelectObservation?: (id: string) => void` prop
- Highlight selected observation
- Click observation → call `onSelectObservation(id)`

### Updated Layout

**TraceDetailPage component structure:**
```tsx
<Box display="flex" flexDirection="row" gap={2}>
  {/* Left: Tree (40%) */}
  <Box flex="0 0 40%">
    <Paper>
      <Tabs>...</Tabs>
      <ObservationTree
        nodes={tree}
        selectedId={selectedObservationId}
        onSelect={(id) => setSelectedObservationId(id)}
      />
    </Paper>
  </Box>

  {/* Right: Details (60%) */}
  <Box flex="1">
    <Paper>
      {selectedObservationId ? (
        <ObservationDetailsPanel
          observation={findObservation(selectedObservationId)}
        />
      ) : (
        <EmptyState />
      )}
    </Paper>
  </Box>
</Box>
```

### Libraries to Add

```json
{
  "dependencies": {
    "@uiw/react-json-view": "^2.0.0",        // JSON viewer with syntax highlighting
    "react-diff-viewer-continued": "^3.3.1",  // Diff viewer
    "react-syntax-highlighter": "^15.5.0"    // Code syntax highlighting
  }
}
```

### API Changes

**Current API returns minimal data in tree endpoint.**

**Option A: Enhance `/traces/{id}/tree` to include full observation data**
- Pro: One API call
- Con: Large payload (includes all input/output)

**Option B: Add `/observations/{id}` endpoint for full details**
- Pro: Lazy loading (fetch when selected)
- Con: Extra API calls

**Recommendation:** Option A for MVP (simplicity), optimize later if performance issue.

### Data Flow

```
1. User loads trace detail page
   → GET /api/v1/traces/{id}/tree
   → Returns full observation tree with input/output

2. User clicks observation in tree
   → Set selectedObservationId
   → ObservationDetailsPanel receives observation data
   → Renders tabs with data

3. User switches tabs
   → Render different view (Overview/IO/Metadata)
   → No additional API calls needed
```

---

## Graph View Enhancements

**Also update Graph View to show details on click:**

When user clicks node in graph:
- Open same `ObservationDetailsPanel` in right sidebar
- OR: Show modal with observation details
- Keep graph visible (don't replace)

**Layout option:**
```
┌──────────────────────────────────────────────────┐
│ Graph View                                       │
├──────────────────┬───────────────────────────────┤
│ Graph Canvas     │ Node Details                  │
│ (70%)            │ (30%)                         │
│                  │                               │
│   ●──●──●        │ [Same ObservationDetailsPanel]│
│   │  │  │        │                               │
│   ●──●──●        │                               │
│                  │                               │
└──────────────────┴───────────────────────────────┘
```

---

## Success Criteria

### Functional Requirements

- [ ] Click observation in tree → details panel opens
- [ ] Details panel shows 3 tabs: Overview, Input/Output, Metadata
- [ ] Overview tab shows type, name, duration, model, tokens, cost
- [ ] Overview tab shows model parameters for GENERATION
- [ ] I/O tab shows input and output side-by-side
- [ ] I/O tab has diff mode toggle
- [ ] Diff mode highlights added (green), removed (red), changed (yellow)
- [ ] For GENERATION, I/O tab shows prompt and response clearly
- [ ] Metadata tab shows all other fields
- [ ] JSON viewer has syntax highlighting
- [ ] Copy to clipboard buttons work
- [ ] Selected observation highlighted in tree
- [ ] Click another observation → details panel updates
- [ ] Click graph node → same details panel opens
- [ ] Empty state when no observation selected
- [ ] ERROR-level observations highlighted in red

### UX Requirements

- [ ] Loads in <200ms (data already fetched)
- [ ] Smooth transitions (no jank)
- [ ] Responsive (works on desktop, tablet, mobile)
- [ ] Accessible (keyboard navigation, screen readers)
- [ ] Professional appearance (matches Langfuse quality)

### Edge Cases

- [ ] Handle observations with no input
- [ ] Handle observations with no output
- [ ] Handle large JSON (>1MB) - truncate or paginate
- [ ] Handle deeply nested JSON - collapsible
- [ ] Handle ERROR observations - show error prominently
- [ ] Handle TOOL observations - show arguments/results

---

## Implementation Phases

### Phase 1: Basic Details Panel (2 days)
- Create `ObservationDetailsPanel` component
- Add to `TraceDetailPage` (side-by-side layout)
- Show overview tab only (basic info)
- Click observation → panel updates

### Phase 2: Input/Output Tab (2 days)
- Add `StateViewer` component (JSON viewer)
- Add `ObservationIOTab` component
- Show input and output side-by-side
- Syntax highlighting
- Copy buttons

### Phase 3: Diff Viewer (1 day)
- Add `DiffViewer` component
- Toggle between side-by-side and diff mode
- Highlight changes

### Phase 4: GENERATION Enhancements (1 day)
- Add `PromptViewer` component
- Parse prompts/responses nicely
- Show model parameters prominently

### Phase 5: Metadata Tab (1 day)
- Show all metadata fields
- Show timestamps
- Show custom metadata

### Phase 6: Graph Integration (1 day)
- Add click handler to graph nodes
- Open details panel on click
- Highlight selected node

### Phase 7: Polish & Testing (1 day)
- Responsive design
- Accessibility
- Browser testing
- Edge cases

**Total Estimate:** 9 days (or ~1.5 weeks)

---

## Open Questions

### Q1: Should we show state diff automatically or require toggle?
**Options:**
- A) Show side-by-side by default, toggle to diff
- B) Show diff by default, toggle to side-by-side
- C) Auto-detect: if small changes, show diff; if large, show side-by-side

**Recommendation:** A (side-by-side default) - less cognitive load

---

### Q2: How to handle very large state (>1MB)?
**Options:**
- A) Truncate and show "View full" button
- B) Paginate JSON viewer
- C) Load on demand (lazy)
- D) Store in separate endpoint

**Recommendation:** A (truncate) - simple, works for 99% of cases

---

### Q3: Should we parse LLM prompts or show raw?
**Options:**
- A) Show raw JSON (exactly as stored)
- B) Parse and format (system/user/assistant messages)
- C) Both: toggle between formatted and raw

**Recommendation:** C (both) - flexibility for debugging

---

### Q4: Should details panel be closable?
**Options:**
- A) Always open (persistent)
- B) Closable with X button (hide panel)
- C) Collapsible (minimize to narrow sidebar)

**Recommendation:** B (closable) - more space for tree when needed

---

## Next Steps

### Before Implementation

1. **Get stakeholder approval on UX design**
   - Review mockups above
   - Confirm layout (side-by-side vs modal)
   - Confirm tab structure (Overview/IO/Metadata)

2. **Create detailed mockups (optional)**
   - Use Figma/Excalidraw if needed
   - Interactive prototype

3. **Write implementation plan**
   - Break down into tasks
   - Estimate effort
   - Identify dependencies

### After Approval

4. **Start Phase 1** (Basic Details Panel)
5. **Iterative UAT** (test after each phase)
6. **Polish and refine**

---

**Ready for review!** Please provide feedback on:
- Is the side-by-side layout (tree | details) acceptable?
- Are the 3 tabs (Overview, I/O, Metadata) sufficient?
- Any missing requirements or edge cases?
- Should we proceed with implementation?

---

**Last Updated:** November 3, 2025  
**Status:** Awaiting approval  
**Next:** Create implementation plan after approval

