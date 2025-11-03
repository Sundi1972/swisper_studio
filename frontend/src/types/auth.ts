/**
 * Authentication type definitions
 */

export type UserRole = 'admin' | 'developer' | 'qa' | 'viewer';

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  last_login: string | null;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

export interface AuthResponse {
  user: User;
  token: string;
  token_type: string;
}

export interface MessageResponse {
  message: string;
}

