import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Button,
  Box,
  Chip,
  Divider
} from '@mui/material';
import { formatDistanceToNow } from 'date-fns';
import type { ConfigVersion } from '../types';
import type { Environment } from '../../../contexts/environment-context';

interface VersionHistoryProps {
  versions: ConfigVersion[];
  onDeploy: (versionId: string) => Promise<void>;
  currentEnvironment: Environment;
  deploymentLoading?: boolean;
}

export function VersionHistory({
  versions,
  onDeploy,
  currentEnvironment,
  deploymentLoading
}: VersionHistoryProps) {
  return (
    <Card>
      <CardHeader title="Version History" />
      <CardContent>
        {versions.length === 0 && (
          <Typography variant="body2" color="text.secondary">
            No versions yet. Save your first version above.
          </Typography>
        )}
        
        {versions.map((version, index) => (
          <Box key={version.id}>
            {index > 0 && <Divider sx={{ my: 2 }} />}
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
              <Box sx={{ flexGrow: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <Chip
                    label={`v${version.version_number}`}
                    size="small"
                    color="primary"
                  />
                  {version.description && (
                    <Typography variant="body2" color="text.secondary">
                      {version.description}
                    </Typography>
                  )}
                </Box>
                
                <Typography variant="caption" color="text.secondary" display="block">
                  Created {formatDistanceToNow(new Date(version.created_at), { addSuffix: true })}
                  {' by '}{version.created_by}
                </Typography>
                
                <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
                  Config: {Object.keys(version.config_data).length} fields
                </Typography>
              </Box>
              
              <Button
                size="small"
                variant="outlined"
                onClick={() => onDeploy(version.id)}
                disabled={deploymentLoading}
              >
                Deploy to {currentEnvironment.env_type}
              </Button>
            </Box>
          </Box>
        ))}
      </CardContent>
    </Card>
  );
}

