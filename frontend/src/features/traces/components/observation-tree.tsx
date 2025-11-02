import { SimpleTreeView } from '@mui/x-tree-view/SimpleTreeView';
import { TreeItem } from '@mui/x-tree-view/TreeItem';
import { Box, Typography, Chip, Stack } from '@mui/material';

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
  children: ObservationNode[];
}

interface ObservationTreeProps {
  nodes: ObservationNode[];
}

/**
 * Observation tree component.
 * 
 * Displays hierarchical observation structure using MUI TreeView.
 * Shows: type, name, duration, tokens, cost for each observation.
 */
export function ObservationTree({ nodes }: ObservationTreeProps) {
  const renderTree = (node: ObservationNode) => (
    <TreeItem
      key={node.id}
      itemId={node.id}
      label={
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, py: 1 }}>
          {/* Type badge */}
          <Chip
            label={node.type}
            size="small"
            color={getTypeColor(node.type)}
            sx={{ minWidth: 100 }}
          />
          
          {/* Name */}
          <Typography variant="body2" sx={{ flexGrow: 1 }}>
            {node.name || 'Unnamed'}
          </Typography>
          
          {/* Metrics */}
          <Stack direction="row" spacing={1}>
            {node.latency_ms !== null && (
              <Chip
                label={`${node.latency_ms.toFixed(0)}ms`}
                size="small"
                variant="outlined"
              />
            )}
            
            {node.model && (
              <Chip
                label={node.model}
                size="small"
                variant="outlined"
              />
            )}
            
            {node.prompt_tokens !== null && node.completion_tokens !== null && (
              <Chip
                label={`${node.prompt_tokens + node.completion_tokens} tokens`}
                size="small"
                variant="outlined"
              />
            )}
            
            {node.calculated_total_cost && (
              <Chip
                label={`$${parseFloat(node.calculated_total_cost).toFixed(6)}`}
                size="small"
                color="success"
                variant="outlined"
              />
            )}
            
            {node.level === 'ERROR' && (
              <Chip
                label="ERROR"
                size="small"
                color="error"
              />
            )}
          </Stack>
        </Box>
      }
    >
      {node.children.map((child) => renderTree(child))}
    </TreeItem>
  );

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
      {nodes.map((node) => renderTree(node))}
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

