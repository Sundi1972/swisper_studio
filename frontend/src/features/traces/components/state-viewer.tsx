/**
 * State viewer - displays JSON state with syntax highlighting and expand/collapse
 */

import { Box, IconButton, Tooltip } from '@mui/material';
import { ContentCopy as CopyIcon } from '@mui/icons-material';
import JsonView from '@uiw/react-json-view';
import { useState } from 'react';

interface StateViewerProps {
  data: Record<string, any> | null;
  title?: string;
  expanded?: boolean;
}

/**
 * JSON viewer with copy functionality
 */
export function StateViewer({ data, title, expanded = false }: StateViewerProps) {
  const [copySuccess, setCopySuccess] = useState(false);

  const handleCopy = () => {
    if (data) {
      navigator.clipboard.writeText(JSON.stringify(data, null, 2));
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    }
  };

  if (!data || Object.keys(data).length === 0) {
    return (
      <Box sx={{ p: 2, color: 'text.secondary', fontStyle: 'italic' }}>
        No {title?.toLowerCase() || 'data'} available
      </Box>
    );
  }

  return (
    <Box sx={{ position: 'relative' }}>
      {/* Copy button */}
      <Box sx={{ position: 'absolute', top: 8, right: 8, zIndex: 1 }}>
        <Tooltip title={copySuccess ? "Copied!" : "Copy to clipboard"} arrow>
          <IconButton size="small" onClick={handleCopy} sx={{ bgcolor: 'background.paper' }}>
            <CopyIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>

      {/* JSON view */}
      <Box sx={{ 
        p: 2, 
        bgcolor: 'grey.900',
        borderRadius: 1,
        overflow: 'auto',
        maxHeight: '400px',
        '& *': { color: '#ffffff !important' }  // Force white text
      }}>
        <JsonView 
          value={data}
          collapsed={expanded ? false : 2}  // Collapse after 2 levels unless expanded
          displayDataTypes={false}
          enableClipboard={false}
          style={{
            background: 'transparent',
            fontSize: '13px',
          }}
        />
      </Box>
    </Box>
  );
}

