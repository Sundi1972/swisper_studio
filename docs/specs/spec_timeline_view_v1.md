# Specification: Timeline View for Trace Visualization

**Version:** 1.0  
**Date:** 2025-11-07  
**Status:** Draft - Awaiting Approval  
**Feature:** Timeline/Waterfall View for Trace Detail Page  
**Priority:** High (UX improvement)  
**Replaces:** Confusing network graph view

---

## 🎯 **Problem Statement**

**Current State:**
- Graph tab shows network diagram (vis-network)
- Node positions are arbitrary/scattered
- No clear execution sequence
- No timing information visible
- Doesn't help users understand "what happened in what order"
- Takes up ~40% of available canvas space

**User Feedback:**
> "The current graph view doesn't make much sense. It is confusing and doesn't add any real value. It should be hierarchical and a sequence like a step-by-step run through what happened."

---

## ✅ **Goals**

### **Primary Goal:**
Replace the network graph with a **waterfall/timeline view** that shows execution as a sequential, hierarchical flow.

### **User Value:**
1. **Debugging:** Quickly identify where errors occurred in the execution sequence
2. **Performance:** See which steps took the longest time
3. **Understanding:** Follow the execution path from user request to final response
4. **Cost Analysis:** Visualize where costs accumulated during execution

---

## 📋 **Functional Requirements**

### **FR1: Sequential Timeline Display**
- Display observations as horizontal bars on a timeline
- X-axis = time (0s → total duration)
- Y-axis = observation list (hierarchical)
- Bar length = observation duration
- Bar position = start time offset from trace beginning

### **FR2: Hierarchical Nesting**
- Parent-child relationships shown via indentation
- Indent = 20px per nesting level
- Expand/collapse controls for nodes with children
- Visual hierarchy matches observation tree

### **FR3: Timing Information**
- Time ruler at top (0s, 0.5s, 1.0s, etc.)
- Duration label on each bar (e.g., "1.2s")
- Hover tooltip shows:
  - Node name
  - Start time offset
  - Duration
  - % of total trace time

