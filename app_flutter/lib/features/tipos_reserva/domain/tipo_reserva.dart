import 'package:freezed_annotation/freezed_annotation.dart';

part 'tipo_reserva.freezed.dart';
part 'tipo_reserva.g.dart';

/// Espejo de `TipoReservaResponse` (`backend/app/schemas/tipo_reserva.py`,
/// Fase 7). `estado` es un string plano (`'activo'|'inactivo'`), no
/// `EstadoEntidad` -- un tipo de reserva no es una entidad física, no tiene
/// el valor `'mantenimiento'` (ver el comentario del schema en el backend).
@freezed
abstract class TipoReserva with _$TipoReserva {
  const factory TipoReserva({
    required int id,
    required int laboratorioId,
    required String nombre,
    required String estado,
    required String createdAt,
    required String updatedAt,
    int? createdBy,
    int? updatedBy,
  }) = _TipoReserva;

  factory TipoReserva.fromJson(Map<String, dynamic> json) => _$TipoReservaFromJson(json);
}
