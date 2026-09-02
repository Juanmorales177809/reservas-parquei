"""Exportación de "mis reservas" y de la auditoría (`control_cambios`) a
CSV y Excel -- mismo patrón que `services/exportar_dashboard.py`.
"""

import csv
import io

from openpyxl import Workbook

from app.models import Reserva
from app.schemas.control_cambio import ControlCambioResponse

_ENCABEZADO_RESERVAS = ("Fecha", "Hora inicio", "Hora fin", "Laboratorio", "Recursos", "Estado", "Asistentes")
_ENCABEZADO_CONTROL_CAMBIOS = ("Fecha", "Actor", "Acción", "Entidad", "ID entidad", "Descripción")


def _fila_reserva(reserva: Reserva) -> tuple:
    return (
        reserva.fecha.isoformat(),
        str(reserva.hora_inicio),
        str(reserva.hora_fin),
        reserva.laboratorio.nombre,
        ", ".join(r.nombre for r in reserva.recursos),
        reserva.estado,
        reserva.asistentes,
    )


def construir_csv_mis_reservas(reservas: list[Reserva]) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(_ENCABEZADO_RESERVAS)
    for reserva in reservas:
        writer.writerow(_fila_reserva(reserva))
    return buffer.getvalue().encode("utf-8-sig")


def construir_xlsx_mis_reservas(reservas: list[Reserva]) -> bytes:
    libro = Workbook()
    hoja = libro.active
    hoja.title = "Mis reservas"
    hoja.append(_ENCABEZADO_RESERVAS)
    for reserva in reservas:
        hoja.append(_fila_reserva(reserva))
    buffer = io.BytesIO()
    libro.save(buffer)
    return buffer.getvalue()


def _fila_control_cambio(cambio: ControlCambioResponse) -> tuple:
    return (
        cambio.created_at.isoformat(),
        cambio.usuario,
        cambio.accion,
        cambio.entidad,
        cambio.entidad_id,
        cambio.descripcion,
    )


def construir_csv_control_cambios(cambios: list[ControlCambioResponse]) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(_ENCABEZADO_CONTROL_CAMBIOS)
    for cambio in cambios:
        writer.writerow(_fila_control_cambio(cambio))
    return buffer.getvalue().encode("utf-8-sig")


def construir_xlsx_control_cambios(cambios: list[ControlCambioResponse]) -> bytes:
    libro = Workbook()
    hoja = libro.active
    hoja.title = "Auditoría"
    hoja.append(_ENCABEZADO_CONTROL_CAMBIOS)
    for cambio in cambios:
        hoja.append(_fila_control_cambio(cambio))
    buffer = io.BytesIO()
    libro.save(buffer)
    return buffer.getvalue()
