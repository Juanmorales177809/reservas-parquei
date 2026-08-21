import 'package:freezed_annotation/freezed_annotation.dart';

part 'tipo_recurso.freezed.dart';
part 'tipo_recurso.g.dart';

/// Espejo de `TipoRecursoResponse` (`backend/app/schemas/recurso.py`).
/// OJO: `activo` es un `String` en el contrato del backend, no un bool —
/// se mapea literal, sin convertir.
@freezed
abstract class TipoRecurso with _$TipoRecurso {
  const factory TipoRecurso({
    required int id,
    required String nombre,
    required String descripcion,
    required String activo,
  }) = _TipoRecurso;

  factory TipoRecurso.fromJson(Map<String, dynamic> json) => _$TipoRecursoFromJson(json);
}
