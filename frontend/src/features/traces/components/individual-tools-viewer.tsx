/**
 * Individual Tools Viewer - Shows each tool call with details
 * 
 * Displays:
 * - Tool name with wrench icon
 * - Parameters used
 * - Success/failure status
 * - Response payload
 */

import { 
  Box, 
  Typography, 
  Accordion, 
  AccordionSummary, 
  AccordionDetails,
  Chip,
  Alert,
  Paper,
  Stack
} from '@mui/material';
import { 
  ExpandMore as ExpandMoreIcon,
  Build as WrenchIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import JsonView from '@uiw/react-json-view';

interface ToolCall {
  name: string;
  parameters: Record<string, any>;
  status: 'success' | 'failure';
  result: any;
  error?: string;
  batch_key?: string;
}

interface IndividualToolsViewerProps {
  toolResults: Record<string, any>;
}

/**
 * Extract individual tool calls from Swisper's tool_results structure
 */
function extractToolCalls(toolResults: any): ToolCall[] {
  const calls: ToolCall[] = [];
  
  if (!toolResults || typeof toolResults !== 'object') {
    return calls;
  }
  
  // Swisper format: tool_results → batches → results → individual tools
  for (const batchKey in toolResults) {
    const batch = toolResults[batchKey];
    
    if (batch && typeof batch === 'object' && batch.results) {
      // Each batch has results object with individual tools
      for (const toolKey in batch.results) {
        const toolData = batch.results[toolKey];
        
        // Extract tool name
        const toolName = toolData.tool_name || toolKey.split('_')[0] || 'unknown_tool';
        
        // Extract parameters from tool key (encoded in key name)
        const parameters = parseToolParameters(toolKey, toolData);
        
        calls.push({
          name: toolName,
          parameters: parameters,
          status: toolData.error ? 'failure' : 'success',
          result: toolData.result,
          error: toolData.error,
          batch_key: batchKey,
        });
      }
    }
  }
  
  return calls;
}

/**
 * Parse parameters from tool key or tool data
 */
function parseToolParameters(toolKey: string, toolData: any): Record<string, any> {
  const params: Record<string, any> = {};
  
  // Try to extract from key (format: toolname_param1_value1_param2_value2)
  // Example: office365_search_emails_folder_inbox_filter_receivedDateTime...
  const parts = toolKey.split('_');
  
  // Skip tool name parts, parse remaining as key-value pairs
  for (let i = 2; i < parts.length; i += 2) {
    if (i + 1 < parts.length) {
      const key = parts[i];
      const value = parts[i + 1];
      params[key] = decodeURIComponent(value);
    }
  }
  
  // Also check if toolData has explicit parameters
  if (toolData.parameters) {
    Object.assign(params, toolData.parameters);
  }
  
  return params;
}

/**
 * Individual tools viewer component
 */
export function IndividualToolsViewer({ toolResults }: IndividualToolsViewerProps) {
  const toolCalls = extractToolCalls(toolResults);
  
  if (toolCalls.length === 0) {
    return (
      <Box sx={{ p: 2, color: 'text.secondary', fontStyle: 'italic' }}>
        No individual tool calls found
      </Box>
    );
  }
  
  // Group by batch if multiple batches
  const batches = new Set(toolCalls.map(tc => tc.batch_key).filter(Boolean));
  const hasMultipleBatches = batches.size > 1;
  
  return (
    <Box>
      <Box sx={{ mb: 2 }}>
        <Typography variant="h6" sx={{ mb: 1 }}>
          🔧 Tool Executions ({toolCalls.length} {toolCalls.length === 1 ? 'tool' : 'tools'})
        </Typography>
        {hasMultipleBatches && (
          <Typography variant="caption" color="text.secondary">
            Executed in {batches.size} batches
          </Typography>
        )}
      </Box>
      
      {toolCalls.map((call, idx) => {
        const isSuccess = call.status === 'success';
        
        return (
          <Accordion key={idx} defaultExpanded={idx === 0}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ width: '100%', pr: 2 }}>
                {/* Wrench icon */}
                <WrenchIcon sx={{ color: isSuccess ? 'success.main' : 'error.main' }} />
                
                {/* Tool name */}
                <Typography sx={{ flexGrow: 1, fontWeight: 'bold' }}>
                  {call.name}
                </Typography>
                
                {/* Status badge */}
                {isSuccess ? (
                  <Chip 
                    icon={<SuccessIcon />}
                    label="Success" 
                    size="small" 
                    color="success"
                    variant="outlined"
                  />
                ) : (
                  <Chip 
                    icon={<ErrorIcon />}
                    label="Failed" 
                    size="small" 
                    color="error"
                  />
                )}
                
                {/* Batch info */}
                {hasMultipleBatches && call.batch_key && (
                  <Chip 
                    label={call.batch_key.split('_').slice(-2).join('_')} 
                    size="small" 
                    variant="outlined"
                    sx={{ fontSize: '0.65rem' }}
                  />
                )}
              </Stack>
            </AccordionSummary>
            
            <AccordionDetails>
              <Stack spacing={2}>
                {/* Parameters Section */}
                {Object.keys(call.parameters).length > 0 && (
                  <Box>
                    <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold' }}>
                      📝 Parameters:
                    </Typography>
                    <Paper sx={{ p: 1.5, bgcolor: 'grey.900' }}>
                      <JsonView 
                        value={call.parameters}
                        collapsed={1}
                        displayDataTypes={false}
                        style={{
                          background: 'transparent',
                          fontSize: '12px',
                        }}
                      />
                    </Paper>
                  </Box>
                )}
                
                {/* Response Section */}
                <Box>
                  <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold' }}>
                    {isSuccess ? '✅ Response:' : '❌ Error:'}
                  </Typography>
                  
                  {isSuccess ? (
                    <Paper sx={{ 
                      p: 1.5, 
                      bgcolor: 'success.dark',
                      border: 1,
                      borderColor: 'success.main'
                    }}>
                      {typeof call.result === 'string' ? (
                        // Try to parse JSON string
                        (() => {
                          try {
                            const parsed = JSON.parse(call.result);
                            return (
                              <JsonView 
                                value={parsed}
                                collapsed={2}
                                displayDataTypes={false}
                                style={{
                                  background: 'transparent',
                                  fontSize: '12px',
                                }}
                              />
                            );
                          } catch {
                            // Not JSON, show as text
                            return (
                              <Typography 
                                variant="body2" 
                                sx={{ 
                                  fontFamily: 'monospace',
                                  whiteSpace: 'pre-wrap',
                                  maxHeight: '300px',
                                  overflow: 'auto'
                                }}
                              >
                                {call.result.length > 500 
                                  ? call.result.substring(0, 500) + '\n\n... (truncated)'
                                  : call.result
                                }
                              </Typography>
                            );
                          }
                        })()
                      ) : (
                        <JsonView 
                          value={call.result}
                          collapsed={2}
                          displayDataTypes={false}
                          style={{
                            background: 'transparent',
                            fontSize: '12px',
                          }}
                        />
                      )}
                    </Paper>
                  ) : (
                    <Alert severity="error">
                      {call.error || 'Tool execution failed'}
                    </Alert>
                  )}
                </Box>
              </Stack>
            </AccordionDetails>
          </Accordion>
        );
      })}
    </Box>
  );
}

