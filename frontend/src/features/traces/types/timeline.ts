/**
 * Timeline View Data Types
 * 
 * Defines data structures for waterfall/timeline visualization.
 * Transformed from ObservationNode tree structure.
 */

import type { ObservationNode } from '../hooks/use-trace-detail';

/**
 * Timeline node - flattened observation for waterfall/timeline display
 * 
 * Represents a single observation in timeline view with calculated positions,
 * timing information, and display state for interactive visualization.
 */
export interface TimelineNode {
  /** Unique identifier (matches observation.id) */
  id: string;
  
  /** Display name of the observation/node */
  name: string;
  
  /** Observation type (SPAN, GENERATION, TOOL, AGENT, EVENT) */
  type: string;
  
  /** Log level (INFO, WARNING, ERROR) */
  level: string;
  
  /** Start time in milliseconds from trace start (for X-axis positioning) */
  startTime: number;
  
  /** End time in milliseconds from trace start (for bar width calculation) */
  endTime: number;
  
  /** Total duration in milliseconds (endTime - startTime) */
  duration: number;
  
  /** Nesting depth in tree (0 = root, 1 = first level child, etc.) */
  depth: number;
  
  /** ID of parent observation (null for root) */
  parentId: string | null;
  
  /** Array of child observation IDs (empty if leaf node) */
  children: string[];
  
  /** Hex color code for bar rendering (based on observation type) */
  color: string;
  
  /** Whether this node's children are currently visible (for collapse/expand) */
  isExpanded: boolean;
  
  /** Whether this node is currently visible (after filtering or collapsing) */
  isVisible: boolean;
  
  /** Number of prompt/input tokens (LLM calls only) */
  promptTokens: number | null;
  
  /** Number of completion/output tokens (LLM calls only) */
  completionTokens: number | null;
  
  /** Total tokens (prompt + completion) */
  totalTokens: number | null;
  
  /** Calculated cost in CHF for this observation */
  totalCost: string | null;
  
  /** Whether this observation has ERROR level */
  hasError: boolean;
  
  /** LLM model used (if applicable) */
  model: string | null;
  
  /** Reference to original observation for details panel */
  observation: ObservationNode;
}

/**
 * Complete timeline data for a trace
 * 
 * Contains flat array of all observations plus metadata needed
 * for timeline rendering (time bounds, dimensions, counts).
 */
export interface TimelineData {
  /** Flat array of all timeline nodes (tree flattened to array) */
  nodes: TimelineNode[];
  
  /** Absolute start time of the trace (earliest observation start_time) */
  traceStart: Date;
  
  /** Absolute end time of the trace (latest observation end_time) */
  traceEnd: Date;
  
  /** Total duration of trace in milliseconds */
  totalDuration: number;
  
  /** Maximum nesting depth in the tree (for layout calculations) */
  maxDepth: number;
  
  /** Total count of nodes (for statistics display) */
  nodeCount: number;
}

/**
 * Type guard to check if observation has timing data
 */
export function hasValidTiming(obs: ObservationNode): boolean {
  return obs.start_time !== null && obs.start_time !== undefined;
}

