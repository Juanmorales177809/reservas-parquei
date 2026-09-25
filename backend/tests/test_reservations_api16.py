"""Pruebas de API-16: transiciones automáticas por horario (UF-RES-21/22).

Sin superficie HTTP: se invoca `avanzar_por_horario` con un `ahora` fijo.
Las franjas pasadas se siembran directo por repositorio (la API rechaza
fechas pasadas, como debe). Cubre RN-TIP-PE-25/27, RN-TIP-RI-08/09,
RN-TIP-PE-26/RN-DIS-11 (disponibilidad independiente del proceso) y
RN-CAN-02 para interno.
"""

from __future__ import annotations

from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from sqlalchemy import text

from .conftest import crear_tecnico

from app.modules.reservations import repository as repo
from app.modules.reservations.transiciones import avanzar_por_horario

_BOGOTA = ZoneInfo("America/Bogota")
_AHORA = datetime(2030, 4, 1, 11, 0, tzinfo=_BOGOTA)
_HOY = date(2030, 4, 1)


def _sembrar(db, tag: str) -> dict:
    from app.db.models.reservas import Espacios, LaboratoriosConfig

    cuenta, id_unidad = crear_tecnico(db, tag)
    from datetime import timezone

    ahora = datetime.now(timezone.utc)
    db.add(
        LaboratoriosConfig(
            id_unidad=id_unidad, habilitado_reservas=True,
            dias_atencion=[0, 1, 2, 3, 4, 5, 6],
            hora_apertura=time(0, 0), hora_cierre=time(23, 59),
            horario_atencion={}, horas_antelacion=0, aprobacion_automatica=False,
            notificar_por_correo=False, mostrar_estado_reserva=False,
            mostrar_reservista=False, recordatorio_horas_antes=24,
        )
    )
    espacio = Espacios(
        id_unidad=id_unidad, nombre=f"Espacio api16 {tag}", capacidad=10,
        habilitado=True, created_at=ahora, updated_at=ahora,
    )
    db.add(espacio)
    db.flush()
    return {"cuenta": cuenta, "id_unidad": id_unidad, "espacio_id": espacio.id}


def _otro_espacio(db, s: dict, tag: str, n: int) -> int:
    from datetime import timezone

    from app.db.models.reservas import Espacios

    ahora = datetime.now(timezone.utc)
    espacio = Espacios(
        id_unidad=s["id_unidad"], nombre=f"Espacio api16 {tag}-{n}",
        capacidad=10, habilitado=True, created_at=ahora, updated_at=ahora,
    )
    db.add(espacio)
    db.flush()
    db.commit()
    return espacio.id


def _reserva(db, s: dict, tipo: str, estado: str, h0: time, h1: time, tag: str, n: int = 0) -> int:
    tipo_id = repo.obtener_tipo_por_codigo(db, tipo).id
    estado_id = repo.obtener_estado_id_codigo(db, estado)
    r = repo.crear_reserva(
        db, id_unidad=s["id_unidad"], tipo_reserva_id=tipo_id,
        id_cuenta=s["cuenta"].id_cuenta, estado_id=estado_id,
        observacion=f"api16-{tag}", requiere_apoyo=False,
        created_by=s["cuenta"].id_cuenta,
    )
    if tipo == "ESPACIO":
        espacio_id = s["espacio_id"] if n == 0 else _otro_espacio(db, s, tag, n)
        repo.crear_detalle_espacio(
            db, r.id, espacio_id=espacio_id, fecha=_HOY,
            hora_inicio=h0, hora_fin=h1, asistentes=0,
        )
    else:
        repo.crear_detalle_interno(
            db, r.id, fecha=_HOY, hora_inicio=h0, hora_fin=h1,
        )
    repo.registrar_historial(
        db, reserva_id=r.id, estado_anterior_id=None,
        estado_nuevo_id=estado_id, actor_cuenta_id=s["cuenta"].id_cuenta, motivo=None,
    )
    db.commit()
    return r.id


def _estado(db, rid: int) -> str:
    return repo.obtener_estado(db, repo.obtener_reserva(db, rid).estado_id).codigo


