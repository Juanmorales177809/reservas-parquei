import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/dio_client.dart';
import '../domain/configuracion_espacio.dart';
import '../domain/espacio.dart';

/// Espejo de `frontend/src/services/espacios.ts`. RN-005 (filtro de estado
/// por rol) lo decide el backend según la cookie de sesión — este
/// repositorio no implementa ningún filtro propio, muestra lo que llegue.
class EspaciosRepository {
  EspaciosRepository(this._dio);

  final Dio _dio;

  Future<List<Espacio>> listar({int skip = 0, int limit = 100}) async {
    final response = await _dio.get<List<dynamic>>(
      '/espacios',
      queryParameters: {'skip': skip, 'limit': limit},
    );
    return response.data!.map((json) => Espacio.fromJson(json as Map<String, dynamic>)).toList();
  }

  Future<Espacio> obtener(int id) async {
    final response = await _dio.get<Map<String, dynamic>>('/espacios/$id');
    return Espacio.fromJson(response.data!);
  }

  /// `GET /espacios/gestion/configuracion` — solo gestor (403 para admin
  /// también, ver `backend/app/api/espacios.py`).
  Future<ConfiguracionEspacio> obtenerConfiguracionGestion() async {
    final response = await _dio.get<Map<String, dynamic>>('/espacios/gestion/configuracion');
    return ConfiguracionEspacio.fromJson(response.data!);
  }

  /// `PUT /espacios/gestion/configuracion`. `horarioAtencion` se reenvía
  /// tal cual se leyó — esta Fase 4 no incluye el editor de grilla
  /// día×hora todavía (ver `app_flutter/CLAUDE.md`), solo antelación y
  /// aprobación automática.
  Future<ConfiguracionEspacio> actualizarConfiguracionGestion({
    required Map<String, List<int>> horarioAtencion,
    required int horasAntelacion,
    required bool aprobacionAutomatica,
  }) async {
    final response = await _dio.put<Map<String, dynamic>>(
      '/espacios/gestion/configuracion',
      data: {
        'horario_atencion': horarioAtencion,
        'horas_antelacion': horasAntelacion,
        'aprobacion_automatica': aprobacionAutomatica,
      },
    );
    return ConfiguracionEspacio.fromJson(response.data!);
  }
}

final espaciosRepositoryProvider = Provider<EspaciosRepository>((ref) {
  return EspaciosRepository(ref.watch(dioProvider));
});
