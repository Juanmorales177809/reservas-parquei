"""Modelos de SQLAlchemy del schema `reservas` (BK-08, ampliado por DB-12 y API-13).

Generados desde la base real; no crean ni alteran tablas (regla 1 de
plan.md). El esquema lo gobiernan las migraciones de backend/migrations/.

`ReservaEspacio.periodo` y `.bloqueante`, y sus equivalentes en
`ReservaRecursos` (incluido `compromiso_fisico`), son proyecciones técnicas
mantenidas por los disparadores de `DB-12` (`009_concurrencia.sql`). Ningún
servicio debe escribirlas directamente; se tipan como `str` aquí porque
`tstzrange` no tiene un tipo Python nativo en este mapeo mínimo, no porque
su contenido sea texto.
"""

from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

from sqlalchemy import FetchedValue, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class EspacioCampoOpciones(Base):
    __tablename__ = "espacio_campo_opciones"
    __table_args__ = {"schema": "reservas"}

    id: Mapped[int] = mapped_column(primary_key=True)
    campo_id: Mapped[int] = mapped_column(ForeignKey("reservas.espacio_campos.id"))
    valor: Mapped[str] = mapped_column()
    orden: Mapped[int] = mapped_column()
    habilitado: Mapped[bool] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column()


class EspacioCampos(Base):
    __tablename__ = "espacio_campos"
    __table_args__ = {"schema": "reservas"}

    id: Mapped[int] = mapped_column(primary_key=True)
    espacio_id: Mapped[int] = mapped_column(ForeignKey("reservas.espacios.id"))
    nombre: Mapped[str] = mapped_column()
    tipo_campo: Mapped[str] = mapped_column()
    obligatorio: Mapped[bool] = mapped_column()
    orden: Mapped[int] = mapped_column()
    habilitado: Mapped[bool] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column()


class EspacioRecursos(Base):
    __tablename__ = "espacio_recursos"
    __table_args__ = {"schema": "reservas"}

    espacio_id: Mapped[int] = mapped_column(ForeignKey("reservas.espacios.id"), primary_key=True)
    recurso_id: Mapped[int] = mapped_column(ForeignKey("recursos.recursos.id"), primary_key=True)
    habilitado: Mapped[bool] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column()


class Espacios(Base):
    __tablename__ = "espacios"
    __table_args__ = {"schema": "reservas"}

    id: Mapped[int] = mapped_column(primary_key=True)
    id_unidad: Mapped[int] = mapped_column(ForeignKey("unidadOrganizacional.unidad_organizacional.id_unidad"))
    nombre: Mapped[str] = mapped_column()
    ubicacion: Mapped[str | None] = mapped_column(nullable=True)
    capacidad: Mapped[int] = mapped_column()
    descripcion: Mapped[str | None] = mapped_column(nullable=True)
    habilitado: Mapped[bool] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column()


class EstadosReserva(Base):
    __tablename__ = "estados_reserva"
    __table_args__ = {"schema": "reservas"}

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column()
    nombre: Mapped[str] = mapped_column()
    habilitado: Mapped[bool] = mapped_column()


class LaboratorioTiposReserva(Base):
    __tablename__ = "laboratorio_tipos_reserva"
    __table_args__ = {"schema": "reservas"}

    id_unidad: Mapped[int] = mapped_column(ForeignKey("unidadOrganizacional.unidad_organizacional.id_unidad"), primary_key=True)
    tipo_reserva_id: Mapped[int] = mapped_column(ForeignKey("reservas.tipos_reserva.id"), primary_key=True)
    habilitado: Mapped[bool] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column()


class LaboratoriosConfig(Base):
    __tablename__ = "laboratorios_config"
    __table_args__ = {"schema": "reservas"}

    id: Mapped[int] = mapped_column(primary_key=True)
    id_unidad: Mapped[int] = mapped_column(ForeignKey("unidadOrganizacional.unidad_organizacional.id_unidad"))
    habilitado_reservas: Mapped[bool] = mapped_column()
    ubicacion: Mapped[str | None] = mapped_column(nullable=True)
    descripcion: Mapped[str | None] = mapped_column(nullable=True)
    dias_atencion: Mapped[dict] = mapped_column(JSONB)
    hora_apertura: Mapped[time] = mapped_column()
    hora_cierre: Mapped[time] = mapped_column()
    horario_atencion: Mapped[dict] = mapped_column(JSONB)
    horas_antelacion: Mapped[int] = mapped_column()
    aprobacion_automatica: Mapped[bool] = mapped_column()
    modalidad_reserva: Mapped[str | None] = mapped_column(nullable=True)
    correo: Mapped[str | None] = mapped_column(nullable=True)
    notificar_por_correo: Mapped[bool] = mapped_column()
    mostrar_estado_reserva: Mapped[bool] = mapped_column()
    mostrar_reservista: Mapped[bool] = mapped_column()
    recordatorio_horas_antes: Mapped[int] = mapped_column()


