// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'lista_espera_entrada.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ListaEsperaEntrada _$ListaEsperaEntradaFromJson(Map<String, dynamic> json) =>
    _ListaEsperaEntrada(
      id: (json['id'] as num).toInt(),
      recursoId: (json['recurso_id'] as num).toInt(),
      fecha: json['fecha'] as String,
      horaInicio: json['hora_inicio'] as String,
      horaFin: json['hora_fin'] as String,
      estado: json['estado'] as String,
      createdAt: json['created_at'] as String,
    );

Map<String, dynamic> _$ListaEsperaEntradaToJson(_ListaEsperaEntrada instance) =>
    <String, dynamic>{
      'id': instance.id,
      'recurso_id': instance.recursoId,
      'fecha': instance.fecha,
      'hora_inicio': instance.horaInicio,
      'hora_fin': instance.horaFin,
      'estado': instance.estado,
      'created_at': instance.createdAt,
    };
