export type NotificacionTipo = 'Pendiente' | 'Aprobada' | 'Rechazada' | 'Cancelada';

export interface Notificacion {
  id: number;
  usuario_id: number;
  reserva_id: number | null;
  tipo: NotificacionTipo;
  leida: boolean;
  created_at: string;
  mensaje: string;
}

export interface NotificacionesSinLeer {
  cantidad: number;
}
