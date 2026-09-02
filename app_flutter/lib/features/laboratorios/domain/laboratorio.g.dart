// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'laboratorio.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_Laboratorio _$LaboratorioFromJson(Map<String, dynamic> json) => _Laboratorio(
  id: (json['id'] as num).toInt(),
  nombre: json['nombre'] as String,
  ubicacion: json['ubicacion'] as String,
  capacidad: (json['capacidad'] as num).toInt(),
  estado: $enumDecode(_$EstadoEntidadEnumMap, json['estado']),
  diasAtencion: (json['dias_atencion'] as List<dynamic>)
      .map((e) => (e as num).toInt())
      .toList(),
  horaApertura: json['hora_apertura'] as String,
  horaCierre: json['hora_cierre'] as String,
  horarioAtencion: (json['horario_atencion'] as Map<String, dynamic>).map(
    (k, e) => MapEntry(
      k,
      (e as List<dynamic>).map((e) => (e as num).toInt()).toList(),
    ),
  ),
  horasAntelacion: (json['horas_antelacion'] as num).toInt(),
  correo: json['correo'] as String?,
);

Map<String, dynamic> _$LaboratorioToJson(_Laboratorio instance) =>
    <String, dynamic>{
      'id': instance.id,
      'nombre': instance.nombre,
      'ubicacion': instance.ubicacion,
      'capacidad': instance.capacidad,
      'estado': _$EstadoEntidadEnumMap[instance.estado]!,
      'dias_atencion': instance.diasAtencion,
      'hora_apertura': instance.horaApertura,
      'hora_cierre': instance.horaCierre,
      'horario_atencion': instance.horarioAtencion,
      'horas_antelacion': instance.horasAntelacion,
      'correo': instance.correo,
    };

const _$EstadoEntidadEnumMap = {
  EstadoEntidad.activo: 'activo',
  EstadoEntidad.inactivo: 'inactivo',
  EstadoEntidad.mantenimiento: 'mantenimiento',
};
