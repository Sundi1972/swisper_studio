import { Box, Typography, Paper, Alert } from '@mui/material';
import { useParams } from 'react-router-dom';

/**
 * Configuration page (Phase 2: Read-only).
 * 
 * MVP version: Simple placeholder showing that config UI is coming.
 * Phase 4: Full configuration management (model pricing CRUD, project settings, API keys)
 */
export function ConfigPage() {
  const { projectId } = useParams<{ projectId: string }>();

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Configuration
      </Typography>
      
      <Alert severity="info" sx={{ mb: 3 }}>
        Full configuration UI coming in Phase 4. For now, model pricing is managed via database.
      </Alert>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Project Settings
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Project ID: {projectId}
        </Typography>
        
        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          Model Pricing
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Model pricing is configured in the database. Default pricing for common models is available.
          Custom project-specific pricing can be added via database directly.
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Phase 4 will add UI for managing pricing, API keys, and team members.
        </Typography>
      </Paper>
    </Box>
  );
}

