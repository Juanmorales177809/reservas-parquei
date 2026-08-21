import 'package:freezed_annotation/freezed_annotation.dart';

part 'configuracion_espacio.freezed.dart';
part 'configuracion_espacio.g.dart';

/// Espejo de `ConfiguracionEspacioResponse`
/// (`backend/app/schemas/espacio.py`) — solo accesible para el gestor de
/// ese espacio (`GET/PUT /espacios/gestion/configuracion`, 403 para
/// cualquier otro rol, incluido admin).
@freezed
abstract class ConfiguracionEspacio with _$ConfiguracionEspacio {
  const factory ConfiguracionEspacio({
    required int espacioId,
    required String espacioNombre,
    required List<int> diasAtencion,
    required String horaApertura,
    required String horaCierre,
    required Map<String, List<int>> horarioAtencion,
    required int horasAntelacion,
    required bool aprobacionAutomatica,
  }) = _ConfiguracionEspacio;

  factory ConfiguracionEspacio.fromJson(Map<String, dynamic> json) => _$ConfiguracionEspacioFromJson(json);
}
