/**
 * Project list page
 * Following Swisper patterns: MUI components, styled components, kebab-case filename
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardActions from '@mui/material/CardActions';
import CircularProgress from '@mui/material/CircularProgress';
import IconButton from '@mui/material/IconButton';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import AddIcon from '@mui/icons-material/Add';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import DeleteIcon from '@mui/icons-material/Delete';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import { styled } from '@mui/material/styles';

import { useProjectsQuery } from '../hooks/use-projects-query';
import { useDeleteProjectMutation } from '../hooks/use-delete-project-mutation';
import { ProjectCreateDialog } from './project-create-dialog';

const Container = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
}));

const ProjectGrid = styled(Box)(({ theme }) => ({
  display: 'grid',
  gap: theme.spacing(2),
  gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
  marginTop: theme.spacing(3),
}));

interface ProjectMenuState {
  anchorEl: HTMLElement | null;
  projectId: string | null;
}

export function ProjectListPage() {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [menuState, setMenuState] = useState<ProjectMenuState>({ anchorEl: null, projectId: null });
  const navigate = useNavigate();
  const { data, isLoading } = useProjectsQuery();
  const { mutateAsync: deleteProject } = useDeleteProjectMutation();

  function handleMenuOpen(event: React.MouseEvent<HTMLElement>, projectId: string) {
    setMenuState({ anchorEl: event.currentTarget, projectId });
  }

  function handleMenuClose() {
    setMenuState({ anchorEl: null, projectId: null });
  }

  async function handleDelete() {
    if (menuState.projectId) {
      try {
        await deleteProject(menuState.projectId);
        handleMenuClose();
      } catch (error) {
        console.error('Failed to delete project:', error);
      }
    }
  }

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container data-testid="project-list-page">
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h4">Projects</Typography>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            startIcon={<AccountTreeIcon />}
            onClick={() => navigate('/swisper-builder')}
          >
            Swisper Builder
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setIsCreateDialogOpen(true)}
          >
            New Project
          </Button>
        </Box>
      </Box>

      <ProjectGrid>
        {data?.data.map((project) => (
          <Card key={project.id}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                <Box flex={1}>
                  <Typography variant="h6" gutterBottom>
                    {project.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {project.swisper_url}
                  </Typography>
                  {project.description && (
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      {project.description}
                    </Typography>
                  )}
                </Box>
                <IconButton
                  size="small"
                  onClick={(e) => handleMenuOpen(e, project.id)}
                >
                  <MoreVertIcon />
                </IconButton>
              </Box>
            </CardContent>
            <CardActions>
              <Button
                size="small"
                onClick={() => navigate(`/projects/${project.id}`)}
              >
                Open Project
              </Button>
            </CardActions>
          </Card>
        ))}
      </ProjectGrid>

      <Menu
        anchorEl={menuState.anchorEl}
        open={Boolean(menuState.anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleDelete}>
          <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
          Delete Project
        </MenuItem>
      </Menu>

      {data?.data.length === 0 && (
        <Box textAlign="center" mt={4}>
          <Typography variant="body1" color="text.secondary">
            No projects yet. Create your first project to get started.
          </Typography>
        </Box>
      )}

      <ProjectCreateDialog
        isOpen={isCreateDialogOpen}
        onClose={() => setIsCreateDialogOpen(false)}
      />
    </Container>
  );
}

