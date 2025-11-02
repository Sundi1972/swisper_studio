import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../../lib/api-client';

export interface Project {
  id: string;
  name: string;
  swisper_url: string;
  description: string | null;
  meta: Record<string, any> | null;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

/**
 * Fetch a single project by ID.
 * 
 * Used by project header and overview page to display project details.
 */
export function useProject(projectId: string) {
  return useQuery({
    queryKey: ['project', projectId],
    queryFn: async () => {
      return apiClient.get<Project>(`/projects/${projectId}`);
    },
    staleTime: 60000, // Cache for 1 minute
  });
}

