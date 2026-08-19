import type { Espacio, DisponibilidadSlot } from './espacio';

export interface TipoRecurso {
  id: number;
  nombre: string;
  descripcion: string;
  activo: string;
}

export interface Recurso {
  id: number;
  nombre: string;
  espacio_id: number;
  tipo_recurso_id: number;
  descripcion: string | null;
  capacidad: number;
  estado: 'activo' | 'inactivo' | 'mantenimiento';
  espacio: Espacio;
  tipo: TipoRecurso;
}

export interface RecursoCreate {
  nombre: string;
  espacio_id?: number;
  tipo_recurso_id: number;
  descripcion?: string;
  capacidad: number;
  estado?: 'activo' | 'inactivo' | 'mantenimiento';
}

export type RecursoUpdate = Partial<RecursoCreate>;
export type RecursoDisponibilidad = DisponibilidadSlot;
