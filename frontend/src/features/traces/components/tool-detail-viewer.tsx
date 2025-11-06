/**
 * Tool Detail Viewer - Shows details for individual TOOL observations
 * 
 * Displays:
 * - Tool name with wrench icon
 * - Parameters used for the call
 * - Success/failure status
 * - Response payload or error message
 */

import { Box, Typography, Paper, Alert, Chip, Stack, Divider } from '@mui/material';
import { 
  Build as WrenchIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import JsonView from '@uiw/react-json-view';

interface ObservationNode {
  id: string;
  type: string;
  name: string | null;
  input: Record<string, any> | null;
  output: Record<string, any> | null;
  level: string;
  status_message: string | null;
}

interface ToolDetailViewerProps {
  observation: ObservationNode;
}

/**
 * Tool detail viewer component
 */
export function ToolDetailViewer({ observation }: ToolDetailViewerProps) {
  const toolInput = observation.input;
  const toolOutput = observation.output;
  
  const toolName = observation.name || toolInput?.tool_name || 'Unknown Tool';
  const parameters = toolInput?.parameters || {};
  const batchKey = toolInput?.batch_key;
  
  const status = toolOutput?.status || 'unknown';
  const isSuccess = status === 'success';
  const result = toolOutput?.result;
  const error = toolOutput?.error;
  
  return (
    <Box>
      {/* Tool Header */}
      <Box sx={{ mb: 3 }}>
        <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
          <WrenchIcon sx={{ fontSize: 32, color: isSuccess ? 'success.main' : 'error.main' }} />
          <Typography variant="h5">
            {toolName}
          </Typography>
          {isSuccess ? (
            <Chip 
              icon={<SuccessIcon />}
              label="Success" 
              color="success"
            />
          ) : (
            <Chip 
              icon={<ErrorIcon />}
              label="Failed" 
              color="error"
            />
          )}
        </Stack>
        
        {batchKey && (
          <Typography variant="caption" color="text.secondary">
            Batch: {batchKey}
          </Typography>
        )}
      </Box>

      <Divider sx={{ my: 2 }} />

      {/* Parameters Section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          📝 Parameters
        </Typography>
        {Object.keys(parameters).length > 0 ? (
          <Paper sx={{ p: 2, bgcolor: 'grey.900' }}>
            <JsonView 
              value={parameters}
              collapsed={false}
              displayDataTypes={false}
              style={{
                background: 'transparent',
                fontSize: '13px',
              }}
            />
          </Paper>
        ) : (
          <Typography variant="body2" color="text.secondary" fontStyle="italic">
            No parameters available
          </Typography>
        )}
      </Box>

      <Divider sx={{ my: 2 }} />

      {/* Result/Error Section */}
      <Box>
        <Typography variant="h6" sx={{ mb: 2 }}>
          {isSuccess ? '✅ Response' : '❌ Error'}
        </Typography>
        
        {isSuccess ? (
          result ? (
            <Paper sx={{ 
              p: 2, 
              bgcolor: '#1a3d2e',  // Dark green background (better contrast)
              border: 1,
              borderColor: 'success.main',
              '& *': { color: '#e0f2e9 !important' }  // Light green text (high contrast)
            }}>
              {typeof result === 'string' ? (
                // Try to parse JSON string
                (() => {
                  try {
                    const parsed = JSON.parse(result);
                    return (
                      <JsonView 
                        value={parsed}
                        collapsed={2}
                        displayDataTypes={false}
                        style={{
                          background: 'transparent',
                          fontSize: '13px',
                        }}
                      />
                    );
                  } catch {
                    // Not JSON, show as text
                    return (
                      <Typography 
                        variant="body2" 
                        component="pre"
                        sx={{ 
                          fontFamily: 'monospace',
                          whiteSpace: 'pre-wrap',
                          maxHeight: '500px',
                          overflow: 'auto',
                          m: 0,
                          color: '#e0f2e9 !important'  // Light green text
                        }}
                      >
                        {result}
                      </Typography>
                    );
                  }
                })()
              ) : (
                <JsonView 
                  value={result}
                  collapsed={2}
                  displayDataTypes={false}
                  style={{
                    background: 'transparent',
                    fontSize: '13px',
                  }}
                />
              )}
            </Paper>
          ) : (
            <Typography variant="body2" color="text.secondary" fontStyle="italic">
              No result data available
            </Typography>
          )
        ) : (
          <Alert severity="error" sx={{ whiteSpace: 'pre-wrap' }}>
            {error || observation.status_message || 'Tool execution failed'}
          </Alert>
        )}
      </Box>

      {/* Tool Key (for debugging) */}
      {toolInput?.tool_key && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="caption" color="text.secondary">
            Tool Key: {toolInput.tool_key}
          </Typography>
        </Box>
      )}
    </Box>
  );
}

