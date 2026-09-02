import 'package:freezed_annotation/freezed_annotation.dart';

import '../../../core/domain/enums.dart';

part 'espacio.freezed.dart';
part 'espacio.g.dart';

/// Espejo de `EspacioResponse` (`backend/app/schemas/espacio.py`).
/// `created_at`/`updated_at` quedan como texto crudo — mismo criterio que
/// `Reserva`/`Laboratorio` (riesgo espacio horaria `America/Bogota`, nunca `DateTime.parse`).
@freezed
abstract class Espacio with _$Espacio {
  const factory Espacio({
    required int id,
    required String nombre,
    required int laboratorioId,
    String? descripcion,
    int? capacidad,
    required EstadoEntidad estado,
    required String createdAt,
    required String updatedAt,
    // Nullable desde 2026-08-29 (bug real de producción, ver
    // backend/CLAUDE.md): un created_by/updated_by huérfano (usuario
    // degradado antes de la separación personal/usuarios) se limpia a
    // NULL en la migración.
    int? createdBy,
    int? updatedBy,
    @Default([]) List<int> recursoIds,
  }) = _Espacio;

  factory Espacio.fromJson(Map<String, dynamic> json) => _$EspacioFromJson(json);
}
