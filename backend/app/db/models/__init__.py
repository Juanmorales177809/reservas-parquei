"""Importa todos los modelos para que se registren en `Base.registry` (BK-08).

`administration.auditoria` la modeló `API-08`; `recursos`, `API-09`;
`notificaciones`, `API-17`.
"""

from app.db.models import administration, auth, identidad, investigacion, notificaciones, recursos, reservas  # noqa: F401
