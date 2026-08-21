import type { EnsayoReserva } from './ensayo';
import type { ZonaReserva } from './zona';

export type ReservaEstado = 'esperando' | 'aprobada' | 'rechazada' | 'cancelada';

// Fase 12D: tipo de reserva académica (RN-012/RN-015). Tres valores exactos
// del roadmap aprobado; `servicio_de_ensayo` habilita la reserva de
// recursos PS para gestor/admin.
export type TipoReserva = 'trabajo_investigacion' | 'trabajo_grado' | 'servicio_de_ensayo';

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
  // Fase 12D: tipo de reserva académica; `null` cuando no se especificó.
  tipo?: TipoReserva | null;
  // Fase 12D-bis: asistencia real, separada de estado/aprobación; `null`
  // cuando aún no se marcó.
  asistio?: boolean | null;
  // Fase 6: motivo de rechazo (solo cuando estado == rechazada).
  motivo_rechazo?: string | null;
  // Fase 12E: ensayos seleccionados (N:1 Zona)
  ensayo_ids?: number[];
  ensayos?: EnsayoReserva[];
  // Fase 12E: acompañantes nombrados (N:1 Reserva)
  acompanantes?: ReservaAcompanante[];
  created_at: string;
  updated_at: string;
  usuario: ReservaUsuario;
  espacio: ReservaEspacio;
}

export interface ReservaAcompanante {
  id: number;
  nombre: string;
  correo: string;
}

export interface AcompananteInput {
  nombre: string;
  correo: string;
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
  // Fase 12D: opcional; solo se envía cuando el usuario eligió un tipo.
  tipo?: TipoReserva | null;
  // Fase 12E: ensayos (N:1 Zona) — solo se envía si hay zonas seleccionadas
  ensayo_ids?: number[];
  // Fase 12E: acompañantes nombrados (N:1 Reserva)
  acompanantes?: AcompananteInput[];
}

export interface ReservaEstadoUpdate {
  nuevo_estado: Extract<ReservaEstado, 'aprobada' | 'rechazada' | 'cancelada'>;
  motivo?: string | null;
}

export interface ReservaAsistioUpdate {
  asistio: boolean;
}

export type ReservaUpdate = Partial<ReservaCreate>;
