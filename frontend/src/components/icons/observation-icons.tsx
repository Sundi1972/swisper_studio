/**
 * Icon components for observation indicators
 */

import { Tooltip } from '@mui/material';
import {
  SwapHoriz as StateChangeIcon,
  Chat as PromptIcon,
  Build as ToolIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  CheckCircle as SuccessIcon,
} from '@mui/icons-material';

interface IndicatorIconProps {
  tooltip: string;
  color?: string;
}

/**
 * State changed indicator (🔄)
 */
export function StateChangedIndicator({ tooltip }: IndicatorIconProps) {
  return (
    <Tooltip title={tooltip} arrow>
      <StateChangeIcon 
        sx={{ 
          fontSize: 16, 
          color: 'info.main',
          cursor: 'help'
        }} 
      />
    </Tooltip>
  );
}

/**
 * Prompt/LLM indicator (💬)
 */
export function PromptIndicator({ tooltip }: IndicatorIconProps) {
  return (
    <Tooltip title={tooltip} arrow>
      <PromptIcon 
        sx={{ 
          fontSize: 16, 
          color: 'primary.main',
          cursor: 'help'
        }} 
      />
    </Tooltip>
  );
}

/**
 * Tool call indicator (🛠️)
 */
export function ToolIndicator({ tooltip }: IndicatorIconProps) {
  return (
    <Tooltip title={tooltip} arrow>
      <ToolIcon 
        sx={{ 
          fontSize: 16, 
          color: 'success.main',
          cursor: 'help'
        }} 
      />
    </Tooltip>
  );
}

/**
 * Error indicator (⚠️)
 */
export function ErrorIndicator({ tooltip }: IndicatorIconProps) {
  return (
    <Tooltip title={tooltip} arrow>
      <ErrorIcon 
        sx={{ 
          fontSize: 16, 
          color: 'error.main',
          cursor: 'help'
        }} 
      />
    </Tooltip>
  );
}

/**
 * Warning indicator (⚠️)
 */
export function WarningIndicator({ tooltip }: IndicatorIconProps) {
  return (
    <Tooltip title={tooltip} arrow>
      <WarningIcon 
        sx={{ 
          fontSize: 16, 
          color: 'warning.main',
          cursor: 'help'
        }} 
      />
    </Tooltip>
  );
}

/**
 * Success indicator (✅)
 */
export function SuccessIndicator({ tooltip }: IndicatorIconProps) {
  return (
    <Tooltip title={tooltip} arrow>
      <SuccessIcon 
        sx={{ 
          fontSize: 16, 
          color: 'success.main',
          cursor: 'help'
        }} 
      />
    </Tooltip>
  );
}


