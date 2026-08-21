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
    required int createdBy,
    required int updatedBy,
  }) = _Zona;

  factory Zona.fromJson(Map<String, dynamic> json) => _$ZonaFromJson(json);
}
