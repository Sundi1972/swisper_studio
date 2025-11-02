import { Box, Typography, Card, CardContent, Button, Stack, Paper } from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import { Search as SearchIcon, Settings as SettingsIcon } from '@mui/icons-material';
import { useProject } from '../hooks/use-project';

/**
 * Project overview/dashboard page.
 * 
 * Landing page when user clicks a project card.
 * 
 * MVP version: Simple landing page with quick actions
 * Post-MVP: Key metrics (total traces, total cost, error rate, recent traces)
 */
export function ProjectOverview() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { data: project, isLoading } = useProject(projectId!);

  if (isLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography>Loading project...</Typography>
      </Box>
    );
  }

  if (!project) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography color="error">Project not found</Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Welcome section */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          {project.name}
        </Typography>
        {project.description && (
          <Typography variant="body1" color="text.secondary" gutterBottom>
            {project.description}
          </Typography>
        )}
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Swisper URL: {project.swisper_url}
        </Typography>
      </Paper>

      {/* Quick actions */}
      <Typography variant="h6" gutterBottom sx={{ mt: 4, mb: 2 }}>
        Quick Actions
      </Typography>
      
      <Stack direction="row" spacing={2}>
        <Card sx={{ minWidth: 250 }}>
          <CardContent>
            <SearchIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
            <Typography variant="h6" gutterBottom>
              View Traces
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Explore execution traces and debug with full context
            </Typography>
            <Button
              variant="contained"
              fullWidth
              onClick={() => navigate(`/projects/${projectId}/tracing`)}
            >
              Go to Tracing
            </Button>
          </CardContent>
        </Card>

        <Card sx={{ minWidth: 250 }}>
          <CardContent>
            <SettingsIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
            <Typography variant="h6" gutterBottom>
              Configuration
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              View model pricing and project settings
            </Typography>
            <Button
              variant="outlined"
              fullWidth
              onClick={() => navigate(`/projects/${projectId}/config`)}
            >
              View Config
            </Button>
          </CardContent>
        </Card>
      </Stack>

      {/* Placeholder for future metrics */}
      <Box sx={{ mt: 4, p: 2, bgcolor: 'action.hover', borderRadius: 1 }}>
        <Typography variant="body2" color="text.secondary">
          📊 Key metrics dashboard coming in future phases (total traces, costs, error rates)
        </Typography>
      </Box>
    </Box>
  );
}

