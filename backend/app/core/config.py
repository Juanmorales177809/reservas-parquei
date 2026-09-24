"""Configuración leída de variables de entorno.

Sin secretos por defecto ni valores hardcodeados salvo los que ya trae
docker-compose.yml para desarrollo local. `DATABASE_URL` permite anular la
construcción automática cuando haga falta (por ejemplo, una base distinta a
la del servicio `db` de Compose).
"""

import os
from functools import lru_cache


class Settings:
    def __init__(self) -> None:
        self.database_url = os.environ.get("DATABASE_URL") or self._build_database_url()

    @staticmethod
    def _build_database_url() -> str:
        user = os.environ.get("POSTGRES_USER", "postgres")
        password = os.environ.get("POSTGRES_PASSWORD", "postgres")
        # "db" es el nombre del servicio en docker-compose.yml: solo resuelve
        # dentro de su red. DB_HOST/DB_PORT permiten apuntar a otra base.
        host = os.environ.get("DB_HOST", "db")
        port = os.environ.get("DB_PORT", "5432")
        database = os.environ.get("POSTGRES_DB", "reservas_db")
        return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{database}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
