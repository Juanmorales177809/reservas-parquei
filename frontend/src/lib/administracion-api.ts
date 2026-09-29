import { apiRequest } from "./http";
import type {
  Asignacion,
  AuditoriaFila,
  Cargo,
  PermisoCatalogo,
  Unidad,
  ValidacionImportacion,
} from "./administracion-types";

/**
 * Un envoltorio delgado por endpoint de administration (§2 a §5), tipado
 * contra specs/contratos/administration/api-contract.md. Ninguna pantalla
 * llama a `apiRequest` con una ruta escrita a mano.
 */

/** §2.1 */
export function crearUnidad(datos: { nombre: string; tipo: string; id_unidad_padre?: number }) {
  return apiRequest<Unidad>("/api/unidades", { method: "POST", body: datos });
}

/** §2.2 */
export function listarUnidades() {
  return apiRequest<{ datos: Unidad[] }>("/api/unidades?tamano=100");
}

/** §2.3 */
export function editarUnidad(id: number, datos: { nombre?: string; tipo?: string; id_unidad_padre?: number | null }) {
  return apiRequest<Unidad>(`/api/unidades/${id}`, { method: "PATCH", body: datos });
}

/** §2.4 */
export function cambiarEstadoUnidad(id: number, estado: boolean) {
  return apiRequest<Unidad>(`/api/unidades/${id}/estado`, {
    method: "PATCH",
    body: { estado },
  });
}

/** §2.5 */
export function crearCargo(datos: { nombre_cargo: string; id_unidad: number }) {
  return apiRequest<Cargo>("/api/cargos", { method: "POST", body: datos });
}

/** §2.6 */
export function listarCargos(id_unidad?: number) {
  const consulta = id_unidad ? `?id_unidad=${id_unidad}` : "";
  return apiRequest<{ datos: Cargo[] }>(`/api/cargos${consulta}`);
}

/** §2.6 */
export function editarCargo(id: number, datos: { nombre_cargo?: string; id_unidad?: number }) {
  return apiRequest<Cargo>(`/api/cargos/${id}`, { method: "PATCH", body: datos });
}

/** §3.1 */
export function catalogoPermisos() {
  return apiRequest<{ datos: PermisoCatalogo[] }>("/api/permisos");
}

/** §3.2 */
export function asignacionesDe(idCuenta: number) {
  return apiRequest<Asignacion[]>(`/api/permisos/cuentas/${idCuenta}`);
}

/** §3.3 */
export function otorgarPermiso(idCuenta: number, codigo: string, id_unidad: number | null) {
  return apiRequest<Asignacion>(`/api/permisos/cuentas/${idCuenta}`, {
    method: "POST",
    body: { codigo, id_unidad },
  });
}

/** §3.4 */
export function retirarPermiso(idCuenta: number, codigo: string) {
  return apiRequest<void>(`/api/permisos/cuentas/${idCuenta}/${encodeURIComponent(codigo)}`, {
    method: "DELETE",
  });
}

/** §4.1 */
export function validarImportacion(formulario: FormData) {
  return apiRequest<ValidacionImportacion>("/api/importaciones", {
    method: "POST",
    body: formulario,
  });
}

/** §4.2 */
export function confirmarImportacion(id: number) {
  return apiRequest<{ creados: number; actualizados: number; desactivados: number }>(
    `/api/importaciones/${id}/confirmacion`,
    { method: "POST", body: {} }
  );
}

/** §4.3 */
export function listarImportaciones() {
  return apiRequest<{ datos: { id: number; catalogo: string }[] }>("/api/importaciones");
}

/** §5.1 */
export function listarAuditoria(filtros: { entidad?: string; actor_cuenta_id?: number; accion?: string } = {}) {
  const params = new URLSearchParams({ tamano: "100" });
  if (filtros.entidad) params.set("entidad", filtros.entidad);
  if (filtros.actor_cuenta_id) params.set("actor_cuenta_id", String(filtros.actor_cuenta_id));
  if (filtros.accion) params.set("accion", filtros.accion);
  return apiRequest<{ datos: AuditoriaFila[] }>(`/api/auditoria?${params.toString()}`);
}

/** §5.1 (usuarios §5.2/§6.2) — alta y edición de identidades (UF-ADM-02/03). */
export function crearUsuarioIdentidad(datos: {
  nombre: string;
  documento: string;
  correo: string;
  telefono: string;
  institucion: string;
  dependencia: string;
}) {
  return apiRequest<{ id_usuario: number }>("/api/usuarios", { method: "POST", body: datos });
}

/** §6.1 (usuarios) */
export function crearFichaPersonal(datos: {
  nombre: string;
  documento: string;
  correo: string;
  telefono: string;
  id_cargo: number;
}) {
  return apiRequest<{ id_persona: number }>("/api/personal", { method: "POST", body: datos });
}
