/**
 * Trace types
 */

export interface Trace {
  id: string;
  project_id: string;
  name: string | null;
  user_id: string | null;
  session_id: string | null;
  timestamp: string;
}

export interface TraceListResponse {
  data: Trace[];
  meta: {
    page: number;
    limit: number;
    total_items: number;
    total_pages: number;
  };
}

