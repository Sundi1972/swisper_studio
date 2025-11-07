import { Box, Typography, Paper, Tabs, Tab, CircularProgress, Alert } from '@mui/material';
import { useState, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { useTraceDetail } from '../hooks/use-trace-detail';
import { ObservationTree } from './observation-tree';
import { TraceGraphView } from './trace-graph-view';
import { ObservationDetailsPanel } from './observation-details-panel';
import { TimelineView } from './timeline-view';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel({ children, value, index }: TabPanelProps) {
  return (
    <div role="tabpanel" hidden={value !== index} style={{ height: '100%' }}>
      {value === index && <Box sx={{ height: '100%' }}>{children}</Box>}
    </div>
  );
}

/**
 * Trace detail page with rich observability data.
 * 
 * Tabs:
 * - Tree View: Hierarchical observation structure (Phase 2) + Details Panel (Phase 2.5)
 * - Graph View: Visual execution flow (Phase 3)
 * - Timeline: Waterfall/timeline view with D3.js (Phase 5c)
 * - JSON: Raw data view (future)
 */
export function TraceDetailPage() {
  const { traceId } = useParams<{ traceId: string }>();
  const [currentTab, setCurrentTab] = useState(0);
  const [selectedObservationId, setSelectedObservationId] = useState<string | null>(null);
  const { data: trace, isLoading, error } = useTraceDetail(traceId!);

  // Find selected observation from tree (flatten and search)
  const selectedObservation = useMemo(() => {
    if (!selectedObservationId || !trace?.tree) return null;
    
    function findInTree(nodes: any[]): any {
      for (const node of nodes) {
        if (node.id === selectedObservationId) return node;
        if (node.children) {
          const found = findInTree(node.children);
          if (found) return found;
        }
      }
      return null;
    }
    
    return findInTree(trace.tree);
  }, [selectedObservationId, trace?.tree]);

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
    <Box sx={{ width: '100%', height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
      {/* Trace header */}
      <Paper sx={{ p: 2, mb: 1 }}>
        <Typography variant="h6" gutterBottom>
          {trace.trace.name || `Trace ${trace.trace.id.substring(0, 8)}`}
        </Typography>
        
        <Box display="flex" gap={3} sx={{ mt: 1, flexWrap: 'wrap' }}>
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
      <Paper sx={{ mb: 1 }}>
        <Tabs value={currentTab} onChange={(_, newValue) => setCurrentTab(newValue)}>
          <Tab label="Tree View" />
          <Tab label="Graph View" />
          <Tab label="Timeline" />
          <Tab label="JSON" disabled />
        </Tabs>
      </Paper>

      {/* Tab panels */}
      <Box sx={{ flex: 1, minHeight: 0, width: '100%' }}>
        <TabPanel value={currentTab} index={0}>
          {trace.tree && trace.tree.length > 0 ? (
            <PanelGroup direction="horizontal">
              {/* Left: Tree View (resizable) */}
              <Panel defaultSize={40} minSize={25} maxSize={60}>
                <Paper sx={{ p: 2, height: '100%', overflow: 'auto' }}>
                  <ObservationTree 
                    nodes={trace.tree}
                    selectedId={selectedObservationId}
                    onSelect={setSelectedObservationId}
                  />
                </Paper>
              </Panel>
              
              {/* Resize handle */}
              <PanelResizeHandle style={{
                width: '8px',
                background: 'transparent',
                cursor: 'col-resize',
                borderLeft: '1px solid #444',
                borderRight: '1px solid #444',
              }} />
              
              {/* Right: Details Panel (resizable) */}
              <Panel defaultSize={60} minSize={40}>
                <ObservationDetailsPanel observation={selectedObservation} />
              </Panel>
            </PanelGroup>
          ) : (
            <Alert severity="info">No observations for this trace yet</Alert>
          )}
        </TabPanel>

        <TabPanel value={currentTab} index={1}>
          <TraceGraphView traceId={traceId!} />
        </TabPanel>

        <TabPanel value={currentTab} index={2}>
          {trace.tree && trace.tree.length > 0 ? (
            <TimelineView observations={trace.tree} />
          ) : (
            <Alert severity="info">No observations for this trace yet</Alert>
          )}
        </TabPanel>

        <TabPanel value={currentTab} index={3}>
          <Typography>JSON view coming soon...</Typography>
        </TabPanel>
      </Box>
    </Box>
  );
}

