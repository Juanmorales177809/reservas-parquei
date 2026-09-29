import { apiRequest } from "./http";
import type {
  AprobacionRespuesta,
  DisponibilidadRespuesta,
  PropuestaRespuesta,
  RechazoRespuesta,
  ReservaCrear,
  ReservaDetalleRespuesta,
  AcompananteOpcion,
  AdjuntoItem,
  OpcionesContexto,
  OrdenSalida,
  PaginacionRespuesta,
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
export function listarReservas(
  filtros: {
    estado?: string;
    tipo_reserva?: string;
    id_unidad?: number;
    espacio_id?: number;
    desde?: string;
    hasta?: string;
    pagina?: number;
    tamano?: number;
  } = {}
) {
  const params = new URLSearchParams({ tamano: String(filtros.tamano ?? 20), orden: "-created_at" });
  if (filtros.pagina) params.set("pagina", String(filtros.pagina));
  if (filtros.estado) params.set("estado", filtros.estado);
  if (filtros.tipo_reserva) params.set("tipo_reserva", filtros.tipo_reserva);
  if (filtros.id_unidad !== undefined) params.set("id_unidad", String(filtros.id_unidad));
  if (filtros.espacio_id !== undefined) params.set("espacio_id", String(filtros.espacio_id));
  if (filtros.desde) params.set("desde", filtros.desde);
  if (filtros.hasta) params.set("hasta", filtros.hasta);
  return apiRequest<{ datos: ReservaResumen[]; paginacion: PaginacionRespuesta }>(`/api/reservas?${params.toString()}`);
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
/** §2.8: cada bloque, si viaja, es la selección completa resultante; los omitidos conservan su valor. */
export type CambiosReserva = Partial<Pick<ReservaCrear, "observacion" | "requiere_apoyo" | "contexto" | "recursos" | "acompanantes" | "campos_adicionales">> & {
  detalle?: Record<string, unknown>;
};

export function editarReserva(id: number, datos: CambiosReserva) {
  return apiRequest<ReservaDetalleRespuesta>(`/api/reservas/${id}`, {
    method: "PATCH",
    body: datos,
  });
}

/** §4.1 */
export function aprobarReserva(id: number, datos: { observacion?: string; material_recibido?: boolean } = {}) {
  return apiRequest<AprobacionRespuesta>(`/api/reservas/${id}/aprobacion`, {
    method: "POST",
    body: {
      ...(datos.observacion ? { observacion: datos.observacion } : {}),
      // Lista de espera: la aprobación registra también la recepción del material (RN-TIP-PLE-05).
      ...(datos.material_recibido !== undefined ? { material_recibido: datos.material_recibido } : {}),
    },
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

/** §2.9 */
export function opcionesContexto() {
  return apiRequest<OpcionesContexto>("/api/reservas/contexto/opciones");
}

/** §2.10 */
export function opcionesAcompanantes(filtros: { proyecto_id?: number; semillero_id?: number }) {
  const params = new URLSearchParams();
  if (filtros.proyecto_id) params.set("proyecto_id", String(filtros.proyecto_id));
  if (filtros.semillero_id) params.set("semillero_id", String(filtros.semillero_id));
  return apiRequest<{ datos: AcompananteOpcion[] }>(`/api/reservas/acompanantes/opciones?${params.toString()}`);
}

/** §2.6 */
export function listarAdjuntos(id: number) {
  return apiRequest<{ datos: AdjuntoItem[] }>(`/api/reservas/${id}/lista-espera/adjuntos?tamano=100`);
}

/** §2.7: descarga autenticada; el navegador envía la cookie de sesión al abrir el enlace. */
export function urlAdjunto(id: number, adjuntoId: number) {
  return `/api/reservas/${id}/lista-espera/adjuntos/${adjuntoId}`;
}

/** §7.1 */
export function ordenSalida(id: number) {
  return apiRequest<OrdenSalida>(`/api/reservas/${id}/orden-salida`);
}

/** §7.2: PDF de la orden; el navegador envía la cookie de sesión al abrir el enlace. */
export function urlOrdenSalidaPdf(id: number) {
  return `/api/reservas/${id}/orden-salida.pdf`;
}

/** §8.1: archivo iCalendar de una reserva aprobada de espacio o recurso interno. */
export function urlCalendario(id: number) {
  return `/api/reservas/${id}/calendario.ics`;
}
