import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/dio_client.dart';
import '../domain/ensayo.dart';

/// Espejo de `frontend/src/services/ensayos.ts` + CRUD gestor/admin.
class EnsayosRepository {
  EnsayosRepository(this._dio);

  final Dio _dio;

  Future<List<Ensayo>> listar({int? zonaId}) async {
    final response = await _dio.get<List<dynamic>>(
      '/ensayos',
      queryParameters: {'zona_id': ?zonaId},
    );
    return response.data!.map((json) => Ensayo.fromJson(json as Map<String, dynamic>)).toList();
  }

  Future<Ensayo> crear({
    required String nombre,
    required int zonaId,
    String estado = 'activo',
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/ensayos',
      data: {'nombre': nombre, 'zona_id': zonaId, 'estado': estado},
    );
    return Ensayo.fromJson(response.data!);
  }

  Future<Ensayo> actualizar(
    int ensayoId, {
    String? nombre,
    int? zonaId,
    String? estado,
  }) async {
    final data = <String, dynamic>{};
    if (nombre != null) data['nombre'] = nombre;
    if (zonaId != null) data['zona_id'] = zonaId;
    if (estado != null) data['estado'] = estado;
    final response = await _dio.put<Map<String, dynamic>>('/ensayos/$ensayoId', data: data);
    return Ensayo.fromJson(response.data!);
  }

  Future<void> eliminar(int ensayoId) async {
    await _dio.delete<void>('/ensayos/$ensayoId');
  }
}

final ensayosRepositoryProvider = Provider<EnsayosRepository>((ref) {
  return EnsayosRepository(ref.watch(dioProvider));
});
