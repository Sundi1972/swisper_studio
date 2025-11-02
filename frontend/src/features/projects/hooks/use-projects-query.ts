/**
 * Projects query hook
 * Following Swisper pattern: useQuery for GET requests
 */

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import type { ProjectListResponse } from '../types';

export function useProjectsQuery() {
  return useQuery<ProjectListResponse>({
    queryKey: ['projects'],
    queryFn: () => apiClient.get<ProjectListResponse>('/projects'),
  });
}

