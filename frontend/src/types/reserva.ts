import type { ZonaReserva } from './zona';

export type ReservaEstado = 'esperando' | 'aprobada' | 'rechazada' | 'cancelada';

export interface ReservaUsuario {
  id: number;
  username: string;
  email: string;
  rol: 'admin' | 'gestor' | 'usuario';
}

export interface ReservaEspacio {
  id: number;
  nombre: string;
  capacidad: number;
  estado: 'activo' | 'inactivo' | 'mantenimiento';
}

export interface Reserva {
  id: number;
  usuario_id: number;
  espacio_id: number;
  recurso_id: number;
  // Fase 12C-6: el backend expone además los conjuntos resueltos desde las
  // tablas de asociación. Se leen como opcionales para conservar la lectura
  // singular (`recurso`/`recurso_id`) mientras el backend la exponga.
  recurso_ids?: number[];
  zona_ids?: number[];
  zonas?: ZonaReserva[];
  fecha: string;
  hora_inicio: string;
  hora_fin: string;
  estado: ReservaEstado;
  asistentes: number;
  created_at: string;
  updated_at: string;
  usuario: ReservaUsuario;
  espacio: ReservaEspacio;
  recurso: {
    id: number;
    nombre: string;
    capacidad: number;
    estado: string;
    espacio: ReservaEspacio;
  };
}

export interface ReservaCreate {
  // Fase 12C-6: el contrato pasa a ejes de conjuntos. Al menos un recurso o
  // una zona; nunca se envía `recurso_id` (422 si se enviara).
  recurso_ids: number[];
  zona_ids: number[];
  fecha: string;
  hora_inicio: string;
  hora_fin: string;
  asistentes: number;
}

export interface ReservaEstadoUpdate {
  nuevo_estado: Extract<ReservaEstado, 'aprobada' | 'rechazada' | 'cancelada'>;
}

export type ReservaUpdate = Partial<ReservaCreate>;
