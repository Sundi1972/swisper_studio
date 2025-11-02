import { Box, Typography, Paper, Tabs, Tab, CircularProgress, Alert } from '@mui/material';
import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useTraceDetail } from '../hooks/use-trace-detail';
import { ObservationTree } from './observation-tree';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel({ children, value, index }: TabPanelProps) {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

/**
 * Trace detail page with rich observability data.
 * 
 * Phase 2 MVP: Shows observation tree with basic details
 * 
 * Tabs:
 * - Tree View: Hierarchical observation structure (MVP)
 * - Timeline: Chronological sequence (future)
 * - JSON: Raw data view (future)
 */
export function TraceDetailPage() {
  const { traceId } = useParams<{ traceId: string }>();
  const [currentTab, setCurrentTab] = useState(0);
  const { data: trace, isLoading, error } = useTraceDetail(traceId!);

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Failed to load trace: {error instanceof Error ? error.message : 'Unknown error'}
      </Alert>
    );
  }

  if (!trace) {
    return <Alert severity="warning">Trace not found</Alert>;
  }

  return (
    <Box>
      {/* Trace header */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          {trace.trace.name || `Trace ${trace.trace.id.substring(0, 8)}`}
        </Typography>
        
        <Box display="flex" gap={3} sx={{ mt: 2 }}>
          {trace.trace.user_id && (
            <Typography variant="body2" color="text.secondary">
              <strong>User:</strong> {trace.trace.user_id}
            </Typography>
          )}
          {trace.trace.session_id && (
            <Typography variant="body2" color="text.secondary">
              <strong>Session:</strong> {trace.trace.session_id}
            </Typography>
          )}
          <Typography variant="body2" color="text.secondary">
            <strong>Time:</strong> {new Date(trace.trace.timestamp).toLocaleString()}
          </Typography>
          {trace.total_cost && (
            <Typography variant="body2" color="text.secondary">
              <strong>Total Cost:</strong> ${Number(trace.total_cost).toFixed(6)}
            </Typography>
          )}
        </Box>
      </Paper>

      {/* Tabs */}
      <Paper sx={{ mb: 2 }}>
        <Tabs value={currentTab} onChange={(_, newValue) => setCurrentTab(newValue)}>
          <Tab label="Tree View" />
          <Tab label="Timeline" disabled />
          <Tab label="JSON" disabled />
        </Tabs>
      </Paper>

      {/* Tab panels */}
      <TabPanel value={currentTab} index={0}>
        {trace.tree && trace.tree.length > 0 ? (
          <ObservationTree nodes={trace.tree} />
        ) : (
          <Alert severity="info">No observations for this trace yet</Alert>
        )}
      </TabPanel>

      <TabPanel value={currentTab} index={1}>
        <Typography>Timeline view coming soon...</Typography>
      </TabPanel>

      <TabPanel value={currentTab} index={2}>
        <Typography>JSON view coming soon...</Typography>
      </TabPanel>
    </Box>
  );
}

