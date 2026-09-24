"""Modelos de SQLAlchemy del schema `investigacion` (BK-08).

Generados desde la base real; no crean ni alteran tablas (regla 1 de
plan.md). El esquema lo gobiernan las migraciones de backend/migrations/."""

from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class ActividadesInstitucionales(Base):
    __tablename__ = "actividades_institucionales"
    __table_args__ = {"schema": "investigacion"}

    id_actividad: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column()
    dependencia: Mapped[str] = mapped_column()
    estado: Mapped[bool] = mapped_column()


class ModalidadesVinculacion(Base):
    __tablename__ = "modalidades_vinculacion"
    __table_args__ = {"schema": "investigacion"}

    id_modalidad: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column()
    descripcion: Mapped[str | None] = mapped_column(nullable=True)
    estado: Mapped[bool] = mapped_column()


class Pasantias(Base):
    __tablename__ = "pasantias"
    __table_args__ = {"schema": "investigacion"}

    id_pasantia: Mapped[int] = mapped_column(primary_key=True)
    universidad: Mapped[str] = mapped_column()
    docente_itm_nombre: Mapped[str] = mapped_column()
    docente_itm_correo: Mapped[str] = mapped_column()
    estado: Mapped[bool] = mapped_column()


class Perfiles(Base):
    __tablename__ = "perfiles"
    __table_args__ = {"schema": "investigacion"}

    id_perfil: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column()
    descripcion: Mapped[str | None] = mapped_column(nullable=True)
    estado: Mapped[bool] = mapped_column()


class Proyectos(Base):
    __tablename__ = "proyectos"
    __table_args__ = {"schema": "investigacion"}

    id_proyecto: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column()
    nombre: Mapped[str] = mapped_column()
    estado: Mapped[bool] = mapped_column()


class Semilleros(Base):
    __tablename__ = "semilleros"
    __table_args__ = {"schema": "investigacion"}

    id_semillero: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column()
    nombre: Mapped[str] = mapped_column()
    estado: Mapped[bool] = mapped_column()


class TrabajosGrado(Base):
    __tablename__ = "trabajos_grado"
    __table_args__ = {"schema": "investigacion"}

    id_trabajo_grado: Mapped[int] = mapped_column(primary_key=True)
    director_nombre: Mapped[str] = mapped_column()
    director_correo: Mapped[str] = mapped_column()
    estado: Mapped[bool] = mapped_column()


class UsuarioModalidadesVinculacion(Base):
    __tablename__ = "usuario_modalidades_vinculacion"
    __table_args__ = {"schema": "investigacion"}

    id_vinculacion: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.usuarios.id_usuario"))
    id_modalidad: Mapped[int] = mapped_column(ForeignKey("investigacion.modalidades_vinculacion.id_modalidad"))
    fecha_inicio: Mapped[date | None] = mapped_column(nullable=True)
    fecha_fin: Mapped[date | None] = mapped_column(nullable=True)
    descripcion: Mapped[str | None] = mapped_column(nullable=True)
    estado: Mapped[bool] = mapped_column()


class UsuarioPasantias(Base):
    __tablename__ = "usuario_pasantias"
    __table_args__ = {"schema": "investigacion"}

    id_usuario_pasantia: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.usuarios.id_usuario"))
    id_pasantia: Mapped[int] = mapped_column(ForeignKey("investigacion.pasantias.id_pasantia"))
    estado: Mapped[bool] = mapped_column()


class UsuarioPerfiles(Base):
    __tablename__ = "usuario_perfiles"
    __table_args__ = {"schema": "investigacion"}

    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.usuarios.id_usuario"), primary_key=True)
    id_perfil: Mapped[int] = mapped_column(ForeignKey("investigacion.perfiles.id_perfil"), primary_key=True)
    fecha_inicio: Mapped[date | None] = mapped_column(nullable=True)
    fecha_fin: Mapped[date | None] = mapped_column(nullable=True)
    estado: Mapped[bool] = mapped_column()


class UsuarioProyectos(Base):
    __tablename__ = "usuario_proyectos"
    __table_args__ = {"schema": "investigacion"}

    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.usuarios.id_usuario"), primary_key=True)
    id_proyecto: Mapped[int] = mapped_column(ForeignKey("investigacion.proyectos.id_proyecto"), primary_key=True)
    fecha_inicio: Mapped[date | None] = mapped_column(nullable=True)
    fecha_fin: Mapped[date | None] = mapped_column(nullable=True)
    estado: Mapped[bool] = mapped_column()


class UsuarioSemilleros(Base):
    __tablename__ = "usuario_semilleros"
    __table_args__ = {"schema": "investigacion"}

    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.usuarios.id_usuario"), primary_key=True)
    id_semillero: Mapped[int] = mapped_column(ForeignKey("investigacion.semilleros.id_semillero"), primary_key=True)
    fecha_inicio: Mapped[date | None] = mapped_column(nullable=True)
    fecha_fin: Mapped[date | None] = mapped_column(nullable=True)
    estado: Mapped[bool] = mapped_column()


class UsuarioTrabajosGrado(Base):
    __tablename__ = "usuario_trabajos_grado"
    __table_args__ = {"schema": "investigacion"}

    id_usuario_trabajo_grado: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.usuarios.id_usuario"))
    id_trabajo_grado: Mapped[int] = mapped_column(ForeignKey("investigacion.trabajos_grado.id_trabajo_grado"))
    estado: Mapped[bool] = mapped_column()


