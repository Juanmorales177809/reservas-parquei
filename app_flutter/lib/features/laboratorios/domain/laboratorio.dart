import 'package:freezed_annotation/freezed_annotation.dart';

import '../../../core/domain/enums.dart';

part 'laboratorio.freezed.dart';
part 'laboratorio.g.dart';

/// Espejo de `LaboratorioResponse` (`backend/app/schemas/laboratorio.py`).
@freezed
abstract class Laboratorio with _$Laboratorio {
  const factory Laboratorio({
    required int id,
    required String nombre,
    required String ubicacion,
    required int capacidad,
    required EstadoEntidad estado,
    required List<int> diasAtencion,
    required String horaApertura,
    required String horaCierre,
    // Las claves de día llegan como STRING en el JSON ("0".."6"), no int
    // (JSON no admite claves enteras) — ver `horasParaDia`.
    required Map<String, List<int>> horarioAtencion,
    required int horasAntelacion,
    String? correo,
  }) = _Laboratorio;

  const Laboratorio._();

  factory Laboratorio.fromJson(Map<String, dynamic> json) => _$LaboratorioFromJson(json);

  /// Horas (0-22) en que el laboratorio atiende el día `dia` (0=lunes, igual
  /// que `dias_atencion`/`horario_atencion` en el backend).
  List<int> horasParaDia(int dia) => horarioAtencion['$dia'] ?? const [];
}

/// Solo-presentación: `"08:00:00"` -> `"08:00"`. `hora_apertura`/
/// `hora_cierre` se guardan como texto crudo (ver riesgo de fechas/horas
/// del plan de migración) — nunca se parsean a `DateTime`.
String formatearHora(String horaConSegundos) {
  final partes = horaConSegundos.split(':');
  if (partes.length < 2) return horaConSegundos;
  return '${partes[0]}:${partes[1]}';
}
