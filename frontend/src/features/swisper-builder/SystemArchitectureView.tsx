/**
 * System Architecture View (Swisper Builder)
 * Shows all Swisper agent graphs with interactive visualization
 */

import React, { useState } from "react";
import {
  Box,
  Typography,
  List,
  ListItemButton,
  ListItemText,
  Paper,
  CircularProgress,
  Alert,
  AppBar,
  Toolbar,
  Button,
} from "@mui/material";
import { ArrowBack } from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { useSystemArchitecture } from "./hooks/useSystemArchitecture";
import { GraphCanvas } from "@/components/graph";

export const SystemArchitectureView: React.FC = () => {
  const navigate = useNavigate();
  const { data: architecture, isLoading, error } = useSystemArchitecture();
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

  // Loading state
  if (isLoading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "calc(100vh - 200px)",
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  // Error state
  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          Failed to load system architecture: {(error as Error).message}
        </Alert>
      </Box>
    );
  }

  // No data state
  if (!architecture || architecture.agents.length === 0) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="info">No agent definitions found</Alert>
      </Box>
    );
  }

  // Select first agent by default
  const currentAgent =
    architecture.agents.find((a) => a.name === selectedAgent) ||
    architecture.agents[0];

  return (
    <Box>
      {/* Navigation bar */}
      <AppBar position="static" color="default" elevation={1}>
        <Toolbar>
          <Button
            startIcon={<ArrowBack />}
            onClick={() => navigate("/projects")}
            sx={{ mr: 2 }}
          >
            Back to Projects
          </Button>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Swisper Builder
          </Typography>
        </Toolbar>
      </AppBar>

      <Box sx={{ p: 3 }}>
        {/* Page header */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" gutterBottom>
            System Architecture
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Visual architecture of all Swisper agents and their execution flows
          </Typography>
        </Box>

      {/* Main content: Sidebar + Graph */}
      <Box sx={{ display: "flex", gap: 2, height: "calc(100vh - 250px)" }}>
        {/* Sidebar: Agent list */}
        <Paper sx={{ width: 280, flexShrink: 0, overflow: "auto" }}>
          <Box sx={{ p: 2, borderBottom: 1, borderColor: "divider" }}>
            <Typography variant="h6">Agents</Typography>
            <Typography variant="caption" color="textSecondary">
              {architecture.agents.length} total
            </Typography>
          </Box>
          <List>
            {architecture.agents.map((agent) => (
              <ListItemButton
                key={agent.name}
                selected={
                  selectedAgent === agent.name ||
                  (!selectedAgent && agent === architecture.agents[0])
                }
                onClick={() => setSelectedAgent(agent.name)}
              >
                <ListItemText
                  primary={agent.name}
                  secondary={`${agent.nodes.length} nodes`}
                  primaryTypographyProps={{
                    fontWeight:
                      selectedAgent === agent.name ||
                      (!selectedAgent && agent === architecture.agents[0])
                        ? 600
                        : 400,
                  }}
                />
              </ListItemButton>
            ))}
          </List>
        </Paper>

        {/* Main area: Graph visualization */}
        <Paper sx={{ flex: 1, p: 2, overflow: "hidden" }}>
          {/* Graph header */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="h5" gutterBottom>
              {currentAgent.name}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {currentAgent.description}
            </Typography>
            <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: "block" }}>
              {currentAgent.nodes.length} nodes • {currentAgent.edges.length}{" "}
              edges
            </Typography>
            
            {/* Legend */}
            <Box sx={{ mt: 1, display: "flex", gap: 2, flexWrap: "wrap" }}>
              <Typography variant="caption" color="textSecondary">
                <Box component="span" sx={{ color: "#d946ef", fontWeight: 600 }}>●</Box> LLM Call (GENERATION)
              </Typography>
              <Typography variant="caption" color="textSecondary">
                <Box component="span" sx={{ color: "#fb923c", fontWeight: 600 }}>●</Box> Tool
              </Typography>
              <Typography variant="caption" color="textSecondary">
                <Box component="span" sx={{ color: "#60a5fa", fontWeight: 600 }}>●</Box> Processing (SPAN)
              </Typography>
              <Typography variant="caption" color="textSecondary">
                --- Conditional Edge
              </Typography>
            </Box>
          </Box>

          {/* Graph canvas */}
          <Box sx={{ height: "calc(100% - 80px)" }}>
            <GraphCanvas
              graph={{
                nodes: currentAgent.nodes,
                edges: currentAgent.edges,
              }}
              onNodeClick={(nodeId) => {
                console.log("Node clicked:", nodeId);
                // Future: Show node details panel
              }}
            />
          </Box>
        </Paper>
      </Box>
      </Box>
    </Box>
  );
};

