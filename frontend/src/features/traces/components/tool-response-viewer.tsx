/**
 * Tool response viewer - displays tool/function results
 * 
 * Extracts tool-specific data from state output (tool_results, tool_calls, etc.)
 */

import { Box, Typography, IconButton, Tooltip, Paper, Alert, Chip } from '@mui/material';
import { ContentCopy as CopyIcon, Build as ToolIcon } from '@mui/icons-material';
import JsonView from '@uiw/react-json-view';
import { useState } from 'react';

interface ToolResponseViewerProps {
  output: Record<string, any> | null;
}

/**
 * Extract tool-specific data from observation output
 * Handles multiple formats (Swisper, LangChain, etc.)
 */
function extractToolData(output: any): any {
  if (!output) return null;
  
  // Priority 1: tool_results (Swisper productivity agent format)
  if (output.tool_results && Object.keys(output.tool_results).length > 0) {
    return {
      format: 'Swisper Productivity Agent',
      data: output.tool_results,
      metadata: {
        operation_type: output.operation_type,
        resource_type: output.resource_type,
        provider: output.selected_provider_name,
        email: output.selected_provider_email,
      }
    };
  }
  
  // Priority 2: tool_calls (LangChain format)
  if (output.tool_calls) {
    return {
      format: 'LangChain Tool Calls',
      data: output.tool_calls,
      metadata: {}
    };
  }
  
  // Priority 3: tool_operations (alternative format)
  if (output.tool_operations) {
    return {
      format: 'Tool Operations',
      data: output.tool_operations,
      metadata: {}
    };
  }
  
  // Priority 4: Check for tool-like keys in output
  const toolKeys = Object.keys(output).filter(key => 
    key.toLowerCase().includes('tool') || 
    key.toLowerCase().includes('function') ||
    key.toLowerCase().includes('action')
  );
  
  if (toolKeys.length > 0) {
    const toolData: Record<string, any> = {};
    toolKeys.forEach(key => {
      toolData[key] = output[key];
    });
    return {
      format: 'Generic Tool Data',
      data: toolData,
      metadata: {}
    };
  }
  
  return null;
}

/**
 * Tool response viewer component
 */
export function ToolResponseViewer({ output }: ToolResponseViewerProps) {
  const [copySuccess, setCopySuccess] = useState(false);
  const toolInfo = extractToolData(output);

  const handleCopy = () => {
    if (toolInfo) {
      const text = JSON.stringify(toolInfo.data, null, 2);
      navigator.clipboard.writeText(text);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    }
  };

  if (!toolInfo) {
    return (
      <Box sx={{ p: 2, color: 'text.secondary', fontStyle: 'italic' }}>
        No tool execution data available
      </Box>
    );
  }

  // Calculate data size
  const dataString = JSON.stringify(toolInfo.data);
  const sizeKB = (dataString.length / 1024).toFixed(1);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <ToolIcon sx={{ color: 'success.main' }} />
          <Typography variant="subtitle2">Tool Execution Results</Typography>
          <Chip label={toolInfo.format} size="small" variant="outlined" />
          <Chip label={`${sizeKB} KB`} size="small" color="info" variant="outlined" />
        </Box>
        <Tooltip title={copySuccess ? "Copied!" : "Copy tool data"} arrow>
          <IconButton size="small" onClick={handleCopy}>
            <CopyIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Metadata (if available) */}
      {toolInfo.metadata && Object.keys(toolInfo.metadata).length > 0 && (
        <Alert severity="info" sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            {Object.entries(toolInfo.metadata).map(([key, value]) => 
              value && (
                <Typography key={key} variant="caption">
                  <strong>{key}:</strong> {String(value)}
                </Typography>
              )
            )}
          </Box>
        </Alert>
      )}

      {/* Tool data */}
      <Paper sx={{ 
        p: 2, 
        bgcolor: 'grey.900', 
        overflow: 'auto', 
        maxHeight: '600px',
        '& *': { color: '#ffffff !important' }
      }}>
        <JsonView 
          value={toolInfo.data}
          collapsed={2}
          displayDataTypes={false}
          enableClipboard={false}
          style={{
            background: 'transparent',
            fontSize: '13px',
          }}
        />
      </Paper>
      
      {/* Size warning for large outputs */}
      {dataString.length > 50000 && (
        <Alert severity="warning" sx={{ mt: 2 }}>
          Large tool output ({sizeKB} KB). Consider using filters or pagination for better performance.
        </Alert>
      )}
    </Box>
  );
}

