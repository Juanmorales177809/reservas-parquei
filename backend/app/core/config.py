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

        # JWT_SECRET no tiene valor por defecto en producción: si falta,
        # security.py aborta al arrancar en vez de firmar con un secreto
        # predecible. Para desarrollo local, docker-compose.yml lo declara.
        self.jwt_secret = os.environ.get("JWT_SECRET", "")
        # Vigencia del JWT de acceso en sí (vida corta; el cliente renueva
        # antes de que expire). No confundir con la vigencia máxima de la
        # sesión, que se comprueba contra auth.sesiones, no contra el token.
        self.jwt_vigencia_acceso_segundos = int(os.environ.get("JWT_VIGENCIA_ACCESO_SEGUNDOS", "900"))
        self.csrf_vigencia_segundos = int(os.environ.get("CSRF_VIGENCIA_SEGUNDOS", str(12 * 60 * 60)))

        # Los tres límites de AUTH-A1, valores por defecto de auth/data-model.md:
        # 12h de vigencia máxima de sesión, 30min de inactividad máxima,
        # 10min de ventana de autenticación reciente.
        self.sesion_vigencia_maxima_segundos = int(
            os.environ.get("SESION_VIGENCIA_MAXIMA_SEGUNDOS", str(12 * 60 * 60))
        )
        self.sesion_inactividad_maxima_segundos = int(
            os.environ.get("SESION_INACTIVIDAD_MAXIMA_SEGUNDOS", str(30 * 60))
        )
        self.reautenticacion_ventana_segundos = int(
            os.environ.get("REAUTENTICACION_VENTANA_SEGUNDOS", str(10 * 60))
        )

        # API-13 §2.5-2.7: sin proveedor de almacenamiento externo en el
        # proyecto, los adjuntos de lista de espera se guardan en disco local.
        # docker-compose.yml lo monta como volumen con nombre, no en el
        # filesystem efímero del contenedor.
        self.adjuntos_storage_dir = os.environ.get("ADJUNTOS_STORAGE_DIR", "/tmp/reserva_adjuntos")

        # API-18: correo saliente. Sin servidor en desarrollo local, el
        # transporte por defecto registra en el log y marca ENVIADO para no
        # bloquear los flujos. Producción usa SMTP o Graph delegado.
        self.email_enabled = os.environ.get("EMAIL_ENABLED", "true").lower() == "true"
        self.email_transport = os.environ.get("EMAIL_TRANSPORT", "log")
        if self.email_transport not in ("log", "smtp", "graph_delegado"):
            raise ValueError("EMAIL_TRANSPORT debe ser 'log', 'smtp' o 'graph_delegado'")
        self.smtp_host = os.environ.get("SMTP_HOST", "")
        self.smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        self.smtp_user = os.environ.get("SMTP_USER", "")
        self.smtp_password = os.environ.get("SMTP_PASSWORD", "")
        self.smtp_from = os.environ.get("SMTP_FROM", "")
        # Patrón del repositorio anterior: cuenta que envía por Graph con
        # token delegado cacheado (login interactivo único, fuera del backend).
        self.graph_mail_sender = os.environ.get("GRAPH_MAIL_SENDER", "")
        self.graph_token_cache_path = os.environ.get(
            "GRAPH_TOKEN_CACHE_PATH", "/tmp/graph_token_cache.json"
        )
        # Base para los enlaces de un solo uso (invitación, recuperación).
        self.app_url = os.environ.get("APP_URL", "http://localhost:3000")

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
