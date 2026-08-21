import 'package:freezed_annotation/freezed_annotation.dart';

import '../../../core/domain/enums.dart';

part 'ensayo.freezed.dart';
part 'ensayo.g.dart';

/// Espejo de `EnsayoResponse` (`backend/app/schemas/ensayo.py`).
@freezed
abstract class Ensayo with _$Ensayo {
  const factory Ensayo({
    required int id,
    required String nombre,
    required int zonaId,
    required EstadoEntidad estado,
    required String createdAt,
    required String updatedAt,
    required int createdBy,
    required int updatedBy,
  }) = _Ensayo;

  factory Ensayo.fromJson(Map<String, dynamic> json) => _$EnsayoFromJson(json);
}
