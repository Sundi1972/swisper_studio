/**
 * Create project mutation hook
 * Following Swisper pattern: useMutation for POST/PUT/DELETE
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import type { Project, ProjectCreatePayload } from '../types';

export function useCreateProjectMutation() {
  const queryClient = useQueryClient();

  return useMutation<Project, Error, ProjectCreatePayload>({
    mutationFn: (payload) => apiClient.post<Project>('/projects', payload),
    onSuccess: () => {
      // Invalidate projects query to refetch list
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

