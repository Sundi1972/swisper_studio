import { Box, Container } from '@mui/material';
import { Outlet, useParams } from 'react-router-dom';
import { ProjectSidebar } from './project-sidebar';
import { ProjectHeader } from './project-header';

/**
 * Project workspace layout with persistent sidebar navigation.
 * 
 * Used for all pages within a project context (overview, tracing, analytics, config).
 * Provides consistent navigation and project context across features.
 */
export function ProjectLayout() {
  const { projectId } = useParams<{ projectId: string }>();

  if (!projectId) {
    return <div>Error: No project ID</div>;
  }

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar - fixed width, persistent across project pages */}
      <ProjectSidebar projectId={projectId} />
      
      {/* Main content area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          bgcolor: 'background.default',
          minHeight: '100vh',
        }}
      >
        {/* Project header */}
        <ProjectHeader projectId={projectId} />
        
        {/* Page content from nested routes */}
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
          <Outlet />
        </Container>
      </Box>
    </Box>
  );
}

