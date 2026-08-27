import os


class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/reservas_db",
    )
    secret_key: str = os.getenv("SECRET_KEY", "")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    app_timezone: str = os.getenv("APP_TIMEZONE", "America/Bogota")
    initial_admin_username: str | None = os.getenv("INITIAL_ADMIN_USERNAME") or None
    initial_admin_email: str | None = os.getenv("INITIAL_ADMIN_EMAIL") or None
    initial_admin_password: str | None = os.getenv("INITIAL_ADMIN_PASSWORD") or None
    backend_cors_origins: list[str] = [
        origin.strip()
        for origin in os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]
    environment: str = os.getenv("ENVIRONMENT", "development")

    # Correo saliente (outbox pattern, app/services/email.py). EMAIL_ENABLED
    # en false (default) mantiene el sistema funcionando solo con
    # notificaciones in-app, sin intentar ningún envío real -- así se puede
    # desplegar todo este código antes de tener credenciales SMTP reales.
    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from: str = os.getenv("SMTP_FROM", "")
    smtp_starttls: bool = os.getenv("SMTP_STARTTLS", "true").lower() == "true"
    email_enabled: bool = os.getenv("EMAIL_ENABLED", "false").lower() == "true"

    # Supabase Auth: único mecanismo de autenticación (corte completo, no
    # convive con un login propio). Por eso estas variables son
    # obligatorias, igual que SECRET_KEY arriba -- sin flag de
    # habilitación, no tendría sentido "apagarlo" y quedarse sin forma de
    # loguearse. Cloud free tier recomendado (sin infra extra): crear
    # proyecto en cloud.supabase.com y copiar estas variables.
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    supabase_jwt_secret: str = os.getenv("SUPABASE_JWT_SECRET", "")

    def validate(self) -> None:
        if len(self.secret_key) < 32 or self.secret_key == "change-me-in-production":
            raise RuntimeError(
                "SECRET_KEY es obligatoria y debe tener al menos 32 caracteres"
            )

        admin_values = (
            self.initial_admin_username,
            self.initial_admin_email,
            self.initial_admin_password,
        )
        if any(admin_values) and not all(admin_values):
            raise RuntimeError(
                "INITIAL_ADMIN_USERNAME, INITIAL_ADMIN_EMAIL e "
                "INITIAL_ADMIN_PASSWORD deben configurarse juntas"
            )
        if self.initial_admin_password and len(self.initial_admin_password) < 12:
            raise RuntimeError(
                "INITIAL_ADMIN_PASSWORD debe tener al menos 12 caracteres"
            )

        if self.email_enabled and not (self.smtp_host and self.smtp_from):
            raise RuntimeError(
                "EMAIL_ENABLED=true requiere SMTP_HOST y SMTP_FROM configurados"
            )

        if not (self.supabase_url and self.supabase_jwt_secret and self.supabase_service_role_key):
            raise RuntimeError(
                "SUPABASE_URL, SUPABASE_JWT_SECRET y SUPABASE_SERVICE_ROLE_KEY son "
                "obligatorias: Supabase Auth es el único mecanismo de autenticación"
            )


settings = Settings()
settings.validate()
