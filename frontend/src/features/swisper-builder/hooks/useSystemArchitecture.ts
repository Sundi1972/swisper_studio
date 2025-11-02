/**
 * Hook to fetch system architecture data (all agent graphs)
 * Calls: GET /api/v1/system-architecture
 */

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { SystemArchitectureData } from "@/components/graph";

export function useSystemArchitecture() {
  return useQuery({
    queryKey: ["system-architecture"],
    queryFn: async () => {
      const data = await apiClient.get<SystemArchitectureData>(
        "/system-architecture"
      );
      return data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes (static data, rarely changes)
  });
}

