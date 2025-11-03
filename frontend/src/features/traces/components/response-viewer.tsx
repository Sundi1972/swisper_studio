/**
 * Response viewer - displays LLM responses
 */

import { Box, Typography, IconButton, Tooltip, Paper } from '@mui/material';
import { ContentCopy as CopyIcon } from '@mui/icons-material';
import JsonView from '@uiw/react-json-view';
import { useState } from 'react';

interface ResponseViewerProps {
  output: Record<string, any> | null;
}

/**
 * Response viewer component
 */
export function ResponseViewer({ output }: ResponseViewerProps) {
  const [copySuccess, setCopySuccess] = useState(false);

  const handleCopy = () => {
    if (output) {
      const text = JSON.stringify(output, null, 2);
      navigator.clipboard.writeText(text);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    }
  };

  if (!output || Object.keys(output).length === 0) {
    return (
      <Box sx={{ p: 2, color: 'text.secondary', fontStyle: 'italic' }}>
        No response data available
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Typography variant="subtitle2">LLM Response</Typography>
        <Tooltip title={copySuccess ? "Copied!" : "Copy response"} arrow>
          <IconButton size="small" onClick={handleCopy}>
            <CopyIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>

      <Paper sx={{ 
        p: 2, 
        bgcolor: 'grey.900', 
        overflow: 'auto', 
        maxHeight: '400px',
        '& *': { color: '#ffffff !important' }
      }}>
        <JsonView 
          value={output}
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
  );
}

