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
  tipoSolicitud:
      $enumDecodeNullable(_$TipoSolicitudEnumMap, json['tipo_solicitud']) ??
      TipoSolicitud.reservaEnLaboratorio,
  ubicacionUso: json['ubicacion_uso'] as String?,
  requiereApoyoAuxiliar: json['requiere_apoyo_auxiliar'] as bool? ?? false,
  createdAt: json['created_at'] as String,
  updatedAt: json['updated_at'] as String,
  usuario: UsuarioReserva.fromJson(json['usuario'] as Map<String, dynamic>),
  espacio: EspacioReserva.fromJson(json['espacio'] as Map<String, dynamic>),
  serieId: json['serie_id'] as String?,
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
  'tipo_solicitud': _$TipoSolicitudEnumMap[instance.tipoSolicitud]!,
  'ubicacion_uso': instance.ubicacionUso,
  'requiere_apoyo_auxiliar': instance.requiereApoyoAuxiliar,
  'created_at': instance.createdAt,
  'updated_at': instance.updatedAt,
  'usuario': instance.usuario,
  'espacio': instance.espacio,
  'serie_id': instance.serieId,
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

const _$TipoSolicitudEnumMap = {
  TipoSolicitud.reservaEnLaboratorio: 'reserva_en_laboratorio',
  TipoSolicitud.reservaFueraLaboratorio: 'reserva_fuera_laboratorio',
  TipoSolicitud.ordenSalida: 'orden_salida',
};

_OcurrenciaOmitida _$OcurrenciaOmitidaFromJson(Map<String, dynamic> json) =>
    _OcurrenciaOmitida(
      fecha: json['fecha'] as String,
      motivo: json['motivo'] as String,
    );

Map<String, dynamic> _$OcurrenciaOmitidaToJson(_OcurrenciaOmitida instance) =>
    <String, dynamic>{'fecha': instance.fecha, 'motivo': instance.motivo};

_ReservaSerieResultado _$ReservaSerieResultadoFromJson(
  Map<String, dynamic> json,
) => _ReservaSerieResultado(
  creadas: (json['creadas'] as List<dynamic>)
      .map((e) => Reserva.fromJson(e as Map<String, dynamic>))
      .toList(),
  omitidas: (json['omitidas'] as List<dynamic>)
      .map((e) => OcurrenciaOmitida.fromJson(e as Map<String, dynamic>))
      .toList(),
);

Map<String, dynamic> _$ReservaSerieResultadoToJson(
  _ReservaSerieResultado instance,
) => <String, dynamic>{
  'creadas': instance.creadas,
  'omitidas': instance.omitidas,
};

_OcurrenciaCancelOmitida _$OcurrenciaCancelOmitidaFromJson(
  Map<String, dynamic> json,
) => _OcurrenciaCancelOmitida(
  reservaId: (json['reserva_id'] as num).toInt(),
  motivo: json['motivo'] as String,
);

Map<String, dynamic> _$OcurrenciaCancelOmitidaToJson(
  _OcurrenciaCancelOmitida instance,
) => <String, dynamic>{
  'reserva_id': instance.reservaId,
  'motivo': instance.motivo,
};

_ReservaSerieCancelResultado _$ReservaSerieCancelResultadoFromJson(
  Map<String, dynamic> json,
) => _ReservaSerieCancelResultado(
  canceladas: (json['canceladas'] as List<dynamic>)
      .map((e) => Reserva.fromJson(e as Map<String, dynamic>))
      .toList(),
  omitidas: (json['omitidas'] as List<dynamic>)
      .map((e) => OcurrenciaCancelOmitida.fromJson(e as Map<String, dynamic>))
      .toList(),
);

Map<String, dynamic> _$ReservaSerieCancelResultadoToJson(
  _ReservaSerieCancelResultado instance,
) => <String, dynamic>{
  'canceladas': instance.canceladas,
  'omitidas': instance.omitidas,
};
