import 'package:freezed_annotation/freezed_annotation.dart';

part 'lista_espera_entrada.freezed.dart';
part 'lista_espera_entrada.g.dart';

/// Espejo de `ListaEsperaResponse` (`backend/app/schemas/lista_espera.py`).
@freezed
abstract class ListaEsperaEntrada with _$ListaEsperaEntrada {
  const factory ListaEsperaEntrada({
    required int id,
    required int recursoId,
    required String fecha,
    required String horaInicio,
    required String horaFin,
    required String estado,
    required String createdAt,
  }) = _ListaEsperaEntrada;

  factory ListaEsperaEntrada.fromJson(Map<String, dynamic> json) => _$ListaEsperaEntradaFromJson(json);
}
