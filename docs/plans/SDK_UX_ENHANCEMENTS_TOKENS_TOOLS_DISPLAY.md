# UX Enhancements: Tokens, Costs, and Tool Display

**Date:** 2025-11-06  
**Version:** Frontend v0.5.0  
**Estimated Time:** 3-4 hours  
**Priority:** P1 - High value UX improvements

---

## 🎯 Objectives

**Enhancement #1:** Show tokens & costs in tree view  
**Enhancement #2:** Verify all research_agent nodes are captured  
**Enhancement #3:** Show individual tool calls with details

---

## 📋 Enhancement #1: Tokens & Costs in Tree View

### **Current State**

Tree view shows:
```
classify_intent (LLM) ⚡ 1.2s
```

### **Desired State**

Tree view shows:
```
classify_intent (LLM) ⚡ 1.2s | 🎫 450 tokens (200↑ 250↓) | 💰 $0.0023
```

---

### **Implementation**

**File:** `frontend/src/features/traces/components/trace-tree.tsx` (or equivalent)

**Changes:**

1. Extract token data from observation
2. Extract cost data from observation
3. Format as compact badges
4. Add to tree node display

**Code:**

```typescript
function ObservationTreeNode({ observation }) {
  const tokens = {
    prompt: observation.prompt_tokens,
    completion: observation.completion_tokens,
    total: observation.total_tokens,
  };
  
  const costs = {
    input: observation.calculated_input_cost,
    output: observation.calculated_output_cost,
    total: observation.calculated_total_cost,
  };
  
  const hasTokens = tokens.total > 0;
  const hasCosts = costs.total > 0;
  
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <Typography>{observation.name}</Typography>
      <Chip label={observation.type} size="small" />
      
      {/* Duration */}
      {observation.latency_ms && (
        <Chip 
          label={`⚡ ${(observation.latency_ms / 1000).toFixed(1)}s`} 
          size="small" 
          variant="outlined"
        />
      )}
      
      {/* Tokens */}
      {hasTokens && (
        <Chip 
          label={`🎫 ${tokens.total} (${tokens.prompt}↑ ${tokens.completion}↓)`}
          size="small"
          variant="outlined"
          color="info"
        />
      )}
      
      {/* Costs */}
      {hasCosts && (
        <Chip 
          label={`💰 $${parseFloat(costs.total).toFixed(4)}`}
          size="small"
          variant="outlined"
          color="warning"
        />
      )}
    </Box>
  );
}
```