class LaboratoriosConfigHistorico(Base):
    __tablename__ = "laboratorios_config_historico"
    __table_args__ = {"schema": "reservas"}

    id: Mapped[int] = mapped_column(primary_key=True)
    id_unidad: Mapped[int] = mapped_column(ForeignKey("unidadOrganizacional.unidad_organizacional.id_unidad"))
    dias_atencion: Mapped[dict] = mapped_column(JSONB)
    hora_apertura: Mapped[time] = mapped_column()
    hora_cierre: Mapped[time] = mapped_column()
    horario_atencion: Mapped[dict] = mapped_column(JSONB)
    vigente_desde: Mapped[datetime] = mapped_column()
    vigente_hasta: Mapped[datetime | None] = mapped_column(nullable=True)


class OrdenSalidaActividades(Base):
    __tablename__ = "orden_salida_actividades"
    __table_args__ = {"schema": "reservas"}

    orden_salida_id: Mapped[int] = mapped_column(ForeignKey("reservas.ordenes_salida.id"), primary_key=True)
    actividad: Mapped[str] = mapped_column(primary_key=True)


class OrdenSalidaItems(Base):
    __tablename__ = "orden_salida_items"
    __table_args__ = {"schema": "reservas"}

    id: Mapped[int] = mapped_column(primary_key=True)
    orden_salida_id: Mapped[int] = mapped_column(ForeignKey("reservas.ordenes_salida.id"))
    reserva_recurso_id: Mapped[int] = mapped_column(ForeignKey("reservas.reserva_recursos.id"))
    placa_snapshot: Mapped[str | None] = mapped_column(nullable=True)
    descripcion_snapshot: Mapped[str] = mapped_column()
    bodega_snapshot: Mapped[str | None] = mapped_column(nullable=True)
    cc_snapshot: Mapped[str | None] = mapped_column(nullable=True)
    fecha_compra_snapshot: Mapped[date | None] = mapped_column(nullable=True)


class OrdenesSalida(Base):
    __tablename__ = "ordenes_salida"
    __table_args__ = {"schema": "reservas"}

    id: Mapped[int] = mapped_column(primary_key=True)
    reserva_id: Mapped[int] = mapped_column(ForeignKey("reservas.reservas.id"))
    fecha_generacion: Mapped[datetime] = mapped_column()
    razon_solicitud: Mapped[str] = mapped_column()
    nombre_actividad_evento: Mapped[str | None] = mapped_column(nullable=True)
    lugar_nombre: Mapped[str] = mapped_column()
    lugar_direccion: Mapped[str] = mapped_column()
    dependencia_solicitante_snapshot: Mapped[str] = mapped_column()
    fecha_retiro_snapshot: Mapped[date] = mapped_column()
    fecha_regreso_snapshot: Mapped[date] = mapped_column()
    proyecto_codigo_snapshot: Mapped[str | None] = mapped_column(nullable=True)
    responsable_nombre_snapshot: Mapped[str] = mapped_column()
    responsable_cedula_snapshot: Mapped[str] = mapped_column()
    responsable_correo_snapshot: Mapped[str] = mapped_column()
    responsable_telefono_snapshot: Mapped[str] = mapped_column()
    observaciones: Mapped[str | None] = mapped_column(nullable=True)


class ReservaAcompanantes(Base):
    __tablename__ = "reserva_acompanantes"
    __table_args__ = {"schema": "reservas"}

    reserva_id: Mapped[int] = mapped_column(ForeignKey("reservas.reservas.id"), primary_key=True)
    id_cuenta: Mapped[int] = mapped_column(ForeignKey("auth.cuentas.id_cuenta"), primary_key=True)


