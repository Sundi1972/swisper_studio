import { SimpleTreeView } from '@mui/x-tree-view/SimpleTreeView';
import { TreeItem } from '@mui/x-tree-view/TreeItem';
import { Box, Typography, Chip, Stack } from '@mui/material';
import { Build as WrenchIcon } from '@mui/icons-material';
import { getObservationIndicators, getIndicatorTooltip } from '../utils/observation-indicators';
import {
  PromptIndicator,
  ToolIndicator,
  ErrorIndicator,
  WarningIndicator,
} from '../../../components/icons/observation-icons';

interface ObservationNode {
  id: string;
  type: string;
  name: string | null;
  latency_ms: number | null;
  model: string | null;
  prompt_tokens: number | null;
  completion_tokens: number | null;
  calculated_total_cost: string | null;
  level: string;
  status_message: string | null;
  input: Record<string, any> | null;
  output: Record<string, any> | null;
  children: ObservationNode[];
}

interface ObservationTreeProps {
  nodes: ObservationNode[];
  selectedId?: string | null;
  onSelect?: (id: string) => void;
}

/**
 * Map technical type to user-friendly label
 */
function getUserFriendlyTypeLabel(type: string): string {
  switch (type) {
    case 'GENERATION':
      return 'LLM';      // User-friendly: LLM call
    case 'SPAN':
      return 'PROC';     // User-friendly: Processing
    case 'TOOL':
      return 'Tool';     // Keep as-is
    case 'AGENT':
      return 'AGENT';    // Keep as-is
    default:
      return type;
  }
}

/**
 * Calculate aggregated metrics (tokens, costs) from node and all descendants
 */
function calculateAggregatedMetrics(node: ObservationNode): {
  totalTokens: number;
  totalCost: number;
  promptTokens: number;
  completionTokens: number;
} {
  let totalTokens = node.total_tokens || 0;
  let promptTokens = node.prompt_tokens || 0;
  let completionTokens = node.completion_tokens || 0;
  let totalCost = node.calculated_total_cost ? parseFloat(String(node.calculated_total_cost)) : 0;
  
  // Recursively add children
  if (node.children && node.children.length > 0) {
    for (const child of node.children) {
      const childMetrics = calculateAggregatedMetrics(child);
      totalTokens += childMetrics.totalTokens;
      promptTokens += childMetrics.promptTokens;
      completionTokens += childMetrics.completionTokens;
      totalCost += childMetrics.totalCost;
    }
  }
  
  return { totalTokens, totalCost, promptTokens, completionTokens };
}

/**
 * Observation tree component.
 * 
 * Displays hierarchical observation structure using MUI TreeView.
 * Shows: type, name, indicators, duration, tokens, cost for each observation.
 * For parent nodes (AGENT), shows aggregated tokens/costs from all children.
 */
