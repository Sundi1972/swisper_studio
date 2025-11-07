/**
 * Transform observation tree to timeline format
 * 
 * Converts hierarchical ObservationNode tree into flat array of TimelineNodes
 * with calculated relative timestamps for waterfall visualization.
 */

import type { ObservationNode } from '../hooks/use-trace-detail';
import type { TimelineNode, TimelineData } from '../types/timeline';

// Constants
const DEFAULT_DURATION_MS = 100; // Default duration for nodes missing end_time
const DEFAULT_COLOR = '#757575'; // Gray for unknown types

/**
 * Color map for observation types
 * Based on MUI color palette for consistency
 */
const OBSERVATION_TYPE_COLORS: Record<string, string> = {
  SPAN: '#1976d2',        // Blue
  GENERATION: '#9c27b0',  // Purple
  TOOL: '#ed6c02',        // Orange
  AGENT: '#2e7d32',       // Green
  EVENT: '#757575',       // Gray
  SYSTEM: '#424242',      // Dark Gray
};

/**
 * Get color for observation type
 * 
 * @param type - Observation type (SPAN, GENERATION, TOOL, etc.)
 * @returns Hex color code for rendering
 */
function getColorForType(type: string): string {
  return OBSERVATION_TYPE_COLORS[type] || DEFAULT_COLOR;
}

/**
 * Find time boundaries of trace (earliest start and latest end)
 * 
 * Single traversal optimization - finds both min and max in one pass.
 * 
 * @param observations - Root observation nodes
 * @returns Object with earliest start time and latest end time
 */
function findTimeBounds(observations: ObservationNode[]): { start: Date; end: Date } {
  if (!observations || observations.length === 0) {
    const now = new Date();
    return { start: now, end: now };
  }
  
  let earliest = new Date(observations[0].start_time);
  let latest = new Date(0); // Epoch
  
  function traverse(nodes: ObservationNode[]) {
    for (const node of nodes) {
      // Validate start_time exists
      if (!node.start_time) {
        console.warn(`Observation ${node.id} missing start_time, skipping time calculation`);
        continue;
      }
      
      // Check start time
      const nodeStart = new Date(node.start_time);
      if (nodeStart < earliest) {
        earliest = nodeStart;
      }
      
      // Check end time
      if (node.end_time) {
        const nodeEnd = new Date(node.end_time);
        if (nodeEnd > latest) {
          latest = nodeEnd;
        }
      }
      
      // Traverse children
      if (node.children && node.children.length > 0) {
        traverse(node.children);
      }
    }
  }
  
  traverse(observations);
  
  // If no end times found, use earliest + some duration
  if (latest.getTime() === 0) {
    latest = new Date(earliest.getTime() + DEFAULT_DURATION_MS);
  }
  
  return { start: earliest, end: latest };
}

/**
 * Process single observation node recursively
 * 
 * Converts ObservationNode to TimelineNode with calculated timing offsets.
 * 
 * @param obs - Observation to process
 * @param depth - Nesting depth (0 for root)
 * @param parentId - Parent observation ID (null for root)
 * @param traceStartMs - Trace start time in milliseconds (for offset calculation)
 * @param nodes - Array to accumulate processed nodes
 */