### **FR4: Type-Based Coloring**
- SPAN: Blue (#1976d2)
- GENERATION: Purple (#9c27b0)
- TOOL: Orange (#ed6c02)
- AGENT: Green (#2e7d32)
- ERROR: Red background (#d32f2f)

### **FR5: Interactivity**
- Click bar → show details panel below timeline
- Details panel shows: Input, Output, Metadata, State, Prompts, Tools
- Reuse existing `ObservationDetails` component

### **FR6: Full Canvas Usage**
- Timeline takes 100% of available width
- Height = number of visible nodes × row height
- Scrollable if content overflows

### **FR7: Error Visibility**
- Errors highlighted with red bar
- Warning icon (⚠️) before error nodes
- Failed nodes stand out visually

---

## 📋 **Non-Functional Requirements**

### **NFR1: Performance**
- Render <2s for traces with <100 nodes
- Render <5s for traces with <500 nodes
- Smooth interactions (60fps zoom/pan)

### **NFR2: Responsive**
- Adapts to window resize
- Works on screens ≥1024px wide
- Maintains aspect ratio on zoom

### **NFR3: Accessibility**
- Keyboard navigation (Tab, Enter)
- ARIA labels for screen readers
- High contrast mode support

---

## 🎨 **UI/UX Requirements**

### **Layout:**

```
┌─────────────────────────────────────────────────────────────────┐
│ Trace Detail: "What's my schedule?"      Duration: 2.3s $0.0054│
├─────────────────────────────────────────────────────────────────┤
│ [Tree View] [Timeline] [Graph] [JSON]                           │ ← Tabs
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ 25 nodes • 2.3s • CHF 0.0054          [🔍] [⬜] [↔]        │ │ ← Header
│ ├────────────────────────────────────────────────────────────┤ │
│ │ 0s ──────── 0.5s ──────── 1.0s ──────── 1.5s ──────── 2.0s│ │ ← Time Ruler
│ │                                                             │ │
│ │ global_supervisor                                     2.3s │ │
│ │ ├─ intent_classification        0.2s  ███                  │ │
│ │ ├─ routing                       0.1s  █                   │ │
│ │ ├─ productivity_agent           1.8s  ████████████████    │ │
│ │ │  ├─ tool_execution            1.2s    ████████          │ │
│ │ │  │  ├─ search_calendar        0.8s      █████   💬 🔧   │ │
│ │ │  │  └─ search_email           0.4s        ██    💬 🔧   │ │
│ │ │  └─ completion                0.3s              ██      │ │
│ │ └─ ui_node                      0.2s                   ███│ │
│ │                                                             │ │
│ │ [Click any bar to see details below]                       │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ Details: search_calendar                                   │ │ ← Details Panel
│ │ Duration: 0.8s | Tokens: 150 | Cost: CHF 0.0012           │ │
│ │ [Input] [Output] [State] [Metadata]                        │ │
│ │ {...JSON...}                                               │ │
│ └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

### **Interaction Flows:**

1. **View Timeline:**
   - User clicks "Timeline" tab
   - System renders waterfall view
   - All nodes initially expanded

2. **Collapse/Expand:**
   - User clicks ▼/▶ icon
   - System toggles children visibility
   - Re-renders timeline

3. **View Details:**
   - User clicks any bar
   - System shows details panel below
   - Panel displays input/output/state/metadata

4. **Zoom/Pan:**
   - User scrolls to zoom
   - User drags to pan
   - "Fit to Screen" button resets view

---

## 🔧 **Technical Requirements**

### **TR1: Technology**
- Use **D3.js v7** for timeline rendering
- SVG-based rendering (scalable, interactive)
- TypeScript for type safety

### **TR2: Data Structure**
- Transform ObservationNode tree → flat TimelineNode array
- Calculate relative timestamps (offset from trace start)
- Maintain parent-child relationships

### **TR3: Components**
```
TimelineView (container)
├─ TimelineHeader (stats + controls)
├─ TimelineCanvas (D3 SVG rendering)
└─ TimelineDetails (observation details panel)
```

### **TR4: State Management**
- Track selected node (for details panel)
- Track expanded/collapsed state per node
- Track zoom/pan transform state

---

## ✅ **Acceptance Criteria**

### **Must Have (MVP):**
- ✅ Timeline displays all observations sequentially (left → right)
- ✅ Bars are proportional to actual duration
- ✅ Nesting shown via indentation (20px per level)
- ✅ Click bar → details panel updates below
- ✅ Color-coded by type (SPAN, GENERATION, TOOL, etc.)
- ✅ Duration labels visible on each bar
- ✅ Time ruler at top shows scale
- ✅ Takes full available canvas width
- ✅ Errors clearly visible (red bars + ⚠️ icon)

### **Should Have (Enhancement):**
- ✅ Expand/collapse nested nodes
- ✅ Zoom in/out timeline
- ✅ Pan left/right for long traces
- ✅ "Fit to Screen" button
- ✅ Hover tooltips with timing breakdown

### **Nice to Have (Future):**
- ⏸️ Filter by observation type
- ⏸️ Critical path highlighting
- ⏸️ Export timeline as PNG
- ⏸️ Keyboard navigation
- ⏸️ Minimap for very long traces

---

## 🚫 **Out of Scope**

- ❌ Replacing tree view (keep both tabs)
- ❌ Replacing graph view yet (we'll deprecate after timeline proves useful)
- ❌ Real-time updates (timeline shows completed traces only)
- ❌ Editing observations from timeline
- ❌ Multi-trace comparison

---

## 📊 **Success Metrics**

### **Quantitative:**
- 90% of users prefer Timeline over Graph view (user survey)
- Average time to identify error location: <10 seconds (vs. 60s with graph)
- 0 performance regressions (rendering <2s for typical traces)

### **Qualitative:**
- PO can understand execution flow without asking developer
- Developers use Timeline as primary debugging view
- Support tickets about "confusing UI" decrease

---

## 🎯 **User Stories**

**US1: Debug Performance Issue**
```
As a developer,
When I see a slow trace (>5s),
I want to quickly identify which step took the longest,
So I can optimize that specific operation.
```

**US2: Find Error Location**
```
As a QA tester,
When a trace has an error,
I want to see exactly where in the sequence it failed,
So I can report the bug with context.
```

**US3: Understand Execution Flow**
```
As a product owner,
When I review a trace,
I want to see the step-by-step flow from user request to response,
So I understand how our system works.
```

**US4: Analyze Costs**
```
As a team lead,
When reviewing expensive traces,
I want to see which LLM calls cost the most,
So I can make cost optimization decisions.
```

---

## 🔍 **References**

**Similar Implementations:**
- **Jaeger UI** - Distributed tracing timeline (industry standard)
- **Chrome DevTools** - Performance tab waterfall view
- **LangSmith** - Trace timeline view
- **DataDog APM** - Trace flamegraph
- **New Relic** - Transaction timeline

**Technical References:**
- D3.js Gantt Charts: https://observablehq.com/@d3/gantt
- D3.js Timeline: https://observablehq.com/@d3/zoomable-timeline

---

## ⚠️ **Risks & Mitigation**

| Risk | Impact | Mitigation |
|------|--------|------------|
| D3.js learning curve | Medium | Use Observable examples, keep it simple for MVP |
| Performance with large traces | Medium | Virtual scrolling if >200 nodes, lazy rendering |
| Responsive sizing | Low | Use ResizeObserver, test on multiple screen sizes |
| Browser compatibility | Low | D3.js v7 supports all modern browsers |

---

## 📝 **Open Questions**

1. ✅ **Answered:** Keep graph view or remove? → Keep both tabs initially
2. ✅ **Answered:** Show all nodes or collapsed by default? → Expanded by default
3. ⏸️ **Pending:** Should we add filtering UI in this phase or later? → Decide in sub-plan

---

**Version:** 1.0  
**Status:** Draft - Awaiting Approval  
**Next Step:** Create implementation plan

