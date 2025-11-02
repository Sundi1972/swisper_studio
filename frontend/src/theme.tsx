import { createTheme } from '@mui/material/styles';

// SwisperStudio theme - Using Swisper's actual dark theme
// Reference: swisper/packages/design-system/src/mui-theme.ts

export const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00A9DD', // Swisper blue-500
    },
    secondary: {
      main: '#B6C2D1', // Swisper steel-400
    },
    error: {
      main: '#FF5252',
    },
    background: {
      default: '#141923', // Swisper dark background
      paper: '#222834',   // Swisper dark surface
    },
    text: {
      primary: '#FFFFFF',
      secondary: '#FFFFFFB2',
    },
    steel: {
      100: '#F9FBFC',
      200: '#DDE9F2',
      300: '#C0C9D6',
      400: '#B6C2D1',
      500: '#8F99AD',
      600: '#5C647C',
      650: '#2E3442',
      700: '#222834',
      800: '#141923',
      900: '#020305',
    },
    blue: {
      100: '#9EDFF7',
      300: '#00C4FF',
      400: '#00B3EB',
      500: '#00A9DD',
      600: '#0093C2',
      700: '#0087B8',
      800: '#007DA8',
    },
  } as any,
  typography: {
    fontFamily: [
      'Hanken Grotesk',
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      'sans-serif',
    ].join(','),
    fontSize: 16,
    h1: {
      fontSize: '2rem',
      lineHeight: '140%',
    },
    h2: {
      fontSize: '1.750rem',
      lineHeight: '140%',
    },
    h3: {
      fontSize: '1.5rem',
      fontWeight: 500,
      lineHeight: '140%',
    },
    h4: {
      fontSize: '1.25rem',
      fontWeight: 500,
      lineHeight: '140%',
    },
    body1: {
      fontSize: '1rem',
      lineHeight: '160%',
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: '160%',
    },
  },
  spacing: 8, // Swisper default padding step
  shape: {
    borderRadius: 16, // Swisper border radius
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: '#222834',
          borderRadius: 16,
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          backgroundColor: '#141923',
          borderRadius: 10,
        },
      },
    },
    MuiDialogContent: {
      styleOverrides: {
        root: {
          backgroundColor: '#222834',
        },
      },
    },
    MuiDialogTitle: {
      styleOverrides: {
        root: {
          backgroundColor: '#222834',
          fontWeight: 600,
          fontSize: '1.25rem',
        },
      },
    },
  },
});

