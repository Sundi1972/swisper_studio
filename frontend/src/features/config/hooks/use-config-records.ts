import { useQuery } from '@tanstack/react-query';
import type { ConfigRecordsResponse } from '../types';
import { useEnvironment } from '../../../contexts/environment-context';

export function useConfigRecords(projectId: string, tableName: string) {
  const { currentEnvironment } = useEnvironment();
  
  return useQuery({
    queryKey: ['config-records', projectId, tableName, currentEnvironment?.id],
    queryFn: async () => {
      if (!currentEnvironment) return null;
      
      // Fetch records directly from Swisper SAP (full URL, bypass apiClient)
      const url = `${currentEnvironment.swisper_url}/api/admin/config/${tableName}`;
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch records: ${response.statusText}`);
      }
      
      const data: ConfigRecordsResponse = await response.json();
      return data;
    },
    enabled: !!projectId && !!tableName && !!currentEnvironment,
  });
}

