/**
 * Create User Dialog (Admin Only)
 * 
 * Allows admins to create new user accounts.
 */

import { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  IconButton,
  InputAdornment,
} from '@mui/material';
import {
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
} from '@mui/icons-material';
import { useMutation } from '@tanstack/react-query';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

interface CreateUserDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

interface CreateUserRequest {
  email: string;
  password: string;
  name: string;
  role?: string;
}

export function CreateUserDialog({ open, onClose, onSuccess }: CreateUserDialogProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [role, setRole] = useState('viewer');
  const [showPassword, setShowPassword] = useState(false);

  const { mutateAsync, isPending, error } = useMutation({
    mutationFn: async (data: CreateUserRequest) => {
      // Get token from localStorage
      const token = localStorage.getItem('swisper_studio_token');
      if (!token) throw new Error('Not authenticated');

      const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to create user');
      }

      return response.json();
    },
    onSuccess: () => {
      onSuccess();
      handleReset();
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await mutateAsync({ email, password, name, role });
  };

  const handleReset = () => {
    setEmail('');
    setPassword('');
    setName('');
    setRole('viewer');
  };

  const handleClose = () => {
    if (!isPending) {
      handleReset();
      onClose();
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>Create New User</DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error instanceof Error ? error.message : 'Failed to create user'}
            </Alert>
          )}

          <TextField
            label="Name"
            fullWidth
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            disabled={isPending}
            sx={{ mb: 2, mt: 1 }}
            autoFocus
          />

          <TextField
            label="Email"
            type="email"
            fullWidth
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={isPending}
            sx={{ mb: 2 }}
          />

          <TextField
            label="Password"
            type={showPassword ? 'text' : 'password'}
            fullWidth
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={isPending}
            helperText="Minimum 8 characters"
            sx={{ mb: 2 }}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={() => setShowPassword(!showPassword)} edge="end" size="small">
                    {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />

          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Role</InputLabel>
            <Select
              value={role}
              label="Role"
              onChange={(e) => setRole(e.target.value)}
              disabled={isPending}
            >
              <MenuItem value="viewer">Viewer - Read-only everywhere</MenuItem>
              <MenuItem value="qa">QA - Staging edit, dev/prod read-only</MenuItem>
              <MenuItem value="developer">Developer - Dev/staging edit, prod read-only</MenuItem>
              <MenuItem value="admin">Admin - Full access</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>

        <DialogActions>
          <Button onClick={handleClose} disabled={isPending}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={isPending}
          >
            {isPending ? 'Creating...' : 'Create User'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}

