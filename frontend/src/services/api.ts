export const API_BASE_URL = '/api';

// Rutas donde un 401 NO dispara el interceptor global de sesión expirada
// (Fase 9F-B):
// - /auth/login: un 401 aquí son credenciales inválidas, no una sesión
//   expirada. El error debe llegar al formulario de login (login/page.tsx)
//   sin redirect.
// - /usuarios/me: AuthContext lo usa como sondeo pasivo de sesión al
//   montar (reemplaza la lectura síncrona de localStorage de antes de esta
//   fase). Un visitante anónimo en una página pública (/, /espacios,
//   /terminos) SIEMPRE recibe 401 aquí — es el resultado normal de "no hay
//   sesión", no una sesión vencida, y no debe forzar un redirect global.
//   ProtectedRoute ya redirige a /login en rutas protegidas cuando
//   isAuthenticated es false, así que ese caso queda cubierto igual.
const RUTAS_SIN_REDIRECT_401 = new Set(['/auth/login', '/usuarios/me']);

export async function parseApiError(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (typeof body.detail === 'string') return body.detail;
    if (Array.isArray(body.detail)) return body.detail.map((item: { msg?: string }) => item.msg ?? JSON.stringify(item)).join(', ');
    return JSON.stringify(body.detail ?? body);
  } catch {
    return `Error HTTP ${response.status}`;
  }
}

export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  // Fase 9F-B: el JWT viaja en una cookie HttpOnly (backend/app/api/auth.py),
  // no en el header Authorization ni en localStorage. `credentials:
  // 'same-origin'` hace que el navegador adjunte esa cookie en cada
  // petición al mismo origen (el proxy /api de Next.js hacia el backend).
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
    credentials: 'same-origin',
  });

  if (response.status === 401 && typeof window !== 'undefined' && !RUTAS_SIN_REDIRECT_401.has(path)) {
    // La cookie HttpOnly no es visible ni manipulable desde JavaScript: no
    // hay nada que "limpiar" aquí (a diferencia de localStorage antes de
    // esta fase). El backend es quien la expira (Max-Age) o la borra
    // (POST /auth/logout); el frontend solo redirige.
    window.location.href = '/login';
    throw new Error('Sesión expirada. Por favor, inicia sesión nuevamente.');
  }

  if (!response.ok) {
    throw new Error(await parseApiError(response));
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const contentType = response.headers.get('content-type');
  if (!contentType?.includes('application/json')) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}
