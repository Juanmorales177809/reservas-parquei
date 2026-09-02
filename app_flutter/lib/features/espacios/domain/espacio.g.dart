// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'espacio.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_Espacio _$EspacioFromJson(Map<String, dynamic> json) => _Espacio(
  id: (json['id'] as num).toInt(),
  nombre: json['nombre'] as String,
  laboratorioId: (json['laboratorio_id'] as num).toInt(),
  descripcion: json['descripcion'] as String?,
  capacidad: (json['capacidad'] as num?)?.toInt(),
  estado: $enumDecode(_$EstadoEntidadEnumMap, json['estado']),
  createdAt: json['created_at'] as String,
  updatedAt: json['updated_at'] as String,
  createdBy: (json['created_by'] as num?)?.toInt(),
  updatedBy: (json['updated_by'] as num?)?.toInt(),
  recursoIds:
      (json['recurso_ids'] as List<dynamic>?)
          ?.map((e) => (e as num).toInt())
          .toList() ??
      const [],
);

Map<String, dynamic> _$EspacioToJson(_Espacio instance) => <String, dynamic>{
  'id': instance.id,
  'nombre': instance.nombre,
  'laboratorio_id': instance.laboratorioId,
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
