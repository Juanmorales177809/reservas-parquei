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
  recurso_id: number;
  fecha: string;
  hora_inicio: string;
  hora_fin: string;
  asistentes: number;
}

export interface ReservaEstadoUpdate {
  nuevo_estado: Extract<ReservaEstado, 'aprobada' | 'rechazada' | 'cancelada'>;
}

export type ReservaUpdate = Partial<ReservaCreate>;
