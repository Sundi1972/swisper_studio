/**
 * Timeline Header Component
 * 
 * Displays summary statistics and control buttons for the timeline view.
 */

import { Box, Typography, Chip, Button, ButtonGroup } from '@mui/material';
import {
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon,
  FitScreen as FitScreenIcon,
} from '@mui/icons-material';
import type { TimelineData } from '../types/timeline';

interface TimelineHeaderProps {
  data: TimelineData;
  onZoomIn?: () => void;
  onZoomOut?: () => void;
  onFitScreen?: () => void;
}

export function TimelineHeader({ 
  data, 
  onZoomIn, 
  onZoomOut, 
  onFitScreen 
}: TimelineHeaderProps) {
  // Calculate total cost
  const totalCost = data.nodes.reduce((sum, node) => {
    const nodeCost = node.totalCost ? parseFloat(node.totalCost) : 0;
    return sum + nodeCost;
  }, 0);
  
  // Count errors
  const errorCount = data.nodes.filter(n => n.hasError).length;
  
  // Format duration
  const durationSeconds = (data.totalDuration / 1000).toFixed(2);

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        p: 2,
        borderBottom: 1,
        borderColor: 'divider',
        bgcolor: 'background.paper',
      }}
    >
      {/* Left: Title and Stats */}
      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
        <Typography variant="h6" sx={{ fontWeight: 500 }}>
          Timeline View
        </Typography>
        
        <Chip
          label={`${data.nodeCount} nodes`}
          size="small"
          variant="outlined"
          sx={{ fontFamily: 'monospace' }}
        />
        
        <Chip
          label={`${durationSeconds}s`}
          size="small"
          color="primary"
          sx={{ fontFamily: 'monospace' }}
        />
        
        {totalCost > 0 && (
          <Chip
            label={`CHF ${totalCost.toFixed(4)}`}
            size="small"
            color="secondary"
            sx={{ fontFamily: 'monospace' }}
          />
        )}
        
        {errorCount > 0 && (
          <Chip
            label={`${errorCount} error${errorCount > 1 ? 's' : ''}`}
            size="small"
            color="error"
          />
        )}
      </Box>

      {/* Right: Control Buttons */}
      <ButtonGroup size="small" variant="outlined">
        <Button 
          onClick={onZoomIn}
          startIcon={<ZoomInIcon fontSize="small" />}
        >
          Zoom In
        </Button>
        <Button 
          onClick={onZoomOut}
          startIcon={<ZoomOutIcon fontSize="small" />}
        >
          Zoom Out
        </Button>
        <Button 
          onClick={onFitScreen}
          startIcon={<FitScreenIcon fontSize="small" />}
        >
          Fit
        </Button>
      </ButtonGroup>
    </Box>
  );
}

