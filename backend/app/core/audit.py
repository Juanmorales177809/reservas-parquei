"""Auditoría administrativa (AUTH-C1, contrato de auth §8; SEC-AUD-01/03).

Escribe en `administration.auditoria` con SQL directo: esa tabla la creó
`DB-03`, pero el schema `administration` no se modela todavía (no es su
alcance; ver `BK-08`). Una sola sentencia no justifica adelantar ese
alcance.

Corre dentro de la misma transacción que la operación auditada a
propósito: si el registro no puede escribirse, la operación tampoco debe
confirmarse en silencio sin dejar rastro.
"""

from __future__ import annotations

import json

from sqlalchemy import text
from sqlalchemy.orm import Session


def registrar(
    db: Session,
    *,
    actor_cuenta_id: int,
    entidad: str,
    entidad_id: str | int,
    accion: str,
    datos_nuevos: dict | None = None,
    datos_anteriores: dict | None = None,
    motivo: str | None = None,
) -> None:
    """Una fila por evento. Nunca incluye contraseñas, secretos de sesión,
    tokens completos ni claves (SEC-AUD-03): los llamadores solo pasan
    identificadores y metadatos, nunca el cuerpo de la solicitud completo.
    """
    db.execute(
        text(
            "INSERT INTO administration.auditoria "
            "(actor_cuenta_id, entidad, entidad_id, accion, datos_anteriores, datos_nuevos, motivo) "
            "VALUES (:actor, :entidad, :entidad_id, :accion, :antes, :despues, :motivo)"
        ),
        {
            "actor": actor_cuenta_id,
            "entidad": entidad,
            "entidad_id": str(entidad_id),
            "accion": accion,
            "antes": json.dumps(datos_anteriores) if datos_anteriores is not None else None,
            "despues": json.dumps(datos_nuevos) if datos_nuevos is not None else None,
            "motivo": motivo,
        },
    )
