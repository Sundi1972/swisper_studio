import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../../../lib/api-client';
import type { ConfigVersion } from '../types';

export function useConfigVersions(
  projectId: string,
  tableName?: string,
  recordId?: string
) {
  return useQuery({
    queryKey: ['config-versions', projectId, tableName, recordId],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (tableName) params.append('table_name', tableName);
      if (recordId) params.append('record_id', recordId);
      
      return await apiClient.get<ConfigVersion[]>(
        `/projects/${projectId}/config/versions?${params}`
      );
    },
    enabled: !!projectId && !!tableName && !!recordId,
  });
}

export function useCreateVersion(projectId: string) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: {
      table_name: string;
      record_id: string;
      config_data: any;
      description?: string;
      created_by: string;
    }) => {
      return await apiClient.post<ConfigVersion>(
        `/projects/${projectId}/config/versions`,
        data
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['config-versions', projectId] });
    },
  });
}

export function useDeployVersion(projectId: string) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({
      environmentId,
      versionId,
      deployedBy,
    }: {
      environmentId: string;
      versionId: string;
      deployedBy: string;
    }) => {
      return await apiClient.post<any>(
        `/projects/${projectId}/environments/${environmentId}/deploy`,
        { version_id: versionId, deployed_by: deployedBy }
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['config-versions'] });
      queryClient.invalidateQueries({ queryKey: ['deployments'] });
    },
  });
}

