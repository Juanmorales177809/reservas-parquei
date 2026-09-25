"""Recordatorios previos al inicio (API-18, RN-EVT-11/UF-RES-16).

Lo revisa la tarea programada junto con la entrega: una reserva APROBADA
de espacio o interno cuyo inicio menos `recordatorio_horas_antes` ya pasó
genera su recordatorio una sola vez (clave por reserva). No es una
operación sobre la reserva.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import text

from app.modules.notifications import productor
from app.modules.notifications import repository as repo
from app.modules.reservations import repository as reservas_repo

_ZONA_OPERATIVA = ZoneInfo("America/Bogota")


def revisar_recordatorios(db, ahora: datetime) -> int:
    local = ahora.astimezone(_ZONA_OPERATIVA)
    creados = 0
    for tabla, codigo in (
        ("reserva_espacio", "ESPACIO"),
        ("reserva_recurso_interno", "RECURSO_INTERNO"),
    ):
        filas = db.execute(
            text(
                f"SELECT r.id, r.id_unidad, d.fecha, d.hora_inicio, c.recordatorio_horas_antes "
                f"FROM reservas.reservas r "
                f"JOIN reservas.estados_reserva e ON e.id = r.estado_id "
                f"JOIN reservas.tipos_reserva t ON t.id = r.tipo_reserva_id "
                f"JOIN reservas.{tabla} d ON d.reserva_id = r.id "
                f"JOIN reservas.laboratorios_config c ON c.id_unidad = r.id_unidad "
                f"WHERE t.codigo = :tipo AND e.codigo = 'APROBADA' AND d.fecha >= :hoy"
            ),
            {"tipo": codigo, "hoy": local.date()},
        ).all()
        for rid, id_unidad, fecha, h0, antelacion in filas:
            inicio = datetime.combine(fecha, h0, tzinfo=_ZONA_OPERATIVA)
            if local < inicio - timedelta(hours=antelacion):
                continue
            if repo.obtener_evento_por_clave(db, f"RESERVA_RECORDATORIO-{rid}") is not None:
                continue
            reserva = reservas_repo.obtener_reserva(db, rid)
            productor.registrar_evento(
                db, tipo_codigo="RESERVA_RECORDATORIO", reserva_id=rid,
                ocurrencia_clave=f"RESERVA_RECORDATORIO-{rid}",
                cuentas=[reserva.id_cuenta], id_unidad=id_unidad,
                datos={
                    "tipo": codigo.lower().replace("_", " "),
                    "cuando": inicio.strftime("%Y-%m-%d %H:%M"),
                },
            )
            creados += 1
    return creados