**Styling Considerations:**
- Make it compact (don't overwhelm)
- Use icons for quick recognition
- Use tooltips for full details
- Responsive (hide on small screens if needed)

---

## 📋 Enhancement #2: Verify Research Agent Capture

### **Analysis of Graph Code**

**Research Agent has 3 nodes:**
1. `research_planner` - Plans what to research
2. `tool_execution` - Executes tools
3. `completion_evaluator` - Checks if complete

**Flow:**
```
research_planner → tool_execution → completion_evaluator → research_planner (loop)
                                                         ↓
                                                        END (when complete)
```

**Key insight:** Can loop multiple times!

---

### **Current Capture (from logs)**

Looking at Trace #8:
```
research_agent (AGENT)
  ├─ research_planner (GENERATION) 💬🧠✨
  ├─ completion_evaluator (GENERATION) 💬✨
  ├─ research_planner (GENERATION) 💬🧠✨
  ├─ tool_execution (SPAN)
  ├─ completion_evaluator (GENERATION) 💬✨
  └─ research_planner (SPAN)
```

**Analysis:**
- ✅ research_planner: 3 captures
- ✅ completion_evaluator: 2 captures
- ✅ tool_execution: 1 capture
- ✅ **All nodes are being captured!**

**Conclusion:** SDK IS capturing everything correctly. The graph loops, and each iteration creates new observations. This is CORRECT behavior!

---

### **What User Might Be Missing:**

**Possible confusion:**
- User expects to see "tool_execution" multiple times
- But in this trace, tool_execution only ran once
- Other iterations might have gone: planner → evaluator → planner (no tools)

**Verification Needed:**
- Check tool_execution observation
- Verify it contains ALL tools that were executed
- Or if tools are batched/sequential

---

## 📋 Enhancement #3: Individual Tool Display

### **Current State**

tool_execution shows:
```json
{
  "tool_results": {
    "batch_read_20251106_064405_339": {
      "current_plan": "...",
      "batch_key": "...",
      "results": {
        "office365_search_emails_folder_inbox_...": {
          "tool_name": "office365_search_emails",
          "result": "{\n \"messages\": [...] \n}",
          ...
        }
      }
    }
  }
}
```

### **Desired State**

```
🔧 Tool Executions (Batch: batch_read_20251106_064405_339)

  🔧 office365_search_emails
     ├─ Parameters:
     │   folder: inbox
     │   filter: receivedDateTime ge 2025-11-06T00:00:00Z
     │   max_results: 50
     ├─ Status: ✅ Success
     └─ Response: 5 emails found
         ├─ Email 1: "New jobs for: IT : Singapore"
         ├─ Email 2: ...
         └─ [Show All]
```

---

### **Implementation**

**Create new component:** `IndividualToolsViewer.tsx`

```typescript
interface ToolCall {
  name: string;
  parameters: Record<string, any>;
  status: 'success' | 'failure';
  result: any;
  error?: string;
}

function extractToolCalls(toolResults: any): ToolCall[] {
  const calls: ToolCall[] = [];
  
  // Handle Swisper format
  if (typeof toolResults === 'object') {
    for (const batchKey in toolResults) {
      const batch = toolResults[batchKey];
      
      if (batch.results) {
        for (const toolKey in batch.results) {
          const toolData = batch.results[toolKey];
          
          calls.push({
            name: toolData.tool_name || toolKey,
            parameters: extractParameters(toolKey), // Parse from key
            status: toolData.error ? 'failure' : 'success',
            result: toolData.result,
            error: toolData.error,
          });
        }
      }
    }
  }
  
  return calls;
}

export function IndividualToolsViewer({ toolResults }: Props) {
  const toolCalls = extractToolCalls(toolResults);
  
  return (
    <Box>
      <Typography variant="h6">Tool Executions ({toolCalls.length})</Typography>
      
      {toolCalls.map((call, idx) => (
        <Accordion key={idx}>
          <AccordionSummary>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Build sx={{ color: 'success.main' }} /> {/* Wrench icon */}
              <Typography>{call.name}</Typography>
              {call.status === 'success' ? (
                <Chip label="✅ Success" size="small" color="success" />
              ) : (
                <Chip label="❌ Failed" size="small" color="error" />
              )}
            </Box>
          </AccordionSummary>
          
          <AccordionDetails>
            {/* Parameters */}
            <Typography variant="subtitle2">Parameters:</Typography>
            <JsonView value={call.parameters} collapsed={1} />
            
            {/* Result */}
            <Typography variant="subtitle2" sx={{ mt: 2 }}>Response:</Typography>
            {call.status === 'success' ? (
              <Paper sx={{ p: 2, bgcolor: 'success.dark' }}>
                <JsonView value={call.result} collapsed={2} />
              </Paper>
            ) : (
              <Alert severity="error">
                {call.error}
              </Alert>
            )}
          </AccordionDetails>
        </Accordion>
      ))}
    </Box>
  );
}
```

---

### **Parameter Extraction**

**From tool key:** `office365_search_emails_folder_inbox_filter_receivedDateTime...`

Need to parse this to extract:
- folder: inbox
- filter: receivedDateTime ge 2025-11-06...
- max_results: 50

**Alternative:** Check if parameters are stored elsewhere in tool data.

---

## 🔍 Investigation: Research Agent Node Capture

### **Question:** Are we capturing all nodes?

**From user's graph code:**
```python
workflow.add_node("research_planner", self.research_planner_node.execute)
workflow.add_node("tool_execution", self.tool_execution_node.execute)
workflow.add_node("completion_evaluator", self.completion_evaluator_node.execute)
```

**From our database (Trace #8):**
```
research_agent
  ├─ research_planner (3 times) ✅
  ├─ tool_execution (1 time) ✅
  └─ completion_evaluator (2 times) ✅
```

**Verdict:** ✅ **ALL nodes are being captured!**

**Why different counts?**
- Graph loops based on conditional routing
- research_planner called 3 times (initial + 2 replans)
- tool_execution called 1 time (only one batch of tools)
- completion_evaluator called 2 times (checked twice)

**This is CORRECT!** Each iteration creates a new observation.

---

### **What to Verify:**

1. **Check if tool_execution contains multiple tools**
   - Does it batch multiple tool calls?
   - Or one observation per tool?

2. **Check tool_execution observation in detail**
   - How many tools in one execution?
   - Are they in `tool_results`?

---

## 🛠️ Implementation Plan

### **Task 1: Tokens & Costs Display** (1.5 hours)

**Step 1.1:** Find tree view component (15 mins)
- Locate component that renders observation tree
- Understand current structure

**Step 1.2:** Add token display logic (30 mins)
- Extract tokens from observation
- Format as badge
- Add to tree node

**Step 1.3:** Add cost display logic (30 mins)
- Extract costs from observation
- Format as currency
- Add tooltip with breakdown

**Step 1.4:** Style and test (15 mins)
- Ensure compact display
- Test with various observations
- Check responsive behavior

---

### **Task 2: Verify Research Agent Capture** (30 mins)

**Step 2.1:** Check tool_execution detail (15 mins)
- Query observation with multiple tools
- Count tools in tool_results
- Verify all captured

**Step 2.2:** Document behavior (15 mins)
- Explain why counts vary
- Document loop behavior
- Add to troubleshooting guide

---

### **Task 3: Individual Tool Display** (2 hours)

**Step 3.1:** Create IndividualToolsViewer component (45 mins)
- Extract tool calls from tool_results
- Create accordion UI
- Add wrench icons

**Step 3.2:** Add parameter display (30 mins)
- Parse parameters from tool data
- Format nicely
- Add syntax highlighting

**Step 3.3:** Add status display (15 mins)
- Success/failure badges
- Error messages
- Response codes

**Step 3.4:** Add response payload display (30 mins)
- JSON viewer for responses
- Truncation for large responses
- "Show More" button

---

## 📊 Success Criteria

**Enhancement #1:**
- [ ] Tokens visible in tree view
- [ ] Costs visible in tree view
- [ ] Compact display (doesn't overwhelm)
- [ ] Tooltips show details

**Enhancement #2:**
- [ ] Confirmed all research nodes captured
- [ ] Documented loop behavior
- [ ] User understands why counts vary

**Enhancement #3:**
- [ ] Individual tools listed
- [ ] Wrench icon before each
- [ ] Parameters shown
- [ ] Status shown (success/failure)
- [ ] Response payload visible

---

## 🎯 Priority Order

**Recommended sequence:**

1. **Enhancement #2** (30 mins) - Quick verification
2. **Enhancement #1** (1.5 hours) - High value, medium effort
3. **Enhancement #3** (2 hours) - Most complex, highest impact

**Total:** 4 hours

---

**Author:** AI Assistant  
**Status:** READY FOR IMPLEMENTATION  
**Approval:** Awaiting go-ahead

