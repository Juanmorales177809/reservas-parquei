from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api import admin_dashboard, auth, control_cambios, espacios, notificaciones, recursos, reservas, usuarios
from app.auth.auth import hash_password
from app.config import settings
from app.db import Base, engine, SessionLocal
from app import models  # noqa: F401
from app.migrations import migrate_resource_reservations


app = FastAPI(
    title="Gestión de Reservas de Recursos Institucionales",
    description="API para gestionar recursos y sus reservas",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    migrate_resource_reservations()
    seed_admin_user()


@app.on_event("shutdown")
def on_shutdown() -> None:
    engine.dispose()


@app.get("/", tags=["health"])
def read_root():
    return {"mensaje": "Bienvenido al sistema de gestión de reservas de recursos institucionales"}


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


def seed_admin_user() -> None:
    db: Session = SessionLocal()
    try:
        from app.models.usuario import Usuario
        from app.initial_data.espacios import init_espacios

        # Poblar espacios iniciales
        init_espacios(db)

        admin = db.query(Usuario).filter(Usuario.rol == "admin").first()
        admin_username = settings.initial_admin_username
        admin_email = settings.initial_admin_email
        admin_password = settings.initial_admin_password
        if admin is not None or admin_username is None:
            return
        # Settings.validate() guarantees that the remaining values are present.
        assert admin_email is not None
        assert admin_password is not None

        existing_identity = (
            db.query(Usuario)
            .filter(
                (Usuario.username == admin_username)
                | (Usuario.email == admin_email)
            )
            .first()
        )
        if existing_identity is not None:
            raise RuntimeError(
                "No se pudo crear el administrador inicial: el usuario o email ya existe"
            )

        db.add(
            Usuario(
                username=admin_username,
                email=admin_email,
                hashed_password=hash_password(admin_password),
                rol="admin",
            )
        )
        db.commit()
    finally:
        db.close()


# Incluir routers
app.include_router(auth.router)
app.include_router(admin_dashboard.router)
app.include_router(admin_dashboard.gestion_router)
app.include_router(control_cambios.router)
app.include_router(usuarios.router)
app.include_router(espacios.router)
app.include_router(recursos.router)
app.include_router(reservas.router)
app.include_router(notificaciones.router)
