# Phase 3 Week 2 UAT - Graph Visualization Features

**Date:** November 2, 2025  
**Tester:** AI Assistant  
**Features Under Test:**
1. Swisper Builder (System Architecture View)
2. Trace Graph View

---

## UAT Test Cases

### Feature 1: Swisper Builder - System Architecture View

#### TC-SB-01: Navigation to Swisper Builder
- **Steps:**
  1. Login to SwisperStudio
  2. From Projects page, click "Swisper Builder" button
- **Expected:** Navigate to `/swisper-builder` route
- **Result:** 

#### TC-SB-02: Agent List Display
- **Steps:**
  1. Open Swisper Builder page
- **Expected:** 
  - Sidebar shows "Agents" header with "5 total"
  - List shows all 5 agents:
    - global_supervisor (6 nodes)
    - productivity_agent (4 nodes)
    - research_agent (3 nodes)
    - wealth_agent (2 nodes)
    - doc_agent (3 nodes)
- **Result:** 

#### TC-SB-03: Default Agent Selection
- **Steps:**
  1. Open Swisper Builder (first time)
- **Expected:** 
  - global_supervisor selected by default
  - Main area shows "global_supervisor" title
  - Shows description: "Main orchestrator..."
  - Shows "6 nodes • 5 edges"
- **Result:** 

#### TC-SB-04: Graph Visualization
- **Steps:**
  1. View default graph (global_supervisor)
- **Expected:**
  - Graph canvas displays with nodes and edges
  - 6 nodes visible: Intent Classification, Memory, Global Planner, Agent Execution, User Interface, Indexing
  - Nodes connected with arrows (top-to-bottom flow)
  - Nodes color-coded by type
  - Graph controls visible (Zoom In, Zoom Out, Reset)
- **Result:** 

#### TC-SB-05: Agent Switching
- **Steps:**
  1. Click "productivity_agent" in sidebar
- **Expected:**
  - Sidebar selection changes
  - Main area title changes to "productivity_agent"
  - Description updates to "Email, calendar..."
  - Shows "4 nodes • 3 edges"
  - Graph updates to show 4 nodes
- **Result:** 

#### TC-SB-06: Multiple Agent Switching
- **Steps:**
  1. Click each agent in sequence:
     - research_agent
     - wealth_agent
     - doc_agent
     - back to global_supervisor
- **Expected:**
  - Each click updates the graph
  - Node count matches expected (3, 2, 3, 6)
  - No errors or flickering
  - Smooth transitions
- **Result:** 

#### TC-SB-07: Zoom Controls
- **Steps:**
  1. Select any agent
  2. Click "Zoom In" button 3 times
  3. Click "Zoom Out" button 2 times
  4. Click "Reset View" button
- **Expected:**
  - Zoom In: Graph gets larger each click
  - Zoom Out: Graph gets smaller each click
  - Reset: Graph returns to original fit
  - Controls responsive (<500ms)
- **Result:** 

#### TC-SB-08: Node Colors by Type
- **Steps:**
  1. Select productivity_agent
  2. Observe node colors
- **Expected:**
  - Provider Selection: Blue (SPAN)
  - Productivity Planner: Blue (SPAN)
  - Productivity Write: Pink (GENERATION)
  - Tool Execution: Orange (TOOL)
  - All nodes have visible borders
- **Result:** 

#### TC-SB-09: Back Navigation
- **Steps:**
  1. From Swisper Builder, click "Back to Projects"
- **Expected:**
  - Navigate to `/projects` page
  - See project list
- **Result:** 

#### TC-SB-10: Performance
- **Steps:**
  1. Navigate to Swisper Builder
  2. Note time from click to graph visible
  3. Switch between agents 5 times
  4. Note average switch time
- **Expected:**
  - Initial load: <1 second
  - Agent switch: <500ms
  - No lag or freezing
- **Result:** 

---

