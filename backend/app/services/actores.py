# -*- coding: utf-8 -*-
"""Un único punto de decisión para las tablas polimórficas (`reservas`,
`notificaciones`, `control_cambios`) que pueden tener como actor a
`Personal` o `Usuario` -- ver `~/.claude/plans/dazzling-wobbling-zebra.md`.
Reusado por `services/reservas.py` y `services/auditoria.py` en vez de
repetir el mismo `if isinstance(...)` en cada punto que crea una
`Notificacion`, registra un cambio de auditoría, o guarda una `Reserva`.
"""

from app.models.personal import Personal
from app.models.usuario import Usuario


def columnas_actor(actor: Personal | Usuario) -> dict:
    if isinstance(actor, Personal):
        return {"usuario_id": None, "personal_id": actor.id}
    return {"usuario_id": actor.id, "personal_id": None}


def mismo_actor(a, b) -> bool:
    """¿`a` y `b` (cualquier combinación de `Reserva`/`Notificacion`/
    `ControlCambio`) tienen el mismo actor? Compara por id+tabla, no por
    identidad de objeto Python -- una reserva de un gestor y una
    notificación para ese mismo gestor dan `True` aunque sean filas de
    tablas distintas. No hace falta cargar los objetos `Personal`/
    `Usuario`: `usuario_id`/`personal_id` ya son comparables directamente
    porque ambos lados referencian el mismo espacio de ids en cada tabla."""
    return (a.usuario_id, a.personal_id) == (b.usuario_id, b.personal_id)


def es_actor(entidad, actor: Personal | Usuario) -> bool:
    """¿`actor` es quien aparece en las columnas polimórficas de `entidad`
    (`Reserva`/`Notificacion`/`ControlCambio`)? Reemplaza la comparación
    directa `entidad.usuario_id == actor.id`, que solo cubre el caso
    `Usuario` -- un gestor dueño de su propia reserva vive en
    `entidad.personal_id`, no en `usuario_id`."""
    if isinstance(actor, Personal):
        return entidad.personal_id == actor.id
    return entidad.usuario_id == actor.id
