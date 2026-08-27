from __future__ import annotations

from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.domain.enums import EstadoEntidad, EstadoReserva, Rol, TipoReserva


class ReservaCreate(BaseModel):
    # Fase 12C-6: contrato aprobado. `recurso_id` legacy se rechaza con 422
    # (`extra="forbid"`), no se acepta como alias silencioso.
    model_config = ConfigDict(extra="forbid")

    recurso_ids: list[int] = Field(default_factory=list)
    zona_ids: list[int] = Field(default_factory=list)
    # Fase 12D (parcial): tipo de reserva académica (RN-012/RN-015).
    # Opcional: las reservas que no lo declaran quedan sin tipo. Solo
    # `servicio_de_ensayo` habilita los recursos PS para gestor/admin
    # (ver services/reservas.py::validar_acceso_ps).
    tipo: TipoReserva | None = None
    # Fase 12E: ensayos seleccionados durante la reserva (N:1 Zona,
    # RN-015/RN-016). Cada ensayo debe pertenecer a una de las zonas
    # efectivamente reservadas (validado en services/reservas.py).
    ensayo_ids: list[int] = Field(default_factory=list)
    # Fase 12E: acompañantes nombrados (N:1 Reserva, RN-015).
    acompanantes: list[AcompananteInput] = Field(default_factory=list)
    # Fase A3: texto libre opcional -- "Actividad a realizar" del formulario
    # real de solicitud de laboratorios.
    descripcion: str | None = None
    fecha: date
    hora_inicio: time
    hora_fin: time
    asistentes: int = Field(gt=0)

    @model_validator(mode="after")
    def _al_menos_un_recurso_o_zona(self) -> "ReservaCreate":
        if not self.recurso_ids and not self.zona_ids:
            raise ValueError("Debes indicar al menos un recurso o una zona")
        return self


class ReservaUpdate(BaseModel):
    # Fase 12C-6: ejes de reemplazo completo. Un eje ausente no modifica su
    # conjunto actual; un eje presente lo reemplaza entero. La combinación
    # final se valida en el servicio (puede quedar vacía según estado actual).
    model_config = ConfigDict(extra="forbid")

    recurso_ids: list[int] | None = None
    zona_ids: list[int] | None = None
    # Fase 12D (parcial): `tipo` es un eje de asignación simple (ausente se
    # conserva; `null` explícito lo limpia). Ver `actualizar_reserva` en
    # services/reservas.py (`cambios.get("tipo", reserva.tipo)`).
    tipo: TipoReserva | None = None
    # Fase 12E: eje de reemplazo completo para ensayos (mismo criterio que
    # recurso_ids/zona_ids: ausente conserva, presente reemplaza).
    ensayo_ids: list[int] | None = None
    # Fase 12E: eje de reemplazo completo para acompañantes (ausente
    # conserva, presente reemplaza; `[]` explícito la vacía).
    acompanantes: list[AcompananteInput] | None = None
    # Fase A3: eje simple, mismo criterio que `tipo` -- ausente conserva el
    # valor actual, `null` explícito lo limpia.
    descripcion: str | None = None
    fecha: date | None = None
    hora_inicio: time | None = None
    hora_fin: time | None = None
    asistentes: int | None = Field(default=None, gt=0)


class ReservaAsistioUpdate(BaseModel):
    """Fase 12D-bis: payload del endpoint dedicado `PUT /reservas/{id}/asistio`.

    Siempre se manda un valor concreto (`true`/`false`); no hay semántica de
    "ausencia conserva" como en `ReservaUpdate`.
    """

    asistio: bool


class ReservaEstadoUpdate(BaseModel):
    nuevo_estado: Literal[
        EstadoReserva.APROBADA, EstadoReserva.RECHAZADA, EstadoReserva.CANCELADA
    ]
    motivo: str | None = Field(default=None, max_length=500)

    @field_validator("motivo")
    @classmethod
    def _validar_motivo(cls, value: str | None) -> str | None:
        if value is not None:
            v = value.strip()
            if len(v) == 0:
                raise ValueError("El motivo no puede estar vacío")
            return v
        return value

    @model_validator(mode="after")
    def _motivo_obligatorio_si_rechazada(self) -> "ReservaEstadoUpdate":
        if self.nuevo_estado == EstadoReserva.RECHAZADA:
            if self.motivo is None or len(self.motivo.strip()) == 0:
                raise ValueError("Debes indicar el motivo del rechazo")
        return self


class UsuarioReservaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    rol: Rol


class EspacioReservaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    # Opcional (Fase 12E): ver app/schemas/espacio.py.
    capacidad: int | None = None
    estado: EstadoEntidad


class RecursoReservaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    # Opcional (Fase 12E): ver app/schemas/recurso.py.
    capacidad: int | None = None
    estado: EstadoEntidad
    espacio: EspacioReservaResponse


class ZonaReservaResponse(BaseModel):
    """Zona asociada a una reserva (Fase 12C-6). Misma base mínima que
    `ZonaResponse` sin timestamps/auditoría — suficiente para la respuesta
    de la reserva y los mensajes de notificación."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    espacio_id: int
    descripcion: str | None
    capacidad: int | None
    estado: EstadoEntidad


class EnsayoReservaResponse(BaseModel):
    """Ensayo asociado a una reserva (Fase 12E, N:1 Zona). Subset mínimo
    para la respuesta de reserva, mismo criterio que ZonaReservaResponse."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    zona_id: int
    estado: EstadoEntidad


class AcompananteInput(BaseModel):
    """Fase 12E: acompañante nombrado (N:1 Reserva). Sin cuenta de usuario
    propia; responde a la pregunta abierta 6 de la Fase 12A (nombre+correo).
    Cedula se omite por estar vacía en los datos reales."""

    model_config = ConfigDict(extra="forbid")

    nombre: str = Field(min_length=1, max_length=150)
    correo: str = Field(min_length=1, max_length=255)

    @field_validator("correo")
    @classmethod
    def _validar_correo(cls, value: str) -> str:
        # Mismo validador manual que UsuarioCreate/EspacioCreate: evita
        # depender de email-validator (ver schemas/README.md).
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Formato de correo inválido")
        return value


class ReservaAcompananteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    correo: str


class ReservaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    espacio_id: int
    fecha: date
    hora_inicio: time
    hora_fin: time
    estado: EstadoReserva
    asistentes: int
    # Fase 12D (parcial): tipo de reserva académica declarada al crear o
    # editar la reserva; `null` cuando no se especificó.
    tipo: TipoReserva | None = None
    # Fase 12D-bis: asistencia real, separada de estado/aprobación; `null`
    # cuando aún no se marcó.
    asistio: bool | None = None
    # Motivo de rechazo (Fase 6): `null` salvo cuando `estado == rechazada`.
    motivo_rechazo: str | None = None
    # Fase A3: `null` cuando no se especificó ninguna descripción.
    descripcion: str | None = None
    created_at: datetime
    updated_at: datetime
    usuario: UsuarioReservaResponse
    espacio: EspacioReservaResponse
    # Fase 12C-4e-schemas: `recurso_id`/`recurso` (el ancla singular) se
    # retiran del contrato. `recursos_asociados` (`crud.reservas`) sigue
    # siendo la fuente de verdad para los conjuntos -- `reservas.recurso_id`
    # (la columna), `Reserva.recurso` (la relación ORM) y
    # `reservas_sin_solapamiento` NO se tocan en esta subfase, solo dejan de
    # exponerse aquí.
    recurso_ids: list[int] = Field(default_factory=list)
    recursos: list[RecursoReservaResponse] = Field(default_factory=list)
    zona_ids: list[int] = Field(default_factory=list)
    zonas: list[ZonaReservaResponse] = Field(default_factory=list)
    ensayo_ids: list[int] = Field(default_factory=list)
    ensayos: list[EnsayoReservaResponse] = Field(default_factory=list)
    acompanantes: list[ReservaAcompananteResponse] = Field(default_factory=list)
