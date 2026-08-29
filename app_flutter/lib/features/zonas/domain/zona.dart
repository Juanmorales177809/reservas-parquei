import 'package:freezed_annotation/freezed_annotation.dart';

import '../../../core/domain/enums.dart';

part 'zona.freezed.dart';
part 'zona.g.dart';

/// Espejo de `ZonaResponse` (`backend/app/schemas/zona.py`).
/// `created_at`/`updated_at` quedan como texto crudo — mismo criterio que
/// `Reserva`/`Espacio` (riesgo zona horaria `America/Bogota`, nunca `DateTime.parse`).
@freezed
abstract class Zona with _$Zona {
  const factory Zona({
    required int id,
    required String nombre,
    required int espacioId,
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
  }) = _Zona;

  factory Zona.fromJson(Map<String, dynamic> json) => _$ZonaFromJson(json);
}
