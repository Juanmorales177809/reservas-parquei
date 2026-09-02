// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'configuracion_laboratorio.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ConfiguracionLaboratorio _$ConfiguracionLaboratorioFromJson(
  Map<String, dynamic> json,
) => _ConfiguracionLaboratorio(
  laboratorioId: (json['laboratorio_id'] as num).toInt(),
  laboratorioNombre: json['laboratorio_nombre'] as String,
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

Map<String, dynamic> _$ConfiguracionLaboratorioToJson(
  _ConfiguracionLaboratorio instance,
) => <String, dynamic>{
  'laboratorio_id': instance.laboratorioId,
  'laboratorio_nombre': instance.laboratorioNombre,
  'dias_atencion': instance.diasAtencion,
  'hora_apertura': instance.horaApertura,
  'hora_cierre': instance.horaCierre,
  'horario_atencion': instance.horarioAtencion,
  'horas_antelacion': instance.horasAntelacion,
  'aprobacion_automatica': instance.aprobacionAutomatica,
};
