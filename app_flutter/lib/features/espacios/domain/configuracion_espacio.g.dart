// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'configuracion_espacio.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ConfiguracionEspacio _$ConfiguracionEspacioFromJson(
  Map<String, dynamic> json,
) => _ConfiguracionEspacio(
  espacioId: (json['espacio_id'] as num).toInt(),
  espacioNombre: json['espacio_nombre'] as String,
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
  aprobacionAutomatica: json['aprobacion_automatica'] as bool,
);

Map<String, dynamic> _$ConfiguracionEspacioToJson(
  _ConfiguracionEspacio instance,
) => <String, dynamic>{
  'espacio_id': instance.espacioId,
  'espacio_nombre': instance.espacioNombre,
  'dias_atencion': instance.diasAtencion,
  'hora_apertura': instance.horaApertura,
  'hora_cierre': instance.horaCierre,
  'horario_atencion': instance.horarioAtencion,
  'horas_antelacion': instance.horasAntelacion,
  'aprobacion_automatica': instance.aprobacionAutomatica,
};
