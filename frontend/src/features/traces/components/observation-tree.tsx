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
 * Observation tree component.
 * 
 * Displays hierarchical observation structure using MUI TreeView.
 * Shows: type, name, indicators, duration, tokens, cost for each observation.
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
    const userFriendlyType = getUserFriendlyTypeLabel(node.type);

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
            
            {node.prompt_tokens !== null && node.completion_tokens !== null && (
              <Chip
                label={`${node.prompt_tokens + node.completion_tokens}t`}
                size="small"
                variant="outlined"
                sx={{ fontSize: '0.7rem', height: '22px' }}
              />
            )}
            
            {node.calculated_total_cost && (
              <Chip
                label={`$${parseFloat(node.calculated_total_cost).toFixed(4)}`}
                size="small"
                color="success"
                variant="outlined"
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

