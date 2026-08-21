// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'tipo_recurso.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_TipoRecurso _$TipoRecursoFromJson(Map<String, dynamic> json) => _TipoRecurso(
  id: (json['id'] as num).toInt(),
  nombre: json['nombre'] as String,
  descripcion: json['descripcion'] as String,
  activo: json['activo'] as String,
);

Map<String, dynamic> _$TipoRecursoToJson(_TipoRecurso instance) =>
    <String, dynamic>{
      'id': instance.id,
      'nombre': instance.nombre,
      'descripcion': instance.descripcion,
      'activo': instance.activo,
    };