### Feature 2: Trace Graph View

#### TC-TG-01: Graph Tab Presence
- **Steps:**
  1. Navigate to any trace detail page
  2. Check tabs
- **Expected:**
  - 4 tabs visible: Tree View, Graph View, Timeline (disabled), JSON (disabled)
  - Tree View selected by default
  - Graph View is clickable
- **Result:** 

#### TC-TG-02: Switch to Graph View
- **Steps:**
  1. On trace detail page, click "Graph View" tab
- **Expected:**
  - Tab becomes active (highlighted)
  - Graph view content displays
  - Tree view content hidden
- **Result:** 

#### TC-TG-03: Graph Data Display
- **Steps:**
  1. View Graph tab for test trace
- **Expected:**
  - Info text shows node and edge count (e.g., "9 nodes • 12 edges")
  - Graph canvas visible
  - Zoom controls visible (Zoom In, Zoom Out, Reset)
- **Result:** 

#### TC-TG-04: Graph Structure
- **Steps:**
  1. Observe graph nodes and edges
- **Expected:**
  - START node visible (gray, system node)
  - END node visible (gray, system node)
  - Observation nodes between START and END
  - Arrows connecting nodes (showing flow)
  - Hierarchical layout (top-to-bottom)
- **Result:** 

#### TC-TG-05: Node Colors in Trace Graph
- **Steps:**
  1. Identify different node types in graph
- **Expected:**
  - AGENT nodes: Purple border
  - GENERATION nodes: Pink border
  - SPAN nodes: Blue border
  - TOOL nodes: Orange border
  - SYSTEM nodes (START/END): Gray border
  - All nodes readable
- **Result:** 

#### TC-TG-06: Graph Zoom Controls
- **Steps:**
  1. Click Zoom In button
  2. Click Zoom Out button
  3. Click Reset View button
- **Expected:**
  - Same behavior as System Architecture
  - Graph scales correctly
  - No visual glitches
- **Result:** 

#### TC-TG-07: Tab Switching Consistency
- **Steps:**
  1. Switch from Graph View to Tree View
  2. Switch back to Graph View
- **Expected:**
  - Graph re-renders correctly
  - No "stale" data
  - State preserved (same zoom level optional)
- **Result:** 

#### TC-TG-08: Empty/Error States
- **Steps:**
  1. (If possible) View a trace with no observations
- **Expected:**
  - Show informative message: "No graph data available..."
  - No crash or blank screen
- **Result:** 

#### TC-TG-09: Performance
- **Steps:**
  1. Click Graph View tab
  2. Note time to render
- **Expected:**
  - Graph visible in <2 seconds
  - No freezing or lag
- **Result:** 

#### TC-TG-10: Multiple Traces
- **Steps:**
  1. View Graph tab for first trace
  2. Navigate back to trace list
  3. Open different trace
  4. View Graph tab again
- **Expected:**
  - Graph updates with new trace data
  - No mixing of data from previous trace
  - Correct node/edge count displayed
- **Result:** 

---

## Overall Quality Checks

### QC-01: Console Errors
- **Steps:** Open browser DevTools console during all tests
- **Expected:** No errors (warnings acceptable)
- **Result:** 

### QC-02: Responsive Design
- **Steps:** Resize browser window
- **Expected:** 
  - Graphs scale appropriately
  - No horizontal scrolling
  - Controls remain accessible
- **Result:** 

### QC-03: Browser Compatibility
- **Steps:** Test in Chrome
- **Expected:** All features work
- **Result:** 

---

## Summary

**Total Test Cases:** 23  
**Passed:** _____  
**Failed:** _____  
**Blocked:** _____  

**Critical Issues:** _____  
**Minor Issues:** _____  

**UAT Status:** [ ] PASS / [ ] FAIL  
**Ready for Production:** [ ] YES / [ ] NO  

**Tester Signature:** _________________  
**Date:** _________________

