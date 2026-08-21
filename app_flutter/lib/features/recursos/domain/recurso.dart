import 'package:freezed_annotation/freezed_annotation.dart';

import '../../../core/domain/enums.dart';
import '../../espacios/domain/espacio.dart';
import 'tipo_recurso.dart';

part 'recurso.freezed.dart';
part 'recurso.g.dart';

/// Espejo de `RecursoResponse` (`backend/app/schemas/recurso.py`).
/// `espacio`/`tipo` vienen embebidos completos en cada recurso — no hace
/// falta una llamada aparte para resolverlos.
@freezed
abstract class Recurso with _$Recurso {
  const factory Recurso({
    required int id,
    required String nombre,
    required int espacioId,
    required int tipoRecursoId,
    String? descripcion,
    required int capacidad,
    required EstadoEntidad estado,
    required Espacio espacio,
    required TipoRecurso tipo,
    required bool esPrestacionServicio,
  }) = _Recurso;

  factory Recurso.fromJson(Map<String, dynamic> json) => _$RecursoFromJson(json);
}
