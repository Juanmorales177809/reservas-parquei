import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/dio_client.dart';
import '../domain/configuracion_laboratorio.dart';
import '../domain/laboratorio.dart';

/// Espejo de `frontend/src/services/laboratorios.ts`. RN-005 (filtro de estado
/// por rol) lo decide el backend según la cookie de sesión — este
/// repositorio no implementa ningún filtro propio, muestra lo que llegue.
class LaboratoriosRepository {
  LaboratoriosRepository(this._dio);

  final Dio _dio;

  Future<List<Laboratorio>> listar({int skip = 0, int limit = 100}) async {
    final response = await _dio.get<List<dynamic>>(
      '/laboratorios',
      queryParameters: {'skip': skip, 'limit': limit},
    );
    return response.data!.map((json) => Laboratorio.fromJson(json as Map<String, dynamic>)).toList();
  }

  Future<Laboratorio> obtener(int id) async {
    final response = await _dio.get<Map<String, dynamic>>('/laboratorios/$id');
    return Laboratorio.fromJson(response.data!);
  }

  /// `GET /laboratorios/gestion/configuracion` — solo gestor (403 para admin
  /// también, ver `backend/app/api/laboratorios.py`).
  Future<ConfiguracionLaboratorio> obtenerConfiguracionGestion() async {
    final response = await _dio.get<Map<String, dynamic>>('/laboratorios/gestion/configuracion');
    return ConfiguracionLaboratorio.fromJson(response.data!);
  }

  /// `PUT /laboratorios/gestion/configuracion`. `horarioAtencion` se reenvía
  /// tal cual se leyó — esta Fase 4 no incluye el editor de grilla
  /// día×hora todavía (ver `app_flutter/CLAUDE.md`), solo antelación y
  /// aprobación automática.
  Future<ConfiguracionLaboratorio> actualizarConfiguracionGestion({
    required Map<String, List<int>> horarioAtencion,
    required int horasAntelacion,
    required bool aprobacionAutomatica,
    required bool notificarPorCorreo,
  }) async {
    final response = await _dio.put<Map<String, dynamic>>(
      '/laboratorios/gestion/configuracion',
      data: {
        'horario_atencion': horarioAtencion,
        'horas_antelacion': horasAntelacion,
        'aprobacion_automatica': aprobacionAutomatica,
        'notificar_por_correo': notificarPorCorreo,
      },
    );
    return ConfiguracionLaboratorio.fromJson(response.data!);
  }

  // --- CRUD admin /admin/laboratorios (Fase P1) ---

  /// `POST /laboratorios` — solo admin. `correo` es obligatorio (RN-007).
  Future<Laboratorio> crear({
    required String nombre,
    required String ubicacion,
    required int capacidad,
    required String correo,
    String estado = 'activo',
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/laboratorios',
      data: {
        'nombre': nombre,
        'ubicacion': ubicacion,
        'capacidad': capacidad,
        'correo': correo,
        'estado': estado,
      },
    );
    return Laboratorio.fromJson(response.data!);
  }

  /// `PUT /laboratorios/{id}` — solo admin. Solo envía campos no nulos.
  Future<Laboratorio> actualizar(
    int id, {
    String? nombre,
    String? ubicacion,
    int? capacidad,
    String? estado,
    String? correo,
  }) async {
    final data = <String, dynamic>{};
    if (nombre != null) data['nombre'] = nombre;
    if (ubicacion != null) data['ubicacion'] = ubicacion;
    if (capacidad != null) data['capacidad'] = capacidad;
    if (estado != null) data['estado'] = estado;
    if (correo != null) data['correo'] = correo;
    final response = await _dio.put<Map<String, dynamic>>('/laboratorios/$id', data: data);
    return Laboratorio.fromJson(response.data!);
  }

  /// `DELETE /laboratorios/{id}` — solo admin. `409` si tiene dependencias.
  Future<void> eliminar(int id) async {
    await _dio.delete<void>('/laboratorios/$id');
  }
}

final laboratoriosRepositoryProvider = Provider<LaboratoriosRepository>((ref) {
  return LaboratoriosRepository(ref.watch(dioProvider));
});
