"""Esquemas Pydantic del contrato de reservations §2 y §3 (API-13).

`detalle` es un `dict[str, Any]` en la petición porque su forma depende de
`tipo_reserva` (contrato §2.1); cada `ReservationStrategy` valida y
normaliza el suyo, igual que `especializacion` en el contrato de resources
(API-09). No se define un schema Pydantic por tipo para no duplicar esa
selección fuera de las estrategias.
"""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any, Literal

from pydantic import BaseModel, Field

TipoReservaCodigo = Literal["ESPACIO", "RECURSO_INTERNO", "RECURSO_CAMPUS", "RECURSO_EXTERNO", "LISTA_ESPERA"]
RolRecurso = Literal["PRINCIPAL", "ADICIONAL"]


class ContextoCrear(BaseModel):
    proyecto_id: int | None = None
    semillero_id: int | None = None
    pasantia_id: int | None = None
    trabajo_grado_id: int | None = None
    actividad_institucional_id: int | None = None


class RecursoAsignarCrear(BaseModel):
    recurso_id: int
    rol: RolRecurso


class CampoValorCrear(BaseModel):
    campo_id: int
    valor_texto: str | None = None
    opcion_id: int | None = None


# --- §2.1 Crear ---------------------------------------------------------------------


class ReservaCrear(BaseModel):
    id_unidad: int
    tipo_reserva: TipoReservaCodigo
    observacion: str | None = None
    requiere_apoyo: bool = False
    contexto: ContextoCrear
    detalle: dict[str, Any] = Field(default_factory=dict)
    recursos: list[RecursoAsignarCrear] = []
    acompanantes: list[int] = []
    campos_adicionales: list[CampoValorCrear] = []


class ReservaResumen(BaseModel):
    id: int
    estado: str
    tipo_reserva: str
    id_unidad: int
    requiere_apoyo: bool
    created_at: datetime


# --- §2.2 Catálogo de tipos ----------------------------------------------------------


class TipoReservaItem(BaseModel):
    codigo: str
    nombre: str


# --- §2.3/§2.4 Lista de espera: formulario y viabilidad -------------------------------


class FormularioParteCuerpo(BaseModel):
    """Exactamente una de las dos partes, como objeto JSON no vacío (contrato §2.3)."""

    datos_usuario: dict[str, Any] | None = None
    datos_tecnico: dict[str, Any] | None = None


class FormularioRespuesta(BaseModel):
    reserva_id: int
    datos_usuario: dict[str, Any]
    datos_tecnico: dict[str, Any] | None
    diligenciado_at: datetime
    revisado_por: int | None
    revisado_at: datetime | None


class ViabilidadCrear(BaseModel):
    viable: bool
    motivo: str | None = None


class ViabilidadRespuesta(BaseModel):
    id: int
    viable: bool
    fecha_evaluacion_viabilidad: datetime
    estado: str


# --- §2.5-2.7 Adjuntos -----------------------------------------------------------------


class AdjuntoRespuesta(BaseModel):
    id: int
    reserva_id: int
    tipo_adjunto: str
    nombre_original: str
    content_type: str
    size_bytes: int
    uploaded_by: int
    created_at: datetime


# --- §2.8 Editar ------------------------------------------------------------------------


class ReservaActualizar(BaseModel):
    observacion: str | None = None
    contexto: ContextoCrear | None = None
    requiere_apoyo: bool | None = None
    detalle: dict[str, Any] | None = None
    recursos: list[RecursoAsignarCrear] | None = None
    acompanantes: list[int] | None = None
    campos_adicionales: list[CampoValorCrear] | None = None


# --- §3 Consulta ------------------------------------------------------------------------


class RecursoAsignadoDetalle(BaseModel):
    reserva_recurso_id: int
    recurso_id: int
    nombre: str | None = None
    rol: str
    estado_asignacion: str
    incorporado_at: datetime | None = None
    retirado_at: datetime | None = None
    causa_retiro: str | None = None
    reserva_causante_id: int | None = None


class ContextoDetalle(BaseModel):
    proyecto_id: int | None = None
    proyecto_codigo: str | None = None
    proyecto_nombre: str | None = None
    semillero_id: int | None = None
    semillero_codigo: str | None = None
    semillero_nombre: str | None = None
    pasantia_id: int | None = None
    pasantia_universidad: str | None = None
    pasantia_docente_nombre: str | None = None
    pasantia_docente_correo: str | None = None
    trabajo_grado_id: int | None = None
    trabajo_grado_director_nombre: str | None = None
    trabajo_grado_director_correo: str | None = None
    actividad_institucional_id: int | None = None
    actividad_nombre: str | None = None


class HistorialEstadoItem(BaseModel):
    actor_nombre: str | None = None
    estado_anterior: str | None
    estado_nuevo: str
    actor_cuenta_id: int | None
    motivo: str | None
    created_at: datetime