class ReservaAdjuntos(Base):
    __tablename__ = "reserva_adjuntos"
    __table_args__ = {"schema": "reservas"}

    id: Mapped[int] = mapped_column(primary_key=True)
    reserva_id: Mapped[int] = mapped_column(ForeignKey("reservas.reservas.id"))
    tipo_adjunto: Mapped[str] = mapped_column()
    nombre_original: Mapped[str] = mapped_column()
    storage_key: Mapped[str] = mapped_column()
    content_type: Mapped[str] = mapped_column()
    size_bytes: Mapped[int] = mapped_column()
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("auth.cuentas.id_cuenta"))
    created_at: Mapped[datetime] = mapped_column()


class ReservaCamposValores(Base):
    __tablename__ = "reserva_campos_valores"
    __table_args__ = {"schema": "reservas"}

    id: Mapped[int] = mapped_column(primary_key=True)
    reserva_id: Mapped[int] = mapped_column(ForeignKey("reservas.reservas.id"))
    campo_id: Mapped[int] = mapped_column(ForeignKey("reservas.espacio_campos.id"))
    campo_nombre_snapshot: Mapped[str] = mapped_column()
    campo_tipo_snapshot: Mapped[str] = mapped_column()
    obligatorio_snapshot: Mapped[bool] = mapped_column()
    valor_texto: Mapped[str | None] = mapped_column(nullable=True)
    opcion_id: Mapped[int | None] = mapped_column(ForeignKey("reservas.espacio_campo_opciones.id"), nullable=True)
    opcion_nombre_snapshot: Mapped[str | None] = mapped_column(nullable=True)


class ReservaContexto(Base):
    __tablename__ = "reserva_contexto"
    __table_args__ = {"schema": "reservas"}

    reserva_id: Mapped[int] = mapped_column(ForeignKey("reservas.reservas.id"), primary_key=True)
    proyecto_id: Mapped[int | None] = mapped_column(ForeignKey("investigacion.proyectos.id_proyecto"), nullable=True)
    semillero_id: Mapped[int | None] = mapped_column(ForeignKey("investigacion.semilleros.id_semillero"), nullable=True)
    pasantia_id: Mapped[int | None] = mapped_column(ForeignKey("investigacion.pasantias.id_pasantia"), nullable=True)
    trabajo_grado_id: Mapped[int | None] = mapped_column(ForeignKey("investigacion.trabajos_grado.id_trabajo_grado"), nullable=True)
    actividad_institucional_id: Mapped[int | None] = mapped_column(ForeignKey("investigacion.actividades_institucionales.id_actividad"), nullable=True)
    proyecto_codigo: Mapped[str | None] = mapped_column(nullable=True)
    proyecto_nombre: Mapped[str | None] = mapped_column(nullable=True)
    semillero_codigo: Mapped[str | None] = mapped_column(nullable=True)
    semillero_nombre: Mapped[str | None] = mapped_column(nullable=True)
    actividad_nombre: Mapped[str | None] = mapped_column(nullable=True)
    pasantia_universidad: Mapped[str | None] = mapped_column(nullable=True)
    pasantia_docente_nombre: Mapped[str | None] = mapped_column(nullable=True)
    pasantia_docente_correo: Mapped[str | None] = mapped_column(nullable=True)
    trabajo_grado_director_nombre: Mapped[str | None] = mapped_column(nullable=True)
    trabajo_grado_director_correo: Mapped[str | None] = mapped_column(nullable=True)


class ReservaDatosSalida(Base):
    __tablename__ = "reserva_datos_salida"
    __table_args__ = {"schema": "reservas"}

    reserva_id: Mapped[int] = mapped_column(ForeignKey("reservas.reservas.id"), primary_key=True)
    razon_solicitud: Mapped[str] = mapped_column()
    nombre_actividad_evento: Mapped[str | None] = mapped_column(nullable=True)
    lugar_nombre: Mapped[str] = mapped_column()
    lugar_direccion: Mapped[str] = mapped_column()


class ReservaEjecucionRecursos(Base):
    __tablename__ = "reserva_ejecucion_recursos"
    __table_args__ = {"schema": "reservas"}

    id: Mapped[int] = mapped_column(primary_key=True)
    reserva_recurso_id: Mapped[int] = mapped_column(ForeignKey("reservas.reserva_recursos.id"))
    entregado_por: Mapped[int] = mapped_column(ForeignKey("auth.cuentas.id_cuenta"))
    recibido_por: Mapped[int | None] = mapped_column(ForeignKey("auth.cuentas.id_cuenta"), nullable=True)
    entregado_at: Mapped[datetime] = mapped_column()
    devuelto_at: Mapped[datetime | None] = mapped_column(nullable=True)
    observacion_entrega: Mapped[str | None] = mapped_column(nullable=True)
    observacion_devolucion: Mapped[str | None] = mapped_column(nullable=True)


