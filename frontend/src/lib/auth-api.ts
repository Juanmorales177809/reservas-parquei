import { apiRequest } from "./http";
import type { ContextoSesion } from "./auth-types";

/**
 * Un envoltorio delgado por endpoint de auth, tipado contra
 * specs/contratos/auth/api-contract.md. No añade lógica de negocio: eso
 * ya lo aplica el backend, esto solo evita repetir rutas y formas a mano
 * en cada pantalla.
 */

export interface RespuestaSesion {
  id_cuenta: number;
  tipo_cuenta: "USUARIO" | "PERSONAL";
  rol: ContextoSesion["rol"];
  actualizacion_inicial_pendiente: boolean | null;
  correo: string;
  id_sesion: string;
  expira_en: string;
}

/** §3.1 */
export function registrar(datos: {
  nombre: string;
  documento: string;
  telefono: string;
  institucion: string;
  dependencia: string;
  correo: string;
  contrasena: string;
}) {
  return apiRequest<{ mensaje: string }>("/api/auth/registro", {
    method: "POST",
    body: datos,
  });
}

/** §3.2 */
export function iniciarSesion(datos: { correo: string; contrasena: string }) {
  return apiRequest<RespuestaSesion>("/api/auth/sesiones", {
    method: "POST",
    body: datos,
  });
}

/** §3.6 */
export function solicitarRecuperacion(correo: string) {
  return apiRequest<{ mensaje: string }>("/api/auth/recuperacion", {
    method: "POST",
    body: { correo },
  });
}

/** §3.7 */
export function validarTokenRecuperacion(token: string) {
  return apiRequest<{ vigente: boolean }>(
    `/api/auth/recuperacion/${encodeURIComponent(token)}`
  );
}

/** §3.8 */
export function restablecerContrasena(token: string, contrasena: string) {
  return apiRequest<void>(
    `/api/auth/recuperacion/${encodeURIComponent(token)}`,
    { method: "POST", body: { contrasena } }
  );
}

/** §3.9 */
export function reautenticar(contrasena: string) {
  return apiRequest<{ autenticacion_reciente_hasta: string }>(
    "/api/auth/reautenticacion",
    { method: "POST", body: { contrasena } }
  );
}

/** §4.1 */
export function invitar(datos: {
  correo: string;
  tipo_cuenta: "USUARIO" | "PERSONAL";
  id_unidad?: number;
}) {
  return apiRequest<{
    id: number;
    correo: string;
    tipo_cuenta: "USUARIO" | "PERSONAL";
    expira_en: string;
    estado: string;
  }>("/api/auth/invitaciones", { method: "POST", body: datos });
}

/** §4.2 */
export function reenviarInvitacion(idInvitacion: number) {
  return apiRequest<{ id: number; expira_en: string; estado: string }>(
    `/api/auth/invitaciones/${idInvitacion}/reenvio`,
    { method: "POST" }
  );
}

/** §4.3 */
export function validarTokenInvitacion(token: string) {
  return apiRequest<{ vigente: boolean; correo: string }>(
    `/api/auth/invitaciones/${encodeURIComponent(token)}`
  );
}

/** §4.4 */
export function activarInvitacion(token: string, contrasena: string) {
  return apiRequest<RespuestaSesion>(
    `/api/auth/invitaciones/${encodeURIComponent(token)}/activacion`,
    { method: "POST", body: { contrasena } }
  );
}

/** §5.1 */
export function cambiarContrasenaPropia(contrasena: string) {
  return apiRequest<void>("/api/auth/cuentas/actual/contrasena", {
    method: "PUT",
    body: { contrasena },
  });
}

/** §6.1 */
export function cambiarEstadoCuenta(idCuenta: number, estado: boolean) {
  return apiRequest<{
    id_cuenta: number;
    estado: boolean;
    sesiones_revocadas: number;
  }>(`/api/auth/cuentas/${idCuenta}/estado`, {
    method: "PATCH",
    body: { estado },
  });
}

/** §6.2 — exactamente uno de id_persona/id_usuario, nunca ambos. */
export function cambiarIdentidadCuenta(
  idCuenta: number,
  destino:
    | { tipo_cuenta: "PERSONAL"; id_persona: number }
    | { tipo_cuenta: "USUARIO"; id_usuario: number }
) {
  return apiRequest<{
    id_cuenta: number;
    tipo_cuenta: "USUARIO" | "PERSONAL";
    id_persona: number | null;
    id_usuario: number | null;
  }>(`/api/auth/cuentas/${idCuenta}/identidad`, {
    method: "PUT",
    body: destino,
  });
}
