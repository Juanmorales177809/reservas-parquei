/**
 * Tipos y constantes de sesión compartidos entre cliente y servidor.
 * Deliberadamente sin `next/headers`: cualquier módulo que lo importe
 * (como `auth.ts`) no puede usarse desde un Client Component — Next.js
 * envenena el bundle entero, no solo el export que de hecho se use.
 */

/** specs/contratos/auth/api-contract.md §7, §9 — los tres únicos valores posibles. */
export type Rol = "USUARIO" | "TECNICO" | "ADMINISTRADOR";

/** Forma exacta de la respuesta de `GET /api/auth/sesiones/actual` (§3.4). */
export interface ContextoSesion {
  id_cuenta: number;
  tipo_cuenta: "USUARIO" | "PERSONAL" | "ADMINISTRADOR";
  rol: Rol;
  correo: string;
  actualizacion_inicial_pendiente: boolean | null;
  id_sesion: string;
  unidades_autorizadas: number[] | "GLOBAL";
  autenticacion_reciente: boolean;
}

/** specs/ui/layout.md#navegación — etiqueta de rol para el estado de sesión. */
export const ETIQUETA_ROL: Record<Rol, string> = {
  USUARIO: "Usuario",
  TECNICO: "Técnico",
  ADMINISTRADOR: "Administrador",
};
