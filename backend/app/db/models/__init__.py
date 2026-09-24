"""Importa todos los modelos para que se registren en `Base.registry` (BK-08).

`recursos` y `notificaciones` no se modelan todavía: no estaban en el
alcance original de esta tarea (ver `backend.md`). Se modelan con el primer
`API-XX` de su propio módulo. `administration.auditoria` la modela API-08.
"""

from app.db.models import administration, auth, identidad, investigacion, reservas  # noqa: F401
