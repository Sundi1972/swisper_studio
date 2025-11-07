/**
 * Timeline View Component
 * 
 * Main container for timeline/waterfall visualization.
 * Combines header, canvas, and details panel.
 */

import { useState, useRef } from 'react';
import { Box, Dialog, DialogContent, DialogTitle, IconButton } from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import type { ObservationNode } from '../hooks/use-trace-detail';
import { transformToTimeline, toggleNodeExpansion } from '../utils/transform-to-timeline';
import { TimelineHeader } from './timeline-header';
import { TimelineCanvas, type TimelineCanvasRef } from './timeline-canvas';
import { ObservationDetailsPanel } from './observation-details-panel';
import type { TimelineNode } from '../types/timeline';

interface TimelineViewProps {
  observations: ObservationNode[];
}

export function TimelineView({ observations }: TimelineViewProps) {
  const canvasRef = useRef<TimelineCanvasRef>(null);
  const [selectedNode, setSelectedNode] = useState<TimelineNode | null>(null);
  const [timelineData, setTimelineData] = useState(() => transformToTimeline(observations));

  // Handle node selection
  const handleNodeClick = (node: TimelineNode) => {
    setSelectedNode(node);
  };

  // Handle expand/collapse
  const handleToggleExpand = (nodeId: string) => {
    const updatedData = toggleNodeExpansion(timelineData, nodeId);
    setTimelineData(updatedData);
  };

  // Zoom controls (call canvas methods via ref)
  const handleZoomIn = () => {
    canvasRef.current?.zoomIn();
  };

  const handleZoomOut = () => {
    canvasRef.current?.zoomOut();
  };

  const handleFitScreen = () => {
    canvasRef.current?.fitToScreen();
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        width: '100%',
        overflow: 'hidden',
      }}
    >
      {/* Header with stats and controls */}
      <TimelineHeader
        data={timelineData}
        onZoomIn={handleZoomIn}
        onZoomOut={handleZoomOut}
        onFitScreen={handleFitScreen}
      />

      {/* Timeline canvas - takes full height */}
      <Box 
        sx={{ 
          flexGrow: 1,
          overflow: 'auto', // Enable scrollbars when zoomed in
          position: 'relative',
        }}
      >
        <TimelineCanvas
          ref={canvasRef}
          data={timelineData}
          onNodeClick={handleNodeClick}
          onToggleExpand={handleToggleExpand}
          selectedNodeId={selectedNode?.id}
        />
      </Box>

      {/* Details Modal - large overlay */}
      <Dialog
        open={!!selectedNode}
        onClose={() => setSelectedNode(null)}
        maxWidth="xl"
        fullWidth
        PaperProps={{
          sx: {
            height: '90vh',
            maxHeight: '90vh',
          },
        }}
      >
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          {selectedNode?.name || 'Observation Details'}
          <IconButton
            onClick={() => setSelectedNode(null)}
            size="small"
            sx={{
              color: 'text.secondary',
            }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent sx={{ p: 0, overflow: 'auto' }}>
          {selectedNode && (
            <Box sx={{ p: 2 }}>
              <ObservationDetailsPanel observation={selectedNode.observation} />
            </Box>
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
}

