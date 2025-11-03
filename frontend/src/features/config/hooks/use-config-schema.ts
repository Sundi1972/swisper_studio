import { useQuery } from '@tanstack/react-query';
import type { ConfigSchema } from '../types';
import { useEnvironment } from '../../../contexts/environment-context';

export function useConfigSchema(projectId: string, environmentId?: string) {
  const { currentEnvironment } = useEnvironment();
  
  return useQuery({
    queryKey: ['config-schema', projectId, environmentId],
    queryFn: async () => {
      if (!currentEnvironment) return null;
      
      // Fetch schema directly from Swisper SAP (full URL, bypass apiClient)
      const url = `${currentEnvironment.swisper_url}/api/admin/config/schema`;
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch schema: ${response.statusText}`);
      }
      
      const data: ConfigSchema = await response.json();
      return data;
    },
    enabled: !!projectId && !!currentEnvironment,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

