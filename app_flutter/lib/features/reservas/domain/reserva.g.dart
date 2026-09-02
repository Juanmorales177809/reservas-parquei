// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'reserva.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_UsuarioReserva _$UsuarioReservaFromJson(Map<String, dynamic> json) =>
    _UsuarioReserva(
      id: (json['id'] as num).toInt(),
      username: json['username'] as String,
      email: json['email'] as String,
      rol: $enumDecode(_$RolUsuarioEnumMap, json['rol']),
    );

Map<String, dynamic> _$UsuarioReservaToJson(_UsuarioReserva instance) =>
    <String, dynamic>{
      'id': instance.id,
      'username': instance.username,
      'email': instance.email,
      'rol': _$RolUsuarioEnumMap[instance.rol]!,
    };

const _$RolUsuarioEnumMap = {
  RolUsuario.usuario: 'usuario',
  RolUsuario.gestor: 'gestor',
  RolUsuario.admin: 'admin',
};

_LaboratorioReserva _$LaboratorioReservaFromJson(Map<String, dynamic> json) =>
    _LaboratorioReserva(
      id: (json['id'] as num).toInt(),
      nombre: json['nombre'] as String,
      capacidad: (json['capacidad'] as num?)?.toInt(),
      estado: $enumDecode(_$EstadoEntidadEnumMap, json['estado']),
    );

Map<String, dynamic> _$LaboratorioReservaToJson(_LaboratorioReserva instance) =>
    <String, dynamic>{
      'id': instance.id,
      'nombre': instance.nombre,
      'capacidad': instance.capacidad,
      'estado': _$EstadoEntidadEnumMap[instance.estado]!,
    };

const _$EstadoEntidadEnumMap = {
  EstadoEntidad.activo: 'activo',
  EstadoEntidad.inactivo: 'inactivo',
  EstadoEntidad.mantenimiento: 'mantenimiento',
};

_RecursoReserva _$RecursoReservaFromJson(Map<String, dynamic> json) =>
    _RecursoReserva(
      id: (json['id'] as num).toInt(),
      nombre: json['nombre'] as String,
      capacidad: (json['capacidad'] as num?)?.toInt(),
      estado: $enumDecode(_$EstadoEntidadEnumMap, json['estado']),
      laboratorio: LaboratorioReserva.fromJson(
        json['laboratorio'] as Map<String, dynamic>,
      ),
    );

Map<String, dynamic> _$RecursoReservaToJson(_RecursoReserva instance) =>
    <String, dynamic>{
      'id': instance.id,
      'nombre': instance.nombre,
      'capacidad': instance.capacidad,
      'estado': _$EstadoEntidadEnumMap[instance.estado]!,
      'laboratorio': instance.laboratorio,
    };

_EspacioReserva _$EspacioReservaFromJson(Map<String, dynamic> json) =>
    _EspacioReserva(
      id: (json['id'] as num).toInt(),
      nombre: json['nombre'] as String,
      laboratorioId: (json['laboratorio_id'] as num).toInt(),
      descripcion: json['descripcion'] as String?,
      capacidad: (json['capacidad'] as num?)?.toInt(),
      estado: $enumDecode(_$EstadoEntidadEnumMap, json['estado']),
    );

Map<String, dynamic> _$EspacioReservaToJson(_EspacioReserva instance) =>
    <String, dynamic>{
      'id': instance.id,
      'nombre': instance.nombre,
      'laboratorio_id': instance.laboratorioId,
      'descripcion': instance.descripcion,
      'capacidad': instance.capacidad,
      'estado': _$EstadoEntidadEnumMap[instance.estado]!,
    };

_TipoReservaReserva _$TipoReservaReservaFromJson(Map<String, dynamic> json) =>
    _TipoReservaReserva(
      id: (json['id'] as num).toInt(),
      laboratorioId: (json['laboratorio_id'] as num).toInt(),
      nombre: json['nombre'] as String,
      estado: json['estado'] as String,
    );

Map<String, dynamic> _$TipoReservaReservaToJson(_TipoReservaReserva instance) =>
    <String, dynamic>{
      'id': instance.id,
      'laboratorio_id': instance.laboratorioId,
      'nombre': instance.nombre,
      'estado': instance.estado,
    };

_ReservaAcompanante _$ReservaAcompananteFromJson(Map<String, dynamic> json) =>
    _ReservaAcompanante(
      id: (json['id'] as num).toInt(),
      nombre: json['nombre'] as String,
      correo: json['correo'] as String,
    );

Map<String, dynamic> _$ReservaAcompananteToJson(_ReservaAcompanante instance) =>
    <String, dynamic>{
      'id': instance.id,
      'nombre': instance.nombre,
      'correo': instance.correo,
    };

