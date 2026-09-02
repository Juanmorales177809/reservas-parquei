import 'package:freezed_annotation/freezed_annotation.dart';

part 'control_cambio.freezed.dart';
part 'control_cambio.g.dart';

/// Espejo de `ControlCambioResponse` (`backend/app/schemas/control_cambio.py`).
/// `accion`/`entidad` son texto libre del backend (no un enum — ver
/// `backend/app/services/auditoria.py`, valores como "crear", "actualizar",
/// "eliminar", "configurar", "cambiar estado", "marcar_asistencia",
/// "cancelar"), así que la UI mapea por prefijo con un color por defecto
/// en vez de un `switch` exhaustivo. `createdAt` queda como texto crudo
/// (mismo criterio que `Reserva`/`Laboratorio`: riesgo espacio horaria
/// `America/Bogota`, nunca `DateTime.parse`).
@freezed
abstract class ControlCambio with _$ControlCambio {
  const factory ControlCambio({
    required int id,
    int? usuarioId,
    required String usuario,
    required String accion,
    required String entidad,
    int? entidadId,
    required String descripcion,
    required String createdAt,
  }) = _ControlCambio;

  factory ControlCambio.fromJson(Map<String, dynamic> json) => _$ControlCambioFromJson(json);
}
