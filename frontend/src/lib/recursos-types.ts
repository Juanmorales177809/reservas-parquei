/**
 * Formas del contrato de resources (§2 y §3) compartidas entre servidor y
 * cliente. Sin `next/headers` — seguro para ambos lados, igual que
 * `auth-types.ts` de FE-07.
 */

export type TipoRecurso = "EQUIPO" | "MOBILIARIO" | "OTRO";

export interface RecursoResumen {
  id: number;
  tipo: TipoRecurso;
  nombre: string | null;
  id_unidad: number;
  habilitado: boolean;
}

export interface RecursoDetalle extends RecursoResumen {
  created_at: string;
  updated_at: string;
  especializacion: Record<string, unknown>;
}

export interface ImpactoDeshabilitacion {
  reservas_a_cancelar: number;
  reservas_a_retirar: number;
}

export interface EstadoRecurso {
  id: number;
  habilitado: boolean;
  reservas_canceladas: number;
  reservas_afectadas: number;
}

export interface ConfiguracionLaboratorio {
  id_unidad: number;
  habilitado_reservas: boolean;
  dias_atencion: number[];
  hora_apertura: string;
  hora_cierre: string;
  horas_antelacion: number;
  aprobacion_automatica: boolean;
  recordatorio_horas_antes: number;
  mostrar_estado_reserva: boolean;
  mostrar_reservista: boolean;
  notificar_por_correo?: boolean;
  tipos_reserva: string[];
}