class ReservaEspacio(Base):
    __tablename__ = "reserva_espacio"
    __table_args__ = {"schema": "reservas"}

    reserva_id: Mapped[int] = mapped_column(ForeignKey("reservas.reservas.id"), primary_key=True)
    espacio_id: Mapped[int] = mapped_column(ForeignKey("reservas.espacios.id"))
    fecha: Mapped[date] = mapped_column()
    hora_inicio: Mapped[time] = mapped_column()
    hora_fin: Mapped[time] = mapped_column()
    asistentes: Mapped[int] = mapped_column()
    # `periodo` es GENERATED ALWAYS (Postgres la rechaza en cualquier INSERT
    # explícito, ni con NULL); `bloqueante` la fija el disparador BEFORE
    # INSERT de DB-12. `FetchedValue()` le dice al ORM que no las incluya en
    # el INSERT cuando el código no las toca; `db.refresh()` trae el valor
    # real que puso la base.
    periodo: Mapped[str | None] = mapped_column(nullable=True, server_default=FetchedValue())
    bloqueante: Mapped[bool] = mapped_column(server_default=FetchedValue())


class ReservaHistorialEstado(Base):
    __tablename__ = "reserva_historial_estado"
    __table_args__ = {"schema": "reservas"}

    id: Mapped[int] = mapped_column(primary_key=True)
    reserva_id: Mapped[int] = mapped_column(ForeignKey("reservas.reservas.id"))
    estado_anterior_id: Mapped[int | None] = mapped_column(ForeignKey("reservas.estados_reserva.id"), nullable=True)
    estado_nuevo_id: Mapped[int] = mapped_column(ForeignKey("reservas.estados_reserva.id"))
    actor_cuenta_id: Mapped[int | None] = mapped_column(ForeignKey("auth.cuentas.id_cuenta"), nullable=True)
    motivo: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column()


class ReservaListaEspera(Base):
    __tablename__ = "reserva_lista_espera"
    __table_args__ = {"schema": "reservas"}

    reserva_id: Mapped[int] = mapped_column(ForeignKey("reservas.reservas.id"), primary_key=True)
    descripcion_necesidad: Mapped[str] = mapped_column()
    viable: Mapped[bool | None] = mapped_column(nullable=True)
    fecha_evaluacion_viabilidad: Mapped[datetime | None] = mapped_column(nullable=True)
    fecha_recepcion_material: Mapped[datetime | None] = mapped_column(nullable=True)
    prioridad: Mapped[int | None] = mapped_column(nullable=True)
    horas_ejecucion: Mapped[Decimal | None] = mapped_column(nullable=True)


class ReservaListaEsperaFormulario(Base):
    __tablename__ = "reserva_lista_espera_formulario"
    __table_args__ = {"schema": "reservas"}

    reserva_id: Mapped[int] = mapped_column(ForeignKey("reservas.reservas.id"), primary_key=True)
    datos_usuario: Mapped[dict] = mapped_column(JSONB)
    diligenciado_at: Mapped[datetime] = mapped_column()
    datos_tecnico: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    revisado_por: Mapped[int | None] = mapped_column(ForeignKey("auth.cuentas.id_cuenta"), nullable=True)
    revisado_at: Mapped[datetime | None] = mapped_column(nullable=True)


class ReservaPropuestas(Base):
    __tablename__ = "reserva_propuestas"
    __table_args__ = {"schema": "reservas"}

    id: Mapped[int] = mapped_column(primary_key=True)
    reserva_id: Mapped[int] = mapped_column(ForeignKey("reservas.reservas.id"))
    origen: Mapped[str] = mapped_column()
    fecha_inicio_propuesta: Mapped[date] = mapped_column()
    fecha_fin_propuesta: Mapped[date] = mapped_column()
    hora_inicio: Mapped[time | None] = mapped_column(nullable=True)
    hora_fin: Mapped[time | None] = mapped_column(nullable=True)
    motivo: Mapped[str] = mapped_column()
    estado: Mapped[str] = mapped_column()
    creada_por: Mapped[int] = mapped_column(ForeignKey("auth.cuentas.id_cuenta"))
    resuelta_por: Mapped[int | None] = mapped_column(ForeignKey("auth.cuentas.id_cuenta"), nullable=True)
    created_at: Mapped[datetime] = mapped_column()
    resuelta_at: Mapped[datetime | None] = mapped_column(nullable=True)


