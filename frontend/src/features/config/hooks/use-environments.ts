import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../../../lib/api-client';
import { Environment } from '../../../contexts/environment-context';
import { useEnvironment } from '../../../contexts/environment-context';
import { useEffect } from 'react';

export function useEnvironments(projectId: string) {
  const { setEnvironments } = useEnvironment();
  
  const query = useQuery({
    queryKey: ['environments', projectId],
    queryFn: async () => {
      return await apiClient.get<Environment[]>(
        `/projects/${projectId}/environments`
      );
    },
    enabled: !!projectId,
  });

  // Update context when environments load
  useEffect(() => {
    if (query.data) {
      setEnvironments(query.data);
    }
  }, [query.data, setEnvironments]);

  return query;
}

export function useUpdateEnvironment(environmentId: string) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: { swisper_url: string; swisper_api_key: string }) => {
      return await apiClient.put(
        `/environments/${environmentId}`,
        data
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['environments'] });
    },
  });
}

