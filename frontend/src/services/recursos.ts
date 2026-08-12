import { apiFetch } from './api';
import type { Recurso, RecursoCreate, RecursoUpdate, TipoRecurso } from '@/types/recurso';
import type { DisponibilidadSlot } from '@/types/espacio';

export function listarRecursos(soloActivos = false, espacioId?: number): Promise<Recurso[]> {
  const params = new URLSearchParams();
  if (soloActivos) params.set('solo_activos', 'true');
  if (espacioId) params.set('espacio_id', String(espacioId));
  const query = params.toString();
  return apiFetch<Recurso[]>(`/recursos${query ? `?${query}` : ''}`);
}

export function listarRecursosGestion(): Promise<Recurso[]> {
  return apiFetch<Recurso[]>('/recursos/gestion');
}

export function listarTiposRecursos(): Promise<TipoRecurso[]> {
  return apiFetch<TipoRecurso[]>('/recursos/tipos');
}

export function crearRecurso(data: RecursoCreate): Promise<Recurso> {
  return apiFetch<Recurso>('/recursos', { method: 'POST', body: JSON.stringify(data) });
}

export function actualizarRecurso(id: number, data: RecursoUpdate): Promise<Recurso> {
  return apiFetch<Recurso>(`/recursos/${id}`, { method: 'PUT', body: JSON.stringify(data) });
}

export function eliminarRecurso(id: number): Promise<void> {
  return apiFetch<void>(`/recursos/${id}`, { method: 'DELETE' });
}

export function getDisponibilidadRecurso(id: number, fecha: string): Promise<DisponibilidadSlot[]> {
  return apiFetch<DisponibilidadSlot[]>(`/recursos/${id}/disponibilidad?fecha=${fecha}`);
}
