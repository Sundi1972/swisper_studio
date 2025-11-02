/**
 * Traces query hook
 * Following Swisper pattern: useQuery for GET requests
 */

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import type { TraceListResponse } from '../types';

export function useTracesQuery(projectId: string, page: number = 1) {
  return useQuery<TraceListResponse>({
    queryKey: ['traces', projectId, page],
    queryFn: () => apiClient.get<TraceListResponse>(`/traces?project_id=${projectId}&page=${page}&limit=50`),
    enabled: !!projectId,
  });
}

