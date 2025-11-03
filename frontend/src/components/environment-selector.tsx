import { Select, MenuItem, Box, Chip } from '@mui/material';
import { useEnvironment } from '../contexts/environment-context';

export function EnvironmentSelector() {
  const { currentEnvironment, environments, setCurrentEnvironment } = useEnvironment();

  const getEnvColor = (envType: string): 'info' | 'warning' | 'error' | 'default' => {
    switch (envType) {
      case 'dev':
        return 'info';
      case 'staging':
        return 'warning';
      case 'production':
        return 'error';
      default:
        return 'default';
    }
  };

  if (environments.length === 0) {
    return null;
  }

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
      <Select
        value={currentEnvironment?.id || ''}
        onChange={(e) => {
          const env = environments.find((env) => env.id === e.target.value);
          if (env) setCurrentEnvironment(env);
        }}
        size="small"
        sx={{ 
          minWidth: 180,
          bgcolor: 'background.paper',
          '& .MuiSelect-select': {
            display: 'flex',
            alignItems: 'center',
            gap: 1
          }
        }}
      >
        {environments.map((env) => (
          <MenuItem key={env.id} value={env.id}>
            <Chip
              label={env.env_type.toUpperCase()}
              color={getEnvColor(env.env_type)}
              size="small"
              sx={{ mr: 1 }}
            />
            {env.env_type}
          </MenuItem>
        ))}
      </Select>
      
      {currentEnvironment && (
        <Box sx={{ fontSize: '0.75rem', color: 'text.secondary', maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis' }}>
          {currentEnvironment.swisper_url}
        </Box>
      )}
    </Box>
  );
}

