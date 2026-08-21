// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'control_cambio.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ControlCambio _$ControlCambioFromJson(Map<String, dynamic> json) =>
    _ControlCambio(
      id: (json['id'] as num).toInt(),
      usuarioId: (json['usuario_id'] as num?)?.toInt(),
      usuario: json['usuario'] as String,
      accion: json['accion'] as String,
      entidad: json['entidad'] as String,
      entidadId: (json['entidad_id'] as num?)?.toInt(),
      descripcion: json['descripcion'] as String,
      createdAt: json['created_at'] as String,
    );

Map<String, dynamic> _$ControlCambioToJson(_ControlCambio instance) =>
    <String, dynamic>{
      'id': instance.id,
      'usuario_id': instance.usuarioId,
      'usuario': instance.usuario,
      'accion': instance.accion,
      'entidad': instance.entidad,
      'entidad_id': instance.entidadId,
      'descripcion': instance.descripcion,
      'created_at': instance.createdAt,
    };
