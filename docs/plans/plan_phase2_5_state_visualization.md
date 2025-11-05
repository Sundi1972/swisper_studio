# Phase 2.5 Implementation Plan: State Visualization & Prompt Display

**Date:** November 3, 2025  
**Status:** Approved - Ready for Implementation  
**Approach:** Hybrid UX (clean tree + indicators + side panel with quick actions)  
**Duration:** 9 days  
**Reference:** `docs/analysis/phase2_5_state_visualization_ux.md`

---

## 📋 Executive Summary

**Goal:** Enable developers and POs to see state transitions, LLM prompts, and tool calls in trace detail view.

**Current Problem:**
- Backend captures state, prompts, tool calls
- Frontend only shows summary metrics (duration, tokens, cost)
- Cannot debug why agent made decisions
- Cannot trace data flow through graph

**Solution:**
- Add status indicators to tree (🔄💬🛠️⚠️)
- Side panel with full observation details (60% width)
- Quick action buttons to jump to sections
- State diff viewer with syntax highlighting
- Type-specific sections (GENERATION prompts, TOOL calls)

**Success Criteria:**
- Click any observation → see state before/after
- GENERATION nodes → see prompt + response + state change
- TOOL nodes → see arguments + results + state change
- Visual diff highlights what changed (green/red/yellow)
- JSON tree viewer (expandable/collapsible)

---

## 🎯 Implementation Phases

### Phase 1: Indicators in Tree (1 day)

**Goal:** Add visual indicators to tree rows showing what data is available

**Tasks:**
- [ ] Create `getObservationIndicators()` utility function
  - Detect state changes (input !== output)
  - Detect prompts (type === GENERATION)
  - Detect tool calls (type === TOOL)
  - Detect errors (level === ERROR/WARNING)
- [ ] Update `ObservationTree` component
  - Add indicator icons to tree rows
  - Position icons after observation name
  - Tooltip on hover explaining each icon
- [ ] Create icon components
  - StateChangedIcon (🔄)
  - PromptIcon (💬)
  - ToolIcon (🛠️)
  - ErrorIcon (⚠️)
  - SuccessIcon (✅)

**Files to modify:**
- `frontend/src/features/traces/components/observation-tree.tsx`
- `frontend/src/features/traces/utils/observation-indicators.ts` (NEW)
- `frontend/src/components/icons/observation-icons.tsx` (NEW)

**Acceptance Criteria:**
- Icons appear next to observations in tree
- 🔄 shows when input !== output
- 💬 shows for GENERATION type
- 🛠️ shows for TOOL type
- ⚠️ shows for ERROR/WARNING level
- Tooltip explains each icon

---

### Phase 2: Side Panel Layout (2 days)

**Goal:** Split trace detail page into tree (40%) + details panel (60%)

**Tasks:**
- [ ] Update `TraceDetailPage` layout
  - Change from single column to two-column grid
  - Left: 40% width (tree view)
  - Right: 60% width (details panel)
  - Responsive: stack on mobile (<768px)
- [ ] Create `ObservationDetailsPanel` component
  - Props: `observation: ObservationNode | null`
  - Header: type badge, name, status
  - Empty state when no observation selected
  - Scroll container for content
- [ ] Update `ObservationTree` component
  - Add `selectedId: string | null` prop
  - Add `onSelect: (id: string) => void` callback
  - Highlight selected observation
  - Click observation → call onSelect
- [ ] Add selection state management
  - useState for selectedObservationId
  - Find observation by ID from tree
  - Pass to details panel

**Files to create:**
- `frontend/src/features/traces/components/observation-details-panel.tsx`

**Files to modify:**
- `frontend/src/features/traces/components/trace-detail-page.tsx`
- `frontend/src/features/traces/components/observation-tree.tsx`

**Acceptance Criteria:**
- Two-column layout renders correctly
- Click observation in tree → highlights in tree
- Click observation → details panel updates
- Empty state shows when no selection
- Layout responsive on mobile

---

### Phase 3: Quick Action Buttons (1 day)

**Goal:** Add button bar in details panel to jump to specific sections

**Tasks:**
- [ ] Create `QuickActionButtons` component
  - Props: `observationType`, `onJumpToSection`
  - Always show: [Input State] [Output State] [Diff]
  - For GENERATION: + [Prompt] [Response] [Params]
  - For TOOL: + [Tool Call] [Tool Response]
