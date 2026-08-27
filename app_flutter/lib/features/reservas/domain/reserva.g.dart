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

_EspacioReserva _$EspacioReservaFromJson(Map<String, dynamic> json) =>
    _EspacioReserva(
      id: (json['id'] as num).toInt(),
      nombre: json['nombre'] as String,
      capacidad: (json['capacidad'] as num?)?.toInt(),
      estado: $enumDecode(_$EstadoEntidadEnumMap, json['estado']),
    );

Map<String, dynamic> _$EspacioReservaToJson(_EspacioReserva instance) =>
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
      espacio: EspacioReserva.fromJson(json['espacio'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$RecursoReservaToJson(_RecursoReserva instance) =>
    <String, dynamic>{
      'id': instance.id,
      'nombre': instance.nombre,
      'capacidad': instance.capacidad,
      'estado': _$EstadoEntidadEnumMap[instance.estado]!,
      'espacio': instance.espacio,
    };

_ZonaReserva _$ZonaReservaFromJson(Map<String, dynamic> json) => _ZonaReserva(
  id: (json['id'] as num).toInt(),
  nombre: json['nombre'] as String,
  espacioId: (json['espacio_id'] as num).toInt(),
  descripcion: json['descripcion'] as String?,
  capacidad: (json['capacidad'] as num?)?.toInt(),
  estado: $enumDecode(_$EstadoEntidadEnumMap, json['estado']),
);

Map<String, dynamic> _$ZonaReservaToJson(_ZonaReserva instance) =>
    <String, dynamic>{
      'id': instance.id,
      'nombre': instance.nombre,
      'espacio_id': instance.espacioId,
      'descripcion': instance.descripcion,
      'capacidad': instance.capacidad,
      'estado': _$EstadoEntidadEnumMap[instance.estado]!,
    };

_EnsayoReserva _$EnsayoReservaFromJson(Map<String, dynamic> json) =>
    _EnsayoReserva(
      id: (json['id'] as num).toInt(),
      nombre: json['nombre'] as String,
      zonaId: (json['zona_id'] as num).toInt(),
      estado: $enumDecode(_$EstadoEntidadEnumMap, json['estado']),
    );

Map<String, dynamic> _$EnsayoReservaToJson(_EnsayoReserva instance) =>
    <String, dynamic>{
      'id': instance.id,
      'nombre': instance.nombre,
      'zona_id': instance.zonaId,
      'estado': _$EstadoEntidadEnumMap[instance.estado]!,
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
  espacioId: (json['espacio_id'] as num).toInt(),
  fecha: json['fecha'] as String,
  horaInicio: json['hora_inicio'] as String,
  horaFin: json['hora_fin'] as String,
  estado: $enumDecode(_$EstadoReservaEnumMap, json['estado']),
  asistentes: (json['asistentes'] as num).toInt(),
  tipo: $enumDecodeNullable(_$TipoReservaEnumMap, json['tipo']),
  asistio: json['asistio'] as bool?,
  motivoRechazo: json['motivo_rechazo'] as String?,
  descripcion: json['descripcion'] as String?,
  createdAt: json['created_at'] as String,
  updatedAt: json['updated_at'] as String,
  usuario: UsuarioReserva.fromJson(json['usuario'] as Map<String, dynamic>),
  espacio: EspacioReserva.fromJson(json['espacio'] as Map<String, dynamic>),
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
  zonaIds:
      (json['zona_ids'] as List<dynamic>?)
          ?.map((e) => (e as num).toInt())
          .toList() ??
      const [],
  zonas:
      (json['zonas'] as List<dynamic>?)
          ?.map((e) => ZonaReserva.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
  ensayoIds:
      (json['ensayo_ids'] as List<dynamic>?)
          ?.map((e) => (e as num).toInt())
          .toList() ??
      const [],
  ensayos:
      (json['ensayos'] as List<dynamic>?)
          ?.map((e) => EnsayoReserva.fromJson(e as Map<String, dynamic>))
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
  'espacio_id': instance.espacioId,
  'fecha': instance.fecha,
  'hora_inicio': instance.horaInicio,
  'hora_fin': instance.horaFin,
  'estado': _$EstadoReservaEnumMap[instance.estado]!,
  'asistentes': instance.asistentes,
  'tipo': _$TipoReservaEnumMap[instance.tipo],
  'asistio': instance.asistio,
  'motivo_rechazo': instance.motivoRechazo,
  'descripcion': instance.descripcion,
  'created_at': instance.createdAt,
  'updated_at': instance.updatedAt,
  'usuario': instance.usuario,
  'espacio': instance.espacio,
  'recurso_ids': instance.recursoIds,
  'recursos': instance.recursos,
  'zona_ids': instance.zonaIds,
  'zonas': instance.zonas,
  'ensayo_ids': instance.ensayoIds,
  'ensayos': instance.ensayos,
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
