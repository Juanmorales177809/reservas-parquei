import 'package:freezed_annotation/freezed_annotation.dart';

part 'configuracion_laboratorio.freezed.dart';
part 'configuracion_laboratorio.g.dart';

/// Espejo de `ConfiguracionLaboratorioResponse`
/// (`backend/app/schemas/laboratorio.py`) — solo accesible para el gestor de
/// ese laboratorio (`GET/PUT /laboratorios/gestion/configuracion`, 403 para
/// cualquier otro rol, incluido admin).
@freezed
abstract class ConfiguracionLaboratorio with _$ConfiguracionLaboratorio {
  const factory ConfiguracionLaboratorio({
    required int laboratorioId,
    required String laboratorioNombre,
    required List<int> diasAtencion,
    required String horaApertura,
    required String horaCierre,
    required Map<String, List<int>> horarioAtencion,
    required int horasAntelacion,
    required bool aprobacionAutomatica,
  }) = _ConfiguracionLaboratorio;

  factory ConfiguracionLaboratorio.fromJson(Map<String, dynamic> json) => _$ConfiguracionLaboratorioFromJson(json);
}
