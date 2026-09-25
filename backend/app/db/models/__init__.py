"""Importa todos los modelos para que se registren en `Base.registry` (BK-08).

`notificaciones` no se modela todavía: no estaba en el alcance original de
esta tarea (ver `backend.md`). Se modela con su primer `API-XX`.
`administration.auditoria` la modeló `API-08`; `recursos`, `API-09`.
"""

from app.db.models import administration, auth, identidad, investigacion, recursos, reservas  # noqa: F401
