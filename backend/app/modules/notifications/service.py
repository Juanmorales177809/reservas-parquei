"""Servicio de notifications (API-17): bandeja y preferencias propias.

Sin permiso administrativo: todo opera sobre la cuenta de la sesión
(contrato §1, RN-CON-01). Marcar lectura no toca reserva, recurso ni
envío de correo (RN-EST-04). Las preferencias solo afectan al canal de
correo (RN-PREF-01/04). La generación de eventos y envíos es API-18.
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.core.deps import ContextoAutenticado
from app.core.errors import NoEncontrado, Validacion
from app.modules.notifications import repository as repo
from app.modules.notifications import schemas


def _ahora():
    return datetime.now(timezone.utc)


def listar_notificaciones(db, filtros: dict, pagina: int, tamano: int, contexto: ContextoAutenticado) -> tuple[list[dict], int]:
    leida = filtros.get("leida")
    filas, total = repo.bandeja(
        db, contexto.id_cuenta, leida=leida, tipo_codigo=filtros.get("tipo_evento"),
        offset=(pagina - 1) * tamano, tamano=tamano,
    )
    datos = [
        {
            "id": n.id,
            "tipo_evento": {"codigo": t.codigo, "nombre": t.nombre},
            "titulo": n.titulo, "cuerpo": n.cuerpo,
            "reserva_id": e.reserva_id, "leida_at": n.leida_at, "created_at": n.created_at,
        }
        for n, e, t in filas
    ]
    return datos, total


def marcar_lectura(db, id_notificacion: int, contexto: ContextoAutenticado) -> dict:
    notificacion = repo.obtener_notificacion(db, id_notificacion, contexto.id_cuenta)
    if notificacion is None:
        raise NoEncontrado()
    repo.marcar_leida(db, notificacion, _ahora())
    db.commit()
    db.refresh(notificacion)
    return {"id": notificacion.id, "leida_at": notificacion.leida_at}


def obtener_preferencias(db, contexto: ContextoAutenticado) -> dict:
    filas = repo.preferencias_de_cuenta(db, contexto.id_cuenta)
    general = True
    por_evento = []
    for p in filas:
        if p.tipo_evento_id is None:
            general = p.correo_habilitado
        else:
            tipo = repo.obtener_tipo(db, p.tipo_evento_id)
            por_evento.append({
                "tipo_evento": {"codigo": tipo.codigo, "nombre": tipo.nombre},
                "correo_habilitado": p.correo_habilitado,
            })
    por_evento.sort(key=lambda item: item["tipo_evento"]["codigo"])
    return {"general": {"correo_habilitado": general}, "por_evento": por_evento}


def reemplazar_preferencias(db, cuerpo: schemas.PreferenciasCuerpo, contexto: ContextoAutenticado) -> dict:
    vistos: set[int] = set()
    for item in cuerpo.por_evento:
        if item.tipo_evento_id in vistos:
            raise Validacion("Un tipo de evento aparece repetido en 'por_evento'.")
        vistos.add(item.tipo_evento_id)
        tipo = repo.obtener_tipo(db, item.tipo_evento_id)
        if tipo is None or not tipo.habilitado:
            raise NoEncontrado(f"El tipo de evento {item.tipo_evento_id} no existe o está deshabilitado.")
    general = cuerpo.general.correo_habilitado if cuerpo.general is not None else True
    repo.reemplazar_preferencias(
        db, contexto.id_cuenta, general,
        [{"tipo_evento_id": i.tipo_evento_id, "correo_habilitado": i.correo_habilitado} for i in cuerpo.por_evento],
    )
    db.commit()
    return obtener_preferencias(db, contexto)


def tipos_evento(db) -> list[dict]:
    return [
        {"id": t.id, "codigo": t.codigo, "nombre": t.nombre, "descripcion": t.descripcion}
        for t in repo.tipos_habilitados(db)
    ]
