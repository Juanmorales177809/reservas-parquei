import 'package:freezed_annotation/freezed_annotation.dart';

part 'dashboard_summary.freezed.dart';
part 'dashboard_summary.g.dart';

/// Espejo de `AdminDashboardSummary` (`backend/app/schemas/admin_dashboard.py`).
@freezed
abstract class ReservasPorEstado with _$ReservasPorEstado {
  const factory ReservasPorEstado({
    required int pendientes,
    required int aprobadas,
    required int rechazadas,
    required int canceladas,
  }) = _ReservasPorEstado;

  factory ReservasPorEstado.fromJson(Map<String, dynamic> json) => _$ReservasPorEstadoFromJson(json);
}

@freezed
abstract class ReservasPorFecha with _$ReservasPorFecha {
  const factory ReservasPorFecha({
    required String fecha,
    required int cantidad,
  }) = _ReservasPorFecha;

  factory ReservasPorFecha.fromJson(Map<String, dynamic> json) => _$ReservasPorFechaFromJson(json);
}

@freezed
abstract class ReservasPorEspacio with _$ReservasPorEspacio {
  const factory ReservasPorEspacio({
    required int espacioId,
    required String nombre,
    required int cantidad,
  }) = _ReservasPorEspacio;

  factory ReservasPorEspacio.fromJson(Map<String, dynamic> json) => _$ReservasPorEspacioFromJson(json);
}

@freezed
abstract class RecursoMasReservado with _$RecursoMasReservado {
  const factory RecursoMasReservado({
    required int recursoId,
    required String nombre,
    required int cantidad,
  }) = _RecursoMasReservado;

  factory RecursoMasReservado.fromJson(Map<String, dynamic> json) => _$RecursoMasReservadoFromJson(json);
}

@freezed
abstract class OcupacionDiaHora with _$OcupacionDiaHora {
  const factory OcupacionDiaHora({
    required String dia,
    required int diaOrden,
    required int hora,
    required int cantidad,
  }) = _OcupacionDiaHora;

  factory OcupacionDiaHora.fromJson(Map<String, dynamic> json) => _$OcupacionDiaHoraFromJson(json);
}

@freezed
abstract class OcupacionGlobal with _$OcupacionGlobal {
  const factory OcupacionGlobal({
    required double horasOcupadas,
    required double horasDisponibles,
    required double porcentaje,
  }) = _OcupacionGlobal;

  factory OcupacionGlobal.fromJson(Map<String, dynamic> json) => _$OcupacionGlobalFromJson(json);
}

@freezed
abstract class DashboardSummary with _$DashboardSummary {
  const factory DashboardSummary({
    required int totalReservas,
    required int reservasPendientes,
    required int recursosActivos,
    required int usuarios,
    String? espacioNombre,
    required ReservasPorEstado reservasPorEstado,
    required List<ReservasPorFecha> reservasPorFecha,
    required List<ReservasPorEspacio> reservasPorEspacio,
    required List<RecursoMasReservado> recursosMasReservados,
    required List<OcupacionDiaHora> ocupacionPorDiaHora,
    required OcupacionGlobal ocupacionGlobal,
  }) = _DashboardSummary;

  factory DashboardSummary.fromJson(Map<String, dynamic> json) => _$DashboardSummaryFromJson(json);
}
