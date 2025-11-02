/**
 * Hook to fetch graph data for a single trace
 * Calls: GET /api/v1/traces/{traceId}/graph
 */

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { GraphData } from "@/components/graph";

export function useTraceGraph(traceId: string) {
  return useQuery({
    queryKey: ["trace-graph", traceId],
    queryFn: async () => {
      const data = await apiClient.get<GraphData>(`/traces/${traceId}/graph`);
      return data;
    },
    enabled: !!traceId, // Only run query if traceId is provided
  });
}

