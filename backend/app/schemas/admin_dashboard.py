from datetime import date

from pydantic import BaseModel


class ReservasPorEstado(BaseModel):
    pendientes: int
    aprobadas: int
    rechazadas: int
    canceladas: int


class ReservasPorFecha(BaseModel):
    fecha: date
    cantidad: int


class RecursoMasReservado(BaseModel):
    recurso_id: int
    nombre: str
    cantidad: int


class ReservasPorEspacio(BaseModel):
    espacio_id: int
    nombre: str
    cantidad: int


class OcupacionDiaHora(BaseModel):
    dia: str
    dia_orden: int
    hora: int
    cantidad: int


class OcupacionGlobal(BaseModel):
    horas_ocupadas: float
    horas_disponibles: float
    porcentaje: float


class AdminDashboardSummary(BaseModel):
    total_reservas: int
    reservas_pendientes: int
    recursos_activos: int
    usuarios: int
    espacio_nombre: str | None = None
    reservas_por_estado: ReservasPorEstado
    reservas_por_fecha: list[ReservasPorFecha]
    reservas_por_espacio: list[ReservasPorEspacio]
    recursos_mas_reservados: list[RecursoMasReservado]
    ocupacion_por_dia_hora: list[OcupacionDiaHora]
    ocupacion_global: OcupacionGlobal