- [ ] Implement scroll-to-section functionality
  - Use refs for each section
  - scrollIntoView with smooth behavior
  - Highlight active section
- [ ] Update `ObservationDetailsPanel`
  - Add QuickActionButtons to header
  - Create refs for sections
  - Pass refs to button handler

**Files to create:**
- `frontend/src/features/traces/components/quick-action-buttons.tsx`

**Files to modify:**
- `frontend/src/features/traces/components/observation-details-panel.tsx`

**Acceptance Criteria:**
- Button bar appears in details panel
- Buttons adapt to observation type
- Click button → scrolls to section smoothly
- Active section highlighted

---

### Phase 4: State Diff Viewer (2 days)

**Goal:** Show state before/after with diff highlighting

**Tasks:**
- [ ] Install dependencies
  - `@uiw/react-json-view` (JSON tree viewer)
  - `react-diff-viewer-continued` (diff viewer)
- [ ] Create `StateDiffViewer` component
  - Props: `inputState`, `outputState`, `mode: 'diff' | 'side-by-side'`
  - Toggle between diff and side-by-side view
  - Diff mode: highlight added (green), removed (red), changed (yellow)
  - Side-by-side mode: two JSON viewers side by side
  - Expand/collapse sections
  - Copy button for each state
- [ ] Create `StateViewer` component (reusable)
  - Props: `data: any`, `title: string`
  - JSON tree viewer with syntax highlighting
  - Expand/collapse functionality
  - Copy button
  - Search/filter capability
- [ ] Add to `ObservationDetailsPanel`
  - Add state diff section (always shown first)
  - Default to diff mode
  - Show toggle for diff/side-by-side

**Files to create:**
- `frontend/src/features/traces/components/state-diff-viewer.tsx`
- `frontend/src/features/traces/components/state-viewer.tsx`

**Files to modify:**
- `frontend/package.json` (add dependencies)
- `frontend/src/features/traces/components/observation-details-panel.tsx`

**Acceptance Criteria:**
- State diff shows added/removed/changed fields
- Colors: green (added), red (removed), yellow (changed)
- Toggle between diff and side-by-side works
- JSON tree expandable/collapsible
- Copy button copies to clipboard
- Large states don't crash browser

---

### Phase 5: Type-Specific Sections (2 days)

**Goal:** Show prompts/responses for GENERATION, tool calls for TOOL

**Tasks:**
- [ ] Create `PromptViewer` component
  - Props: `input: any`
  - Parse input to extract prompt/messages
  - Format nicely (system, user, assistant sections)
  - Syntax highlighting for code in prompts
  - Copy button
- [ ] Create `ResponseViewer` component
  - Props: `output: any`
  - Show LLM response
  - Format JSON if structured
  - Show reasoning if available
  - Copy button
- [ ] Create `ModelParametersViewer` component
  - Props: `modelParameters: any`
  - Show temperature, max_tokens, etc.
  - Format as key-value table
- [ ] Create `ToolCallViewer` component
  - Props: `input: any`
  - Extract tool name and arguments
  - Show function name prominently
  - Format arguments as JSON tree
  - Copy button
- [ ] Create `ToolResponseViewer` component
  - Props: `output: any`
  - Show tool response/results
  - Format as JSON tree
  - Show execution status
  - Copy button
- [ ] Update `ObservationDetailsPanel`
  - Conditionally render based on observation.type
  - For GENERATION: Prompt + Response + Params sections
  - For TOOL: ToolCall + ToolResponse sections
  - For others: State only

**Files to create:**
- `frontend/src/features/traces/components/prompt-viewer.tsx`
- `frontend/src/features/traces/components/response-viewer.tsx`
- `frontend/src/features/traces/components/model-parameters-viewer.tsx`
- `frontend/src/features/traces/components/tool-call-viewer.tsx`
- `frontend/src/features/traces/components/tool-response-viewer.tsx`

**Files to modify:**
- `frontend/src/features/traces/components/observation-details-panel.tsx`

**Acceptance Criteria:**
- GENERATION nodes show: state + prompt + response + params
- TOOL nodes show: state + call args + response
- SPAN nodes show: state only
- All sections visible simultaneously (scroll to see)
- Prompts formatted nicely (system/user/assistant)
- Tool calls show function name and arguments
- Copy buttons work for all sections

---

### Phase 6: Polish & UX (1 day)

**Goal:** Add finishing touches for professional appearance

