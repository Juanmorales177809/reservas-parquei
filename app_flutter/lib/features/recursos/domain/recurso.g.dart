// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'recurso.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_Recurso _$RecursoFromJson(Map<String, dynamic> json) => _Recurso(
  id: (json['id'] as num).toInt(),
  nombre: json['nombre'] as String,
  laboratorioId: (json['laboratorio_id'] as num).toInt(),
  tipoRecursoId: (json['tipo_recurso_id'] as num).toInt(),
  descripcion: json['descripcion'] as String?,
  capacidad: (json['capacidad'] as num).toInt(),
  estado: $enumDecode(_$EstadoEntidadEnumMap, json['estado']),
  laboratorio: Laboratorio.fromJson(
    json['laboratorio'] as Map<String, dynamic>,
  ),
  tipo: TipoRecurso.fromJson(json['tipo'] as Map<String, dynamic>),
  esPrestacionServicio: json['es_prestacion_servicio'] as bool,
);

Map<String, dynamic> _$RecursoToJson(_Recurso instance) => <String, dynamic>{
  'id': instance.id,
  'nombre': instance.nombre,
  'laboratorio_id': instance.laboratorioId,
  'tipo_recurso_id': instance.tipoRecursoId,
  'descripcion': instance.descripcion,
  'capacidad': instance.capacidad,
  'estado': _$EstadoEntidadEnumMap[instance.estado]!,
  'laboratorio': instance.laboratorio,
  'tipo': instance.tipo,
  'es_prestacion_servicio': instance.esPrestacionServicio,
};

const _$EstadoEntidadEnumMap = {
  EstadoEntidad.activo: 'activo',
  EstadoEntidad.inactivo: 'inactivo',
  EstadoEntidad.mantenimiento: 'mantenimiento',
};
