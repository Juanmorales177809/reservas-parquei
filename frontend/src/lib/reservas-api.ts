import { apiRequest } from "./http";
import type {
  AprobacionRespuesta,
  DisponibilidadRespuesta,
  PropuestaRespuesta,
  RechazoRespuesta,
  ReservaCrear,
  ReservaDetalleRespuesta,
  ReservaResumen,
  TipoReservaItem,
  TransicionRespuesta,
  ViabilidadRespuesta,
} from "./reservas-types";

/**
 * Un envoltorio delgado por endpoint de reservations (§2 a §8), tipado
 * contra specs/contratos/reservations/api-contract.md. Ninguna pantalla
 * llama a `apiRequest` con una ruta escrita a mano.
 */

/** §2.1 */
export function crearReserva(datos: ReservaCrear) {
  return apiRequest<ReservaResumen>("/api/reservas", { method: "POST", body: datos });
}

/** §2.2 */
export function tiposHabilitados(idUnidad: number) {
  return apiRequest<{ datos: TipoReservaItem[] }>(
    `/api/reservas/tipos?id_unidad=${idUnidad}`
  );
}

/** §3.1 */
export function listarReservas(filtros: { estado?: string; tipo_reserva?: string; id_unidad?: number } = {}) {
  const params = new URLSearchParams({ tamano: "100" });
  if (filtros.estado) params.set("estado", filtros.estado);
  if (filtros.tipo_reserva) params.set("tipo_reserva", filtros.tipo_reserva);
  if (filtros.id_unidad !== undefined) params.set("id_unidad", String(filtros.id_unidad));
  return apiRequest<{ datos: ReservaResumen[] }>(`/api/reservas?${params.toString()}`);
}

/** §3.2 */
export function detalleReserva(id: number) {
  return apiRequest<ReservaDetalleRespuesta>(`/api/reservas/${id}`);
}

/** §3.3 */
export function consultarDisponibilidad(datos: {
  id_unidad: number;
  espacio_id?: number;
  recurso_id?: number;
  desde: string;
  hasta: string;
}) {
  const params = new URLSearchParams({
    id_unidad: String(datos.id_unidad),
    desde: datos.desde,
    hasta: datos.hasta,
  });
  if (datos.espacio_id !== undefined) params.set("espacio_id", String(datos.espacio_id));
  if (datos.recurso_id !== undefined) params.set("recurso_id", String(datos.recurso_id));
  return apiRequest<DisponibilidadRespuesta>(`/api/reservas/disponibilidad?${params.toString()}`);
}

/** §2.8 */
export function editarReserva(id: number, datos: { observacion?: string; detalle?: Record<string, unknown> }) {
  return apiRequest<ReservaDetalleRespuesta>(`/api/reservas/${id}`, {
    method: "PATCH",
    body: datos,
  });
}

/** §4.1 */
export function aprobarReserva(id: number, observacion?: string) {
  return apiRequest<AprobacionRespuesta>(`/api/reservas/${id}/aprobacion`, {
    method: "POST",
    body: observacion ? { observacion } : {},
  });
}

/** §4.2 */
export function rechazarReserva(id: number, motivo: string) {
  return apiRequest<RechazoRespuesta>(`/api/reservas/${id}/rechazo`, {
    method: "POST",
    body: { motivo },
  });
}

/** §4.3 */
export function agregarRecursos(id: number, recursos: { recurso_id: number; rol: "PRINCIPAL" | "ADICIONAL" }[]) {
  return apiRequest<unknown>(`/api/reservas/${id}/recursos`, {
    method: "POST",
    body: { recursos },
  });
}

/** §4.4 */
export function retirarRecurso(id: number, reservaRecursoId: number) {
  return apiRequest<void>(`/api/reservas/${id}/recursos/${reservaRecursoId}`, {
    method: "DELETE",
  });
}

/** §5.1 */
export function crearPropuesta(id: number, datos: {
  fecha_inicio_propuesta: string;
  fecha_fin_propuesta: string;
  hora_inicio?: string;
  hora_fin?: string;
  motivo: string;
}) {
  return apiRequest<PropuestaRespuesta>(`/api/reservas/${id}/propuestas`, {
    method: "POST",
    body: datos,
  });
}

/** §5.2 */
export function aceptarPropuesta(id: number) {
  return apiRequest<ReservaDetalleRespuesta>(`/api/reservas/${id}/propuestas/vigente/aceptacion`, {
    method: "POST",
    body: {},
  });
}

/** §5.3 */
export function rechazarPropuesta(id: number) {
  return apiRequest<PropuestaRespuesta>(`/api/reservas/${id}/propuestas/vigente/rechazo`, {
    method: "POST",
    body: {},
  });
}

/** §6.1 */
export function ejecutarReserva(id: number, recursos?: { reserva_recurso_id: number; observacion_entrega?: string }[]) {
  return apiRequest<TransicionRespuesta>(`/api/reservas/${id}/ejecucion`, {
    method: "POST",
    body: recursos ? { recursos } : {},
  });
}

/** §6.2 */
export function finalizarReserva(
  id: number,
  datos: { recursos?: { reserva_recurso_id: number; observacion_devolucion?: string }[]; horas_ejecucion?: number } = {}
) {
  return apiRequest<TransicionRespuesta>(`/api/reservas/${id}/finalizacion`, {
    method: "POST",
    body: datos,
  });
}

/** §6.3 */
export function cancelarReserva(id: number, motivo?: string) {
  return apiRequest<TransicionRespuesta>(`/api/reservas/${id}/cancelacion`, {
    method: "POST",
    body: motivo ? { motivo } : {},
  });
}

/** §2.3/§2.4 lista de espera */
export function diligenciarFormulario(id: number, datos: { datos_usuario?: Record<string, unknown>; datos_tecnico?: Record<string, unknown> }) {
  return apiRequest<unknown>(`/api/reservas/${id}/lista-espera/formulario`, {
    method: "PUT",
    body: datos,
  });
}

/** §2.4 */
export function registrarViabilidad(id: number, viable: boolean, motivo?: string) {
  return apiRequest<ViabilidadRespuesta>(`/api/reservas/${id}/lista-espera/viabilidad`, {
    method: "POST",
    body: motivo !== undefined ? { viable, motivo } : { viable },
  });
}

/** §2.5 */
export function subirAdjunto(id: number, archivo: File, tipo_adjunto: string) {
  const formulario = new FormData();
  formulario.append("archivo", archivo);
  formulario.append("tipo_adjunto", tipo_adjunto);
  return apiRequest<unknown>(`/api/reservas/${id}/lista-espera/adjuntos`, {
    method: "POST",
    body: formulario,
  });
}

/** §7.1 */
export function ordenSalida(id: number) {
  return apiRequest<Record<string, unknown>>(`/api/reservas/${id}/orden-salida`);
}