**Tasks:**
- [ ] Add syntax highlighting
  - Use react-syntax-highlighter for code blocks
  - Theme: VS Code dark (matches Swisper)
- [ ] Copy to clipboard functionality
  - Add copy buttons to all viewers
  - Show toast notification on copy
  - "Copied!" feedback
- [ ] Empty states
  - "No input data" when observation.input is null
  - "No output data" when observation.output is null
  - "No prompt available" for GENERATION without prompt
- [ ] Error handling
  - Handle malformed JSON gracefully
  - Show error message if state can't be parsed
  - Fallback to raw text display
- [ ] Loading states
  - Show spinner while parsing large JSON
  - Debounce expand/collapse for performance
- [ ] Accessibility
  - Keyboard navigation (Tab through buttons)
  - ARIA labels for all buttons
  - Screen reader announcements
- [ ] Visual polish
  - Consistent spacing and padding
  - Hover states for buttons
  - Smooth transitions
  - Color scheme matches Swisper dark theme

**Files to modify:**
- All viewer components (add copy, empty states, error handling)
- `frontend/src/features/traces/components/observation-details-panel.tsx`

**Acceptance Criteria:**
- Copy buttons work everywhere
- Empty states look professional
- Errors handled gracefully
- Keyboard navigation works
- Matches Swisper visual design

---

### Phase 7: Browser Testing & UAT (2 days)

**Goal:** Test with real data, find and fix bugs

**Tasks:**
- [ ] Create test traces
  - GENERATION observation with prompt/response
  - TOOL observation with args/response
  - SPAN observation with state changes
  - ERROR observation
  - Large state (>100 fields)
  - Deeply nested state (>5 levels)
- [ ] Browser testing
  - Chrome: All features
  - Firefox: All features
  - Safari: All features (if available)
  - Mobile: Responsive layout
- [ ] Performance testing
  - Load trace with 50+ observations
  - Expand all JSON trees
  - Switch between observations quickly
  - Check memory usage
- [ ] UAT Scenarios
  - Developer debugs LLM prompt
  - Developer traces state flow
  - PO sees what changed in state
  - Developer finds error in tool call
  - Developer compares states
- [ ] Bug fixes
  - Fix any issues found
  - Edge cases
  - Performance issues
- [ ] Documentation
  - Update QUICK_START.md
  - Add screenshots to docs
  - Update PHASE5_HANDOVER.md

**Acceptance Criteria:**
- All UAT scenarios pass
- No console errors
- Performance acceptable (<1s to open details)
- Works on all browsers
- Documentation updated

---

## 📦 Dependencies

**NPM Packages to Add:**

```bash
cd frontend
npm install @uiw/react-json-view react-diff-viewer-continued react-syntax-highlighter
npm install -D @types/react-syntax-highlighter
```

**Versions:**
- `@uiw/react-json-view`: ^2.0.0
- `react-diff-viewer-continued`: ^3.3.1
- `react-syntax-highlighter`: ^15.5.0

---

## 🗂️ File Structure

**New Files:**

```
frontend/src/features/traces/
├── components/
│   ├── observation-details-panel.tsx         (NEW - main panel)
│   ├── quick-action-buttons.tsx              (NEW - jump buttons)
│   ├── state-diff-viewer.tsx                 (NEW - diff view)
│   ├── state-viewer.tsx                      (NEW - JSON tree)
│   ├── prompt-viewer.tsx                     (NEW - LLM prompts)
│   ├── response-viewer.tsx                   (NEW - LLM responses)
│   ├── model-parameters-viewer.tsx           (NEW - params table)
│   ├── tool-call-viewer.tsx                  (NEW - tool args)
│   └── tool-response-viewer.tsx              (NEW - tool results)
├── utils/
│   └── observation-indicators.ts             (NEW - indicator logic)
└── hooks/
    └── use-observation-selection.ts          (NEW - selection state)

frontend/src/components/icons/
└── observation-icons.tsx                     (NEW - indicator icons)
```

**Modified Files:**

```
frontend/src/features/traces/
├── components/
│   ├── trace-detail-page.tsx                 (MODIFIED - split layout)
│   └── observation-tree.tsx                  (MODIFIED - selection + icons)
└── hooks/
    └── use-trace-detail.ts                   (MODIFIED - if needed)
```

---

## 🎯 Success Metrics

**Functional:**
- ✅ All observation types show state before/after
- ✅ GENERATION shows prompts + responses
- ✅ TOOL shows arguments + results
- ✅ Diff highlighting works (green/red/yellow)
- ✅ JSON tree expandable/collapsible
- ✅ Copy buttons work everywhere

