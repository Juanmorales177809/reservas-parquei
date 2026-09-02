// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'motivo_solicitud.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_MotivoSolicitud _$MotivoSolicitudFromJson(Map<String, dynamic> json) =>
    _MotivoSolicitud(
      id: (json['id'] as num).toInt(),
      laboratorioId: (json['laboratorio_id'] as num).toInt(),
      nombre: json['nombre'] as String,
      codigo: json['codigo'] as String,
      estado: json['estado'] as String,
      createdAt: json['created_at'] as String,
      updatedAt: json['updated_at'] as String,
      createdBy: (json['created_by'] as num?)?.toInt(),
      updatedBy: (json['updated_by'] as num?)?.toInt(),
    );

Map<String, dynamic> _$MotivoSolicitudToJson(_MotivoSolicitud instance) =>
    <String, dynamic>{
      'id': instance.id,
      'laboratorio_id': instance.laboratorioId,
      'nombre': instance.nombre,
      'codigo': instance.codigo,
      'estado': instance.estado,
      'created_at': instance.createdAt,
      'updated_at': instance.updatedAt,
      'created_by': instance.createdBy,
      'updated_by': instance.updatedBy,
    };
