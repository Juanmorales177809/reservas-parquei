import { apiFetch } from './api';
import type { Reserva, ReservaCreate, ReservaEstadoUpdate, ReservaUpdate } from '@/types/reserva';

export function crearReserva(data: ReservaCreate): Promise<Reserva> {
  return apiFetch<Reserva>('/reservas', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export function listarReservas(): Promise<Reserva[]> {
  return apiFetch<Reserva[]>('/reservas');
}

export function listarMisReservas(): Promise<Reserva[]> {
  return apiFetch<Reserva[]>('/reservas/mis-reservas');
}

export function cambiarEstado(
  id: number,
  nuevo_estado: ReservaEstadoUpdate['nuevo_estado'],
  motivo?: string | null,
): Promise<Reserva> {
  const body: Record<string, unknown> = { nuevo_estado };
  if (motivo !== undefined) body.motivo = motivo;
  return apiFetch<Reserva>(`/reservas/${id}/estado`, {
    method: 'PUT',
    body: JSON.stringify(body),
  });
}

export function actualizarReserva(id: number, data: ReservaUpdate): Promise<Reserva> {
  return apiFetch<Reserva>(`/reservas/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export function cancelarMiReserva(id: number): Promise<Reserva> {
  return apiFetch<Reserva>(`/reservas/${id}/cancelar`, {
    method: 'PUT',
  });
}

export function eliminarReserva(id: number): Promise<void> {
  return apiFetch<void>(`/reservas/${id}`, {
    method: 'DELETE',
  });
}

export function marcarAsistencia(id: number, asistio: boolean): Promise<Reserva> {
  return apiFetch<Reserva>(`/reservas/${id}/asistio`, {
    method: 'PUT',
    body: JSON.stringify({ asistio }),
  });
}
