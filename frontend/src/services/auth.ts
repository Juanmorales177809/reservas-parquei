import { apiFetch } from './api';
import type { AuthUser } from '@/types/auth';

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

/**
 * Fase 9F-B: la sesión la establece la cookie HttpOnly que fija el
 * backend (Set-Cookie en la respuesta), no el body. `access_token` sigue
 * presente en la respuesta (TokenResponse sin cambios de contrato, Fase
 * 9F-A) pero el frontend ya no lo lee ni lo almacena — solo se queda con
 * el usuario.
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
