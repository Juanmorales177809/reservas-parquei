// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'disponibilidad_slot.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_DisponibilidadSlot _$DisponibilidadSlotFromJson(Map<String, dynamic> json) =>
    _DisponibilidadSlot(
      horaInicio: json['hora_inicio'] as String,
      horaFin: json['hora_fin'] as String,
      estado: $enumDecode(_$EstadoSlotEnumMap, json['estado']),
    );

Map<String, dynamic> _$DisponibilidadSlotToJson(_DisponibilidadSlot instance) =>
    <String, dynamic>{
      'hora_inicio': instance.horaInicio,
      'hora_fin': instance.horaFin,
      'estado': _$EstadoSlotEnumMap[instance.estado]!,
    };

const _$EstadoSlotEnumMap = {
  EstadoSlot.libre: 'libre',
  EstadoSlot.ocupado: 'ocupado',
  EstadoSlot.mantenimiento: 'mantenimiento',
};
