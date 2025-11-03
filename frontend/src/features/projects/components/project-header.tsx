import { AppBar, Toolbar, Typography, Chip, Box, Breadcrumbs, Link } from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useProject } from '../hooks/use-project';
import { EnvironmentSelector } from '../../../components/environment-selector';
import { useEnvironments } from '../../config/hooks/use-environments';
import { UserMenu } from '../../auth/components/user-menu';

interface ProjectHeaderProps {
  projectId: string;
}

/**
 * Project header with breadcrumbs and project info.
 * 
 * Shows:
 * - Breadcrumb navigation (Projects > Project Name > Current Page)
 * - Project name and environment badge
 */
export function ProjectHeader({ projectId }: ProjectHeaderProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { data: project, isLoading } = useProject(projectId);
  
  // Load environments for this project (updates context)
  useEnvironments(projectId);

  // Extract current page from path
  const pathSegments = location.pathname.split('/').filter(Boolean);
  const currentPage = pathSegments[pathSegments.length - 1];
  
  // Map path segment to display name
  const getPageName = (segment: string): string => {
    const pageNames: Record<string, string> = {
      tracing: 'Tracing',
      analytics: 'Analytics',
      graphs: 'Graphs',
      config: 'Configuration',
    };
    return pageNames[segment] || 'Overview';
  };

  if (isLoading) {
    return (
      <AppBar position="static" color="default" elevation={0}>
        <Toolbar>
          <Typography variant="h6">Loading...</Typography>
        </Toolbar>
      </AppBar>
    );
  }

  return (
    <AppBar position="static" color="default" elevation={0} sx={{ borderBottom: 1, borderColor: 'divider' }}>
      <Toolbar>
        <Box sx={{ flexGrow: 1 }}>
          {/* Breadcrumbs */}
          <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 0.5 }}>
            <Link
              underline="hover"
              color="inherit"
              sx={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 0.5 }}
              onClick={() => navigate('/projects')}
            >
              <Typography variant="body2" component="span" fontWeight="bold">SwisperStudio</Typography>
            </Link>
            <Link
              underline="hover"
              color="inherit"
              sx={{ cursor: 'pointer' }}
              onClick={() => navigate(`/projects/${projectId}`)}
            >
              {project?.name || 'Project'}
            </Link>
            {currentPage !== projectId && (
              <Typography color="text.primary">
                {getPageName(currentPage)}
              </Typography>
            )}
          </Breadcrumbs>
          
          {/* Project name and environment */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
            <Typography variant="h6" component="h1">
              {project?.name || 'Project'}
            </Typography>
            {project?.description && (
              <Chip
                label={project.description}
                size="small"
                variant="outlined"
              />
            )}
          </Box>
        </Box>
        
        {/* Environment Selector */}
        <EnvironmentSelector />
        
        {/* User Menu */}
        <Box sx={{ ml: 2 }}>
          <UserMenu />
        </Box>
      </Toolbar>
    </AppBar>
  );
}

