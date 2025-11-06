/**
 * Observation details panel - shows full details for selected observation
 * 
 * Phase 2.5: State visualization with prompts, responses, and diffs
 */

import { Box, Paper, Typography, Chip, Stack, Button, Divider } from '@mui/material';
import { 
  Search as SearchIcon,
  Output as OutputIcon,
  SwapHoriz as DiffIcon,
  Chat as PromptIcon,
  Build as ToolIcon,
  Psychology as ReasoningIcon,
} from '@mui/icons-material';
import { useRef } from 'react';
import { StateDiffViewer } from './state-diff-viewer';
import { PromptViewer } from './prompt-viewer';
import { ReasoningViewer } from './reasoning-viewer';
import { ResponseViewer } from './response-viewer';
import { ToolCallViewer } from './tool-call-viewer';
import { ToolResponseViewer } from './tool-response-viewer';
import { IndividualToolsViewer } from './individual-tools-viewer';

interface ObservationNode {
  id: string;
  type: string;
  name: string | null;
  latency_ms: number | null;
  model: string | null;
  model_parameters: Record<string, any> | null;
  prompt_tokens: number | null;
  completion_tokens: number | null;
  total_tokens: number | null;
  calculated_input_cost: string | null;
  calculated_output_cost: string | null;
  calculated_total_cost: string | null;
  input: Record<string, any> | null;
  output: Record<string, any> | null;
  meta: Record<string, any> | null;
  level: string;
  status_message: string | null;
  start_time: string;
  end_time: string | null;
}

interface ObservationDetailsPanelProps {
  observation: ObservationNode | null;
}

function getTypeColor(type: string): 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'error' {
  switch (type) {
    case 'GENERATION':
      return 'primary';
    case 'TOOL':
      return 'success';
    case 'AGENT':
      return 'secondary';
    case 'SPAN':
      return 'default';
    default:
      return 'default';
  }
}

function getLevelColor(level: string): 'default' | 'success' | 'warning' | 'error' {
  switch (level) {
    case 'ERROR':
      return 'error';
    case 'WARNING':
      return 'warning';
    case 'DEFAULT':
      return 'success';
    default:
      return 'default';
  }
}

/**
 * Empty state when no observation is selected
 */
function EmptyState() {
  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="400px"
      sx={{ color: 'text.secondary' }}
    >
      <SearchIcon sx={{ fontSize: 64, mb: 2, opacity: 0.3 }} />
      <Typography variant="h6" gutterBottom>
        Select an observation
      </Typography>
      <Typography variant="body2" textAlign="center" sx={{ maxWidth: 400 }}>
        Click on any observation in the tree to view its details,
        including state transitions, prompts, and responses.
      </Typography>
    </Box>
  );
}

/**
 * Observation details panel component
 */
