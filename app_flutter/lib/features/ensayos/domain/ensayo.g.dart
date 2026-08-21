// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'ensayo.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_Ensayo _$EnsayoFromJson(Map<String, dynamic> json) => _Ensayo(
  id: (json['id'] as num).toInt(),
  nombre: json['nombre'] as String,
  zonaId: (json['zona_id'] as num).toInt(),
  estado: $enumDecode(_$EstadoEntidadEnumMap, json['estado']),
  createdAt: json['created_at'] as String,
  updatedAt: json['updated_at'] as String,
  createdBy: (json['created_by'] as num).toInt(),
  updatedBy: (json['updated_by'] as num).toInt(),
);

Map<String, dynamic> _$EnsayoToJson(_Ensayo instance) => <String, dynamic>{
  'id': instance.id,
  'nombre': instance.nombre,
  'zona_id': instance.zonaId,
  'estado': _$EstadoEntidadEnumMap[instance.estado]!,
  'created_at': instance.createdAt,
  'updated_at': instance.updatedAt,
  'created_by': instance.createdBy,
  'updated_by': instance.updatedBy,
};

const _$EstadoEntidadEnumMap = {
  EstadoEntidad.activo: 'activo',
  EstadoEntidad.inactivo: 'inactivo',
  EstadoEntidad.mantenimiento: 'mantenimiento',
};
