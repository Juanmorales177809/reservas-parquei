// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'zona.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_Zona _$ZonaFromJson(Map<String, dynamic> json) => _Zona(
  id: (json['id'] as num).toInt(),
  nombre: json['nombre'] as String,
  espacioId: (json['espacio_id'] as num).toInt(),
  descripcion: json['descripcion'] as String?,
  capacidad: (json['capacidad'] as num?)?.toInt(),
  estado: $enumDecode(_$EstadoEntidadEnumMap, json['estado']),
  createdAt: json['created_at'] as String,
  updatedAt: json['updated_at'] as String,
  createdBy: (json['created_by'] as num).toInt(),
  updatedBy: (json['updated_by'] as num).toInt(),
  recursoIds:
      (json['recurso_ids'] as List<dynamic>?)
          ?.map((e) => (e as num).toInt())
          .toList() ??
      const [],
);

Map<String, dynamic> _$ZonaToJson(_Zona instance) => <String, dynamic>{
  'id': instance.id,
  'nombre': instance.nombre,
  'espacio_id': instance.espacioId,
  'descripcion': instance.descripcion,
  'capacidad': instance.capacidad,
  'estado': _$EstadoEntidadEnumMap[instance.estado]!,
  'created_at': instance.createdAt,
  'updated_at': instance.updatedAt,
  'created_by': instance.createdBy,
  'updated_by': instance.updatedBy,
  'recurso_ids': instance.recursoIds,
};

const _$EstadoEntidadEnumMap = {
  EstadoEntidad.activo: 'activo',
  EstadoEntidad.inactivo: 'inactivo',
  EstadoEntidad.mantenimiento: 'mantenimiento',
};
