import 'package:freezed_annotation/freezed_annotation.dart';

part 'motivo_solicitud.freezed.dart';
part 'motivo_solicitud.g.dart';

/// Espejo de `MotivoSolicitudResponse` (`backend/app/schemas/motivo_solicitud.py`).
@freezed
abstract class MotivoSolicitud with _$MotivoSolicitud {
  const factory MotivoSolicitud({
    required int id,
    required int laboratorioId,
    required String nombre,
    required String codigo,
    required String estado,
    required String createdAt,
    required String updatedAt,
    int? createdBy,
    int? updatedBy,
  }) = _MotivoSolicitud;

  factory MotivoSolicitud.fromJson(Map<String, dynamic> json) => _$MotivoSolicitudFromJson(json);
}
