/**
 * Users API client
 */

import { apiClient } from '@/lib/api-client';
import type { User } from '@/types/auth';

export interface ListUsersResponse {
  users: User[];
  total: number;
  limit: number;
  offset: number;
}

export interface UpdateUserRequest {
  name?: string;
  role?: string;
  is_active?: boolean;
}

/**
 * List all users (admin only)
 */
export async function listUsers(params?: {
  limit?: number;
  offset?: number;
  role?: string;
  is_active?: boolean;
}): Promise<ListUsersResponse> {
  const queryParams = new URLSearchParams();
  if (params?.limit) queryParams.set('limit', params.limit.toString());
  if (params?.offset) queryParams.set('offset', params.offset.toString());
  if (params?.role) queryParams.set('role', params.role);
  if (params?.is_active !== undefined) queryParams.set('is_active', params.is_active.toString());

  const query = queryParams.toString();
  return apiClient.get<ListUsersResponse>(`/users${query ? `?${query}` : ''}`);
}

/**
 * Update user (admin only)
 */
export async function updateUser(userId: string, data: UpdateUserRequest): Promise<User> {
  return apiClient.patch<User>(`/users/${userId}`, data);
}