**Performance:**
- ✅ Details panel opens in <200ms
- ✅ Diff calculation in <100ms
- ✅ Handles 1000+ line JSON without lag
- ✅ Switching observations in <50ms

**UX:**
- ✅ Professional appearance (Langfuse quality)
- ✅ Intuitive (no training needed)
- ✅ Responsive (works on tablet/mobile)
- ✅ Accessible (keyboard + screen reader)

---

## 🔍 Testing Checklist

### Unit Tests (Optional for MVP)
- [ ] `getObservationIndicators()` returns correct icons
- [ ] State diff calculation works correctly
- [ ] JSON parsing handles edge cases

### Integration Tests
- [ ] Click observation → details panel updates
- [ ] Toggle diff/side-by-side works
- [ ] Copy buttons copy to clipboard
- [ ] Quick action buttons scroll to sections

### Browser Tests
- [ ] All features work in Chrome
- [ ] All features work in Firefox
- [ ] Responsive layout on mobile
- [ ] No console errors

### UAT Scenarios
- [ ] Developer can see LLM prompt that caused error
- [ ] PO can see state changes between nodes
- [ ] Developer can copy tool arguments for debugging
- [ ] Developer can trace data flow through 10 nodes
- [ ] Developer can find where field was added to state

---

## 📝 Implementation Notes

### Data Structure Assumptions

**Backend API returns full observation data:**
```json
{
  "id": "obs-123",
  "type": "GENERATION",
  "name": "intent_classification",
  "input": {
    "state": {...},
    "prompt": "...",
    "messages": [...]
  },
  "output": {
    "state": {...},
    "llm_response": {...}
  },
  "model": "gpt-4-turbo",
  "model_parameters": {...}
}
```

**If backend doesn't return full data:**
- Option A: Enhance `/traces/{id}/tree` endpoint
- Option B: Add `/observations/{id}` endpoint for lazy loading

**For MVP:** Assume `/tree` endpoint returns full data (easier, one API call).

---

### State Diff Algorithm

**Simple approach (client-side):**
```typescript
function diffObjects(before: any, after: any) {
  const diff = {
    added: {},
    removed: {},
    changed: {}
  };
  
  // Find added and changed
  for (const key in after) {
    if (!(key in before)) {
      diff.added[key] = after[key];
    } else if (JSON.stringify(before[key]) !== JSON.stringify(after[key])) {
      diff.changed[key] = { before: before[key], after: after[key] };
    }
  }
  
  // Find removed
  for (const key in before) {
    if (!(key in after)) {
      diff.removed[key] = before[key];
    }
  }
  
  return diff;
}
```

**Alternative:** Use `react-diff-viewer-continued` library (handles nested objects).

---

### Prompt Parsing

**For LLM prompts, we need to handle different formats:**

**OpenAI messages format:**
```json
{
  "messages": [
    {"role": "system", "content": "You are..."},
    {"role": "user", "content": "What's..."}
  ]
}
```

**String prompt:**
```json
{
  "prompt": "You are a helpful assistant..."
}
```

**Anthropic format:**
```json
{
  "system": "You are...",
  "messages": [{"role": "user", "content": "..."}]
}
```

**Solution:** Detect format and render appropriately.

---

## 🚀 Deployment Plan

**After Phase 7 complete:**

1. **Merge to feature branch**
   - Create PR with all changes
   - Code review (if applicable)
   
2. **Update documentation**
   - Screenshots in docs/
   - Update QUICK_START.md
   - Update PHASE5_HANDOVER.md

3. **Deploy to dev environment**
   - Test with real Swisper traces
   - Gather feedback

4. **Production deployment**
   - Merge to main
   - Deploy SwisperStudio
   - User training (if needed)

---

## 📚 References

- **Analysis:** `docs/analysis/phase2_5_state_visualization_ux.md`
- **Langfuse Reference:** Observation detail patterns
- **Swisper Theme:** Dark mode colors, MUI components
- **Libraries:**
  - [@uiw/react-json-view docs](https://uiwjs.github.io/react-json-view/)
  - [react-diff-viewer-continued](https://github.com/aeaton/react-diff-viewer)

---

**Last Updated:** November 3, 2025  
**Status:** Approved - Ready for Implementation  
**Next Step:** Start Phase 1 (Indicators in Tree)


