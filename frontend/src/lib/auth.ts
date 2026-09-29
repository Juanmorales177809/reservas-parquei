import { cookies } from "next/headers";
import { apiRequest, ApiRequestError } from "./http";

/**
 * specs/contratos/auth/api-contract.md §7, §9 — el rol se deriva en el
 * servidor y nunca se guarda; estos son los tres únicos valores posibles.
 */
export type Rol = "USUARIO" | "TECNICO" | "ADMINISTRADOR";

/** Forma exacta de la respuesta de `GET /api/auth/sesiones/actual` (§3.4). */
export interface ContextoSesion {
  id_cuenta: number;
  tipo_cuenta: "USUARIO" | "PERSONAL";
  rol: Rol;
  correo: string;
  actualizacion_inicial_pendiente: boolean | null;
  id_sesion: string;
  unidades_autorizadas: number[] | "GLOBAL";
  autenticacion_reciente: boolean;
}

/**
 * Solo desde un Server Component: `apiRequest` no importa `next/headers`
 * (para poder usarse también en el cliente), así que este módulo lee la
 * cookie de la petición entrante y se la pasa explícitamente.
 *
 * `null` cuando no hay sesión válida (401 `NO_AUTENTICADO`) — el shell
 * autenticado decide qué hacer con eso (specs/ui/layout.md).
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

/** specs/ui/layout.md#navegación — etiqueta de rol para el estado de sesión. */
export const ETIQUETA_ROL: Record<Rol, string> = {
  USUARIO: "Usuario",
  TECNICO: "Técnico",
  ADMINISTRADOR: "Administrador",
};
