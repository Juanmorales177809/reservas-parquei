export interface Ensayo {
  id: number;
  nombre: string;
  zona_id: number;
  estado: 'activo' | 'inactivo' | 'mantenimiento';
  created_at: string;
  updated_at: string;
  created_by: number;
  updated_by: number;
}

export interface EnsayoCreate {
  nombre: string;
  zona_id: number;
  estado?: 'activo' | 'inactivo' | 'mantenimiento';
}

export interface EnsayoReserva {
  id: number;
  nombre: string;
  zona_id: number;
  estado: 'activo' | 'inactivo' | 'mantenimiento';
}
