/**
 * Delete project mutation hook
 * Following Swisper pattern: useMutation for DELETE
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export function useDeleteProjectMutation() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: (projectId: string) => apiClient.delete(`/projects/${projectId}`),
    onSuccess: () => {
      // Invalidate projects query to refetch list
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

