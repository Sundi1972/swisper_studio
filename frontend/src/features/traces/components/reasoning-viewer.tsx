/**
 * Reasoning viewer - displays LLM reasoning process (<think>...</think> tags)
 * 
 * Shows the thinking process/chain-of-thought from models like DeepSeek R1, o1, etc.
 */

import { Box, Typography, IconButton, Tooltip, Paper, Alert, Stack, Chip } from '@mui/material';
import { ContentCopy as CopyIcon, Psychology as ReasoningIcon } from '@mui/icons-material';
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ReasoningViewerProps {
  output: Record<string, any> | null;
}

/**
 * Extract reasoning from observation output
 * SDK v0.4.0 stores reasoning in output._llm_reasoning
 */
function extractReasoning(output: any): string | null {
  if (!output) return null;
  
  // SDK v0.4.0 format
  if (output._llm_reasoning && typeof output._llm_reasoning === 'string') {
    return output._llm_reasoning;
  }
  
  return null;
}

/**
 * Check if reasoning was truncated
 */
function isTruncated(reasoning: string): boolean {
  return reasoning.includes('[Truncated. Full length:');
}

/**
 * Extract truncation info
 */
function getTruncationInfo(reasoning: string): { shown: number; total: number } | null {
  const match = reasoning.match(/\[Truncated\. Full length: ([\d,]+) characters\]/);
  if (match) {
    const total = parseInt(match[1].replace(/,/g, ''));
    const shown = reasoning.length - match[0].length - 4; // Subtract truncation message and newlines
    return { shown, total };
  }
  return null;
}

/**
 * Reasoning viewer component
 */
export function ReasoningViewer({ output }: ReasoningViewerProps) {
  const [copySuccess, setCopySuccess] = useState(false);
  const reasoning = extractReasoning(output);

  const handleCopy = () => {
    if (reasoning) {
      navigator.clipboard.writeText(reasoning);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    }
  };

  if (!reasoning) {
    return (
      <Box sx={{ p: 2, color: 'text.secondary', fontStyle: 'italic' }}>
        No reasoning data available (model did not use &lt;think&gt; tags)
      </Box>
    );
  }

  const truncationInfo = getTruncationInfo(reasoning);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Stack direction="row" spacing={1} alignItems="center">
          <ReasoningIcon sx={{ color: 'warning.main' }} />
          <Typography variant="subtitle2">LLM Thinking Process</Typography>
          {truncationInfo && (
            <Chip 
              label={`${truncationInfo.shown.toLocaleString()} / ${truncationInfo.total.toLocaleString()} chars`}
              size="small"
              color="warning"
              variant="outlined"
            />
          )}
        </Stack>
        <Tooltip title={copySuccess ? "Copied!" : "Copy reasoning"} arrow>
          <IconButton size="small" onClick={handleCopy}>
            <CopyIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Truncation warning */}
      {truncationInfo && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          Reasoning was truncated at {truncationInfo.shown.toLocaleString()} characters.
          Full reasoning is {truncationInfo.total.toLocaleString()} characters.
        </Alert>
      )}

      {/* Reasoning content */}
      <Paper 
        sx={{ 
          p: 2, 
          bgcolor: 'warning.dark', 
          color: 'warning.contrastText',
          border: 1,
          borderColor: 'warning.main'
        }}
      >
        <Typography 
          variant="caption" 
          sx={{ 
            color: 'warning.light', 
            fontWeight: 'bold', 
            mb: 1, 
            display: 'block',
            textTransform: 'uppercase'
          }}
        >
          🧠 Thinking Process:
        </Typography>
        <Box sx={{ 
          '& p': { mb: 1 }, 
          '& h1, & h2, & h3': { color: 'warning.light', mb: 1, mt: 2 },
          '& code': { bgcolor: 'rgba(0,0,0,0.3)', p: 0.5, borderRadius: 1 },
          '& pre': { bgcolor: 'rgba(0,0,0,0.3)', p: 1, borderRadius: 1, overflow: 'auto' },
          '& ul, & ol': { pl: 2 },
          fontStyle: 'italic',
        }}>
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {reasoning}
          </ReactMarkdown>
        </Box>
      </Paper>

      {/* Character count info */}
      <Typography variant="caption" sx={{ color: 'text.secondary', mt: 1, display: 'block' }}>
        {reasoning.length.toLocaleString()} characters
      </Typography>
    </Box>
  );
}

