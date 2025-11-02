/**
 * Project types
 */

export interface Project {
  id: string;
  name: string;
  swisper_url: string;
  description: string | null;
  meta: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export interface ProjectListResponse {
  data: Project[];
  meta: {
    page: number;
    limit: number;
    total_items: number;
    total_pages: number;
  };
}

export interface ProjectCreatePayload {
  name: string;
  swisper_url: string;
  swisper_api_key: string;
  description?: string;
}

