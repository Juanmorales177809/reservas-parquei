// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'notificacion.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_Notificacion _$NotificacionFromJson(Map<String, dynamic> json) =>
    _Notificacion(
      id: (json['id'] as num).toInt(),
      usuarioId: (json['usuario_id'] as num).toInt(),
      reservaId: (json['reserva_id'] as num?)?.toInt(),
      tipo: $enumDecode(_$TipoNotificacionEnumMap, json['tipo']),
      leida: json['leida'] as bool,
      createdAt: json['created_at'] as String,
      mensaje: json['mensaje'] as String,
    );

Map<String, dynamic> _$NotificacionToJson(_Notificacion instance) =>
    <String, dynamic>{
      'id': instance.id,
      'usuario_id': instance.usuarioId,
      'reserva_id': instance.reservaId,
      'tipo': _$TipoNotificacionEnumMap[instance.tipo]!,
      'leida': instance.leida,
      'created_at': instance.createdAt,
      'mensaje': instance.mensaje,
    };

const _$TipoNotificacionEnumMap = {
  TipoNotificacion.pendiente: 'Pendiente',
  TipoNotificacion.aprobada: 'Aprobada',
  TipoNotificacion.rechazada: 'Rechazada',
  TipoNotificacion.cancelada: 'Cancelada',
  TipoNotificacion.actualizada: 'Actualizada',
};
