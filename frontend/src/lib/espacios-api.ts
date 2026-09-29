import { apiRequest } from "./http";
import type {
  CampoCrear,
  EspacioDetalle,
  EspacioResumen,
  EstadoEspacio,
  ImpactoEspacio,
} from "./espacios-types";

/**
 * Un envoltorio delgado por endpoint de espacios (§2 a §4), tipado contra
 * specs/contratos/espacios/api-contract.md. Ninguna pantalla llama a
 * `apiRequest` con una ruta escrita a mano.
 */

/** §2.1 */
export function crearEspacio(datos: {
  id_unidad: number;
  nombre: string;
  ubicacion?: string;
  capacidad: number;
  descripcion?: string;
  recursos?: number[];
  campos?: CampoCrear[];
}) {
  return apiRequest<EspacioDetalle>("/api/espacios", { method: "POST", body: datos });
}

/** §2.2 */
export function editarEspacio(id: number, datos: {
  nombre?: string;
  ubicacion?: string;
  capacidad?: number;
  descripcion?: string;
}) {
  return apiRequest<EspacioDetalle>(`/api/espacios/${id}`, { method: "PATCH", body: datos });
}

/** §2.3 */
export function listarEspacios(filtros: { id_unidad?: number; habilitado?: boolean; capacidad_minima?: number } = {}) {
  const params = new URLSearchParams({ tamano: "100" });
  if (filtros.id_unidad !== undefined) params.set("id_unidad", String(filtros.id_unidad));
  if (filtros.habilitado !== undefined) params.set("habilitado", String(filtros.habilitado));
  if (filtros.capacidad_minima !== undefined) params.set("capacidad_minima", String(filtros.capacidad_minima));
  return apiRequest<{ datos: EspacioResumen[] }>(`/api/espacios?${params.toString()}`);
}

/** §2.4 */
export function detalleEspacio(id: number) {
  return apiRequest<EspacioDetalle>(`/api/espacios/${id}`);
}

/** §2.5 */
export function cambiarEstadoEspacio(id: number, habilitado: boolean, confirmado = false) {
  return apiRequest<EstadoEspacio>(`/api/espacios/${id}/estado`, {
    method: "PATCH",
    body: { habilitado, confirmado },
  });
}

/** §2.6 */
export function impactoDeshabilitacionEspacio(id: number) {
  return apiRequest<ImpactoEspacio>(`/api/espacios/${id}/impacto-deshabilitacion`);
}

/** §3.1 */
export function asociarRecursos(id: number, recursos: number[]) {
  return apiRequest<unknown>(`/api/espacios/${id}/recursos`, {
    method: "POST",
    body: { recursos },
  });
}

/** §3.2 */
export function retirarRecurso(id: number, recursoId: number) {
  return apiRequest<void>(`/api/espacios/${id}/recursos/${recursoId}`, {
    method: "DELETE",
  });
}

/** §4.1 */
export function crearCampo(id: number, campo: CampoCrear) {
  return apiRequest<unknown>(`/api/espacios/${id}/campos`, {
    method: "POST",
    body: campo,
  });
}

/** §4.2 */
export function editarCampo(id: number, campoId: number, datos: { nombre?: string; obligatorio?: boolean; orden?: number }) {
  return apiRequest<unknown>(`/api/espacios/${id}/campos/${campoId}`, {
    method: "PATCH",
    body: datos,
  });
}

/** §4.3 */
export function cambiarEstadoCampo(id: number, campoId: number, habilitado: boolean) {
  return apiRequest<unknown>(`/api/espacios/${id}/campos/${campoId}/estado`, {
    method: "PATCH",
    body: { habilitado },
  });
}

/** §4.4 */
export function reordenarCampos(id: number, orden: { campo_id: number; orden: number }[]) {
  return apiRequest<unknown>(`/api/espacios/${id}/campos/orden`, {
    method: "PUT",
    body: { orden },
  });
}

/** §4.5 */
export function agregarOpciones(id: number, campoId: number, opciones: { valor: string; orden?: number }[]) {
  return apiRequest<unknown>(`/api/espacios/${id}/campos/${campoId}/opciones`, {
    method: "POST",
    body: { opciones },
  });
}

/** §4.6 */
export function editarOpcion(id: number, campoId: number, opcionId: number, datos: { valor?: string; orden?: number; habilitado?: boolean }) {
  return apiRequest<unknown>(`/api/espacios/${id}/campos/${campoId}/opciones/${opcionId}`, {
    method: "PATCH",
    body: datos,
  });
}
