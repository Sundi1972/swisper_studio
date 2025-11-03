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
import Typography from '@mui/material/Typography';
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
    description: '',
    github_repo_url: '',
    github_token: '',
    dev_url: '',
    dev_api_key: '',
    staging_url: '',
    staging_api_key: '',
    production_url: '',
    production_api_key: '',
  });
  const [showDevKey, setShowDevKey] = useState(false);
  const [showStagingKey, setShowStagingKey] = useState(false);
  const [showProdKey, setShowProdKey] = useState(false);
  const [showGitHubToken, setShowGitHubToken] = useState(false);

  const { mutateAsync: createProject, isPending, isError, error } = useCreateProjectMutation();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    try {
      await createProject({
        name: formData.name,
        description: formData.description || undefined,
        github_repo_url: formData.github_repo_url || undefined,
        github_token: formData.github_token || undefined,
        dev_environment: {
          swisper_url: formData.dev_url,
          swisper_api_key: formData.dev_api_key,
        },
        staging_environment: {
          swisper_url: formData.staging_url,
          swisper_api_key: formData.staging_api_key,
        },
        production_environment: {
          swisper_url: formData.production_url,
          swisper_api_key: formData.production_api_key,
        },
      });
      onClose();
      // Reset form
      setFormData({
        name: '',
        description: '',
        github_repo_url: '',
        github_token: '',
        dev_url: '',
        dev_api_key: '',
        staging_url: '',
        staging_api_key: '',
        production_url: '',
        production_api_key: '',
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

          <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>Project Details</Typography>

          <TextField
            fullWidth
            label="Project Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
            margin="normal"
            disabled={isPending}
            helperText="Example: Customer A, Internal Swisper"
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
            helperText="Optional description of this project"
          />

          <TextField
            fullWidth
            label="GitHub Repository URL (optional)"
            value={formData.github_repo_url}
            onChange={(e) => setFormData({ ...formData, github_repo_url: e.target.value })}
            margin="normal"
            placeholder="https://github.com/org/swisper"
            disabled={isPending}
            helperText="GitHub repo for config deployment (e.g., commit configs to Git)"
          />

          <TextField
            fullWidth
            type={showGitHubToken ? 'text' : 'password'}
            label="GitHub Personal Access Token (optional)"
            value={formData.github_token}
            onChange={(e) => setFormData({ ...formData, github_token: e.target.value })}
            margin="normal"
            placeholder="ghp_..."
            disabled={isPending}
            helperText="GitHub PAT with 'repo' scope for pushing config commits (Settings → Developer → Tokens)"
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={() => setShowGitHubToken(!showGitHubToken)} edge="end" size="small">
                    {showGitHubToken ? <VisibilityOffIcon /> : <VisibilityIcon />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />

          {/* Development Environment */}
          <Typography variant="h6" sx={{ mt: 3, mb: 1 }}>Development Environment</Typography>
          <TextField
            fullWidth
            label="Dev Swisper URL"
            value={formData.dev_url}
            onChange={(e) => setFormData({ ...formData, dev_url: e.target.value })}
            required
            margin="normal"
            placeholder="http://localhost:8000"
            disabled={isPending}
            helperText="URL of your development Swisper instance"
          />
          <TextField
            fullWidth
            type={showDevKey ? 'text' : 'password'}
            label="Dev Swisper API Key"
            value={formData.dev_api_key}
            onChange={(e) => setFormData({ ...formData, dev_api_key: e.target.value })}
            required
            margin="normal"
            disabled={isPending}
            helperText="API key to access Swisper SAP endpoints (for config management)"
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={() => setShowDevKey(!showDevKey)} edge="end" size="small">
                    {showDevKey ? <VisibilityOffIcon /> : <VisibilityIcon />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />

          {/* Staging Environment */}
          <Typography variant="h6" sx={{ mt: 3, mb: 1 }}>Staging Environment</Typography>
          <TextField
            fullWidth
            label="Staging Swisper URL"
            value={formData.staging_url}
            onChange={(e) => setFormData({ ...formData, staging_url: e.target.value })}
            required
            margin="normal"
            placeholder="https://staging.swisper.mycompany.com"
            disabled={isPending}
            helperText="URL of your staging Swisper instance"
          />
          <TextField
            fullWidth
            type={showStagingKey ? 'text' : 'password'}
            label="Staging Swisper API Key"
            value={formData.staging_api_key}
            onChange={(e) => setFormData({ ...formData, staging_api_key: e.target.value })}
            required
            margin="normal"
            disabled={isPending}
            helperText="API key for staging Swisper SAP endpoints"
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={() => setShowStagingKey(!showStagingKey)} edge="end" size="small">
                    {showStagingKey ? <VisibilityOffIcon /> : <VisibilityIcon />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />

          {/* Production Environment */}
          <Typography variant="h6" sx={{ mt: 3, mb: 1 }}>Production Environment</Typography>
          <TextField
            fullWidth
            label="Production Swisper URL"
            value={formData.production_url}
            onChange={(e) => setFormData({ ...formData, production_url: e.target.value })}
            required
            margin="normal"
            placeholder="https://swisper.mycompany.com"
            disabled={isPending}
            helperText="URL of your production Swisper instance"
          />
          <TextField
            fullWidth
            type={showProdKey ? 'text' : 'password'}
            label="Production Swisper API Key"
            value={formData.production_api_key}
            onChange={(e) => setFormData({ ...formData, production_api_key: e.target.value })}
            required
            margin="normal"
            disabled={isPending}
            helperText="API key for production Swisper SAP endpoints"
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={() => setShowProdKey(!showProdKey)} edge="end" size="small">
                    {showProdKey ? <VisibilityOffIcon /> : <VisibilityIcon />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
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

