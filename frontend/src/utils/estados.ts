import type { ReservaEstado } from '@/types/reserva';

export const BADGE_ESTADO_RESERVA: Record<ReservaEstado, string> = {
  esperando: 'badge-warning',
  aprobada: 'badge-success',
  rechazada: 'badge-danger',
  cancelada: 'badge-neutral',
};

export const LABEL_ESTADO_RESERVA: Record<ReservaEstado, string> = {
  esperando: 'Pendiente',
  aprobada: 'Aprobada',
  rechazada: 'Rechazada',
  cancelada: 'Cancelada',
};

export const BADGE_ESTADO_ENTIDAD: Record<'activo' | 'inactivo' | 'mantenimiento', string> = {
  activo: 'badge-success',
  inactivo: 'badge-neutral',
  mantenimiento: 'badge-warning',
};

export function badgeEstadoReserva(estado: string): string {
  return BADGE_ESTADO_RESERVA[estado as ReservaEstado] ?? 'badge-neutral';
}

export function labelEstadoReserva(estado: string): string {
  return LABEL_ESTADO_RESERVA[estado as ReservaEstado] ?? estado;
}

export function badgeEstadoEntidad(estado: string): string {
  return (
    BADGE_ESTADO_ENTIDAD[estado as keyof typeof BADGE_ESTADO_ENTIDAD] ?? 'badge-neutral'
  );
}
