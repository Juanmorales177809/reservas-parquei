export interface Espacio {
  id: number;
  nombre: string;
  ubicacion: string;
  capacidad: number;
  estado: 'activo' | 'inactivo' | 'mantenimiento';
  dias_atencion: number[];
  hora_apertura: string;
  hora_cierre: string;
  horario_atencion: Record<number, number[]>;
  horas_antelacion: number;
}

export interface EspacioCreate {
  nombre: string;
  ubicacion: string;
  capacidad: number;
  estado?: 'activo' | 'inactivo' | 'mantenimiento';
}

export interface EspacioUpdate {
  nombre?: string;
  ubicacion?: string;
  capacidad?: number;
  estado?: 'activo' | 'inactivo' | 'mantenimiento';
}

export interface DisponibilidadSlot {
  hora_inicio: string;
  hora_fin: string;
  estado: 'libre' | 'ocupado' | 'mantenimiento';
}

export interface ConfiguracionEspacio {
  espacio_id: number;
  espacio_nombre: string;
  dias_atencion: number[];
  hora_apertura: string;
  hora_cierre: string;
  horario_atencion: Record<number, number[]>;
  horas_antelacion: number;
  aprobacion_automatica: boolean;
}

export interface ConfiguracionEspacioUpdate {
  horario_atencion: Record<number, number[]>;
  horas_antelacion: number;
  aprobacion_automatica: boolean;
}