def _limpiar(db, s: dict, rids: list[int]) -> None:
    for rid in rids:
        for tabla in (
            "reserva_historial_estado",
            "reserva_contexto",
            "reserva_espacio",
            "reserva_recurso_interno",
        ):
            db.execute(
                text(f"DELETE FROM reservas.{tabla} WHERE reserva_id = :i"),
                {"i": rid},
            )
        db.execute(text("DELETE FROM reservas.reservas WHERE id = :i"), {"i": rid})
    db.execute(
        text("DELETE FROM reservas.espacios WHERE id_unidad = :u"), {"u": s["id_unidad"]}
    )
    db.execute(
        text("DELETE FROM reservas.laboratorios_config WHERE id_unidad = :u"),
        {"u": s["id_unidad"]},
    )
    db.commit()


def test_inicios_y_vencimientos(client, db, tag):
    """UF-RES-22/21: inicia lo vigente; vence a CANCELADA/FINALIZADA; terminales quietos."""
    s = _sembrar(db, tag)
    T = time
    rids = [
        _reserva(db, s, "ESPACIO", "APROBADA", T(10, 0), T(12, 0), tag, 0),      # inicia
        _reserva(db, s, "ESPACIO", "APROBADA", T(8, 0), T(9, 0), tag, 1),        # finaliza
        _reserva(db, s, "ESPACIO", "SOLICITADA", T(8, 0), T(9, 0), tag, 2),      # cancela
        _reserva(db, s, "ESPACIO", "EN_EJECUCION", T(8, 0), T(9, 0), tag, 3),    # finaliza
        _reserva(db, s, "ESPACIO", "RECHAZADA", T(8, 0), T(9, 0), tag, 4),       # quieta
        _reserva(db, s, "RECURSO_INTERNO", "APROBADA", T(10, 0), T(12, 0), tag, 5),
        _reserva(db, s, "RECURSO_INTERNO", "EN_EJECUCION", T(8, 0), T(9, 0), tag, 6),
    ]
    try:
        mov = avanzar_por_horario(db, _AHORA)
        assert mov == {"iniciadas": 2, "finalizadas": 3, "canceladas": 1}
        assert _estado(db, rids[0]) == "EN_EJECUCION"
        assert _estado(db, rids[1]) == "FINALIZADA"
        assert _estado(db, rids[2]) == "CANCELADA"
        assert _estado(db, rids[3]) == "FINALIZADA"
        assert _estado(db, rids[4]) == "RECHAZADA"
        assert _estado(db, rids[5]) == "EN_EJECUCION"
        assert _estado(db, rids[6]) == "FINALIZADA"

        reserva = repo.obtener_reserva(db, rids[2])
        assert reserva.motivo_cancelacion is not None
        assert reserva.fecha_cancelacion is not None
        historial = repo.historial_de_reserva(db, rids[0])
        assert historial[-1].actor_cuenta_id is None

        # Idempotente: segunda pasada no mueve nada.
        assert avanzar_por_horario(db, _AHORA) == {
            "iniciadas": 0, "finalizadas": 0, "canceladas": 0,
        }
    finally:
        _limpiar(db, s, rids)


def test_vencida_no_se_inicia(client, db, tag):
    """Un espacio APROBADA ya vencido no se inicia por una pasada tardía."""
    s = _sembrar(db, tag)
    T = time
    rid = _reserva(db, s, "ESPACIO", "APROBADA", T(8, 0), T(9, 0), tag)
    try:
        avanzar_por_horario(db, _AHORA)
        assert _estado(db, rid) == "FINALIZADA"
    finally:
        _limpiar(db, s, [rid])


def test_disponibilidad_no_depende_del_proceso(client, db, tag):
    """RN-TIP-PE-26: un intervalo posterior libre lo está aunque el proceso
    no haya corrido (aquí ni siquiera se invoca)."""
    from datetime import timedelta

    s = _sembrar(db, tag)
    T = time
    rid = _reserva(db, s, "ESPACIO", "APROBADA", T(8, 0), T(9, 0), tag)
    try:
        manana = _HOY + timedelta(days=1)
        assert not repo.existe_solapamiento_espacio(
            db, s["espacio_id"],
            datetime.combine(manana, T(10, 0), tzinfo=_BOGOTA),
            datetime.combine(manana, T(12, 0), tzinfo=_BOGOTA),
        )
    finally:
        _limpiar(db, s, [rid])
