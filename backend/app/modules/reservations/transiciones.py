"""Transiciones automáticas por horario (API-16: UF-RES-21 y UF-RES-22).

Sin superficie HTTP y sin entrega/devolución física: solo espacio e
interno avanzan por el mero paso del tiempo. `avanzar_por_horario` es pura
y recibe `ahora` para poder probarse sin esperar al reloj. El `lifespan`
de `main.py` la invoca cada 60 segundos con su propia sesión.

No toca asignaciones de recursos: por construcción no compite con el
retiro por préstamo de DB-12. La disponibilidad nunca depende de este
proceso (RN-TIP-PE-26/RN-DIS-11): se calcula por periodo y solapamiento.
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.modules.reservations import repository as repo

_ZONA_OPERATIVA = ZoneInfo("America/Bogota")
_MOTIVO_VENCIMIENTO = "Vencimiento de la franja sin aprobación."
_MOTIVO_INICIO = "Inicio automático por horario."
_MOTIVO_FIN = "Fin automático de la franja."

_DETALLE = {"ESPACIO": "reserva_espacio", "RECURSO_INTERNO": "reserva_recurso_interno"}


def _candidatas(db: Session, tipo: str, estados: tuple[str, ...], hoy, hora, *, iniciar: bool) -> list[int]:
    """Ids con franja vigente (iniciar) o vencida (finalizar/vencer)."""
    tabla = _DETALLE[tipo]
    if iniciar:
        condicion = "(d.fecha = :hoy AND d.hora_inicio <= :hora AND :hora < d.hora_fin)"
    else:
        condicion = "(d.fecha < :hoy OR (d.fecha = :hoy AND d.hora_fin <= :hora))"
    filas = db.execute(
        text(
            f"SELECT r.id FROM reservas.reservas r "
            f"JOIN reservas.estados_reserva e ON e.id = r.estado_id "
            f"JOIN reservas.tipos_reserva t ON t.id = r.tipo_reserva_id "
            f"JOIN reservas.{tabla} d ON d.reserva_id = r.id "
            f"WHERE t.codigo = :tipo AND e.codigo IN :estados AND {condicion}"
        ).bindparams(bindparam("estados", expanding=True)),
        {"tipo": tipo, "estados": list(estados), "hoy": hoy, "hora": hora},
    ).all()
    return [f[0] for f in filas]


def _transitar(db: Session, reserva_id: int, nuevo_id: int, ahora: datetime, motivo: str | None, *, cancela: bool = False) -> None:
    reserva = repo.obtener_reserva(db, reserva_id)
    anterior_id = reserva.estado_id
    reserva.estado_id = nuevo_id
    if cancela:
        reserva.fecha_cancelacion = ahora
        reserva.motivo_cancelacion = motivo
    repo.registrar_historial(
        db, reserva_id=reserva_id, estado_anterior_id=anterior_id,
        estado_nuevo_id=nuevo_id, actor_cuenta_id=None, motivo=motivo,
    )


def avanzar_por_horario(db: Session, ahora: datetime) -> dict[str, int]:
    """Aplica UF-RES-22 (inicios) y UF-RES-21 (vencimientos). Idempotente:
    una segunda pasada inmediata no encuentra nada que mover."""
    local = ahora.astimezone(_ZONA_OPERATIVA)
    hoy, hora = local.date(), local.time()
    en_ejecucion = repo.obtener_estado_id_codigo(db, "EN_EJECUCION")
    finalizada = repo.obtener_estado_id_codigo(db, "FINALIZADA")
    cancelada = repo.obtener_estado_id_codigo(db, "CANCELADA")
    cuenta = {"iniciadas": 0, "finalizadas": 0, "canceladas": 0}

    for tipo in ("ESPACIO", "RECURSO_INTERNO"):
        for rid in _candidatas(db, tipo, ("APROBADA",), hoy, hora, iniciar=True):
            _transitar(db, rid, en_ejecucion, ahora, _MOTIVO_INICIO)
            cuenta["iniciadas"] += 1
    for rid in _candidatas(db, "ESPACIO", ("SOLICITADA",), hoy, hora, iniciar=False):
        _transitar(db, rid, cancelada, ahora, _MOTIVO_VENCIMIENTO, cancela=True)
        cuenta["canceladas"] += 1
    for rid in _candidatas(db, "ESPACIO", ("APROBADA", "EN_EJECUCION"), hoy, hora, iniciar=False):
        _transitar(db, rid, finalizada, ahora, _MOTIVO_FIN)
        cuenta["finalizadas"] += 1
    for rid in _candidatas(db, "RECURSO_INTERNO", ("EN_EJECUCION",), hoy, hora, iniciar=False):
        _transitar(db, rid, finalizada, ahora, _MOTIVO_FIN)
        cuenta["finalizadas"] += 1

    db.commit()
    return cuenta
