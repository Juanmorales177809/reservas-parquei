import 'package:freezed_annotation/freezed_annotation.dart';

import '../../../core/domain/enums.dart';

part 'notificacion.freezed.dart';
part 'notificacion.g.dart';

/// Espejo de `NotificacionResponse` (`backend/app/schemas/notificacion.py`).
/// `mensaje` ya viene armado por el backend (incluye el nombre del
/// recurso/espacio) — se muestra literal, sin recomponerlo en el cliente.
@freezed
abstract class Notificacion with _$Notificacion {
  const factory Notificacion({
    required int id,
    required int usuarioId,
    int? reservaId,
    required TipoNotificacion tipo,
    required bool leida,
    required String createdAt,
    required String mensaje,
  }) = _Notificacion;

  factory Notificacion.fromJson(Map<String, dynamic> json) => _$NotificacionFromJson(json);
}
