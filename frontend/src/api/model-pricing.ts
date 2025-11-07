/**
 * Model Pricing API client
 */

import { apiClient } from '@/lib/api-client';

export interface ModelPricing {
  id: string;
  project_id: string | null;
  hosting_provider: string;
  model_name: string;
  type: string;
  description: string | null;
  input_price_per_million: string; // Decimal from backend comes as string
  output_price_per_million: string; // Decimal from backend comes as string
  created_at: string;
  updated_at: string;
}

export interface CreateModelPricingRequest {
  hosting_provider: string;
  model_name: string;
  type: string;
  description?: string;
  input_price_per_million: number;
  output_price_per_million: number;
}

export interface UpdateModelPricingRequest {
  hosting_provider?: string;
  model_name?: string;
  type?: string;
  description?: string;
  input_price_per_million?: number;
  output_price_per_million?: number;
}

/**
 * List all global model pricing (admin only)
 */
export async function listModelPricing(): Promise<ModelPricing[]> {
  return apiClient.get<ModelPricing[]>('/model-pricing');
}

/**
 * Create new model pricing (admin only)
 */
export async function createModelPricing(data: CreateModelPricingRequest): Promise<ModelPricing> {
  return apiClient.post<ModelPricing>('/model-pricing', data);
}

/**
 * Update model pricing (admin only)
 */
export async function updateModelPricing(
  pricingId: string,
  data: UpdateModelPricingRequest
): Promise<ModelPricing> {
  return apiClient.put<ModelPricing>(`/model-pricing/${pricingId}`, data);
}

/**
 * Delete model pricing (admin only)
 */
export async function deleteModelPricing(pricingId: string): Promise<void> {
  return apiClient.delete(`/model-pricing/${pricingId}`);
}