_Reserva _$ReservaFromJson(Map<String, dynamic> json) => _Reserva(
  id: (json['id'] as num).toInt(),
  usuarioId: (json['usuario_id'] as num).toInt(),
  laboratorioId: (json['laboratorio_id'] as num).toInt(),
  fecha: json['fecha'] as String,
  horaInicio: json['hora_inicio'] as String,
  horaFin: json['hora_fin'] as String,
  estado: $enumDecode(_$EstadoReservaEnumMap, json['estado']),
  asistentes: (json['asistentes'] as num).toInt(),
  tipo: $enumDecodeNullable(_$TipoReservaEnumMap, json['tipo']),
  tipoReservaId: (json['tipo_reserva_id'] as num?)?.toInt(),
  tipoReserva: json['tipo_reserva'] == null
      ? null
      : TipoReservaReserva.fromJson(
          json['tipo_reserva'] as Map<String, dynamic>,
        ),
  asistio: json['asistio'] as bool?,
  motivoRechazo: json['motivo_rechazo'] as String?,
  descripcion: json['descripcion'] as String?,
  tipoSolicitud:
      $enumDecodeNullable(_$TipoSolicitudEnumMap, json['tipo_solicitud']) ??
      TipoSolicitud.reservaEnLaboratorio,
  ubicacionUso: json['ubicacion_uso'] as String?,
  requiereApoyoAuxiliar: json['requiere_apoyo_auxiliar'] as bool? ?? false,
  createdAt: json['created_at'] as String,
  updatedAt: json['updated_at'] as String,
  usuario: UsuarioReserva.fromJson(json['usuario'] as Map<String, dynamic>),
  laboratorio: LaboratorioReserva.fromJson(
    json['laboratorio'] as Map<String, dynamic>,
  ),
  recursoIds:
      (json['recurso_ids'] as List<dynamic>?)
          ?.map((e) => (e as num).toInt())
          .toList() ??
      const [],
  recursos:
      (json['recursos'] as List<dynamic>?)
          ?.map((e) => RecursoReserva.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
  espacioIds:
      (json['espacio_ids'] as List<dynamic>?)
          ?.map((e) => (e as num).toInt())
          .toList() ??
      const [],
  espacios:
      (json['espacios'] as List<dynamic>?)
          ?.map((e) => EspacioReserva.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
  acompanantes:
      (json['acompanantes'] as List<dynamic>?)
          ?.map((e) => ReservaAcompanante.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
);

Map<String, dynamic> _$ReservaToJson(_Reserva instance) => <String, dynamic>{
  'id': instance.id,
  'usuario_id': instance.usuarioId,
  'laboratorio_id': instance.laboratorioId,
  'fecha': instance.fecha,
  'hora_inicio': instance.horaInicio,
  'hora_fin': instance.horaFin,
  'estado': _$EstadoReservaEnumMap[instance.estado]!,
  'asistentes': instance.asistentes,
  'tipo': _$TipoReservaEnumMap[instance.tipo],
  'tipo_reserva_id': instance.tipoReservaId,
  'tipo_reserva': instance.tipoReserva,
  'asistio': instance.asistio,
  'motivo_rechazo': instance.motivoRechazo,
  'descripcion': instance.descripcion,
  'tipo_solicitud': _$TipoSolicitudEnumMap[instance.tipoSolicitud]!,
  'ubicacion_uso': instance.ubicacionUso,
  'requiere_apoyo_auxiliar': instance.requiereApoyoAuxiliar,
  'created_at': instance.createdAt,
  'updated_at': instance.updatedAt,
  'usuario': instance.usuario,
  'laboratorio': instance.laboratorio,
  'recurso_ids': instance.recursoIds,
  'recursos': instance.recursos,
  'espacio_ids': instance.espacioIds,
  'espacios': instance.espacios,
  'acompanantes': instance.acompanantes,
};

const _$EstadoReservaEnumMap = {
  EstadoReserva.esperando: 'esperando',
  EstadoReserva.aprobada: 'aprobada',
  EstadoReserva.rechazada: 'rechazada',
  EstadoReserva.cancelada: 'cancelada',
};

const _$TipoReservaEnumMap = {
  TipoReserva.trabajoInvestigacion: 'trabajo_investigacion',
  TipoReserva.trabajoGrado: 'trabajo_grado',
  TipoReserva.servicioDeEnsayo: 'servicio_de_ensayo',
};

const _$TipoSolicitudEnumMap = {
  TipoSolicitud.reservaEnLaboratorio: 'reserva_en_laboratorio',
  TipoSolicitud.reservaFueraLaboratorio: 'reserva_fuera_laboratorio',
  TipoSolicitud.ordenSalida: 'orden_salida',
};
