import type { Reserva } from '@/types/reserva';

/**
 * Etiqueta mostrable del objetivo de una reserva (Fase 12C-4e-schemas):
 * la/s zona/s si la reserva las tiene; si no, todos los nombres de
 * `recursos` (conjunto completo, no solo el ancla). Mismo criterio de
 * prioridad zona-antes-que-recurso, y misma forma "nombre, nombre" para
 * varios recursos, que `_etiqueta_objetivo` en
 * `backend/app/api/notificaciones.py`.
 *
 * `recurso`/`recurso_id` (el ancla singular) ya no llegan del backend --
 * el fallback a `reserva.recurso?.nombre` solo cubre un contrato en caché
 * de un cliente sin actualizar.
 */
export function etiquetaObjetivoReserva(reserva: Reserva): string {
  const zonas = reserva.zonas ?? [];
  if (zonas.length > 0) {
    return zonas.map((zona) => zona.nombre).join(', ');
  }
  const recursos = reserva.recursos ?? [];
  if (recursos.length > 0) {
    return recursos.map((recurso) => recurso.nombre).join(', ');
  }
  return reserva.recurso?.nombre ?? '';
}
