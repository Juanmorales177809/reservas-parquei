import 'package:freezed_annotation/freezed_annotation.dart';

import '../../../core/domain/enums.dart';
import '../../laboratorios/domain/laboratorio.dart';
import 'tipo_recurso.dart';

part 'recurso.freezed.dart';
part 'recurso.g.dart';

/// Espejo de `RecursoResponse` (`backend/app/schemas/recurso.py`).
/// `laboratorio`/`tipo` vienen embebidos completos en cada recurso — no hace
/// falta una llamada aparte para resolverlos.
@freezed
abstract class Recurso with _$Recurso {
  const factory Recurso({
    required int id,
    required String nombre,
    required int laboratorioId,
    required int tipoRecursoId,
    String? descripcion,
    required int capacidad,
    required EstadoEntidad estado,
    required Laboratorio laboratorio,
    required TipoRecurso tipo,
    required bool esPrestacionServicio,
  }) = _Recurso;

  factory Recurso.fromJson(Map<String, dynamic> json) => _$RecursoFromJson(json);
}
