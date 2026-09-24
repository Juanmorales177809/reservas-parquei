"""Sesión de SQLAlchemy.

Regla 1 de plan.md: el backend nunca crea ni modifica tablas. No hay
`Base.metadata.create_all` aquí ni en ningún otro sitio. El esquema lo
gobiernan las migraciones versionadas de `backend/migrations/`.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

# pool_pre_ping evita reutilizar una conexión muerta tras una caída breve
# de la base; no abre conexión hasta el primer uso.
engine = create_engine(get_settings().database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
