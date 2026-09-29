import { apiRequest } from "./http";
import type {
  LecturaRespuesta,
  NotificacionItem,
  Preferencias,
  TipoEventoItem,
} from "./notificaciones-types";

/**
 * Un envoltorio delgado por endpoint de notifications (§2 y §3), tipado
 * contra specs/contratos/notifications/api-contract.md. Ninguna pantalla
 * llama a `apiRequest` con una ruta escrita a mano.
 */

/** §2.1 */
export function bandeja(filtros: { leida?: boolean; tipo_evento?: string } = {}) {
  const params = new URLSearchParams({ tamano: "100" });
  if (filtros.leida !== undefined) params.set("leida", String(filtros.leida));
  if (filtros.tipo_evento) params.set("tipo_evento", filtros.tipo_evento);
  return apiRequest<{ datos: NotificacionItem[] }>(`/api/notificaciones?${params.toString()}`);
}

/** §2.2 */
export function marcarLectura(id: number) {
  return apiRequest<LecturaRespuesta>(`/api/notificaciones/${id}/lectura`, {
    method: "POST",
    body: {},
  });
}

/** §3.1 */
export function obtenerPreferencias() {
  return apiRequest<Preferencias>("/api/notificaciones/preferencias");
}

/** §3.2 */
export function guardarPreferencias(datos: {
  general?: { correo_habilitado: boolean };
  por_evento: { tipo_evento_id: number; correo_habilitado: boolean }[];
}) {
  return apiRequest<Preferencias>("/api/notificaciones/preferencias", {
    method: "PUT",
    body: datos,
  });
}

/** §3.3 */
export function tiposEvento() {
  return apiRequest<{ datos: TipoEventoItem[] }>("/api/notificaciones/tipos-evento");
}
