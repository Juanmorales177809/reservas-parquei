import 'package:freezed_annotation/freezed_annotation.dart';

import '../../../core/domain/enums.dart';

part 'disponibilidad_slot.freezed.dart';
part 'disponibilidad_slot.g.dart';

/// Espejo de `backend/app/schemas/disponibilidad.py` — mismo shape para
/// `GET /laboratorios/{id}/disponibilidad` y `GET /recursos/{id}/disponibilidad`
/// (compartido entre las features `laboratorios` y `recursos`).
@freezed
abstract class DisponibilidadSlot with _$DisponibilidadSlot {
  const factory DisponibilidadSlot({
    required String horaInicio,
    required String horaFin,
    required EstadoSlot estado,
  }) = _DisponibilidadSlot;

  factory DisponibilidadSlot.fromJson(Map<String, dynamic> json) => _$DisponibilidadSlotFromJson(json);
}
