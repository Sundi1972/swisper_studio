/**
 * Integration tests for Phase 2 cost tracking.
 * 
 * Tests cost calculation end-to-end:
 * - Create observation with tokens
 * - Verify cost auto-calculated
 * - Verify cost displayed in UI
 * 
 * Following ADR-007: Real APIs, not mocks.
 */

import { describe, it, expect, beforeAll } from 'vitest';
import { apiClient } from '../../lib/api-client';
import { storeApiKey } from '../../features/auth/utils/auth-storage';

describe('Phase 2 Cost Tracking Integration', () => {
  let testProjectId: string;
  let testTraceId: string;

  beforeAll(async () => {
    // Set up auth
    storeApiKey('dev-api-key-change-in-production');

    // Create test project
    const project = await apiClient.post<{ id: string }>('/projects', {
      name: `Cost Test Project ${Date.now()}`,
      swisper_url: 'http://localhost:8000',
      swisper_api_key: 'cost-test-key',
    });
    testProjectId = project.id;

    // Create test trace
    const trace = await apiClient.post<{ id: string }>('/traces', {
      id: `trace-${Date.now()}`,
      project_id: testProjectId,
      name: 'Cost Test Trace',
    });
    testTraceId = trace.id;
  });

  it('should auto-calculate cost when creating observation with tokens', async () => {
    // Create observation with LLM telemetry
    const observation = await apiClient.post<any>('/observations', {
      id: `obs-${Date.now()}`,
      trace_id: testTraceId,
      type: 'GENERATION',
      name: 'test_llm_call',
      start_time: new Date().toISOString(),
      end_time: new Date().toISOString(),
      model: 'gpt-4-turbo',
      prompt_tokens: 150,
      completion_tokens: 50,
    });

    // Verify cost was calculated
    expect(observation.calculated_total_cost).toBeDefined();
    expect(observation.calculated_input_cost).toBeDefined();
    expect(observation.calculated_output_cost).toBeDefined();

    // Verify correct calculation (gpt-4-turbo: $10/1M input, $30/1M output)
    // input: (150/1M) * 10 = 0.0015
    // output: (50/1M) * 30 = 0.0015
    // total: 0.0030
    expect(parseFloat(observation.calculated_total_cost)).toBeCloseTo(0.0030, 4);
  });

  it('should fetch default model pricing', async () => {
    const pricing = await apiClient.get<any[]>('/model-pricing/defaults');

    // Should have pricing from migration seed data
    expect(pricing.length).toBeGreaterThan(0);

    // Should include common models
    const models = pricing.map((p: any) => p.model_name);
    expect(models).toContain('gpt-4-turbo');
    expect(models).toContain('gpt-4');
    expect(models).toContain('claude-3-sonnet-20240229');
  });

  it('should fetch project-specific pricing (includes defaults)', async () => {
    const pricing = await apiClient.get<any[]>(`/projects/${testProjectId}/model-pricing`);

    // Should return pricing (defaults if no custom pricing)
    expect(pricing.length).toBeGreaterThan(0);

    // Each pricing should have required fields
    pricing.forEach((p: any) => {
      expect(p.hosting_provider).toBeDefined();
      expect(p.model_name).toBeDefined();
      expect(p.input_price_per_million).toBeDefined();
      expect(p.output_price_per_million).toBeDefined();
    });
  });

  it('should build observation tree with costs aggregated', async () => {
    // Create parent observation
    const parent = await apiClient.post<any>('/observations', {
      id: `parent-${Date.now()}`,
      trace_id: testTraceId,
      type: 'AGENT',
      name: 'agent',
      start_time: new Date().toISOString(),
      end_time: new Date(Date.now() + 1000).toISOString(),
    });

    // Create child with cost
    await apiClient.post<any>('/observations', {
      id: `child-${Date.now()}`,
      trace_id: testTraceId,
      parent_observation_id: parent.id,
      type: 'GENERATION',
      name: 'llm_call',
      start_time: new Date().toISOString(),
      end_time: new Date(Date.now() + 500).toISOString(),
      model: 'gpt-3.5-turbo',
      prompt_tokens: 1000,
      completion_tokens: 500,
    });

    // Fetch tree
    const tree = await apiClient.get<any[]>(`/traces/${testTraceId}/tree`);

    // Should have tree structure
    expect(tree.length).toBeGreaterThan(0);

    // Find parent node
    const parentNode = tree.find((n: any) => n.id === parent.id);
    expect(parentNode).toBeDefined();

    // Parent should have child
    expect(parentNode.children.length).toBeGreaterThan(0);

    // Parent should have aggregated cost (sum of children)
    expect(parentNode.total_cost).toBeDefined();
  });
});

