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
 * Extract LLM response from output (SDK v0.3.0 format)
 */
function extractLLMResponse(output: any): any {
  if (!output) return null;
  
  // SDK v0.3.0: Check _llm_result first
  if (output._llm_result) {
    return output._llm_result;
  }
  
  // Fallback: show whole output (filter out internal fields)
  if (typeof output === 'object' && !Array.isArray(output)) {
    const filtered: any = {};
    for (const key in output) {
      if (!key.startsWith('_')) {
        filtered[key] = output[key];
      }
    }
    return Object.keys(filtered).length > 0 ? filtered : output;
  }
  
  return output;
}

/**
 * Response viewer component
 */
export function ResponseViewer({ output }: ResponseViewerProps) {
  const [copySuccess, setCopySuccess] = useState(false);
  
  // Extract LLM result (might be in _llm_result for SDK v0.3.0)
  const response = extractLLMResponse(output);

  const handleCopy = () => {
    if (response) {
      const text = JSON.stringify(response, null, 2);
      navigator.clipboard.writeText(text);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    }
  };

  if (!response || (typeof response === 'object' && Object.keys(response).length === 0)) {
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
          value={response}
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

