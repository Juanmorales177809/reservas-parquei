"""Base declarativa compartida por todos los modelos (BK-08).

Un único `Base` para que todos los modelos compartan el mismo registro de
metadatos, útil para introspección y pruebas. No se usa `Base.metadata.create_all`
en ningún sitio: el esquema lo gobiernan las migraciones (regla 1 de plan.md).
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
