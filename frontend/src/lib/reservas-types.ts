/**
 * Formas del contrato de reservations (§2 a §8) compartidas entre servidor
 * y cliente. Sin `next/headers` — seguro para ambos lados, igual que
 * `auth-types.ts` de FE-07.
 */

export type TipoReservaCodigo =
  | "ESPACIO"
  | "RECURSO_INTERNO"
  | "RECURSO_CAMPUS"
  | "RECURSO_EXTERNO"
  | "LISTA_ESPERA";

export interface ReservaResumen {
  id: number;
  estado: string;
  tipo_reserva: string;
  id_unidad: number;
  requiere_apoyo: boolean;
  created_at: string;
}

export interface ReservaDetalleRespuesta {
  id: number;
  estado: string;
  tipo_reserva: string;
  id_unidad: number;
  id_cuenta: number;
  observacion: string | null;
  requiere_apoyo: boolean;
  created_at: string;
  updated_at: string;
  fecha_aprobacion: string | null;
  fecha_cancelacion: string | null;
  motivo_cancelacion: string | null;
  detalle: Record<string, unknown>;
  contexto: Record<string, unknown>;
  recursos: {
    reserva_recurso_id: number;
    recurso_id: number;
    rol: string;
    estado_asignacion: string;
  }[];
  acompanantes: number[];
  campos_adicionales: Record<string, unknown>[];
  historial: {
    estado_anterior: string | null;
    estado_nuevo: string;
    actor_cuenta_id: number | null;
    motivo: string | null;
    created_at: string;
  }[];
  propuesta_vigente: {
    id: number;
    origen: string;
    fecha_inicio_propuesta: string;
    fecha_fin_propuesta: string;
    hora_inicio: string | null;
    hora_fin: string | null;
    motivo: string;
    created_at: string;
  } | null;
  lista_espera: Record<string, unknown> | null;
}

export interface AprobacionRespuesta {
  id: number;
  estado: string;
  fecha_aprobacion: string;
  detalle?: Record<string, unknown> | null;
}

export interface RechazoRespuesta {
  id: number;
  estado: string;
  motivo: string;
}

export interface PropuestaRespuesta {
  id: number;
  reserva_id: number;
  origen: string;
  fecha_inicio_propuesta: string;
  fecha_fin_propuesta: string;
  hora_inicio: string | null;
  hora_fin: string | null;
  motivo: string;
  estado: string;
  creada_por: number;
  resuelta_por: number | null;
  created_at: string;
  resuelta_at: string | null;
}

export interface TransicionRespuesta {
  id: number;
  estado: string;
  detalle?: Record<string, unknown> | null;
}

export interface ViabilidadRespuesta {
  id: number;
  viable: boolean;
  fecha_evaluacion_viabilidad: string;
  estado: string;
}

export interface DisponibilidadRespuesta {
  horario_unidad: Record<string, unknown>;
  franjas: { fecha: string; hora_inicio: string | null; hora_fin: string | null; disponible: boolean }[];
}

export interface TipoReservaItem {
  codigo: string;
  nombre: string;
}

export interface ReservaCrear {
  id_unidad: number;
  tipo_reserva: TipoReservaCodigo;
  observacion?: string;
  requiere_apoyo?: boolean;
  contexto: {
    proyecto_id?: number;
    semillero_id?: number;
    pasantia_id?: number;
    trabajo_grado_id?: number;
    actividad_institucional_id?: number;
  };
  detalle: Record<string, unknown>;
  recursos?: { recurso_id: number; rol: "PRINCIPAL" | "ADICIONAL" }[];
  acompanantes?: number[];
  campos_adicionales?: { campo_id: number; valor_texto?: string; opcion_id?: number }[];
}
