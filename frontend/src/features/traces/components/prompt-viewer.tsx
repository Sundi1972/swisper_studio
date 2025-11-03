/**
 * Prompt viewer - displays LLM prompts in a readable format with markdown support
 */

import { Box, Typography, IconButton, Tooltip, Paper } from '@mui/material';
import { ContentCopy as CopyIcon } from '@mui/icons-material';
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface PromptViewerProps {
  input: Record<string, any> | null;
}

/**
 * Extract prompt from input (handles different formats)
 */
function extractPrompt(input: any): { system?: string; user?: string; messages?: any[] } | null {
  if (!input) return null;

  // OpenAI messages format
  if (input.messages && Array.isArray(input.messages)) {
    return { messages: input.messages };
  }

  // Anthropic format
  if (input.system && input.messages) {
    return { system: input.system, messages: input.messages };
  }

  // Simple prompt string
  if (input.prompt) {
    return { user: input.prompt };
  }

  // Direct input might be the prompt
  if (typeof input === 'string') {
    return { user: input };
  }

  return null;
}

/**
 * Prompt viewer component
 */
export function PromptViewer({ input }: PromptViewerProps) {
  const [copySuccess, setCopySuccess] = useState(false);
  const prompt = extractPrompt(input);

  const handleCopy = () => {
    if (prompt) {
      const text = JSON.stringify(prompt, null, 2);
      navigator.clipboard.writeText(text);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    }
  };

  if (!prompt) {
    return (
      <Box sx={{ p: 2, color: 'text.secondary', fontStyle: 'italic' }}>
        No prompt data available
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Typography variant="subtitle2">LLM Prompt</Typography>
        <Tooltip title={copySuccess ? "Copied!" : "Copy prompt"} arrow>
          <IconButton size="small" onClick={handleCopy}>
            <CopyIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Render prompt field if present (Swisper format) */}
      {input?.prompt && typeof input.prompt === 'string' && (
        <Paper sx={{ p: 2, mb: 2, bgcolor: 'grey.900' }}>
          <Typography variant="caption" sx={{ color: 'primary.main', fontWeight: 'bold', mb: 1, display: 'block' }}>
            PROMPT:
          </Typography>
          <Box sx={{ 
            '& p': { mb: 1 }, 
            '& h1, & h2, & h3': { color: 'primary.light', mb: 1, mt: 2 },
            '& code': { bgcolor: 'grey.800', p: 0.5, borderRadius: 1 },
            '& pre': { bgcolor: 'grey.800', p: 1, borderRadius: 1, overflow: 'auto' },
          }}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {input.prompt}
            </ReactMarkdown>
          </Box>
        </Paper>
      )}

      {/* Render messages */}
      {prompt.messages ? (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          {prompt.messages.map((msg: any, idx: number) => (
            <Paper key={idx} sx={{ p: 1.5, bgcolor: 'grey.900' }}>
              <Typography variant="caption" sx={{ color: 'primary.main', fontWeight: 'bold', textTransform: 'uppercase' }}>
                {msg.role}:
              </Typography>
              <Box sx={{ 
                mt: 0.5,
                '& p': { mb: 1 }, 
                '& h1, & h2, & h3': { color: 'primary.light', mb: 1, mt: 2 },
                '& code': { bgcolor: 'grey.800', p: 0.5, borderRadius: 1 },
                '& pre': { bgcolor: 'grey.800', p: 1, borderRadius: 1, overflow: 'auto' },
              }}>
                {typeof msg.content === 'string' ? (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {msg.content}
                  </ReactMarkdown>
                ) : (
                  <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                    {JSON.stringify(msg.content, null, 2)}
                  </Typography>
                )}
              </Box>
            </Paper>
          ))}
        </Box>
      ) : (
        <>
          {/* System message */}
          {prompt.system && (
            <Paper sx={{ p: 1.5, mb: 1, bgcolor: 'grey.900' }}>
              <Typography variant="caption" sx={{ color: 'primary.main', fontWeight: 'bold' }}>
                SYSTEM:
              </Typography>
              <Box sx={{ 
                mt: 0.5,
                '& p': { mb: 1 }, 
                '& h1, & h2, & h3': { color: 'primary.light', mb: 1, mt: 2 },
                '& code': { bgcolor: 'grey.800', p: 0.5, borderRadius: 1 },
              }}>
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {prompt.system}
                </ReactMarkdown>
              </Box>
            </Paper>
          )}

          {/* User message */}
          {prompt.user && (
            <Paper sx={{ p: 1.5, bgcolor: 'grey.900' }}>
              <Typography variant="caption" sx={{ color: 'success.main', fontWeight: 'bold' }}>
                USER:
              </Typography>
              <Box sx={{ mt: 0.5 }}>
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {prompt.user}
                </ReactMarkdown>
              </Box>
            </Paper>
          )}
        </>
      )}
    </Box>
  );
}

