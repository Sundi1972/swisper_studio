/**
 * State diff viewer - shows what changed between input and output states
 */

import { Box, Typography, ToggleButtonGroup, ToggleButton, Stack, Button } from '@mui/material';
import { UnfoldMore as ExpandAllIcon } from '@mui/icons-material';
import { useState } from 'react';
import { StateViewer } from './state-viewer';
import JsonView from '@uiw/react-json-view';

interface StateDiffViewerProps {
  inputState: Record<string, any> | null;
  outputState: Record<string, any> | null;
}

type ViewMode = 'diff' | 'side-by-side';

/**
 * Calculate diff between two objects
 */
function calculateDiff(before: any, after: any): {
  added: Record<string, any>;
  removed: Record<string, any>;
  changed: Record<string, any>;
  unchanged: Record<string, any>;
} {
  const diff = {
    added: {} as Record<string, any>,
    removed: {} as Record<string, any>,
    changed: {} as Record<string, any>,
    unchanged: {} as Record<string, any>,
  };

  if (!before && !after) return diff;
  if (!before) return { ...diff, added: after };
  if (!after) return { ...diff, removed: before };

  // Find added and changed
  for (const key in after) {
    if (!(key in before)) {
      diff.added[key] = after[key];
    } else if (JSON.stringify(before[key]) !== JSON.stringify(after[key])) {
      diff.changed[key] = { before: before[key], after: after[key] };
    } else {
      diff.unchanged[key] = after[key];
    }
  }

  // Find removed
  for (const key in before) {
    if (!(key in after)) {
      diff.removed[key] = before[key];
    }
  }

  return diff;
}

/**
 * State diff viewer with toggle between diff and side-by-side views
 */
