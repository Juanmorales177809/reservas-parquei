"""Repositorio de notifications (API-17): solo lectura de la bandeja y
preferencias propias. La generación de eventos y envíos es API-18; aquí no
se crea ninguna notificación.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.notificaciones import (
    EnviosCorreo,
    Eventos,
    Notificaciones,
    Preferencias,
    TiposEvento,
)


def bandeja(
    db: Session, id_cuenta: int, *, leida: bool | None, tipo_codigo: str | None,
    offset: int, tamano: int,
) -> tuple[list[tuple[Notificaciones, Eventos, TiposEvento]], int]:
    stmt = (
        select(Notificaciones, Eventos, TiposEvento)
        .join(Eventos, Eventos.id == Notificaciones.evento_id)
        .join(TiposEvento, TiposEvento.id == Eventos.tipo_evento_id)
        .where(Notificaciones.id_cuenta == id_cuenta)
    )
    if leida is True:
        stmt = stmt.where(Notificaciones.leida_at.is_not(None))
    elif leida is False:
        stmt = stmt.where(Notificaciones.leida_at.is_(None))
    if tipo_codigo is not None:
        stmt = stmt.where(TiposEvento.codigo == tipo_codigo)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    filas = db.execute(
        stmt.order_by(Notificaciones.created_at.desc()).offset(offset).limit(tamano)
    ).all()
    return list(filas), total


def obtener_notificacion(db: Session, id_notificacion: int, id_cuenta: int) -> Notificaciones | None:
    """Solo propia: ajena e inexistente son indistinguibles (RN-CON-01)."""
    return db.scalar(
        select(Notificaciones).where(
            Notificaciones.id == id_notificacion, Notificaciones.id_cuenta == id_cuenta
        )
    )


def marcar_leida(db: Session, notificacion: Notificaciones, ahora) -> Notificaciones:
    if notificacion.leida_at is None:
        notificacion.leida_at = ahora
    return notificacion


def tipos_habilitados(db: Session) -> list[TiposEvento]:
    return list(db.scalars(
        select(TiposEvento).where(TiposEvento.habilitado.is_(True)).order_by(TiposEvento.id)
    ).all())


def obtener_tipo(db: Session, tipo_evento_id: int) -> TiposEvento | None:
    return db.get(TiposEvento, tipo_evento_id)


def obtener_tipo_por_codigo(db: Session, codigo: str) -> TiposEvento | None:
    return db.scalar(select(TiposEvento).where(TiposEvento.codigo == codigo))


def obtener_evento_por_clave(db: Session, clave: str) -> Eventos | None:
    return db.scalar(select(Eventos).where(Eventos.ocurrencia_clave == clave))


def crear_evento(db: Session, tipo_evento_id: int, reserva_id: int | None, clave: str, ahora) -> Eventos:
    evento = Eventos(
        tipo_evento_id=tipo_evento_id, reserva_id=reserva_id,
        ocurrencia_clave=clave, created_at=ahora,
    )
    db.add(evento)
    db.flush()
    return evento


def crear_notificacion_inapp(db: Session, evento_id: int, id_cuenta: int, titulo: str, cuerpo: str, ahora) -> None:
    existe = db.scalar(
        select(Notificaciones.id).where(
            Notificaciones.evento_id == evento_id, Notificaciones.id_cuenta == id_cuenta
        )
    )
    if existe is None:
        db.add(Notificaciones(
            evento_id=evento_id, id_cuenta=id_cuenta, titulo=titulo,
            cuerpo=cuerpo, created_at=ahora,
        ))
        db.flush()


def crear_envio(db: Session, evento_id: int, notificacion_id: int | None, correo: str, titulo: str, cuerpo: str, ahora) -> None:
    existe = db.scalar(
        select(EnviosCorreo.id).where(
            EnviosCorreo.evento_id == evento_id, EnviosCorreo.destinatario_correo == correo
        )
    )
    if existe is None:
        db.add(EnviosCorreo(
            evento_id=evento_id, notificacion_id=notificacion_id,
            destinatario_correo=correo, titulo=titulo, cuerpo=cuerpo,
            estado="PENDIENTE", intentos=0, proximo_intento_at=ahora, created_at=ahora,
        ))
        db.flush()


def correo_de_cuenta(db: Session, id_cuenta: int) -> str | None:
    from app.db.models.auth import Cuentas

    cuenta = db.get(Cuentas, id_cuenta)
    return cuenta.correo if cuenta is not None and cuenta.estado else None


def correo_habilitado_para(db: Session, id_cuenta: int, tipo_evento_id: int) -> bool:
    """Preferencia más específica vigente (RN-PREF-04); por defecto True."""
    filas = db.scalars(
        select(Preferencias).where(Preferencias.id_cuenta == id_cuenta)
    ).all()
    general = True
    for p in filas:
        if p.tipo_evento_id is None:
            general = p.correo_habilitado
        elif p.tipo_evento_id == tipo_evento_id:
            return p.correo_habilitado
    return general


def unidad_permite_correo(db: Session, id_unidad: int) -> bool:
    """RN-PREF-02: la unidad manda sobre la preferencia individual."""
    from app.db.models.reservas import LaboratoriosConfig

    config = db.scalar(
        select(LaboratoriosConfig).where(LaboratoriosConfig.id_unidad == id_unidad)
    )
    return config is not None and bool(config.notificar_por_correo)


def anular_pendientes_de_reserva(db: Session, reserva_id: int, motivo: str, ahora) -> int:
    """RN-COR-07: anula envíos PENDIENTE cuya condición desapareció."""
    filas = db.scalars(
        select(EnviosCorreo)
        .join(Eventos, Eventos.id == EnviosCorreo.evento_id)
        .where(Eventos.reserva_id == reserva_id, EnviosCorreo.estado == "PENDIENTE")
    ).all()
    for envio in filas:
        envio.estado = "ANULADO"
        envio.anulado_at = ahora
        envio.motivo_anulacion = motivo
        envio.proximo_intento_at = None
    db.flush()
    return len(filas)


def preferencias_de_cuenta(db: Session, id_cuenta: int) -> list[Preferencias]:
    return list(db.scalars(
        select(Preferencias).where(Preferencias.id_cuenta == id_cuenta)
    ).all())


def reemplazar_preferencias(db: Session, id_cuenta: int, general: bool, por_evento: list[dict]) -> None:
    db.query(Preferencias).filter(Preferencias.id_cuenta == id_cuenta).delete()
    db.add(Preferencias(id_cuenta=id_cuenta, tipo_evento_id=None, correo_habilitado=general))
    for item in por_evento:
        db.add(Preferencias(
            id_cuenta=id_cuenta, tipo_evento_id=item["tipo_evento_id"],
            correo_habilitado=item["correo_habilitado"],
        ))
    db.flush()


def tecnicos_de_unidad(db: Session, id_unidad: int) -> list[int]:
    """Cuentas PERSONAL activas cuyo cargo es del laboratorio: el técnico que lo gestiona, contraparte
    de una contrapropuesta de Usuario (RN-EVT-08). Los permisos los define el rol, no una asignación."""
    from app.db.models.auth import Cuentas
    from app.db.models.identidad import Cargo, Personal

    return list(db.scalars(
        select(Cuentas.id_cuenta)
        .join(Personal, Personal.id_persona == Cuentas.id_persona)
        .join(Cargo, Cargo.id_cargo == Personal.id_cargo)
        .where(
            Cuentas.tipo_cuenta == "PERSONAL", Cuentas.estado.is_(True),
            Personal.estado.is_(True), Cargo.id_unidad == id_unidad,
        )
    ).all())
