// Reusable vis-network graph visualization component
// Adapted from Langfuse's TraceGraphCanvas.tsx

import React, { useEffect, useRef } from "react";
import { Network, DataSet } from "vis-network/standalone";
import { Box, IconButton, Paper } from "@mui/material";
import { ZoomIn, ZoomOut, RestartAlt } from "@mui/icons-material";
import { GraphData } from "./types";

interface GraphCanvasProps {
  graph: GraphData;
  onNodeClick?: (nodeId: string) => void;
}

// Color scheme from Langfuse (adapted for our observation types)
// GENERATION nodes (LLM calls) use brighter colors for prominence
const NODE_COLORS = {
  AGENT: { border: "#a78bfa", background: "#ede9fe", borderWidth: 2 }, // purple - more vibrant
  TOOL: { border: "#fb923c", background: "#fed7aa", borderWidth: 2 }, // orange - more vibrant
  GENERATION: { border: "#d946ef", background: "#fae8ff", borderWidth: 3 }, // bright magenta - LLM calls stand out!
  SPAN: { border: "#60a5fa", background: "#dbeafe", borderWidth: 2 }, // blue
  RETRIEVER: { border: "#2dd4bf", background: "#ccfbf1", borderWidth: 2 }, // teal
  EVENT: { border: "#34d399", background: "#d1fae5", borderWidth: 2 }, // green
  SYSTEM: { border: "#9ca3af", background: "#f3f4f6", borderWidth: 2 }, // gray
};

function getNodeColor(type: string) {
  return (
    NODE_COLORS[type as keyof typeof NODE_COLORS] || NODE_COLORS.SPAN
  );
}

export const GraphCanvas: React.FC<GraphCanvasProps> = ({
  graph,
  onNodeClick,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const networkRef = useRef<Network | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Convert graph nodes to vis-network format with colors
    const nodesDataSet = new DataSet(
      graph.nodes.map((node) => {
        const colorConfig = getNodeColor(node.type);
        return {
          id: node.id,
          label: node.label,
          color: {
            border: colorConfig.border,
            background: colorConfig.background,
          },
          borderWidth: colorConfig.borderWidth,
        };
      })
    );

    // Convert edges to vis-network format
    // Backend returns edges with "from" and "to" fields (Pydantic aliases)
    // Conditional edges are rendered with dashed lines and labels
    const edges = graph.edges.map((edge) => ({
      from: edge.from,
      to: edge.to,
      dashes: edge.conditional ? [5, 5] : false, // Dashed for conditional
      label: edge.label || undefined, // Show label if present
      font: { size: 11, color: "#64748b", strokeWidth: 0 },
    }));

    // Create vis-network instance with hierarchical layout
    const network = new Network(
      containerRef.current,
      {
        nodes: nodesDataSet,
        edges: edges,
      },
      {
        layout: {
          hierarchical: {
            enabled: true,
            direction: "LR", // Left to right - better for branching
            levelSeparation: 200,
            nodeSpacing: 120,
            sortMethod: "directed",
            shakeTowards: "leaves",
          },
        },
        nodes: {
          shape: "box",
          margin: { top: 10, right: 10, bottom: 10, left: 10 },
          font: { size: 14, color: "#000000", face: "Arial", multi: true },
          widthConstraint: { minimum: 140, maximum: 200 },
        },
        edges: {
          arrows: { to: { enabled: true, scaleFactor: 0.8 } },
          color: { color: "#64748b" },
          smooth: {
            enabled: true,
            type: "cubicBezier",
            roundness: 0.5,
          },
        },
        physics: {
          enabled: false, // Disable physics for stable layout
        },
      }
    );

    // Handle node click events
    if (onNodeClick) {
      network.on("click", (params) => {
        if (params.nodes.length > 0) {
          onNodeClick(params.nodes[0] as string);
        }
      });
    }

    networkRef.current = network;

    // Cleanup on unmount to prevent memory leaks
    return () => {
      network.destroy();
    };
  }, [graph, onNodeClick]);

  const handleZoomIn = () => {
    if (networkRef.current) {
      const scale = networkRef.current.getScale();
      networkRef.current.moveTo({ scale: scale * 1.2 });
    }
  };

  const handleZoomOut = () => {
    if (networkRef.current) {
      const scale = networkRef.current.getScale();
      networkRef.current.moveTo({ scale: scale / 1.2 });
    }
  };

  const handleReset = () => {
    if (networkRef.current) {
      networkRef.current.fit();
    }
  };

  return (
    <Box sx={{ position: "relative", height: "100%", width: "100%" }}>
      {/* Control buttons */}
      <Paper
        elevation={2}
        sx={{
          position: "absolute",
          top: 8,
          right: 8,
          zIndex: 10,
          display: "flex",
          gap: 0.5,
          p: 0.5,
        }}
      >
        <IconButton size="small" onClick={handleZoomIn} title="Zoom In">
          <ZoomIn />
        </IconButton>
        <IconButton size="small" onClick={handleZoomOut} title="Zoom Out">
          <ZoomOut />
        </IconButton>
        <IconButton size="small" onClick={handleReset} title="Reset View">
          <RestartAlt />
        </IconButton>
      </Paper>

      {/* Graph canvas */}
      <div ref={containerRef} style={{ height: "100%", width: "100%" }} />
    </Box>
  );
};