export function StateDiffViewer({ inputState, outputState }: StateDiffViewerProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('diff');
  const [showUnchanged, setShowUnchanged] = useState(false);
  const [expandAll, setExpandAll] = useState(false);

  const diff = calculateDiff(inputState, outputState);
  const hasChanges = Object.keys(diff.added).length > 0 || 
                     Object.keys(diff.removed).length > 0 ||
                     Object.keys(diff.changed).length > 0;

  if (!inputState && !outputState) {
    return (
      <Box sx={{ p: 2, color: 'text.secondary', fontStyle: 'italic' }}>
        No state data available
      </Box>
    );
  }

  return (
    <Box>
      {/* Controls */}
      <Stack direction="row" spacing={2} sx={{ mb: 2, flexWrap: 'wrap' }}>
        <ToggleButtonGroup
          value={viewMode}
          exclusive
          onChange={(_, newMode) => newMode && setViewMode(newMode)}
          size="small"
        >
          <ToggleButton value="diff">Diff View</ToggleButton>
          <ToggleButton value="side-by-side">Side-by-Side</ToggleButton>
        </ToggleButtonGroup>

        {viewMode === 'diff' && (
          <ToggleButtonGroup
            value={showUnchanged ? 'show' : 'hide'}
            exclusive
            onChange={(_, newValue) => setShowUnchanged(newValue === 'show')}
            size="small"
          >
            <ToggleButton value="hide">Hide Unchanged</ToggleButton>
            <ToggleButton value="show">Show All</ToggleButton>
          </ToggleButtonGroup>
        )}

        <Button
          size="small"
          startIcon={<ExpandAllIcon />}
          onClick={() => setExpandAll(!expandAll)}
          variant="outlined"
        >
          {expandAll ? 'Collapse All' : 'Expand All'}
        </Button>
      </Stack>

      {/* Content */}
      {viewMode === 'diff' ? (
        <Box sx={{ 
          p: 2, 
          bgcolor: 'grey.900',
          borderRadius: 1
        }}>
          {!hasChanges ? (
            <Typography variant="body2" color="text.secondary">
              No changes detected
            </Typography>
          ) : (
            <Box sx={{ fontFamily: 'monospace', fontSize: '13px' }}>
              {/* Added fields - GREEN BACKGROUND */}
              {Object.keys(diff.added).map((key) => {
                const value = diff.added[key];
                const isPrimitive = typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean' || value === null || value === undefined;
                
                return (
                  <Box key={`added-${key}`} sx={{ 
                    mb: 1, 
                    backgroundColor: 'rgba(76, 175, 80, 0.2)', 
                    p: 1, 
                    borderRadius: 1,
                    '& *': { color: '#ffffff !important' }  // Force white text on green
                  }}>
                    <Box component="span" sx={{ color: '#4caf50', fontWeight: 'bold' }}>+ </Box>
                    <Box component="span">
                      {key}: {isPrimitive ? (
                        <Box component="span" sx={{ fontFamily: 'monospace' }}>
                          {value === null ? 'null' : value === undefined ? 'undefined' : typeof value === 'string' ? `"${value}"` : String(value)}
                        </Box>
                      ) : (
                        <JsonView value={value} collapsed={expandAll ? false : 1} displayDataTypes={false} enableClipboard={false} style={{ display: 'inline', background: 'transparent' }} />
                      )}
                    </Box>
                  </Box>
                );
              })}

              {/* Removed fields - RED BACKGROUND */}
              {Object.keys(diff.removed).map((key) => {
                const value = diff.removed[key];
                const isPrimitive = typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean' || value === null || value === undefined;
                
                return (
                  <Box key={`removed-${key}`} sx={{ 
                    mb: 1, 
                    backgroundColor: 'rgba(244, 67, 54, 0.2)', 
                    p: 1, 
                    borderRadius: 1,
                    '& *': { color: '#ffffff !important' }  // Force white text on red
                  }}>
                    <Box component="span" sx={{ color: '#f44336', fontWeight: 'bold' }}>- </Box>
                    <Box component="span">
                      {key}: {isPrimitive ? (
                        <Box component="span" sx={{ fontFamily: 'monospace' }}>
                          {value === null ? 'null' : value === undefined ? 'undefined' : typeof value === 'string' ? `"${value}"` : String(value)}
                        </Box>
                      ) : (
                        <JsonView value={value} collapsed={expandAll ? false : 1} displayDataTypes={false} enableClipboard={false} style={{ display: 'inline', background: 'transparent' }} />
                      )}
                    </Box>
                  </Box>
                );
              })}

              {/* Changed fields - YELLOW BACKGROUND */}
              {Object.keys(diff.changed).map((key) => {
                const beforeValue = diff.changed[key].before;
                const afterValue = diff.changed[key].after;
                const beforeIsPrimitive = typeof beforeValue === 'string' || typeof beforeValue === 'number' || typeof beforeValue === 'boolean' || beforeValue === null || beforeValue === undefined;
                const afterIsPrimitive = typeof afterValue === 'string' || typeof afterValue === 'number' || typeof afterValue === 'boolean' || afterValue === null || afterValue === undefined;
                
                return (
                  <Box key={`changed-${key}`} sx={{ mb: 1 }}>
                    <Box sx={{ 
                      backgroundColor: 'rgba(244, 67, 54, 0.2)', 
                      p: 1, 
                      borderRadius: 1, 
                      mb: 0.5,
                      '& *': { color: '#ffffff !important' }
                    }}>
                      <Box component="span" sx={{ color: '#f44336', fontWeight: 'bold' }}>- </Box>
                      <Box component="span">
                        {key}: {beforeIsPrimitive ? (
                          <Box component="span" sx={{ fontFamily: 'monospace' }}>
                            {beforeValue === null ? 'null' : beforeValue === undefined ? 'undefined' : typeof beforeValue === 'string' ? `"${beforeValue}"` : String(beforeValue)}
                          </Box>
                        ) : (
                          <JsonView value={beforeValue} collapsed={expandAll ? false : 1} displayDataTypes={false} enableClipboard={false} style={{ display: 'inline', background: 'transparent' }} />
                        )}
                      </Box>
                    </Box>
                    <Box sx={{ 
                      backgroundColor: 'rgba(76, 175, 80, 0.2)', 
                      p: 1, 
                      borderRadius: 1,
                      '& *': { color: '#ffffff !important' }
                    }}>
                      <Box component="span" sx={{ color: '#4caf50', fontWeight: 'bold' }}>+ </Box>
                      <Box component="span">
                        {key}: {afterIsPrimitive ? (
                          <Box component="span" sx={{ fontFamily: 'monospace' }}>
                            {afterValue === null ? 'null' : afterValue === undefined ? 'undefined' : typeof afterValue === 'string' ? `"${afterValue}"` : String(afterValue)}
                          </Box>
                        ) : (
                          <JsonView value={afterValue} collapsed={expandAll ? false : 1} displayDataTypes={false} enableClipboard={false} style={{ display: 'inline', background: 'transparent' }} />
                        )}
                      </Box>
                    </Box>
                  </Box>
                );
              })}

              {/* Unchanged fields (if showing) */}
              {showUnchanged && Object.keys(diff.unchanged).map((key) => {
                const value = diff.unchanged[key];
                const isPrimitive = typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean' || value === null || value === undefined;
                
                return (
                  <Box key={`unchanged-${key}`} sx={{ mb: 1, color: 'text.secondary', p: 1 }}>
                    {key}: {isPrimitive ? (
                      <Box component="span" sx={{ fontFamily: 'monospace' }}>
                        {value === null ? 'null' : value === undefined ? 'undefined' : typeof value === 'string' ? `"${value}"` : String(value)}
                      </Box>
                    ) : (
                      <JsonView value={value} collapsed={expandAll ? false : 1} displayDataTypes={false} enableClipboard={false} style={{ display: 'inline', background: 'transparent' }} />
                    )}
                  </Box>
                );
              })}
            </Box>
          )}
        </Box>
      ) : (
        <Box sx={{ display: 'flex', gap: 2 }}>
          {/* Before (Input) */}
          <Box sx={{ flex: 1 }}>
            <Typography variant="subtitle2" sx={{ mb: 1 }}>State Before</Typography>
            <StateViewer data={inputState} expanded={expandAll} />
          </Box>

          {/* After (Output) */}
          <Box sx={{ flex: 1 }}>
            <Typography variant="subtitle2" sx={{ mb: 1 }}>State After</Typography>
            <StateViewer data={outputState} expanded={expandAll} />
          </Box>
        </Box>
      )}
    </Box>
  );
}

