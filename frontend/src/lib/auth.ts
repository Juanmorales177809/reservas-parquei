import { cookies } from "next/headers";
import { apiRequest, ApiRequestError } from "./http";
import type { ContextoSesion } from "./auth-types";

/**
 * Solo desde un Server Component: `apiRequest` no importa `next/headers`
 * (para poder usarse también en el cliente), así que este módulo lee la
 * cookie de la petición entrante y se la pasa explícitamente.
 *
 * `null` cuando no hay sesión válida (401 `NO_AUTENTICADO`) — el shell
 * autenticado decide qué hacer con eso (specs/ui/layout.md).
 *
 * Nota: se evaluó envolver esta función en `cache()` de `react` para que
 * un layout anidado (p. ej. `(app)/administracion/layout.tsx`) no repita
 * la petición HTTP dentro del mismo request. Se descartó: `cache()` solo
 * está disponible en la versión de React que Next.js empaqueta para App
 * Router en build — bajo el `react@18.3.1` de npm que usa Vitest no
 * existe, y rompía las pruebas (`TypeError: cache is not a function`).
 * Repetir la llamada es una petición HTTP de más por request en rutas
 * anidadas, no un error — se revisita si se sube a React 19, donde
 * `cache()` es parte estable del paquete público.
 */
export async function obtenerSesionActual(): Promise<ContextoSesion | null> {
  const cookieHeader = cookies().toString();
  try {
    return await apiRequest<ContextoSesion>("/api/auth/sesiones/actual", {
      cookieHeader,
    });
  } catch (error) {
    if (error instanceof ApiRequestError && error.status === 401) {
      return null;
    }
    throw error;
  }
}
