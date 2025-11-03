/**
 * Login mutation hook
 * Updated for JWT authentication with email + password
 */

import { useMutation } from '@tanstack/react-query';
import { storeToken, storeUser } from '../utils/auth-storage';
import type { LoginRequest, AuthResponse } from '@/types/auth';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

export function useLoginMutation() {
  return useMutation<AuthResponse, Error, LoginRequest>({
    mutationFn: async ({ email, password }) => {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Login failed');
      }

      const data: AuthResponse = await response.json();
      
      // Store token and user in localStorage
      storeToken(data.token);
      storeUser(data.user);

      return data;
    },
  });
}