class PropuestaVigente(BaseModel):
    id: int
    origen: str
    fecha_inicio_propuesta: date
    fecha_fin_propuesta: date
    hora_inicio: time | None
    hora_fin: time | None
    motivo: str
    created_at: datetime


class ReservaListItem(BaseModel):
    id: int
    estado: str
    tipo_reserva: str
    id_unidad: int
    id_cuenta: int
    observacion: str | None
    requiere_apoyo: bool
    created_at: datetime
    periodo: dict[str, Any] | None = None
    objeto: str | None = None
    unidad_nombre: str | None = None
    solicitante_nombre: str | None = None


class ReservaDetalleRespuesta(BaseModel):
    id: int
    estado: str
    tipo_reserva: str
    id_unidad: int
    id_cuenta: int
    observacion: str | None
    requiere_apoyo: bool
    created_at: datetime
    updated_at: datetime
    fecha_aprobacion: datetime | None
    fecha_cancelacion: datetime | None
    motivo_cancelacion: str | None
    detalle: dict[str, Any]
    contexto: ContextoDetalle
    recursos: list[RecursoAsignadoDetalle] = []
    acompanantes: list[int] = []
    acompanantes_detalle: list[dict[str, Any]] = []
    unidad_nombre: str | None = None
    solicitante_nombre: str | None = None
    campos_adicionales: list[dict[str, Any]] = []
    historial: list[HistorialEstadoItem] = []
    propuesta_vigente: PropuestaVigente | None = None
    lista_espera: dict[str, Any] | None = None


# --- §4 Gestión por el Técnico -----------------------------------------------------------

class AprobacionCuerpo(BaseModel):
    observacion: str | None = None
    material_recibido: bool | None = None


class AprobacionRespuesta(BaseModel):
    id: int
    estado: str
    fecha_aprobacion: datetime
    detalle: dict[str, Any] | None = None


class RechazoCuerpo(BaseModel):
    motivo: str


class RechazoRespuesta(BaseModel):
    id: int
    estado: str
    motivo: str


class RecursosAgregarCuerpo(BaseModel):
    recursos: list[RecursoAsignarCrear]


# --- §5 Propuestas de periodo ------------------------------------------------------------

class PropuestaCrear(BaseModel):
    fecha_inicio_propuesta: date
    fecha_fin_propuesta: date
    hora_inicio: time | None = None
    hora_fin: time | None = None
    motivo: str


class PropuestaRespuesta(BaseModel):
    id: int
    reserva_id: int
    origen: str
    fecha_inicio_propuesta: date
    fecha_fin_propuesta: date
    hora_inicio: time | None
    hora_fin: time | None
    motivo: str
    estado: str
    creada_por: int
    resuelta_por: int | None
    created_at: datetime
    resuelta_at: datetime | None


# --- §6 Ejecución --------------------------------------------------------------------------

class RecursoEntregaItem(BaseModel):
    reserva_recurso_id: int
    observacion_entrega: str | None = None


class EjecucionCuerpo(BaseModel):
    recursos: list[RecursoEntregaItem] | None = None


class RecursoDevolucionItem(BaseModel):
    reserva_recurso_id: int
    observacion_devolucion: str | None = None


class FinalizacionCuerpo(BaseModel):
    recursos: list[RecursoDevolucionItem] | None = None
    horas_ejecucion: float | None = None


class CancelacionCuerpo(BaseModel):
    motivo: str | None = None


class TransicionRespuesta(BaseModel):
    id: int
    estado: str
    detalle: dict[str, Any] | None = None


# --- §3.3 Disponibilidad -----------------------------------------------------------------


class HorarioUnidadItem(BaseModel):
    dias_atencion: list[int]
    hora_apertura: time
    hora_cierre: time


class DisponibilidadFranja(BaseModel):
    fecha: date
    hora_inicio: time | None = None
    hora_fin: time | None = None
    disponible: bool


class DisponibilidadRespuesta(BaseModel):
    horario_unidad: HorarioUnidadItem
    franjas: list[DisponibilidadFranja]


# --- §7 Orden de salida ------------------------------------------------------------------------


class OrdenSalidaItemRespuesta(BaseModel):
    reserva_recurso_id: int
    placa_snapshot: str | None = None
    descripcion_snapshot: str
    bodega_snapshot: str | None = None
    cc_snapshot: str | None = None
    fecha_compra_snapshot: date | None = None


class OrdenSalidaRespuesta(BaseModel):
    id: int
    reserva_id: int
    fecha_generacion: datetime
    razon_solicitud: str
    nombre_actividad_evento: str | None = None
    lugar_nombre: str
    lugar_direccion: str
    dependencia_solicitante_snapshot: str
    fecha_retiro_snapshot: date
    fecha_regreso_snapshot: date
    proyecto_codigo_snapshot: str | None = None
    responsable_nombre_snapshot: str
    responsable_cedula_snapshot: str
    responsable_correo_snapshot: str
    responsable_telefono_snapshot: str
    observaciones: str | None = None
    actividades: list[str] = []
    items: list[OrdenSalidaItemRespuesta] = []
