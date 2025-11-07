import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../../lib/api-client';

export interface TraceInfo {
  id: string;
  project_id: string;
  name: string | null;
  user_id: string | null;
  session_id: string | null;
  timestamp: string;
}

export interface ObservationNode {
  id: string;
  trace_id: string;
  parent_observation_id: string | null;
  type: string;
  name: string | null;
  start_time: string;
  end_time: string | null;
  completion_start_time: string | null;
  latency_ms: number | null;
  model: string | null;
  model_parameters: Record<string, any> | null;
  prompt_tokens: number | null;
  completion_tokens: number | null;
  total_tokens: number | null;
  calculated_input_cost: string | null;
  calculated_output_cost: string | null;
  calculated_total_cost: string | null;
  input: Record<string, any> | null;
  output: Record<string, any> | null;
  meta: Record<string, any> | null;
  level: string;
  status_message: string | null;
  children: ObservationNode[];
  total_cost: string | null;
  total_duration_ms: number | null;
}

export interface TraceDetail {
  trace: TraceInfo;
  tree: ObservationNode[];
  total_cost: string | null;
}

/**
 * Fetch trace with observation tree.
 * 
 * Combines trace info with observation tree for rich detail view.
 */
export function useTraceDetail(traceId: string) {
  return useQuery({
    queryKey: ['trace-detail', traceId],
    queryFn: async () => {
      // Fetch trace and tree in parallel
      const [trace, tree] = await Promise.all([
        apiClient.get<TraceInfo>(`/traces/${traceId}`),
        apiClient.get<ObservationNode[]>(`/traces/${traceId}/tree`)
      ]);

      // Calculate total cost from tree
      const calculateTotalCost = (nodes: ObservationNode[]): number => {
        return nodes.reduce((sum, node) => {
          const nodeCost = node.calculated_total_cost ? parseFloat(node.calculated_total_cost) : 0;
          const childrenCost = calculateTotalCost(node.children);
          return sum + nodeCost + childrenCost;
        }, 0);
      };

      const totalCost = calculateTotalCost(tree);

      return {
        trace,
        tree,
        total_cost: totalCost > 0 ? totalCost.toString() : null
      } as TraceDetail;
    },
    staleTime: 30000, // Cache for 30 seconds
  });
}

