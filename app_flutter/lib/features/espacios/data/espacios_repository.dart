import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/dio_client.dart';
import '../domain/espacio.dart';

/// Espejo de `frontend/src/services/espacios.ts` + CRUD gestor/admin.
/// `GET /espacios` es público (RN-005), `POST/PUT/DELETE` requieren `gestor`/`admin`.
class EspaciosRepository {
  EspaciosRepository(this._dio);

  final Dio _dio;

  Future<List<Espacio>> listar({int? laboratorioId}) async {
    final response = await _dio.get<List<dynamic>>(
      '/espacios',
      queryParameters: {'laboratorio_id': ?laboratorioId},
    );
    return response.data!.map((json) => Espacio.fromJson(json as Map<String, dynamic>)).toList();
  }

  Future<Espacio> crear({
    required String nombre,
    required int laboratorioId,
    String? descripcion,
    int? capacidad,
    String estado = 'activo',
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/espacios',
      data: {
        'nombre': nombre,
        'laboratorio_id': laboratorioId,
        'descripcion': descripcion,
        'capacidad': capacidad,
        'estado': estado,
      },
    );
    return Espacio.fromJson(response.data!);
  }

  Future<Espacio> actualizar(
    int espacioId, {
    String? nombre,
    int? laboratorioId,
    String? descripcion,
    int? capacidad,
    String? estado,
  }) async {
    final data = <String, dynamic>{};
    if (nombre != null) data['nombre'] = nombre;
    if (laboratorioId != null) data['laboratorio_id'] = laboratorioId;
    if (descripcion != null) data['descripcion'] = descripcion;
    if (capacidad != null) data['capacidad'] = capacidad;
    if (estado != null) data['estado'] = estado;
    final response = await _dio.put<Map<String, dynamic>>('/espacios/$espacioId', data: data);
    return Espacio.fromJson(response.data!);
  }

  Future<void> eliminar(int espacioId) async {
    await _dio.delete<void>('/espacios/$espacioId');
  }

  /// `PUT /espacios/{id}/recursos` — reemplazo completo de la asociación.
  Future<List<int>> reemplazarRecursos(int espacioId, List<int> recursoIds) async {
    final response = await _dio.put<Map<String, dynamic>>(
      '/espacios/$espacioId/recursos',
      data: {'recurso_ids': recursoIds},
    );
    final ids = response.data!['recurso_ids'] as List<dynamic>;
    return ids.map((e) => e as int).toList();
  }
}

final espaciosRepositoryProvider = Provider<EspaciosRepository>((ref) {
  return EspaciosRepository(ref.watch(dioProvider));
});
