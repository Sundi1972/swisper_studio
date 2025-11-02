/**
 * Project create dialog
 * Following Swisper patterns: MUI Dialog, form validation with zod
 */

import { useState } from 'react';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import InputAdornment from '@mui/material/InputAdornment';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';

import { useCreateProjectMutation } from '../hooks/use-create-project-mutation';

interface ProjectCreateDialogProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ProjectCreateDialog({ isOpen, onClose }: ProjectCreateDialogProps) {
  const [formData, setFormData] = useState({
    name: '',
    swisper_url: '',
    swisper_api_key: '',
    description: '',
  });
  const [showApiKey, setShowApiKey] = useState(false);

  const { mutateAsync: createProject, isPending, isError, error } = useCreateProjectMutation();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    try {
      await createProject({
        ...formData,
        description: formData.description || undefined,
      });
      onClose();
      // Reset form
      setFormData({
        name: '',
        swisper_url: '',
        swisper_api_key: '',
        description: '',
      });
    } catch (err) {
      // Error displayed via error state
    }
  }

  function handleClose() {
    if (!isPending) {
      onClose();
    }
  }

  return (
    <Dialog open={isOpen} onClose={handleClose} maxWidth="sm" fullWidth>
      <Box component="form" onSubmit={handleSubmit}>
        <DialogTitle>Create New Project</DialogTitle>

        <DialogContent>
          {isError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error?.message || 'Failed to create project'}
            </Alert>
          )}

          <TextField
            fullWidth
            label="Project Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
            margin="normal"
            disabled={isPending}
            helperText="Example: Production Swisper, Staging Environment"
          />

          <TextField
            fullWidth
            label="Swisper Instance URL"
            value={formData.swisper_url}
            onChange={(e) => setFormData({ ...formData, swisper_url: e.target.value })}
            required
            margin="normal"
            placeholder="https://swisper.mycompany.com"
            disabled={isPending}
            helperText="The URL where your Swisper instance is running"
          />

          <TextField
            fullWidth
            type={showApiKey ? 'text' : 'password'}
            label="Swisper Instance API Key"
            value={formData.swisper_api_key}
            onChange={(e) => setFormData({ ...formData, swisper_api_key: e.target.value })}
            required
            margin="normal"
            disabled={isPending}
            helperText="API key for authenticating to your Swisper instance (can be any string for now)"
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

          <TextField
            fullWidth
            label="Description (optional)"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            margin="normal"
            multiline
            rows={2}
            disabled={isPending}
            helperText="Optional description of this Swisper deployment"
          />
        </DialogContent>

        <DialogActions>
          <Button onClick={handleClose} disabled={isPending}>
            Cancel
          </Button>
          <Button type="submit" variant="contained" disabled={isPending}>
            {isPending ? 'Creating...' : 'Create Project'}
          </Button>
        </DialogActions>
      </Box>
    </Dialog>
  );
}

