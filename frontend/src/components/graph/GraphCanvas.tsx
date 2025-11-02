// Reusable vis-network graph visualization component
// Adapted from Langfuse's TraceGraphCanvas.tsx

import React, { useEffect, useRef, useCallback, useState } from "react";
import { Network, DataSet } from "vis-network/standalone";
import { Box, IconButton, Paper, Tooltip } from "@mui/material";
import { ZoomIn, ZoomOut, RestartAlt, AccountTree } from "@mui/icons-material";
import { GraphData } from "./types";

interface GraphCanvasProps {
  graph: GraphData;
  onNodeClick?: (nodeId: string) => void;
  persistenceKey?: string; // Optional key for persisting layout in localStorage
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
  persistenceKey,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const networkRef = useRef<Network | null>(null);
  const [resetKey, setResetKey] = useState(0); // Force re-mount on reset

  // Load saved positions from localStorage
  const loadSavedPositions = useCallback(() => {
    if (!persistenceKey) return null;
    try {
      const saved = localStorage.getItem(`graph-layout-${persistenceKey}`);
      return saved ? JSON.parse(saved) : null;
    } catch (e) {
      console.warn("Failed to load saved graph positions:", e);
      return null;
    }
  }, [persistenceKey]);

  // Save positions to localStorage
  const savePositions = useCallback(() => {
    if (!persistenceKey || !networkRef.current) return;
    try {
      const positions = networkRef.current.getPositions();
      localStorage.setItem(
        `graph-layout-${persistenceKey}`,
        JSON.stringify(positions)
      );
    } catch (e) {
      console.warn("Failed to save graph positions:", e);
    }
  }, [persistenceKey]);

  useEffect(() => {
    if (!containerRef.current) return;

    const savedPositions = loadSavedPositions();

    // Convert graph nodes to vis-network format with colors and saved positions
    const nodesDataSet = new DataSet(
      graph.nodes.map((node) => {
        const colorConfig = getNodeColor(node.type);
        const savedPos = savedPositions?.[node.id];
        return {
          id: node.id,
          label: node.label,
          color: {
            border: colorConfig.border,
            background: colorConfig.background,
          },
          borderWidth: colorConfig.borderWidth,
          ...(savedPos && { x: savedPos.x, y: savedPos.y }), // Restore saved position
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
          // Force-directed layout - better for complex graphs with cycles
          randomSeed: 42, // Consistent initial layout
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
            type: "dynamic",
            roundness: 0.5,
          },
        },
        physics: {
          enabled: !savedPositions, // Enable physics only if no saved positions
          stabilization: {
            enabled: true,
            iterations: 200,
            updateInterval: 25,
          },
          barnesHut: {
            gravitationalConstant: -4000,
            centralGravity: 0.3,
            springLength: 150,
            springConstant: 0.04,
            damping: 0.09,
            avoidOverlap: 0.5,
          },
        },
        interaction: {
          dragNodes: true, // Enable node dragging
          dragView: true, // Enable canvas panning
          zoomView: true,
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

    // Save positions after dragging
    network.on("dragEnd", () => {
      savePositions();
    });

    // Disable physics after stabilization to allow manual positioning
    network.on("stabilizationIterationsDone", () => {
      network.setOptions({ physics: { enabled: false } });
      if (!savedPositions) {
        // Save initial layout
        savePositions();
      }
    });

    networkRef.current = network;

    // Cleanup on unmount to prevent memory leaks
    return () => {
      network.destroy();
    };
  }, [graph, onNodeClick, loadSavedPositions, savePositions, resetKey]);

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

  const handleRedrawConnections = () => {
    if (!networkRef.current) return;

    // Get current node positions
    const positions = networkRef.current.getPositions();
    const nodeIds = Object.keys(positions);

    // Update nodes to be fixed at current positions
    const network = networkRef.current as any; // Access internal API
    nodeIds.forEach((nodeId) => {
      if (network.body?.nodes[nodeId]) {
        network.body.nodes[nodeId].setOptions({
          fixed: { x: true, y: true },
        });
      }
    });

    // Enable physics briefly to optimize edge routing
    networkRef.current.setOptions({
      physics: {
        enabled: true,
        stabilization: {
          enabled: true,
          iterations: 100,
          updateInterval: 10,
        },
      },
    });

    // Function to unfix nodes after optimization
    const unfixNodes = () => {
      if (!networkRef.current) return;
      const net = networkRef.current as any;

      // Disable physics
      networkRef.current.setOptions({ physics: { enabled: false } });

      // Unfix all nodes so they're draggable again
      nodeIds.forEach((nodeId) => {
        if (net.body?.nodes[nodeId]) {
          net.body.nodes[nodeId].setOptions({
            fixed: { x: false, y: false },
          });
        }
      });

      // Save the positions (node positions unchanged, but edges optimized)
      savePositions();
    };

    // Try event-based first
    networkRef.current.once("stabilizationIterationsDone", unfixNodes);

    // Fallback timeout to ensure nodes get unfixed (in case event doesn't fire)
    setTimeout(() => {
      unfixNodes();
    }, 2000); // 2 seconds should be enough for 100 iterations
  };

  const handleReset = () => {
    if (persistenceKey) {
      // Clear saved positions from localStorage
      localStorage.removeItem(`graph-layout-${persistenceKey}`);
      // Force component re-mount to generate fresh layout
      setResetKey((prev) => prev + 1);
    } else {
      // No persistence - just fit to view
      if (networkRef.current) {
        networkRef.current.fit();
      }
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
        <Tooltip title="Zoom In">
          <IconButton size="small" onClick={handleZoomIn}>
            <ZoomIn />
          </IconButton>
        </Tooltip>
        <Tooltip title="Zoom Out">
          <IconButton size="small" onClick={handleZoomOut}>
            <ZoomOut />
          </IconButton>
        </Tooltip>
        <Tooltip title="Redraw Connections - Optimize edge curves while keeping node positions">
          <IconButton size="small" onClick={handleRedrawConnections}>
            <AccountTree />
          </IconButton>
        </Tooltip>
        <Tooltip title="Reset Layout - Clear saved positions and generate fresh layout">
          <IconButton size="small" onClick={handleReset}>
            <RestartAlt />
          </IconButton>
        </Tooltip>
      </Paper>

      {/* Graph canvas */}
      <div ref={containerRef} style={{ height: "100%", width: "100%" }} />
    </Box>
  );
};

