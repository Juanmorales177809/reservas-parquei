// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'dashboard_summary.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ReservasPorEstado _$ReservasPorEstadoFromJson(Map<String, dynamic> json) =>
    _ReservasPorEstado(
      pendientes: (json['pendientes'] as num).toInt(),
      aprobadas: (json['aprobadas'] as num).toInt(),
      rechazadas: (json['rechazadas'] as num).toInt(),
      canceladas: (json['canceladas'] as num).toInt(),
    );

Map<String, dynamic> _$ReservasPorEstadoToJson(_ReservasPorEstado instance) =>
    <String, dynamic>{
      'pendientes': instance.pendientes,
      'aprobadas': instance.aprobadas,
      'rechazadas': instance.rechazadas,
      'canceladas': instance.canceladas,
    };

_ReservasPorFecha _$ReservasPorFechaFromJson(Map<String, dynamic> json) =>
    _ReservasPorFecha(
      fecha: json['fecha'] as String,
      cantidad: (json['cantidad'] as num).toInt(),
    );

Map<String, dynamic> _$ReservasPorFechaToJson(_ReservasPorFecha instance) =>
    <String, dynamic>{'fecha': instance.fecha, 'cantidad': instance.cantidad};

_ReservasPorEspacio _$ReservasPorEspacioFromJson(Map<String, dynamic> json) =>
    _ReservasPorEspacio(
      espacioId: (json['espacio_id'] as num).toInt(),
      nombre: json['nombre'] as String,
      cantidad: (json['cantidad'] as num).toInt(),
    );

Map<String, dynamic> _$ReservasPorEspacioToJson(_ReservasPorEspacio instance) =>
    <String, dynamic>{
      'espacio_id': instance.espacioId,
      'nombre': instance.nombre,
      'cantidad': instance.cantidad,
    };

_RecursoMasReservado _$RecursoMasReservadoFromJson(Map<String, dynamic> json) =>
    _RecursoMasReservado(
      recursoId: (json['recurso_id'] as num).toInt(),
      nombre: json['nombre'] as String,
      cantidad: (json['cantidad'] as num).toInt(),
    );

Map<String, dynamic> _$RecursoMasReservadoToJson(
  _RecursoMasReservado instance,
) => <String, dynamic>{
  'recurso_id': instance.recursoId,
  'nombre': instance.nombre,
  'cantidad': instance.cantidad,
};

_OcupacionDiaHora _$OcupacionDiaHoraFromJson(Map<String, dynamic> json) =>
    _OcupacionDiaHora(
      dia: json['dia'] as String,
      diaOrden: (json['dia_orden'] as num).toInt(),
      hora: (json['hora'] as num).toInt(),
      cantidad: (json['cantidad'] as num).toInt(),
    );

Map<String, dynamic> _$OcupacionDiaHoraToJson(_OcupacionDiaHora instance) =>
    <String, dynamic>{
      'dia': instance.dia,
      'dia_orden': instance.diaOrden,
      'hora': instance.hora,
      'cantidad': instance.cantidad,
    };

_OcupacionGlobal _$OcupacionGlobalFromJson(Map<String, dynamic> json) =>
    _OcupacionGlobal(
      horasOcupadas: (json['horas_ocupadas'] as num).toDouble(),
      horasDisponibles: (json['horas_disponibles'] as num).toDouble(),
      porcentaje: (json['porcentaje'] as num).toDouble(),
    );

Map<String, dynamic> _$OcupacionGlobalToJson(_OcupacionGlobal instance) =>
    <String, dynamic>{
      'horas_ocupadas': instance.horasOcupadas,
      'horas_disponibles': instance.horasDisponibles,
      'porcentaje': instance.porcentaje,
    };

_DashboardSummary _$DashboardSummaryFromJson(Map<String, dynamic> json) =>
    _DashboardSummary(
      totalReservas: (json['total_reservas'] as num).toInt(),
      reservasPendientes: (json['reservas_pendientes'] as num).toInt(),
      recursosActivos: (json['recursos_activos'] as num).toInt(),
      usuarios: (json['usuarios'] as num).toInt(),
      espacioNombre: json['espacio_nombre'] as String?,
      reservasPorEstado: ReservasPorEstado.fromJson(
        json['reservas_por_estado'] as Map<String, dynamic>,
      ),
      reservasPorFecha: (json['reservas_por_fecha'] as List<dynamic>)
          .map((e) => ReservasPorFecha.fromJson(e as Map<String, dynamic>))
          .toList(),
      reservasPorEspacio: (json['reservas_por_espacio'] as List<dynamic>)
          .map((e) => ReservasPorEspacio.fromJson(e as Map<String, dynamic>))
          .toList(),
      recursosMasReservados: (json['recursos_mas_reservados'] as List<dynamic>)
          .map((e) => RecursoMasReservado.fromJson(e as Map<String, dynamic>))
          .toList(),
      ocupacionPorDiaHora: (json['ocupacion_por_dia_hora'] as List<dynamic>)
          .map((e) => OcupacionDiaHora.fromJson(e as Map<String, dynamic>))
          .toList(),
      ocupacionGlobal: OcupacionGlobal.fromJson(
        json['ocupacion_global'] as Map<String, dynamic>,
      ),
    );

Map<String, dynamic> _$DashboardSummaryToJson(_DashboardSummary instance) =>
    <String, dynamic>{
      'total_reservas': instance.totalReservas,
      'reservas_pendientes': instance.reservasPendientes,
      'recursos_activos': instance.recursosActivos,
      'usuarios': instance.usuarios,
      'espacio_nombre': instance.espacioNombre,
      'reservas_por_estado': instance.reservasPorEstado,
      'reservas_por_fecha': instance.reservasPorFecha,
      'reservas_por_espacio': instance.reservasPorEspacio,
      'recursos_mas_reservados': instance.recursosMasReservados,
      'ocupacion_por_dia_hora': instance.ocupacionPorDiaHora,
      'ocupacion_global': instance.ocupacionGlobal,
    };
