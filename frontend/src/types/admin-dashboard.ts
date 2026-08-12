export interface ReservasPorEstado {
  pendientes: number;
  aprobadas: number;
  rechazadas: number;
  canceladas: number;
}

export interface ReservaPorFecha {
  fecha: string;
  cantidad: number;
}

export interface RecursoMasReservado {
  recurso_id: number;
  nombre: string;
  cantidad: number;
}

export interface ReservasPorEspacio {
  espacio_id: number;
  nombre: string;
  cantidad: number;
}

export interface OcupacionDiaHora {
  dia: string;
  dia_orden: number;
  hora: number;
  cantidad: number;
}

export interface OcupacionGlobal {
  horas_ocupadas: number;
  horas_disponibles: number;
  porcentaje: number;
}

export interface AdminDashboardSummary {
  total_reservas: number;
  reservas_pendientes: number;
  recursos_activos: number;
  usuarios: number;
  espacio_nombre: string | null;
  reservas_por_estado: ReservasPorEstado;
  reservas_por_fecha: ReservaPorFecha[];
  reservas_por_espacio: ReservasPorEspacio[];
  recursos_mas_reservados: RecursoMasReservado[];
  ocupacion_por_dia_hora: OcupacionDiaHora[];
  ocupacion_global: OcupacionGlobal;
}
