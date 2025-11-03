/**
 * Tool call viewer - displays tool/function call arguments
 */

import { Box, Typography, IconButton, Tooltip, Paper } from '@mui/material';
import { ContentCopy as CopyIcon } from '@mui/icons-material';
import JsonView from '@uiw/react-json-view';
import { useState } from 'react';

interface ToolCallViewerProps {
  input: Record<string, any> | null;
  name: string | null;
}

/**
 * Extract tool call from input
 */
function extractToolCall(input: any): { function?: string; arguments?: any } | null {
  if (!input) return null;

  // Direct tool_call object
  if (input.tool_call) {
    return input.tool_call;
  }

  // Arguments directly
  if (input.arguments || input.args) {
    return { arguments: input.arguments || input.args };
  }

  // Entire input might be the arguments
  return { arguments: input };
}

/**
 * Tool call viewer component
 */
export function ToolCallViewer({ input, name }: ToolCallViewerProps) {
  const [copySuccess, setCopySuccess] = useState(false);
  const toolCall = extractToolCall(input);

  const handleCopy = () => {
    if (toolCall) {
      const text = JSON.stringify(toolCall, null, 2);
      navigator.clipboard.writeText(text);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    }
  };

  if (!toolCall) {
    return (
      <Box sx={{ p: 2, color: 'text.secondary', fontStyle: 'italic' }}>
        No tool call data available
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Typography variant="subtitle2">Tool Call</Typography>
        <Tooltip title={copySuccess ? "Copied!" : "Copy arguments"} arrow>
          <IconButton size="small" onClick={handleCopy}>
            <CopyIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Function name */}
      {(toolCall.function || name) && (
        <Paper sx={{ p: 1.5, mb: 1, bgcolor: 'grey.900' }}>
          <Typography variant="caption" sx={{ color: 'success.main', fontWeight: 'bold' }}>
            FUNCTION:
          </Typography>
          <Typography variant="body1" sx={{ mt: 0.5, fontFamily: 'monospace' }}>
            {toolCall.function || name}
          </Typography>
        </Paper>
      )}

      {/* Arguments */}
      {toolCall.arguments && (
        <Box>
          <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block', mb: 0.5 }}>
            ARGUMENTS:
          </Typography>
          <Paper sx={{ 
            p: 2, 
            bgcolor: 'grey.900', 
            overflow: 'auto', 
            maxHeight: '300px',
            '& *': { color: '#ffffff !important' }
          }}>
            <JsonView 
              value={toolCall.arguments}
              collapsed={2}
              displayDataTypes={false}
              enableClipboard={false}
              style={{
                background: 'transparent',
                fontSize: '13px',
              }}
            />
          </Paper>
        </Box>
      )}
    </Box>
  );
}

