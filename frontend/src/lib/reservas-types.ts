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
  id_cuenta?: number;
  requiere_apoyo: boolean;
  created_at: string;
  /** Contrato §3.1: `{fecha,hora_inicio,hora_fin}`, `{fecha_salida,fecha_devolucion_estimada}` o `null`. */
  periodo?: Record<string, string | null> | null;
  objeto?: string | null;
  unidad_nombre?: string | null;
  solicitante_nombre?: string | null;
}

export interface PaginacionRespuesta {
  pagina: number;
  tamano: number;
  total: number;
  paginas: number;
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
  unidad_nombre?: string | null;
  solicitante_nombre?: string | null;
  recursos: {
    reserva_recurso_id: number;
    recurso_id: number;
    nombre?: string | null;
    rol: string;
    estado_asignacion: string;
  }[];
  acompanantes: number[];
  acompanantes_detalle?: { id_cuenta: number; nombre: string | null }[];
  campos_adicionales: Record<string, unknown>[];
  historial: {
    estado_anterior: string | null;
    estado_nuevo: string;
    actor_cuenta_id: number | null;
    actor_nombre?: string | null;
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
  lista_espera: ListaEsperaDetalle | null;
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
  horario_unidad: { dias_atencion: number[]; hora_apertura: string; hora_cierre: string };
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

/** Metadatos de un adjunto de lista de espera (contrato reservations §2.5 y §2.6). */
export interface AdjuntoItem {
  id: number;
  reserva_id: number;
  tipo_adjunto: "PLANO" | "IMAGEN" | "DOCUMENTO";
  nombre_original: string;
  content_type: string;
  size_bytes: number;
  created_at: string;
}

/** Contextos elegibles según el tipo de cuenta (contrato reservations §2.9). */
export interface OpcionesContexto {
  tipo_cuenta: "USUARIO" | "PERSONAL" | "ADMINISTRADOR";
  proyectos: { id: number; codigo: string; nombre: string }[];
  semilleros: { id: number; codigo: string; nombre: string }[];
  pasantias: { id: number; universidad: string; docente_nombre: string }[];
  trabajos_grado: { id: number; director_nombre: string }[];
  actividades: { id: number; nombre: string; dependencia: string }[];
}

/** Cuenta elegible como acompañante (contrato reservations §2.10). */
export interface AcompananteOpcion {
  id_cuenta: number;
  nombre: string;
}

/** Bloque `lista_espera` del detalle (contrato reservations §3.2). */
export interface ListaEsperaDetalle {
  viable: boolean | null;
  fecha_evaluacion_viabilidad: string | null;
  fecha_recepcion_material: string | null;
  prioridad: number | null;
  horas_ejecucion: number | null;
  formulario: {
    datos_usuario: Record<string, unknown> | null;
    datos_tecnico: Record<string, unknown> | null;
    diligenciado_at: string | null;
    revisado_por: number | null;
    revisado_at: string | null;
  } | null;
}

/** Orden de salida FGL 030 (contrato reservations §7.1). */
export interface OrdenSalida {
  id: number;
  reserva_id: number;
  fecha_generacion: string;
  razon_solicitud: string;
  nombre_actividad_evento: string | null;
  lugar_nombre: string;
  lugar_direccion: string;
  dependencia_solicitante_snapshot: string;
  fecha_retiro_snapshot: string;
  fecha_regreso_snapshot: string;
  proyecto_codigo_snapshot: string | null;
  responsable_nombre_snapshot: string;
  responsable_cedula_snapshot: string;
  responsable_correo_snapshot: string;
  responsable_telefono_snapshot: string;
  observaciones: string | null;
  actividades: string[];
  items: {
    reserva_recurso_id: number;
    placa_snapshot: string | null;
    descripcion_snapshot: string;
    bodega_snapshot: string | null;
    cc_snapshot: string | null;
    fecha_compra_snapshot: string | null;
  }[];
}
