// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'tipo_reserva.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_TipoReserva _$TipoReservaFromJson(Map<String, dynamic> json) => _TipoReserva(
  id: (json['id'] as num).toInt(),
  laboratorioId: (json['laboratorio_id'] as num).toInt(),
  nombre: json['nombre'] as String,
  estado: json['estado'] as String,
  createdAt: json['created_at'] as String,
  updatedAt: json['updated_at'] as String,
  createdBy: (json['created_by'] as num?)?.toInt(),
  updatedBy: (json['updated_by'] as num?)?.toInt(),
);

Map<String, dynamic> _$TipoReservaToJson(_TipoReserva instance) =>
    <String, dynamic>{
      'id': instance.id,
      'laboratorio_id': instance.laboratorioId,
      'nombre': instance.nombre,
      'estado': instance.estado,
      'created_at': instance.createdAt,
      'updated_at': instance.updatedAt,
      'created_by': instance.createdBy,
      'updated_by': instance.updatedBy,
    };
