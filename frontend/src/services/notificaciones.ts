import { apiFetch } from './api';
import type { Notificacion, NotificacionesSinLeer } from '@/types/notificacion';

export function listarMisNotificaciones(): Promise<Notificacion[]> {
  return apiFetch<Notificacion[]>('/notificaciones');
}

export function contarSinLeer(): Promise<NotificacionesSinLeer> {
  return apiFetch<NotificacionesSinLeer>('/notificaciones/sin-leer/count');
}

export function marcarComoLeida(id: number): Promise<Notificacion> {
  return apiFetch<Notificacion>(`/notificaciones/${id}/leer`, { method: 'PATCH' });
}

export function marcarTodasComoLeidas(): Promise<NotificacionesSinLeer> {
  return apiFetch<NotificacionesSinLeer>('/notificaciones/leer-todas', { method: 'PATCH' });
}
