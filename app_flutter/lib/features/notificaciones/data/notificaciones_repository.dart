import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/dio_client.dart';
import '../domain/notificacion.dart';

/// Espejo de `frontend/src/services/notificaciones.ts`.
class NotificacionesRepository {
  NotificacionesRepository(this._dio);

  final Dio _dio;

  Future<List<Notificacion>> listar() async {
    final response = await _dio.get<List<dynamic>>('/notificaciones');
    return response.data!.map((json) => Notificacion.fromJson(json as Map<String, dynamic>)).toList();
  }

  Future<int> contarSinLeer() async {
    final response = await _dio.get<Map<String, dynamic>>('/notificaciones/sin-leer/count');
    return response.data!['cantidad'] as int;
  }

  Future<Notificacion> marcarLeida(int id) async {
    final response = await _dio.patch<Map<String, dynamic>>('/notificaciones/$id/leer');
    return Notificacion.fromJson(response.data!);
  }

  Future<int> marcarTodasLeidas() async {
    final response = await _dio.patch<Map<String, dynamic>>('/notificaciones/leer-todas');
    return response.data!['cantidad'] as int;
  }
}

final notificacionesRepositoryProvider = Provider<NotificacionesRepository>((ref) {
  return NotificacionesRepository(ref.watch(dioProvider));
});
