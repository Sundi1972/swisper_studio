/**
 * Utility functions to determine which indicators to show for observations
 */

export interface ObservationIndicators {
  hasStateChange: boolean;
  hasPrompt: boolean;
  hasTool: boolean;
  hasError: boolean;
  hasWarning: boolean;
}

interface ObservationData {
  type: string;
  level: string;
  input: Record<string, any> | null;
  output: Record<string, any> | null;
  children?: ObservationData[];  // For aggregating child state changes
}

/**
 * Determine which indicators to show for an observation
 * 
 * State change aggregation: Shows STATE CHANGED if:
 * - This observation's input ≠ output, OR
 * - Any child observation changed state
 */
export function getObservationIndicators(observation: ObservationData): ObservationIndicators {
  // Check if this node changed state
  const thisNodeChangedState = hasStateChanged(observation.input, observation.output);
  
  // Check if any child changed state (aggregate up)
  const anyChildChangedState = observation.children?.some(child => 
    getObservationIndicators(child).hasStateChange
  ) || false;

  return {
    // State changed if this node OR any child changed state
    hasStateChange: thisNodeChangedState || anyChildChangedState,
    
    // Has prompt if it's a GENERATION type
    hasPrompt: observation.type === 'GENERATION',
    
    // Has tool if it's a TOOL type
    hasTool: observation.type === 'TOOL',
    
    // Has error if level is ERROR
    hasError: observation.level === 'ERROR',
    
    // Has warning if level is WARNING
    hasWarning: observation.level === 'WARNING',
  };
}

/**
 * Check if state has changed between input and output
 */
function hasStateChanged(input: Record<string, any> | null, output: Record<string, any> | null): boolean {
  // If both null, no change
  if (!input && !output) {
    return false;
  }
  
  // If one is null, there's a change
  if (!input || !output) {
    return true;
  }
  
  // Compare JSON strings (simple but effective for most cases)
  // Note: This might have false positives for objects with different key ordering
  // For production, consider using a proper deep equality check
  try {
    return JSON.stringify(input) !== JSON.stringify(output);
  } catch {
    // If JSON stringification fails, assume there's a change
    return true;
  }
}

/**
 * Get tooltip text for an indicator
 */
export function getIndicatorTooltip(indicator: keyof ObservationIndicators): string {
  const tooltips: Record<keyof ObservationIndicators, string> = {
    hasStateChange: 'State changed during execution',
    hasPrompt: 'Contains LLM prompt and response',
    hasTool: 'Contains tool call and response',
    hasError: 'Error occurred during execution',
    hasWarning: 'Warning during execution',
  };
  
  return tooltips[indicator];
}