function processNode(
  obs: ObservationNode,
  depth: number,
  parentId: string | null,
  traceStartMs: number,
  nodes: TimelineNode[]
): void {
  // Validate start_time
  if (!obs.start_time) {
    console.warn(`Observation ${obs.id} (${obs.name}) missing start_time, using current time`);
    obs.start_time = new Date().toISOString();
  }
  
  // Calculate relative timestamps
  const startMs = new Date(obs.start_time).getTime();
  const startTime = startMs - traceStartMs;
  
  // Handle missing end_time (priority: end_time > latency_ms > default)
  let endTime: number;
  if (obs.end_time) {
    const endMs = new Date(obs.end_time).getTime();
    endTime = endMs - traceStartMs;
  } else if (obs.latency_ms && obs.latency_ms > 0) {
    endTime = startTime + obs.latency_ms;
  } else {
    endTime = startTime + DEFAULT_DURATION_MS;
  }
  
  const duration = Math.max(1, endTime - startTime); // Ensure minimum 1ms
  
  // Create timeline node
  const timelineNode: TimelineNode = {
    id: obs.id,
    name: obs.name || 'Unknown',
    type: obs.type,
    level: obs.level || 'INFO',
    startTime,
    endTime,
    duration,
    depth,
    parentId,
    children: obs.children.map((c: ObservationNode) => c.id),
    color: getColorForType(obs.type),
    isExpanded: true,  // Initially expanded
    isVisible: true,   // Initially visible
    promptTokens: obs.prompt_tokens,
    completionTokens: obs.completion_tokens,
    totalTokens: obs.total_tokens,
    totalCost: obs.calculated_total_cost,
    hasError: obs.level === 'ERROR',
    model: obs.model,
    observation: obs, // Keep reference to original
  };
  
  nodes.push(timelineNode);
  
  // Process children recursively
  if (obs.children && obs.children.length > 0) {
    for (const child of obs.children) {
      processNode(child, depth + 1, obs.id, traceStartMs, nodes);
    }
  }
}

/**
 * Transform observation tree to timeline data
 * 
 * Converts hierarchical tree structure to flat array with relative timestamps
 * for waterfall/timeline visualization.
 * 
 * @param observations - Array of root observation nodes (usually just 1 root)
 * @returns TimelineData with flat array of nodes and timing metadata
 */
export function transformToTimeline(observations: ObservationNode[]): TimelineData {
  // Handle empty input
  if (!observations || observations.length === 0) {
    const now = new Date();
    return {
      nodes: [],
      traceStart: now,
      traceEnd: now,
      totalDuration: 0,
      maxDepth: 0,
      nodeCount: 0,
    };
  }
  
  // Find trace time boundaries (single traversal optimization)
  const { start: traceStart, end: traceEnd } = findTimeBounds(observations);
  const traceStartMs = traceStart.getTime();
  
  // Transform tree to flat array
  const nodes: TimelineNode[] = [];
  
  // Process each root observation (usually just one)
  for (const rootObs of observations) {
    processNode(rootObs, 0, null, traceStartMs, nodes);
  }
  
  // Calculate metadata
  const maxDepth = Math.max(...nodes.map(n => n.depth), 0);
  const totalDuration = traceEnd.getTime() - traceStart.getTime();
  
  return {
    nodes,
    traceStart,
    traceEnd,
    totalDuration,
    maxDepth,
    nodeCount: nodes.length,
  };
}

/**
 * Toggle expand/collapse state for a node and update visibility of descendants
 * 
 * When collapsing a node, all its descendants become hidden.
 * When expanding a node, only immediate children become visible (they control their own descendants).
 * 
 * @param data - Current timeline data
 * @param nodeId - ID of node to toggle
 * @returns Updated timeline data (new object for React re-render)
 */
export function toggleNodeExpansion(
  data: TimelineData,
  nodeId: string
): TimelineData {
  const node = data.nodes.find(n => n.id === nodeId);
  if (!node || node.children.length === 0) {
    return data; // No change if node not found or has no children
  }
  
  // Toggle expansion state
  node.isExpanded = !node.isExpanded;
  
  // Update visibility of all descendants
  function setDescendantsVisibility(parentId: string, visible: boolean) {
    data.nodes.forEach(n => {
      if (n.parentId === parentId) {
        n.isVisible = visible;
        
        // If hiding or parent is collapsed, hide all descendants recursively
        if (!visible || !n.isExpanded) {
          setDescendantsVisibility(n.id, false);
        } else {
          setDescendantsVisibility(n.id, true);
        }
      }
    });
  }
  
  setDescendantsVisibility(nodeId, node.isExpanded);
  
  return { ...data }; // Return new object to trigger re-render
}

