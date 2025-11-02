/**
 * Trace Graph View
 * Displays execution flow of a single trace as an interactive graph
 */

import React from "react";
import { Box, Typography, CircularProgress, Alert } from "@mui/material";
import { useTraceGraph } from "../hooks/use-trace-graph";
import { GraphCanvas } from "@/components/graph";

interface TraceGraphViewProps {
  traceId: string;
}

export const TraceGraphView: React.FC<TraceGraphViewProps> = ({ traceId }) => {
  const { data: graph, isLoading, error } = useTraceGraph(traceId);

  // Loading state
  if (isLoading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: 400,
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  // Error state
  if (error) {
    return (
      <Alert severity="error">
        Failed to load graph: {(error as Error).message}
      </Alert>
    );
  }

  // No data state
  if (!graph || graph.nodes.length === 0) {
    return (
      <Alert severity="info">
        No graph data available for this trace. The trace may not have any
        observations yet.
      </Alert>
    );
  }

  return (
    <Box>
      {/* Graph info */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" color="textSecondary">
          {graph.nodes.length} nodes • {graph.edges.length} edges
        </Typography>
        <Typography variant="caption" color="textSecondary" sx={{ display: "block", mt: 0.5 }}>
          💡 Tip: Drag nodes to rearrange the layout. Your layout will be saved automatically.
        </Typography>
      </Box>

      {/* Graph visualization */}
      <Box sx={{ height: 600, border: 1, borderColor: "divider", borderRadius: 1 }}>
        <GraphCanvas
          graph={graph}
          persistenceKey={`trace-${traceId}`}
          onNodeClick={(nodeId) => {
            console.log("Node clicked:", nodeId);
            // Future: Show observation details when node clicked
            // Could scroll to observation in tree view or show details panel
          }}
        />
      </Box>
    </Box>
  );
};

