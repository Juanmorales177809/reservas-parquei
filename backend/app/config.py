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


settings = Settings()
settings.validate()
