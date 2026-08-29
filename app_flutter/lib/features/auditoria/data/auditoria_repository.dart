import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/dio_client.dart';
import '../domain/control_cambio.dart';

/// Espejo de `frontend/src/services/control-cambios.ts` — solo lectura,
/// `GET /admin/control-cambios` (`require_admin`, ver `backend/app/api/control_cambios.py`).
class AuditoriaRepository {
  AuditoriaRepository(this._dio);

  final Dio _dio;

  Future<List<ControlCambio>> listar({int limit = 200}) async {
    final response = await _dio.get<List<dynamic>>(
      '/admin/control-cambios',
      queryParameters: {'limit': limit},
    );
    return response.data!.map((json) => ControlCambio.fromJson(json as Map<String, dynamic>)).toList();
  }

  /// `GET /admin/control-cambios/export` (2026-08-29).
  Future<List<int>> exportar(String formato, {int limit = 200}) async {
    final response = await _dio.get<List<int>>(
      '/admin/control-cambios/export',
      queryParameters: {'formato': formato, 'limit': limit},
      options: Options(responseType: ResponseType.bytes),
    );
    return response.data!;
  }
}

final auditoriaRepositoryProvider = Provider<AuditoriaRepository>((ref) {
  return AuditoriaRepository(ref.watch(dioProvider));
});
