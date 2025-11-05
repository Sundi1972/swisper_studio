/**
 * Project Settings Page (Tabbed Version)
 * 
 * Tab 1: Project Details - Edit name, description, GitHub
 * Tab 2: Environments - Manage environment URLs (editable)
 * Tab 3: Integration Keys - Copy project ID, API key, SDK code
 */

import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Alert,
  IconButton,
  InputAdornment,
  Chip,
  Stack,
  Tabs,
  Tab,
} from '@mui/material';
import {
  ContentCopy as CopyIcon,
  Save as SaveIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Edit as EditIcon,
  Check as CheckIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

interface Environment {
  id: string;
  env_type: string;
  swisper_url: string;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index } = props;
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ py: 2 }}>{children}</Box>}
    </div>
  );
}

export function ProjectSettingsPage() {
  const { projectId } = useParams();
  const queryClient = useQueryClient();
  
  const [currentTab, setCurrentTab] = useState(0);
  const [showGitHubToken, setShowGitHubToken] = useState(false);
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [editingEnv, setEditingEnv] = useState<string | null>(null);
  const [editedUrl, setEditedUrl] = useState('');

  // Fetch project
  const { data: project, isLoading } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => apiClient.get(`/projects/${projectId}`),
  });

  // Fetch environments
  const { data: environments } = useQuery({
    queryKey: ['environments', projectId],
    queryFn: () => apiClient.get<Environment[]>(`/projects/${projectId}/environments`),
  });

  // Form state for project details
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    github_repo_url: '',
    github_token: '',
  });

  // Update form when project loads
  React.useEffect(() => {
    if (project) {
      setFormData({
        name: (project as any).name || '',
        description: (project as any).description || '',
        github_repo_url: (project as any).github_repo_url || '',
        github_token: '',
      });
    }
  }, [project]);

  // Update project mutation
  const updateProjectMutation = useMutation({
    mutationFn: (data: any) => apiClient.put(`/projects/${projectId}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', projectId] });
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });

  // Update environment mutation
  const updateEnvMutation = useMutation({
    mutationFn: ({ envId, url }: { envId: string; url: string }) => 
      apiClient.put(`/environments/${envId}`, { swisper_url: url }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['environments', projectId] });
      setEditingEnv(null);
    },
  });

  const handleCopy = async (text: string, fieldName: string) => {
    await navigator.clipboard.writeText(text);
    setCopiedField(fieldName);
    setTimeout(() => setCopiedField(null), 2000);
  };

  const handleSaveProject = () => {
    updateProjectMutation.mutate({
      name: formData.name,
      description: formData.description || undefined,
      github_repo_url: formData.github_repo_url || undefined,
      github_token: formData.github_token || undefined,
    });
  };

  const startEditingEnv = (env: Environment) => {
    setEditingEnv(env.id);
    setEditedUrl(env.swisper_url);
  };

  const cancelEditingEnv = () => {
    setEditingEnv(null);
    setEditedUrl('');
  };

  const saveEnvUrl = (envId: string) => {
    updateEnvMutation.mutate({ envId, url: editedUrl });
  };

  if (isLoading) {
    return <Box sx={{ p: 3 }}>Loading...</Box>;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Project Settings
      </Typography>

      {(updateProjectMutation.isSuccess || updateEnvMutation.isSuccess) && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => { 
          updateProjectMutation.reset(); 
          updateEnvMutation.reset(); 
        }}>
          Settings updated successfully!
        </Alert>
      )}

      {(updateProjectMutation.isError || updateEnvMutation.isError) && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Failed to update settings. Please try again.
        </Alert>
      )}

      {/* Tabs */}
      <Paper sx={{ mb: 2 }}>
        <Tabs value={currentTab} onChange={(_, newValue) => setCurrentTab(newValue)}>
          <Tab label="Project Details" />
          <Tab label="Environments" />
          <Tab label="Integration Keys" />
        </Tabs>
      </Paper>

      {/* Tab 1: Project Details */}
      <TabPanel value={currentTab} index={0}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Project Information
          </Typography>

          <Stack spacing={2}>
            <TextField
              fullWidth
              label="Project Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />

            <TextField
              fullWidth
              label="Description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              multiline
              rows={2}
            />

            <TextField
              fullWidth
              label="GitHub Repository URL"
              value={formData.github_repo_url}
              onChange={(e) => setFormData({ ...formData, github_repo_url: e.target.value })}
              placeholder="https://github.com/org/swisper"
              helperText="For config deployment via Git"
            />

            <TextField
              fullWidth
              type={showGitHubToken ? 'text' : 'password'}
              label="GitHub Personal Access Token"
              value={formData.github_token}
              onChange={(e) => setFormData({ ...formData, github_token: e.target.value })}
              placeholder="ghp_..."
              helperText="Leave empty to keep existing token. Scope: repo"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={() => setShowGitHubToken(!showGitHubToken)} edge="end">
                      {showGitHubToken ? <VisibilityOffIcon /> : <VisibilityIcon />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <Button
              variant="contained"
              startIcon={<SaveIcon />}
              onClick={handleSaveProject}
              disabled={updateProjectMutation.isPending}
            >
              {updateProjectMutation.isPending ? 'Saving...' : 'Save Changes'}
            </Button>
          </Stack>
        </Paper>
      </TabPanel>

      {/* Tab 2: Environments */}
      <TabPanel value={currentTab} index={1}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Environment Configuration
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Each environment connects to a different Swisper instance. URLs can be updated as your infrastructure changes.
          </Typography>

          {environments?.map((env) => (
            <Box key={env.id} sx={{ mb: 3, p: 2, border: 1, borderColor: 'divider', borderRadius: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Typography variant="subtitle1" sx={{ textTransform: 'uppercase', fontWeight: 'bold' }}>
                  {env.env_type}
                </Typography>
                <Chip 
                  label={env.env_type === 'production' ? 'PROD' : env.env_type === 'staging' ? 'STAGING' : 'DEV'} 
                  size="small" 
                  color={env.env_type === 'production' ? 'error' : env.env_type === 'staging' ? 'warning' : 'info'}
                  sx={{ ml: 1 }}
                />
              </Box>

              <Stack spacing={2}>
                {/* Environment ID (read-only) */}
                <TextField
                  fullWidth
                  label="Environment ID"
                  value={env.id}
                  InputProps={{
                    readOnly: true,
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton onClick={() => handleCopy(env.id, `env_id_${env.env_type}`)} edge="end">
                          {copiedField === `env_id_${env.env_type}` ? <CheckIcon color="success" /> : <CopyIcon />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                  size="small"
                />

                {/* Swisper Instance URL (editable) */}
                {editingEnv === env.id ? (
                  <Box>
                    <TextField
                      fullWidth
                      label="Swisper Instance URL"
                      value={editedUrl}
                      onChange={(e) => setEditedUrl(e.target.value)}
                      size="small"
                      autoFocus
                    />
                    <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                      <Button
                        size="small"
                        variant="contained"
                        startIcon={<CheckIcon />}
                        onClick={() => saveEnvUrl(env.id)}
                        disabled={updateEnvMutation.isPending}
                      >
                        Save
                      </Button>
                      <Button
                        size="small"
                        variant="outlined"
                        startIcon={<CloseIcon />}
                        onClick={cancelEditingEnv}
                      >
                        Cancel
                      </Button>
                    </Box>
                  </Box>
                ) : (
                  <TextField
                    fullWidth
                    label="Swisper Instance URL"
                    value={env.swisper_url}
                    InputProps={{
                      readOnly: true,
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton onClick={() => handleCopy(env.swisper_url, `url_${env.env_type}`)} edge="end">
                            {copiedField === `url_${env.env_type}` ? <CheckIcon color="success" /> : <CopyIcon />}
                          </IconButton>
                          <IconButton onClick={() => startEditingEnv(env)} edge="end" color="primary">
                            <EditIcon />
                          </IconButton>
                        </InputAdornment>
                      ),
                    }}
                    size="small"
                    helperText="Swisper instance URL for SAP endpoints"
                  />
                )}
              </Stack>
            </Box>
          ))}

          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="body2">
              <strong>Note:</strong> API keys are set during project creation and cannot be changed here for security. 
              To rotate API keys, contact your administrator.
            </Typography>
          </Alert>
        </Paper>
      </TabPanel>

      {/* Tab 3: Integration Keys */}
      <TabPanel value={currentTab} index={2}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            🔑 SDK Integration Keys
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Use these values when integrating Swisper with SwisperStudio (in your SDK initialization code)
          </Typography>

          <Stack spacing={2}>
            {/* Project ID */}
            <TextField
              fullWidth
              label="Project ID"
              value={(project as any)?.id || ''}
              InputProps={{
                readOnly: true,
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => handleCopy((project as any)?.id || '', 'project_id')}
                      edge="end"
                    >
                      {copiedField === 'project_id' ? <CheckIcon color="success" /> : <CopyIcon />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              helperText="Use this in SDK: project_id='...'"
            />

            {/* SwisperStudio API Key */}
            <TextField
              fullWidth
              label="SwisperStudio API Key"
              value="dev-api-key-change-in-production"
              InputProps={{
                readOnly: true,
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => handleCopy('dev-api-key-change-in-production', 'api_key')}
                      edge="end"
                    >
                      {copiedField === 'api_key' ? <CheckIcon color="success" /> : <CopyIcon />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              helperText="Use this in SDK: api_key='...'"
            />

            {/* SwisperStudio API URL */}
            <TextField
              fullWidth
              label="SwisperStudio API URL"
              value="http://localhost:8001"
              InputProps={{
                readOnly: true,
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => handleCopy('http://localhost:8001', 'api_url')}
                      edge="end"
                    >
                      {copiedField === 'api_url' ? <CheckIcon color="success" /> : <CopyIcon />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              helperText="Use this in SDK: api_url='...'"
            />
          </Stack>

          {/* SDK Code Snippet */}
          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle2" gutterBottom>
              SDK Initialization Code
            </Typography>
            <Box sx={{ p: 2, bgcolor: 'grey.900', borderRadius: 1, position: 'relative' }}>
              <Box
                component="pre"
                sx={{ 
                  m: 0,
                  fontSize: '0.875rem',
                  color: 'success.light',
                  overflow: 'auto',
                  fontFamily: 'monospace',
                }}
              >
{`from swisper_studio_sdk import initialize_tracing

initialize_tracing(
    api_url="http://localhost:8001",
    api_key="dev-api-key-change-in-production",
    project_id="${(project as any)?.id || 'PROJECT_ID'}",
    enabled=True
)`}
              </Box>
            </Box>
            <Button
              size="small"
              variant="outlined"
              startIcon={copiedField === 'sdk_code' ? <CheckIcon /> : <CopyIcon />}
              onClick={() => handleCopy(
                `from swisper_studio_sdk import initialize_tracing\n\ninitialize_tracing(\n    api_url="http://localhost:8001",\n    api_key="dev-api-key-change-in-production",\n    project_id="${(project as any)?.id}",\n    enabled=True\n)`,
                'sdk_code'
              )}
              sx={{ mt: 1 }}
            >
              {copiedField === 'sdk_code' ? 'Copied!' : 'Copy Code'}
            </Button>
          </Box>

          <Alert severity="info" sx={{ mt: 3 }}>
            <Typography variant="body2">
              <strong>Next Steps:</strong><br />
              1. Install SDK: <code>uv pip install -e /path/to/swisper_studio/sdk</code><br />
              2. Add initialization code to Swisper's <code>main.py</code><br />
              3. Wrap your graph: <code>create_traced_graph(YourState, trace_name="...")</code><br />
              4. Send a test request and check SwisperStudio!
            </Typography>
          </Alert>
        </Paper>
      </TabPanel>
    </Box>
  );
}

