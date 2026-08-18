export type EstadoEntidad = 'activo' | 'inactivo' | 'mantenimiento';

/** Zona devuelta por el backend (`GET /zonas`). */
export interface Zona {
  id: number;
  nombre: string;
  espacio_id: number;
  descripcion: string | null;
  capacidad: number | null;
  estado: EstadoEntidad;
  created_at: string;
  updated_at: string;
  created_by: number;
  updated_by: number;
}

/** Subconjunto de zona incluido en `ReservaResponse.zonas` (12C-6). */
export interface ZonaReserva {
  id: number;
  nombre: string;
  espacio_id: number;
  descripcion: string | null;
  capacidad: number | null;
  estado: EstadoEntidad;
}