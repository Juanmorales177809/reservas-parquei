"""Importa todos los modelos para que se registren en `Base.registry` (BK-08).

`recursos`, `administration` y `notificaciones` no se modelan todavía: no
estaban en el alcance original de esta tarea (ver `backend.md`). Se
modelan con el primer `API-XX` de su propio módulo.
"""

from app.db.models import auth, identidad, investigacion, reservas  # noqa: F401
