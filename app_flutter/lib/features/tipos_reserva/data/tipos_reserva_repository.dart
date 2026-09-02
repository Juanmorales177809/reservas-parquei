import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/dio_client.dart';
import '../domain/tipo_reserva.dart';

/// Espejo de `api/tipos_reserva.py` (Fase 7). `GET /tipos-reserva` es
/// público (RN-005), `POST/PUT/DELETE` requieren `gestor`/`admin`.
class TiposReservaRepository {
  TiposReservaRepository(this._dio);

  final Dio _dio;

  Future<List<TipoReserva>> listar({int? laboratorioId}) async {
    final response = await _dio.get<List<dynamic>>(
      '/tipos-reserva',
      queryParameters: {'laboratorio_id': ?laboratorioId},
    );
    return response.data!.map((json) => TipoReserva.fromJson(json as Map<String, dynamic>)).toList();
  }

  Future<TipoReserva> crear({
    required String nombre,
    required int laboratorioId,
    String estado = 'activo',
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/tipos-reserva',
      data: {'nombre': nombre, 'laboratorio_id': laboratorioId, 'estado': estado},
    );
    return TipoReserva.fromJson(response.data!);
  }

  Future<TipoReserva> actualizar(
    int tipoReservaId, {
    String? nombre,
    String? estado,
  }) async {
    final data = <String, dynamic>{};
    if (nombre != null) data['nombre'] = nombre;
    if (estado != null) data['estado'] = estado;
    final response = await _dio.put<Map<String, dynamic>>('/tipos-reserva/$tipoReservaId', data: data);
    return TipoReserva.fromJson(response.data!);
  }

  Future<void> eliminar(int tipoReservaId) async {
    await _dio.delete<void>('/tipos-reserva/$tipoReservaId');
  }
}

final tiposReservaRepositoryProvider = Provider<TiposReservaRepository>((ref) {
  return TiposReservaRepository(ref.watch(dioProvider));
});
