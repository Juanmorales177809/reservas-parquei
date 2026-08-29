import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/dio_client.dart';
import '../domain/lista_espera_entrada.dart';

/// Espejo de `backend/app/api/lista_espera.py`.
class ListaEsperaRepository {
  ListaEsperaRepository(this._dio);

  final Dio _dio;

  Future<ListaEsperaEntrada> crear({
    required int recursoId,
    required DateTime fecha,
    required String horaInicio,
    required String horaFin,
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/lista-espera',
      data: {
        'recurso_id': recursoId,
        'fecha': fecha.toIso8601String().split('T').first,
        'hora_inicio': horaInicio,
        'hora_fin': horaFin,
      },
    );
    return ListaEsperaEntrada.fromJson(response.data!);
  }

  Future<List<ListaEsperaEntrada>> listarMias() async {
    final response = await _dio.get<List<dynamic>>('/lista-espera/mias');
    return response.data!.map((json) => ListaEsperaEntrada.fromJson(json as Map<String, dynamic>)).toList();
  }

  Future<void> cancelar(int id) => _dio.delete<void>('/lista-espera/$id');
}

final listaEsperaRepositoryProvider = Provider<ListaEsperaRepository>((ref) {
  return ListaEsperaRepository(ref.watch(dioProvider));
});
