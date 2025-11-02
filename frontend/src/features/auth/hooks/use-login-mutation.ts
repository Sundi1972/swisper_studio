/**
 * Login mutation hook
 * Following Swisper pattern: useMutation for POST/PUT/DELETE
 */

import { useMutation } from '@tanstack/react-query';
import { storeApiKey } from '../utils/auth-storage';

interface LoginPayload {
  apiKey: string;
}

export function useLoginMutation() {
  return useMutation<void, Error, LoginPayload>({
    mutationFn: async ({ apiKey }) => {
      // Validate API key by calling backend health endpoint (via Vite proxy)
      const response = await fetch('/api/health', {
        headers: { 'X-API-Key': apiKey },
      });

      if (!response.ok) {
        throw new Error('Invalid API key');
      }

      // Store in localStorage
      storeApiKey(apiKey);
    },
  });
}

