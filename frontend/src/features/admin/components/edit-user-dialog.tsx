/**
 * Edit User Dialog
 * 
 * Allows admins to update user role, name, and active status.
 */

import { useState, useEffect } from 'react';
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
  FormControlLabel,
  Switch,
  Alert,
} from '@mui/material';
import { useMutation } from '@tanstack/react-query';
import { updateUser } from '@/api/users';
import type { User } from '@/types/auth';

interface EditUserDialogProps {
  user: User;
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function EditUserDialog({ user, open, onClose, onSuccess }: EditUserDialogProps) {
  const [name, setName] = useState(user.name);
  const [role, setRole] = useState(user.role);
  const [isActive, setIsActive] = useState(user.is_active);

  // Reset form when user changes
  useEffect(() => {
    setName(user.name);
    setRole(user.role);
    setIsActive(user.is_active);
  }, [user]);

  const { mutateAsync, isPending, error } = useMutation({
    mutationFn: () =>
      updateUser(user.id, {
        name: name !== user.name ? name : undefined,
        role: role !== user.role ? role : undefined,
        is_active: isActive !== user.is_active ? isActive : undefined,
      }),
    onSuccess: () => {
      onSuccess();
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await mutateAsync();
  };

  const hasChanges =
    name !== user.name || role !== user.role || isActive !== user.is_active;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>Edit User</DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error instanceof Error ? error.message : 'Failed to update user'}
            </Alert>
          )}

          <TextField
            label="Name"
            fullWidth
            value={name}
            onChange={(e) => setName(e.target.value)}
            disabled={isPending}
            sx={{ mb: 2, mt: 1 }}
          />

          <TextField
            label="Email"
            fullWidth
            value={user.email}
            disabled
            helperText="Email cannot be changed"
            sx={{ mb: 2 }}
          />

          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Role</InputLabel>
            <Select
              value={role}
              label="Role"
              onChange={(e) => setRole(e.target.value)}
              disabled={isPending}
            >
              <MenuItem value="admin">Admin - Full access</MenuItem>
              <MenuItem value="developer">Developer - Dev/staging edit, prod read-only</MenuItem>
              <MenuItem value="qa">QA - Staging edit, dev/prod read-only</MenuItem>
              <MenuItem value="viewer">Viewer - Read-only everywhere</MenuItem>
            </Select>
          </FormControl>

          <FormControlLabel
            control={
              <Switch
                checked={isActive}
                onChange={(e) => setIsActive(e.target.checked)}
                disabled={isPending}
              />
            }
            label={isActive ? 'Active' : 'Inactive'}
          />
        </DialogContent>

        <DialogActions>
          <Button onClick={onClose} disabled={isPending}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={isPending || !hasChanges}
          >
            {isPending ? 'Saving...' : 'Save Changes'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}