export function ObservationTree({ nodes, selectedId, onSelect }: ObservationTreeProps) {
  const renderTree = (node: ObservationNode, depth: number = 0) => {
    // Get indicators for this observation (includes child aggregation)
    const indicators = getObservationIndicators({
      type: node.type,
      level: node.level,
      input: node.input,
      output: node.output,
      children: node.children,  // Pass children for aggregation
    });

    const isSelected = selectedId === node.id;
    const isTool = node.type === 'TOOL';
    const isAgent = node.type === 'AGENT';
    const userFriendlyType = getUserFriendlyTypeLabel(node.type);
    
    // For AGENT nodes, show aggregated metrics from all children
    const metrics = isAgent ? calculateAggregatedMetrics(node) : {
      totalTokens: node.total_tokens || 0,
      totalCost: node.calculated_total_cost ? parseFloat(String(node.calculated_total_cost)) : 0,
      promptTokens: node.prompt_tokens || 0,
      completionTokens: node.completion_tokens || 0,
    };

    return (
      <TreeItem
        key={node.id}
        itemId={node.id}
        label={
          <Box 
            onClick={(e) => {
              e.stopPropagation();
              onSelect?.(node.id);
            }}
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 1, 
              py: 1,
              backgroundColor: isSelected ? 'action.selected' : 'transparent',
              borderRadius: 1,
              px: 1,
              paddingLeft: depth > 0 ? `${depth * 24}px` : '8px',  // Indent children
              cursor: 'pointer',
              '&:hover': {
                backgroundColor: isSelected ? 'action.selected' : 'action.hover',
              }
            }}
          >
            {/* Tool icon for TOOL type */}
            {isTool && (
              <WrenchIcon sx={{ fontSize: 18, color: 'success.main' }} />
            )}
            
            {/* Type badge - user-friendly labels */}
            <Chip
              label={userFriendlyType}
              size="small"
              color={getTypeColor(node.type)}
              sx={{ 
                minWidth: 60,
                fontSize: '0.7rem',
                height: '22px',
              }}
            />
            
            {/* Name */}
            <Typography variant="body2" sx={{ flexGrow: 1 }}>
              {node.name || 'Unnamed'}
            </Typography>
            
            {/* Indicators - prominent state change indicator */}
            <Stack direction="row" spacing={0.5} sx={{ mr: 1 }}>
              {indicators.hasStateChange && (
                <Chip 
                  label="STATE CHANGED"
                  size="small"
                  color="info"
                  variant="outlined"
                  sx={{ fontSize: '0.65rem', height: '20px', fontWeight: 'bold' }}
                />
              )}
              {indicators.hasPrompt && (
                <PromptIndicator tooltip={getIndicatorTooltip('hasPrompt')} />
              )}
              {indicators.hasTool && (
                <ToolIndicator tooltip={getIndicatorTooltip('hasTool')} />
              )}
              {indicators.hasError && (
                <ErrorIndicator tooltip={getIndicatorTooltip('hasError')} />
              )}
              {indicators.hasWarning && (
                <WarningIndicator tooltip={getIndicatorTooltip('hasWarning')} />
              )}
            </Stack>
            
            {/* Metrics */}
            <Stack direction="row" spacing={1}>
            {node.latency_ms !== null && (
              <Chip
                label={`${node.latency_ms.toFixed(0)}ms`}
                size="small"
                variant="outlined"
                sx={{ fontSize: '0.7rem', height: '22px' }}
              />
            )}
            
            {node.model && (
              <Chip
                label={node.model}
                size="small"
                variant="outlined"
                sx={{ fontSize: '0.7rem', height: '22px' }}
              />
            )}
            
            {/* Tokens (aggregated for AGENT nodes) */}
            {metrics.totalTokens > 0 && (
              <Chip
                label={`🎫 ${metrics.totalTokens.toLocaleString()} (${metrics.promptTokens.toLocaleString()}↑ ${metrics.completionTokens.toLocaleString()}↓)`}
                size="small"
                variant="outlined"
                title={isAgent ? 
                  `Total tokens (this agent + all children): ${metrics.totalTokens.toLocaleString()}` :
                  `Input: ${metrics.promptTokens} tokens, Output: ${metrics.completionTokens} tokens`
                }
                sx={{ fontSize: '0.7rem', height: '22px' }}
              />
            )}
            
            {/* Costs (aggregated for AGENT nodes) */}
            {metrics.totalCost > 0 && (
              <Chip
                label={`💰 CHF ${metrics.totalCost.toFixed(4)}`}
                size="small"
                color="warning"
                variant="outlined"
                title={isAgent ?
                  `Total cost (this agent + all children): CHF ${metrics.totalCost.toFixed(6)}` :
                  `Cost for this LLM call`
                }
                sx={{ fontSize: '0.7rem', height: '22px' }}
              />
            )}
            
            {node.level === 'ERROR' && (
              <Chip
                label="ERROR"
                size="small"
                color="error"
                sx={{ fontSize: '0.7rem', height: '22px' }}
              />
            )}
          </Stack>
        </Box>
      }
    >
        {/* Recursively render children with increased depth */}
        {node.children.map(child => renderTree(child, depth + 1))}
      </TreeItem>
    );
  };

  return (
    <SimpleTreeView
      defaultExpandedItems={nodes.map(n => n.id)} // Expand all by default
      sx={{
        flexGrow: 1,
        overflowY: 'auto',
        '& .MuiTreeItem-content': {
          padding: 1,
          borderRadius: 1,
          '&:hover': {
            backgroundColor: 'action.hover',
          },
        },
      }}
    >
      {nodes.map((node) => renderTree(node, 0))}
    </SimpleTreeView>
  );
}

function getTypeColor(type: string): 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'error' {
  switch (type) {
    case 'GENERATION':
      return 'primary';
    case 'TOOL':
      return 'success';
    case 'AGENT':
      return 'secondary';
    case 'SPAN':
      return 'default';
    default:
      return 'default';
  }
}

