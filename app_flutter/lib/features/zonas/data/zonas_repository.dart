import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/dio_client.dart';
import '../domain/zona.dart';

/// Espejo de `frontend/src/services/zonas.ts` + CRUD gestor/admin.
/// `GET /zonas` es público (RN-005), `POST/PUT/DELETE` requieren `gestor`/`admin`.
class ZonasRepository {
  ZonasRepository(this._dio);

  final Dio _dio;

  Future<List<Zona>> listar({int? espacioId}) async {
    final response = await _dio.get<List<dynamic>>(
      '/zonas',
      queryParameters: {'espacio_id': ?espacioId},
    );
    return response.data!.map((json) => Zona.fromJson(json as Map<String, dynamic>)).toList();
  }

  Future<Zona> crear({
    required String nombre,
    required int espacioId,
    String? descripcion,
    int? capacidad,
    String estado = 'activo',
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/zonas',
      data: {
        'nombre': nombre,
        'espacio_id': espacioId,
        'descripcion': descripcion,
        'capacidad': capacidad,
        'estado': estado,
      },
    );
    return Zona.fromJson(response.data!);
  }

  Future<Zona> actualizar(
    int zonaId, {
    String? nombre,
    int? espacioId,
    String? descripcion,
    int? capacidad,
    String? estado,
  }) async {
    final data = <String, dynamic>{};
    if (nombre != null) data['nombre'] = nombre;
    if (espacioId != null) data['espacio_id'] = espacioId;
    if (descripcion != null) data['descripcion'] = descripcion;
    if (capacidad != null) data['capacidad'] = capacidad;
    if (estado != null) data['estado'] = estado;
    final response = await _dio.put<Map<String, dynamic>>('/zonas/$zonaId', data: data);
    return Zona.fromJson(response.data!);
  }

  Future<void> eliminar(int zonaId) async {
    await _dio.delete<void>('/zonas/$zonaId');
  }

  /// `PUT /zonas/{id}/recursos` — reemplazo completo de la asociación.
  Future<List<int>> reemplazarRecursos(int zonaId, List<int> recursoIds) async {
    final response = await _dio.put<Map<String, dynamic>>(
      '/zonas/$zonaId/recursos',
      data: {'recurso_ids': recursoIds},
    );
    final ids = response.data!['recurso_ids'] as List<dynamic>;
    return ids.map((e) => e as int).toList();
  }
}

final zonasRepositoryProvider = Provider<ZonasRepository>((ref) {
  return ZonasRepository(ref.watch(dioProvider));
});
