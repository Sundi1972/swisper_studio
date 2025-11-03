/**
 * Auth storage utilities
 * Manages JWT token and user data in localStorage
 */

import type { User } from '@/types/auth';

const TOKEN_STORAGE_KEY = 'swisper_studio_token';
const USER_STORAGE_KEY = 'swisper_studio_user';
const API_KEY_STORAGE_KEY = 'swisper_studio_api_key'; // Keep for backward compat

/**
 * JWT Token storage
 */
export function storeToken(token: string): void {
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
}

/**
 * User data storage
 */
export function storeUser(user: User): void {
  localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
}

export function getUser(): User | null {
  const userJson = localStorage.getItem(USER_STORAGE_KEY);
  if (!userJson) return null;
  
  try {
    return JSON.parse(userJson) as User;
  } catch {
    return null;
  }
}

export function clearUser(): void {
  localStorage.removeItem(USER_STORAGE_KEY);
}

/**
 * Clear all auth data
 */
export function clearAuth(): void {
  clearToken();
  clearUser();
  clearApiKey(); // Also clear old API key
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return getToken() !== null && getUser() !== null;
}

/**
 * Legacy API key storage (backward compatibility)
 */
export function storeApiKey(apiKey: string): void {
  localStorage.setItem(API_KEY_STORAGE_KEY, apiKey);
}

export function getApiKey(): string | null {
  return localStorage.getItem(API_KEY_STORAGE_KEY);
}

export function clearApiKey(): void {
  localStorage.removeItem(API_KEY_STORAGE_KEY);
}