class ReservaRecursoCampus(Base):
    __tablename__ = "reserva_recurso_campus"
    __table_args__ = {"schema": "reservas"}

    reserva_id: Mapped[int] = mapped_column(ForeignKey("reservas.reservas.id"), primary_key=True)
    fecha_salida: Mapped[date] = mapped_column()
    fecha_devolucion_estimada: Mapped[date] = mapped_column()


class ReservaRecursoExterno(Base):
    __tablename__ = "reserva_recurso_externo"
    __table_args__ = {"schema": "reservas"}

    reserva_id: Mapped[int] = mapped_column(ForeignKey("reservas.reservas.id"), primary_key=True)
    fecha_salida: Mapped[date] = mapped_column()
    fecha_devolucion_estimada: Mapped[date] = mapped_column()


class ReservaRecursoInterno(Base):
    __tablename__ = "reserva_recurso_interno"
    __table_args__ = {"schema": "reservas"}

    reserva_id: Mapped[int] = mapped_column(ForeignKey("reservas.reservas.id"), primary_key=True)
    fecha: Mapped[date] = mapped_column()
    hora_inicio: Mapped[time] = mapped_column()
    hora_fin: Mapped[time] = mapped_column()


class ReservaRecursos(Base):
    __tablename__ = "reserva_recursos"
    __table_args__ = {"schema": "reservas"}

    id: Mapped[int] = mapped_column(primary_key=True)
    reserva_id: Mapped[int] = mapped_column(ForeignKey("reservas.reservas.id"))
    recurso_id: Mapped[int] = mapped_column(ForeignKey("recursos.recursos.id"))
    rol: Mapped[str] = mapped_column()
    estado_asignacion: Mapped[str] = mapped_column()
    incorporado_at: Mapped[datetime | None] = mapped_column(nullable=True)
    # `periodo` es `tstzrange`, mantenida por los disparadores de DB-12;
    # `Mapped[str]` no tiene un tipo Python nativo para rangos (ver
    # docstring del módulo), así que el ORM la trataría como VARCHAR al
    # insertar NULL si no se marca `FetchedValue()` — Postgres rechaza ese
    # NULL::VARCHAR contra una columna tstzrange.
    periodo: Mapped[str | None] = mapped_column(nullable=True, server_default=FetchedValue())
    bloqueante: Mapped[bool] = mapped_column()
    compromiso_fisico: Mapped[bool] = mapped_column()
    retirado_at: Mapped[datetime | None] = mapped_column(nullable=True)
    causa_retiro: Mapped[str | None] = mapped_column(nullable=True)
    reserva_causante_id: Mapped[int | None] = mapped_column(ForeignKey("reservas.reservas.id"), nullable=True)


class Reservas(Base):
    __tablename__ = "reservas"
    __table_args__ = {"schema": "reservas"}

    id: Mapped[int] = mapped_column(primary_key=True)
    id_unidad: Mapped[int] = mapped_column(ForeignKey("unidadOrganizacional.unidad_organizacional.id_unidad"))
    tipo_reserva_id: Mapped[int] = mapped_column(ForeignKey("reservas.tipos_reserva.id"))
    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column()
    id_cuenta: Mapped[int] = mapped_column(ForeignKey("auth.cuentas.id_cuenta"))
    estado_id: Mapped[int] = mapped_column(ForeignKey("reservas.estados_reserva.id"))
    observacion: Mapped[str | None] = mapped_column(nullable=True)
    requiere_apoyo: Mapped[bool] = mapped_column()
    created_by: Mapped[int] = mapped_column(ForeignKey("auth.cuentas.id_cuenta"))
    fecha_aprobacion: Mapped[datetime | None] = mapped_column(nullable=True)
    fecha_cancelacion: Mapped[datetime | None] = mapped_column(nullable=True)
    motivo_cancelacion: Mapped[str | None] = mapped_column(nullable=True)


class TiposReserva(Base):
    __tablename__ = "tipos_reserva"
    __table_args__ = {"schema": "reservas"}

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column()
    descripcion: Mapped[str] = mapped_column()
    habilitado: Mapped[bool] = mapped_column()
    codigo: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column()


