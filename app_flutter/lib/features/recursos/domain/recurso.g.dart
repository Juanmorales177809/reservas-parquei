// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'recurso.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_Recurso _$RecursoFromJson(Map<String, dynamic> json) => _Recurso(
  id: (json['id'] as num).toInt(),
  nombre: json['nombre'] as String,
  espacioId: (json['espacio_id'] as num).toInt(),
  tipoRecursoId: (json['tipo_recurso_id'] as num).toInt(),
  descripcion: json['descripcion'] as String?,
  capacidad: (json['capacidad'] as num).toInt(),
  estado: $enumDecode(_$EstadoEntidadEnumMap, json['estado']),
  espacio: Espacio.fromJson(json['espacio'] as Map<String, dynamic>),
  tipo: TipoRecurso.fromJson(json['tipo'] as Map<String, dynamic>),
  esPrestacionServicio: json['es_prestacion_servicio'] as bool,
);

Map<String, dynamic> _$RecursoToJson(_Recurso instance) => <String, dynamic>{
  'id': instance.id,
  'nombre': instance.nombre,
  'espacio_id': instance.espacioId,
  'tipo_recurso_id': instance.tipoRecursoId,
  'descripcion': instance.descripcion,
  'capacidad': instance.capacidad,
  'estado': _$EstadoEntidadEnumMap[instance.estado]!,
  'espacio': instance.espacio,
  'tipo': instance.tipo,
  'es_prestacion_servicio': instance.esPrestacionServicio,
};

const _$EstadoEntidadEnumMap = {
  EstadoEntidad.activo: 'activo',
  EstadoEntidad.inactivo: 'inactivo',
  EstadoEntidad.mantenimiento: 'mantenimiento',
};
