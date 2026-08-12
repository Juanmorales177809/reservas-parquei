import { apiFetch } from './api';
import type { AuthUser } from '@/types/auth';

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  return apiFetch<LoginResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
}

export async function getProfile(): Promise<AuthUser> {
  return apiFetch<AuthUser>('/usuarios/me');
}
