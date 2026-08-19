import { apiFetch } from './api';
import type { AuthUser } from '@/types/auth';

interface LoginResponse {
  user: AuthUser;
}

/**
 * Fase 9G (cookie-only): el login devuelve únicamente el usuario
 * (`LoginResponse.user`). La sesión la establece la cookie HttpOnly que fija
 * el backend (Set-Cookie en la respuesta de POST /auth/login); el body ya no
 * expone `access_token` ni `token_type`, y el frontend nunca lo guarda.
 */
export async function login(username: string, password: string): Promise<AuthUser> {
  const data = await apiFetch<LoginResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
  return data.user;
}

export async function getProfile(): Promise<AuthUser> {
  return apiFetch<AuthUser>('/usuarios/me');
}

/** Cierra la sesión de cookie en el backend (POST /auth/logout, Fase 9F-A). */
export async function logout(): Promise<void> {
  await apiFetch<void>('/auth/logout', { method: 'POST' });
}
