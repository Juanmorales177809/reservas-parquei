"""Productor de eventos (API-18): registra el evento una vez y deriva los
dos canales independientes (RN-NOT-05/06).

Lo llama el módulo propietario DESPUÉS de confirmar su operación
(RN-INT-01/02), en transacción propia: si esto falla, el negocio ya quedó
(RN-INT-04). Los textos viven aquí, en código (RN-CNT-06); el llamador
aporta datos, no redacción.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from sqlalchemy import select

from app.db.models.notificaciones import (
    EnvioCorreoAdjuntos,
    EnviosCorreo,
    Notificaciones,
)
from app.modules.notifications import plantillas, repository as repo


def _ahora():
    return datetime.now(timezone.utc)


_TEXTOS = {
    "SOLICITUD_REGISTRADA": (
        "Solicitud de reserva registrada",
        "Tu solicitud de reserva {tipo} quedó registrada con el número {reserva}.",
    ),
    "RESERVA_APROBADA": (
        "Reserva aprobada",
        "Tu reserva {tipo} número {reserva} quedó aprobada.",
    ),
    "RESERVA_RECHAZADA": (
        "Reserva rechazada",
        "Tu reserva {tipo} número {reserva} fue rechazada. Motivo: {motivo}.",
    ),
    "RESERVA_CANCELADA": (
        "Reserva cancelada",
        "Tu reserva {tipo} número {reserva} quedó cancelada.",
    ),
    "RESERVA_AFECTADA_DESHABILITACION": (
        "Reserva afectada por deshabilitación",
        "Tu reserva {tipo} número {reserva} resultó afectada por la deshabilitación de un elemento.",
    ),
    "PROPUESTA_PERIODO_REGISTRADA": (
        "Propuesta de periodo",
        "Hay una propuesta de periodo para tu reserva número {reserva}: {motivo}.",
    ),
    "RECURSO_ADICIONAL_INCORPORADO": (
        "Recurso incorporado a tu reserva",
        "Se incorporó un recurso adicional a tu reserva número {reserva}.",
    ),
    "LISTA_ESPERA_CAMBIO_ESTADO": (
        "Tu solicitud cambió de estado",
        "Tu solicitud de lista de espera número {reserva} pasó a {estado}.",
    ),
    "RESERVA_RECORDATORIO": (
        "Recordatorio de reserva",
        "Tu reserva {tipo} número {reserva} inicia {cuando}.",
    ),
    "INVITACION_CUENTA": (
        "Invitación a Reservas Parquei",
        "Te invitaron a crear tu cuenta. Actívala aquí: {enlace}. Vence {vence}.",
    ),
    "RECUPERACION_CONTRASENA": (
        "Recupera tu contraseña",
        "Solicitaste restablecer tu contraseña. Continúa aquí: {enlace}. Vence en una hora.",
    ),
    "CONTRASENA_CAMBIADA": (
        "Contraseña actualizada",
        "La contraseña de tu cuenta se actualizó correctamente.",
    ),
}


def registrar_evento(
    db,
    *,
    tipo_codigo: str,
    reserva_id: int | None = None,
    ocurrencia_clave: str,
    cuentas: list[int] | None = None,
    correos: list[str] | None = None,
    id_unidad: int | None = None,
    datos: dict | None = None,
    adjuntos: list[dict] | None = None,
    forzar_correo: bool = False,
) -> int | None:
    """Crea evento + in-app + envíos según canales vigentes. Idempotente por
    clave: repetir la misma ocurrencia no duplica nada (RN-NOT-05).

    `cuentas`: destinatarios con in-app. `correos`: direcciones sin cuenta
    (RN-DES-06, sin in-app). `forzar_correo`: comunicaciones de auth que
    ignoran preferencias (RN-PREF-03). Devuelve el id del evento o None si
    el tipo está deshabilitado.
    """
    from app.core.config import get_settings

    settings = get_settings()
    ahora = _ahora()
    datos = {"reserva": reserva_id, "motivo": "", "estado": "", "tipo": "", **(datos or {})}

    tipo = repo.obtener_tipo_por_codigo(db, tipo_codigo)
    if tipo is None or not tipo.habilitado:
        return None

    evento = repo.obtener_evento_por_clave(db, ocurrencia_clave)
    if evento is None:
        evento = repo.crear_evento(db, tipo.id, reserva_id, ocurrencia_clave, ahora)
    titulo, cuerpo = _TEXTOS[tipo_codigo][0], _TEXTOS[tipo_codigo][1].format(**datos)

    notificacion_ids: dict[int, int] = {}
    for id_cuenta in cuentas or []:
        repo.crear_notificacion_inapp(db, evento.id, id_cuenta, titulo, cuerpo, ahora)
        db.flush()
        notificacion_ids[id_cuenta] = db.scalar(
            select(Notificaciones.id).where(
                Notificaciones.evento_id == evento.id,
                Notificaciones.id_cuenta == id_cuenta,
            )
        )

    if settings.email_enabled:
        unidad_ok = id_unidad is None or repo.unidad_permite_correo(db, id_unidad)
        if unidad_ok or forzar_correo:
            for id_cuenta in cuentas or []:
                correo = repo.correo_de_cuenta(db, id_cuenta)
                if correo is None:
                    continue
                if not forzar_correo and not repo.correo_habilitado_para(db, id_cuenta, tipo.id):
                    continue
                html = _html_envio(
                    db, tipo_codigo, reserva_id, datos,
                    nombre=_nombre_de_cuenta(db, id_cuenta),
                    es_contraparte=_es_contraparte(db, tipo_codigo, reserva_id, id_cuenta),
                )
                repo.crear_envio(
                    db, evento.id, notificacion_ids.get(id_cuenta), correo,
                    titulo, html, ahora,
                )
            for correo in correos or []:
                html = _html_envio(
                    db, tipo_codigo, reserva_id, datos,
                    nombre=correo, es_contraparte=False,
                )
                repo.crear_envio(db, evento.id, None, correo, titulo, html, ahora)

    if adjuntos:
        import os

        from app.core.config import get_settings as _ajustes

        base = _ajustes().adjuntos_storage_dir
        envios = db.scalars(
            select(EnviosCorreo).where(EnviosCorreo.evento_id == evento.id)
        ).all()
        for envio in envios:
            for orden, adj in enumerate(adjuntos, start=1):
                existe = db.scalar(
                    select(EnvioCorreoAdjuntos.id).where(
                        EnvioCorreoAdjuntos.envio_correo_id == envio.id,
                        EnvioCorreoAdjuntos.orden == orden,
                    )
                )
                if existe is None:
                    clave = f"notificaciones/{envio.id}/{orden}-{adj['nombre']}"
                    ruta = os.path.join(base, *clave.split("/"))
                    os.makedirs(os.path.dirname(ruta), exist_ok=True)
                    with open(ruta, "wb") as f:
                        f.write(adj["contenido"])
                    db.add(EnvioCorreoAdjuntos(
                        envio_correo_id=envio.id, orden=orden,
                        nombre_original=adj["nombre"], storage_key=clave,
                        content_type=adj["content_type"], size_bytes=len(adj["contenido"]),
                        contenido_hash=hashlib.sha256(adj["contenido"]).hexdigest(),
                    ))
        db.flush()

    db.commit()
    return evento.id


def notificar_reserva(db, reserva_id: int, tipo_evento: str, clave: str, *, datos: dict | None = None, tecnicos: bool = False) -> None:
    """Atajo para productores de reservas: notifica al responsable y, si
    `tecnicos`, también a los técnicos de la unidad (contrapropuestas).
    Nunca propaga excepciones: el negocio ya quedó (RN-INT-04)."""
    import logging

    from app.modules.reservations import repository as _repo_reservas

    logger = logging.getLogger("reservas.notificaciones")
    try:
        reserva = _repo_reservas.obtener_reserva(db, reserva_id)
        if reserva is None:
            return
        tipo = _repo_reservas.obtener_tipo(db, reserva.tipo_reserva_id)
        cuentas = [reserva.id_cuenta]
        if tecnicos:
            cuentas += [
                c for c in repo.tecnicos_de_unidad(db, reserva.id_unidad)
                if c != reserva.id_cuenta
            ]
        registrar_evento(
            db, tipo_codigo=tipo_evento, reserva_id=reserva_id,
            ocurrencia_clave=clave, cuentas=cuentas, id_unidad=reserva.id_unidad,
            datos={"tipo": tipo.codigo, "reserva": reserva_id, **(datos or {})},
        )
    except Exception:
        logger.exception("No se pudo registrar el evento %s de la reserva %s", tipo_evento, reserva_id)


def anular_por_cambio(db, reserva_id: int, motivo: str) -> None:
    """RN-COR-07: al reprogramar o cancelar, los pendientes pierden su condición."""
    import logging

    logger = logging.getLogger("reservas.notificaciones")
    try:
        repo.anular_pendientes_de_reserva(db, reserva_id, motivo, _ahora())
        db.commit()
    except Exception:
        logger.exception("No se pudieron anular envíos de la reserva %s", reserva_id)


def _nombre_de_cuenta(db, id_cuenta: int) -> str:
    from app.db.models.auth import Cuentas
    from app.db.models.identidad import Personal, Usuarios

    cuenta = db.get(Cuentas, id_cuenta)
    if cuenta is None:
        return ""
    if cuenta.id_usuario is not None:
        usuario = db.get(Usuarios, cuenta.id_usuario)
        if usuario is not None:
            return usuario.nombre
    if cuenta.id_persona is not None:
        persona = db.get(Personal, cuenta.id_persona)
        if persona is not None:
            return persona.nombre
    return cuenta.correo


def _resumen_reserva(db, reserva_id: int | None) -> tuple[str, str]:
    """(titulo_tarjeta, detalle) para el HTML a partir del detalle vigente."""
    if reserva_id is None:
        return "", ""
    from app.modules.espacios import repository as _espacios
    from app.modules.reservations import repository as _reservas

    reserva = _reservas.obtener_reserva(db, reserva_id)
    if reserva is None:
        return "", ""
    tipo = _reservas.obtener_tipo(db, reserva.tipo_reserva_id)
    if tipo.codigo == "ESPACIO":
        detalle = _reservas.obtener_detalle_espacio(db, reserva_id)
        espacio = _espacios.obtener_espacio(db, detalle.espacio_id)
        return espacio.nombre, f"{detalle.fecha} · {detalle.hora_inicio}–{detalle.hora_fin}"
    if tipo.codigo == "RECURSO_INTERNO":
        detalle = _reservas.obtener_detalle_interno(db, reserva_id)
        return "Recurso interno", f"{detalle.fecha} · {detalle.hora_inicio}–{detalle.hora_fin}"
    if tipo.codigo in ("RECURSO_CAMPUS", "RECURSO_EXTERNO"):
        detalle = (
            _reservas.obtener_detalle_campus(db, reserva_id)
            if tipo.codigo == "RECURSO_CAMPUS"
            else _reservas.obtener_detalle_externo(db, reserva_id)
        )
        return "Préstamo de recurso", f"Salida {detalle.fecha_salida} · Devolución {detalle.fecha_devolucion_estimada}"
    return "Lista de espera", ""


def _es_contraparte(db, tipo_codigo: str, reserva_id: int | None, id_cuenta: int) -> bool:
    if tipo_codigo != "PROPUESTA_PERIODO_REGISTRADA" or reserva_id is None:
        return False
    from app.modules.reservations import repository as _reservas

    reserva = _reservas.obtener_reserva(db, reserva_id)
    return reserva is not None and id_cuenta != reserva.id_cuenta


_ESTADO_HTML = {
    "SOLICITADA": "pendiente", "APROBADA": "aprobada", "RECHAZADA": "rechazada",
    "CANCELADA": "cancelada", "EN_EJECUCION": "aprobada", "FINALIZADA": "aprobada",
}


def _html_envio(db, tipo_codigo: str, reserva_id: int | None, datos: dict, *, nombre: str, es_contraparte: bool) -> str:
    titulo, detalle = _resumen_reserva(db, reserva_id)
    motivo = str(datos.get("motivo") or "")
    if tipo_codigo == "INVITACION_CUENTA":
        return plantillas.invitacion(nombre=nombre, link=str(datos.get("enlace") or ""))
    if tipo_codigo == "RECUPERACION_CONTRASENA":
        return plantillas.recuperacion(nombre=nombre, link=str(datos.get("enlace") or ""))
    if tipo_codigo == "CONTRASENA_CAMBIADA":
        return plantillas.contrasena_actualizada(nombre=nombre)
    if tipo_codigo == "PROPUESTA_PERIODO_REGISTRADA":
        return plantillas.propuesta(
            nombre=nombre, reserva_id=reserva_id or 0, detalle=titulo or "Reserva",
            motivo=motivo, contraparte_tecnico=es_contraparte,
        )
    if tipo_codigo == "RESERVA_RECORDATORIO":
        return plantillas.recordatorio(
            nombre=nombre, reserva_id=reserva_id or 0,
            detalle=titulo or str(datos.get("cuando") or ""),
        )
    if tipo_codigo == "RECURSO_ADICIONAL_INCORPORADO":
        return plantillas.reserva_estado(
            nombre=nombre, reserva_id=reserva_id or 0, estado="actualizada",
            titulo_tarjeta=titulo or "Reserva", detalle=detalle,
        )
    if tipo_codigo == "LISTA_ESPERA_CAMBIO_ESTADO":
        estado = _ESTADO_HTML.get(str(datos.get("estado") or ""), "pendiente")
        return plantillas.reserva_estado(
            nombre=nombre, reserva_id=reserva_id or 0, estado=estado,
            titulo_tarjeta=titulo or "Lista de espera", detalle=detalle,
        )
    estado = _ESTADO_HTML.get(
        {
            "SOLICITUD_REGISTRADA": "SOLICITADA", "RESERVA_APROBADA": "APROBADA",
            "RESERVA_RECHAZADA": "RECHAZADA", "RESERVA_CANCELADA": "CANCELADA",
            "RESERVA_AFECTADA_DESHABILITACION": "CANCELADA",
        }.get(tipo_codigo, ""),
        "pendiente",
    )
    return plantillas.reserva_estado(
        nombre=nombre, reserva_id=reserva_id or 0, estado=estado,
        titulo_tarjeta=titulo or "Reserva", detalle=detalle, motivo=motivo or None,
    )
