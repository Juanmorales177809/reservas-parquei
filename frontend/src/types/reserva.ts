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

export interface ReservaRecurso {
  id: number;
  nombre: string;
  capacidad: number;
  estado: string;
  espacio: ReservaEspacio;
}

export interface Reserva {
  id: number;
  usuario_id: number;
  espacio_id: number;
  // Fase 12C-4e-schemas: el backend retiró `recurso_id`/`recurso` (el ancla
  // singular) de `ReservaResponse` -- ya no los envía. Se conservan aquí
  // como opcionales únicamente por si un contrato anterior en caché (SW,
  // cliente no actualizado) los sigue esperando; el código nuevo debe leer
  // `recursos`/`zonas` (conjuntos, siempre presentes) en su lugar.
  recurso_id?: number;
  recurso?: ReservaRecurso;
  // Fase 12C-6/12C-4e-schemas: conjuntos resueltos desde las tablas de
  // asociación. `recursos` (objetos completos) reemplaza al ancla singular.
  recurso_ids?: number[];
  recursos?: ReservaRecurso[];
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
