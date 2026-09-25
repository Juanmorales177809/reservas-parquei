"""Tarea de entrega de correo (API-18, UF-NOT-03).

La ejecuta el `lifespan` cada ~30 s (< 1 min, la espera más corta de
RN-COR-03). Selecciona por el índice `(estado, proximo_intento_at)`.
Reintentos 1/5/15/60/240 min; agotados → FALLIDO definitivo sin tocar el
negocio (RN-COR-04/RN-INT-04). Un reintento usa los mismos adjuntos
persistidos (RN-COR-06).
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.db.models.notificaciones import EnvioCorreoAdjuntos, EnviosCorreo
from app.modules.notifications import envio as remitente

_ESPERAS_MINUTOS = (1, 5, 15, 60, 240)


def _ahora():
    return datetime.now(timezone.utc)


def envios_elegibles(db) -> list:
    ahora = _ahora()
    return list(db.scalars(
        select(EnviosCorreo).where(
            EnviosCorreo.estado == "PENDIENTE",
            (EnviosCorreo.proximo_intento_at.is_(None)) | (EnviosCorreo.proximo_intento_at <= ahora),
        ).order_by(EnviosCorreo.proximo_intento_at)
    ).all())


def _adjuntos(db, envio) -> list[dict]:
    from app.core.config import get_settings

    base = get_settings().adjuntos_storage_dir
    filas = db.scalars(
        select(EnvioCorreoAdjuntos)
        .where(EnvioCorreoAdjuntos.envio_correo_id == envio.id)
        .order_by(EnvioCorreoAdjuntos.orden)
    ).all()
    adjuntos = []
    for fila in filas:
        with open(os.path.join(base, *fila.storage_key.split("/")), "rb") as f:
            adjuntos.append({
                "nombre": fila.nombre_original,
                "content_type": fila.content_type,
                "contenido": f.read(),
            })
    return adjuntos


def procesar_envio(db, envio) -> str:
    """Transmite un envío y actualiza su estado. Devuelve el estado final."""
    ahora = _ahora()
    try:
        remitente.transmitir(
            envio.destinatario_correo, envio.titulo, envio.cuerpo,
            _adjuntos(db, envio),
        )
    except remitente.ErrorTransmision as exc:
        envio.intentos += 1
        envio.ultimo_error = str(exc)
        if envio.intentos >= len(_ESPERAS_MINUTOS):
            envio.estado = "FALLIDO"
            envio.proximo_intento_at = None
        else:
            envio.proximo_intento_at = ahora + timedelta(minutes=_ESPERAS_MINUTOS[envio.intentos - 1])
        db.flush()
        return envio.estado
    envio.estado = "ENVIADO"
    envio.enviado_at = ahora
    envio.proximo_intento_at = None
    db.flush()
    return envio.estado


def procesar_pendientes(db) -> dict[str, int]:
    """Un tick de la tarea. Idempotente por envío."""
    cuenta = {"enviados": 0, "fallidos": 0, "reintentados": 0}
    for envio in envios_elegibles(db):
        estado = procesar_envio(db, envio)
        if estado == "ENVIADO":
            cuenta["enviados"] += 1
        elif estado == "FALLIDO":
            cuenta["fallidos"] += 1
        else:
            cuenta["reintentados"] += 1
    db.commit()
    return cuenta
