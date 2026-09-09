"""Read-only access to LIA master data from the shared PostgreSQL."""

from sqlalchemy.orm import Session

from app.models.espacio import LaboratorioConfig
from app.models.lia import Cargo, Equipo, Personal, UnidadOrganizacional


def listar_unidades_con_configuracion(db: Session):
    """Return every LIA unit and its optional Reservations configuration."""
    return (
        db.query(UnidadOrganizacional, LaboratorioConfig)
        .outerjoin(
            LaboratorioConfig,
            LaboratorioConfig.id_unidad == UnidadOrganizacional.id_unidad,
        )
        .order_by(UnidadOrganizacional.nombre.asc())
        .all()
    )


def obtener_unidad_con_configuracion(db: Session, id_unidad: int):
    return (
        db.query(UnidadOrganizacional, LaboratorioConfig)
        .outerjoin(
            LaboratorioConfig,
            LaboratorioConfig.id_unidad == UnidadOrganizacional.id_unidad,
        )
        .filter(UnidadOrganizacional.id_unidad == id_unidad)
        .first()
    )


def obtener_personal_con_contexto(db: Session, id_persona: int):
    """Return personal, cargo and organizational unit from LIA."""
    return (
        db.query(Personal, Cargo, UnidadOrganizacional)
        .join(Cargo, Personal.id_cargo == Cargo.id_cargo)
        .join(UnidadOrganizacional, Cargo.id_unidad == UnidadOrganizacional.id_unidad)
        .filter(Personal.id_persona == id_persona)
        .first()
    )


def listar_personal_por_unidad(db: Session, id_unidad: int, solo_activo: bool = False):
    query = (
        db.query(Personal, Cargo, UnidadOrganizacional)
        .join(Cargo, Personal.id_cargo == Cargo.id_cargo)
        .join(UnidadOrganizacional, Cargo.id_unidad == UnidadOrganizacional.id_unidad)
        .filter(UnidadOrganizacional.id_unidad == id_unidad)
    )
    if solo_activo:
        query = query.filter(Personal.estado.is_(True))
    return query.order_by(Personal.nombre.asc()).all()


def listar_equipos_por_unidad(db: Session, id_unidad: int, solo_operativos: bool = False):
    query = db.query(Equipo).filter(Equipo.id_unidad == id_unidad)
    if solo_operativos:
        query = query.filter(Equipo.estado.is_(True))
    return query.order_by(Equipo.nombre_equipo.asc()).all()


def obtener_equipo(db: Session, id_equipo: int) -> Equipo | None:
    return db.query(Equipo).filter(Equipo.id_equipo == id_equipo).first()
