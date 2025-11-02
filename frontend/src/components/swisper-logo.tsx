/**
 * Swisper Logo component
 * Displays main Swisper logo with optional "Studio" subtitle
 */

import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

import SwisperLogoSvg from '@/assets/logos/swisperLogo.svg';

interface SwisperLogoProps {
  showStudio?: boolean;
  width?: number;
}

export function SwisperLogo({ showStudio = false, width = 150 }: SwisperLogoProps) {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <img 
        src={SwisperLogoSvg} 
        alt="Swisper" 
        style={{ width: `${width}px`, height: 'auto' }}
      />
      {showStudio && (
        <Typography 
          variant="caption" 
          sx={{ 
            mt: 0.5,
            color: 'text.secondary',
            letterSpacing: '0.1em',
            textTransform: 'uppercase',
            fontSize: '0.75rem'
          }}
        >
          Studio
        </Typography>
      )}
    </Box>
  );
}

