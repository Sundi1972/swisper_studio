/**
 * Login page component
 * Following Swisper patterns: MUI components, styled components, function declarations
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Alert from '@mui/material/Alert';
import IconButton from '@mui/material/IconButton';
import InputAdornment from '@mui/material/InputAdornment';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import { styled, useTheme } from '@mui/material/styles';

import { useLoginMutation } from '../hooks/use-login-mutation';
import { SwisperLogo } from '@/components/swisper-logo';

// Styled components (Swisper pattern)
const Container = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: '100vh',
  padding: theme.spacing(3),
  backgroundColor: theme.palette.background.default, // Use theme background
}));

export function LoginPage() {
  const [apiKey, setApiKey] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const navigate = useNavigate();
  const theme = useTheme();
  const { mutateAsync: login, isPending, isError, error } = useLoginMutation();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    try {
      await login({ apiKey });
      navigate('/projects');
    } catch (err) {
      // Error handled by mutation hook
    }
  }

  return (
    <Container data-testid="login-page">
      <Box 
        component="form" 
        onSubmit={handleSubmit}
        sx={{
          width: '100%',
          maxWidth: '400px',
          padding: theme.spacing(4),
          borderRadius: theme.spacing(1),
          backgroundColor: theme.palette.background.paper,
          boxShadow: theme.shadows[3],
        }}
      >
        <Box sx={{ mb: 3 }}>
          <SwisperLogo showStudio width={150} />
        </Box>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 3, textAlign: 'center' }}>
          AI Observability & Development Platform
        </Typography>

        {isError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error?.message || 'Login failed'}
          </Alert>
        )}

        <TextField
          fullWidth
          type={showApiKey ? 'text' : 'password'}
          label="SwisperStudio API Key"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          required
          helperText="Enter your SwisperStudio API key (API_KEY from docker-compose.yml)"
          sx={{ mb: 2 }}
          disabled={isPending}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  onClick={() => setShowApiKey(!showApiKey)}
                  edge="end"
                  size="small"
                >
                  {showApiKey ? <VisibilityOffIcon /> : <VisibilityIcon />}
                </IconButton>
              </InputAdornment>
            ),
          }}
        />

        <Button
          fullWidth
          type="submit"
          variant="contained"
          disabled={isPending || !apiKey}
        >
          {isPending ? 'Logging in...' : 'Login'}
        </Button>
      </Box>
    </Container>
  );
}