export function ObservationDetailsPanel({ observation }: ObservationDetailsPanelProps) {
  // Refs for scrolling to sections
  const stateDiffRef = useRef<HTMLDivElement>(null);
  const promptRef = useRef<HTMLDivElement>(null);
  const reasoningRef = useRef<HTMLDivElement>(null);
  const responseRef = useRef<HTMLDivElement>(null);
  const toolCallRef = useRef<HTMLDivElement>(null);
  const toolResponseRef = useRef<HTMLDivElement>(null);

  // Scroll to section
  const scrollToSection = (ref: React.RefObject<HTMLDivElement>) => {
    ref.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  // Show empty state if no observation selected
  if (!observation) {
    return (
      <Paper sx={{ p: 3, height: '100%' }}>
        <EmptyState />
      </Paper>
    );
  }

  const isGeneration = observation.type === 'GENERATION';
  const isTool = observation.type === 'TOOL';
  
  // Check if reasoning is available (SDK v0.4.0)
  const hasReasoning = observation.output?._llm_reasoning && 
                       typeof observation.output._llm_reasoning === 'string';

  return (
    <Paper sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header (fixed) */}
      <Box sx={{ p: 3, borderBottom: 1, borderColor: 'divider' }}>
        <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
          <Chip
            label={observation.type}
            size="small"
            color={getTypeColor(observation.type)}
          />
          <Chip
            label={observation.level}
            size="small"
            color={getLevelColor(observation.level)}
            variant="outlined"
          />
        </Stack>
        
        <Typography variant="h6" gutterBottom>
          {observation.name || 'Unnamed Observation'}
        </Typography>
        
        {/* Quick stats */}
        <Stack direction="row" spacing={2} sx={{ mt: 2, flexWrap: 'wrap' }}>
          {observation.latency_ms !== null && (
            <Typography variant="body2" color="text.secondary">
              <strong>Duration:</strong> {observation.latency_ms.toFixed(0)}ms
            </Typography>
          )}
          {observation.model && (
            <Typography variant="body2" color="text.secondary">
              <strong>Model:</strong> {observation.model}
            </Typography>
          )}
          {observation.prompt_tokens !== null && observation.completion_tokens !== null && (
            <Typography variant="body2" color="text.secondary">
              <strong>Tokens:</strong> {observation.prompt_tokens} + {observation.completion_tokens} = {observation.total_tokens}
            </Typography>
          )}
          {observation.calculated_total_cost && (
            <Typography variant="body2" color="text.secondary">
              <strong>Cost:</strong> ${parseFloat(observation.calculated_total_cost).toFixed(6)}
            </Typography>
          )}
        </Stack>

        {/* Quick action buttons */}
        <Stack direction="row" spacing={1} sx={{ mt: 2, flexWrap: 'wrap' }}>
          <Button
            size="small"
            startIcon={<DiffIcon />}
            onClick={() => scrollToSection(stateDiffRef)}
          >
            State Diff
          </Button>
          {isGeneration && (
            <>
              <Button
                size="small"
                startIcon={<PromptIcon />}
                onClick={() => scrollToSection(promptRef)}
              >
                Prompt
              </Button>
              {hasReasoning && (
                <Button
                  size="small"
                  startIcon={<ReasoningIcon />}
                  onClick={() => scrollToSection(reasoningRef)}
                  sx={{ color: 'warning.main' }}
                >
                  Reasoning
                </Button>
              )}
              <Button
                size="small"
                startIcon={<OutputIcon />}
                onClick={() => scrollToSection(responseRef)}
              >
                Response
              </Button>
            </>
          )}
          {isTool && (
            <>
              <Button
                size="small"
                startIcon={<ToolIcon />}
                onClick={() => scrollToSection(toolCallRef)}
              >
                Tool Call
              </Button>
              <Button
                size="small"
                startIcon={<OutputIcon />}
                onClick={() => scrollToSection(toolResponseRef)}
              >
                Tool Response
              </Button>
            </>
          )}
        </Stack>

        {/* Error message (if present) */}
        {observation.level === 'ERROR' && observation.status_message && (
          <Paper sx={{ p: 2, mt: 2, bgcolor: 'error.dark', color: 'error.contrastText' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
              ERROR
            </Typography>
            <Typography variant="body2">
              {observation.status_message}
            </Typography>
          </Paper>
        )}
      </Box>

      {/* Content (scrollable) */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 3 }}>
        {/* State Diff (always shown) */}
        <Box ref={stateDiffRef} sx={{ mb: 4 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            State Transition
          </Typography>
          <StateDiffViewer 
            inputState={observation.input}
            outputState={observation.output}
          />
        </Box>

        <Divider sx={{ my: 3 }} />

        {/* Type-specific sections */}
        {isGeneration && (
          <>
            {/* LLM Prompt */}
            <Box ref={promptRef} sx={{ mb: 4 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                LLM Prompt
              </Typography>
              <PromptViewer input={observation.input} output={observation.output} />
            </Box>

            <Divider sx={{ my: 3 }} />

            {/* LLM Reasoning (if available) */}
            {hasReasoning && (
              <>
                <Box ref={reasoningRef} sx={{ mb: 4 }}>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    LLM Thinking Process
                  </Typography>
                  <ReasoningViewer output={observation.output} />
                </Box>

                <Divider sx={{ my: 3 }} />
              </>
            )}

            {/* LLM Response */}
            <Box ref={responseRef} sx={{ mb: 4 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                LLM Response
              </Typography>
              <ResponseViewer output={observation.output} />
            </Box>

            {/* Model Parameters */}
            {observation.model_parameters && (
              <>
                <Divider sx={{ my: 3 }} />
                <Box sx={{ mb: 4 }}>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Model Parameters
                  </Typography>
                  <Paper sx={{ p: 2, bgcolor: 'grey.900' }}>
                    {Object.entries(observation.model_parameters).map(([key, value]) => (
                      <Typography key={key} variant="body2" sx={{ fontFamily: 'monospace', mb: 0.5 }}>
                        <strong>{key}:</strong> {JSON.stringify(value)}
                      </Typography>
                    ))}
                  </Paper>
                </Box>
              </>
            )}
          </>
        )}

        {isTool && (
          <>
            {/* Tool Call */}
            <Box ref={toolCallRef} sx={{ mb: 4 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Tool Execution
              </Typography>
              <ToolCallViewer input={observation.input} name={observation.name} />
            </Box>

            <Divider sx={{ my: 3 }} />

            {/* Tool Response - Individual Tools */}
            <Box ref={toolResponseRef} sx={{ mb: 4 }}>
              {/* Check if we have tool_results (productivity/research agent format) */}
              {observation.output?.tool_results ? (
                <>
                  <IndividualToolsViewer toolResults={observation.output.tool_results} />
                  
                  <Divider sx={{ my: 3 }} />
                  
                  {/* Also show full data for reference */}
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Full Tool Data (Raw)
                  </Typography>
                  <ToolResponseViewer output={observation.output} />
                </>
              ) : (
                <>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Tool Result
                  </Typography>
                  <ToolResponseViewer output={observation.output} />
                </>
              )}
            </Box>
          </>
        )}
      </Box>
    </Paper>
  );
}
