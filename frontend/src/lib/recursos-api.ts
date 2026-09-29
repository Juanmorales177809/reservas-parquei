import { apiRequest } from "./http";
import type {
  ConfiguracionLaboratorio,
  EstadoRecurso,
  ImpactoDeshabilitacion,
  RecursoDetalle,
  RecursoResumen,
  TipoRecurso,
} from "./recursos-types";

/**
 * Un envoltorio delgado por endpoint de resources (§2 y §3), tipado contra
 * specs/contratos/resources/api-contract.md. Ninguna pantalla llama a
 * `apiRequest` con una ruta escrita a mano.
 */

/** §2.1 */
export function crearRecurso(datos: {
  id_unidad: number;
  tipo: TipoRecurso;
  especializacion: Record<string, unknown>;
}) {
  return apiRequest<RecursoResumen>("/api/recursos", { method: "POST", body: datos });
}

/** §2.2 */
export function listarRecursos(filtros: { id_unidad?: number; tipo?: string; reservable?: boolean; busqueda?: string } = {}) {
  const params = new URLSearchParams({ tamano: "100" });
  if (filtros.id_unidad !== undefined) params.set("id_unidad", String(filtros.id_unidad));
  if (filtros.tipo) params.set("tipo", filtros.tipo);
  if (filtros.reservable) params.set("reservable", "true");
  if (filtros.busqueda) params.set("busqueda", filtros.busqueda);
  return apiRequest<{ datos: RecursoResumen[] }>(`/api/recursos?${params.toString()}`);
}

/** §2.3 */
export function detalleRecurso(id: number) {
  return apiRequest<RecursoDetalle>(`/api/recursos/${id}`);
}

/** §2.4 */
export function actualizarRecurso(id: number, especializacion: Record<string, unknown>) {
  return apiRequest<RecursoDetalle>(`/api/recursos/${id}`, {
    method: "PATCH",
    body: { especializacion },
  });
}

/** §2.5 */
export function cambiarEstadoRecurso(id: number, habilitado: boolean, confirmado = false) {
  return apiRequest<EstadoRecurso>(`/api/recursos/${id}/estado`, {
    method: "PATCH",
    body: { habilitado, confirmado },
  });
}

/** §2.6 */
export function impactoDeshabilitacion(id: number) {
  return apiRequest<ImpactoDeshabilitacion>(`/api/recursos/${id}/impacto-deshabilitacion`);
}

/** §2.7 */
export function reasignarRecurso(id: number, id_unidad: number) {
  return apiRequest<RecursoResumen>(`/api/recursos/${id}/unidad`, {
    method: "PATCH",
    body: { id_unidad },
  });
}

/** §3.1 */
export function configuracionLaboratorio(idUnidad: number) {
  return apiRequest<ConfiguracionLaboratorio>(`/api/laboratorios/${idUnidad}/configuracion`);
}

/** §3.2 */
export function guardarConfiguracion(idUnidad: number, datos: Record<string, unknown>) {
  return apiRequest<ConfiguracionLaboratorio>(`/api/laboratorios/${idUnidad}/configuracion`, {
    method: "PATCH",
    body: datos,
  });
}

/** §3.3 */
export function guardarTiposReserva(idUnidad: number, tipos: string[]) {
  return apiRequest<{ tipos_reserva: string[] }>(`/api/laboratorios/${idUnidad}/tipos-reserva`, {
    method: "PUT",
    body: { tipos },
  });
}

/** §3.4 */
export function guardarVisibilidad(
  idUnidad: number,
  datos: { mostrar_estado_reserva: boolean; mostrar_reservista: boolean }
) {
  return apiRequest<ConfiguracionLaboratorio>(`/api/laboratorios/${idUnidad}/visibilidad`, {
    method: "PATCH",
    body: datos,
  });
}

/** §3.0: catálogo de laboratorios, legible por cualquier cuenta autenticada. */
export function listarLaboratorios() {
  return apiRequest<{ datos: { id_unidad: number; nombre: string; habilitado_reservas: boolean }[] }>("/api/laboratorios");
}
