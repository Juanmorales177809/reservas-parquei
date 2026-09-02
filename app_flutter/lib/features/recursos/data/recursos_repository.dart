import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../core/network/dio_client.dart';
import '../../laboratorios/domain/disponibilidad_slot.dart';
import '../domain/recurso.dart';
import '../domain/tipo_recurso.dart';

final _formatoFecha = DateFormat('yyyy-MM-dd');

/// Espejo de `frontend/src/services/recursos.ts`. RN-009 (ocultar recursos
/// de "prestación de servicio" a rol `usuario`) lo decide el backend según
/// la cookie de sesión — este repositorio no implementa ningún filtro
/// propio, muestra lo que llegue.
class RecursosRepository {
  RecursosRepository(this._dio);

  final Dio _dio;

  Future<List<Recurso>> listar({int? laboratorioId, bool soloActivos = false}) async {
    final response = await _dio.get<List<dynamic>>(
      '/recursos',
      queryParameters: {
        'laboratorio_id': ?laboratorioId,
        'solo_activos': soloActivos,
      },
    );
    return response.data!.map((json) => Recurso.fromJson(json as Map<String, dynamic>)).toList();
  }

  Future<List<DisponibilidadSlot>> disponibilidad(int recursoId, DateTime fecha) async {
    final response = await _dio.get<List<dynamic>>(
      '/recursos/$recursoId/disponibilidad',
      queryParameters: {'fecha': _formatoFecha.format(fecha)},
    );
    return response.data!.map((json) => DisponibilidadSlot.fromJson(json as Map<String, dynamic>)).toList();
  }

  Future<List<Recurso>> listarGestion() async {
    final response = await _dio.get<List<dynamic>>('/recursos/gestion');
    return response.data!.map((json) => Recurso.fromJson(json as Map<String, dynamic>)).toList();
  }

  Future<List<TipoRecurso>> listarTipos() async {
    final response = await _dio.get<List<dynamic>>('/recursos/tipos');
    return response.data!.map((json) => TipoRecurso.fromJson(json as Map<String, dynamic>)).toList();
  }

  /// `POST /recursos` — solo gestor/admin (`require_resource_manager`).
  Future<Recurso> crear({
    required String nombre,
    required int tipoRecursoId,
    String? descripcion,
    required int capacidad,
    String estado = 'activo',
    int? laboratorioId,
    bool esPrestacionServicio = false,
    bool requiereApoyoAuxiliar = false,
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/recursos',
      data: {
        'nombre': nombre,
        'tipo_recurso_id': tipoRecursoId,
        'descripcion': descripcion,
        'capacidad': capacidad,
        'estado': estado,
        'laboratorio_id': ?laboratorioId,
        'es_prestacion_servicio': esPrestacionServicio,
        'requiere_apoyo_auxiliar': requiereApoyoAuxiliar,
      },
    );
    return Recurso.fromJson(response.data!);
  }

  /// `PUT /recursos/{id}` — solo gestor/admin.
  Future<Recurso> actualizar(
    int recursoId, {
    String? nombre,
    int? tipoRecursoId,
    String? descripcion,
    int? capacidad,
    String? estado,
    int? laboratorioId,
    bool? esPrestacionServicio,
    bool? requiereApoyoAuxiliar,
  }) async {
    final data = <String, dynamic>{};
    if (nombre != null) data['nombre'] = nombre;
    if (tipoRecursoId != null) data['tipo_recurso_id'] = tipoRecursoId;
    if (descripcion != null) data['descripcion'] = descripcion;
    if (capacidad != null) data['capacidad'] = capacidad;
    if (estado != null) data['estado'] = estado;
    if (laboratorioId != null) data['laboratorio_id'] = laboratorioId;
    if (esPrestacionServicio != null) data['es_prestacion_servicio'] = esPrestacionServicio;
    if (requiereApoyoAuxiliar != null) data['requiere_apoyo_auxiliar'] = requiereApoyoAuxiliar;
    final response = await _dio.put<Map<String, dynamic>>('/recursos/$recursoId', data: data);
    return Recurso.fromJson(response.data!);
  }

  /// `DELETE /recursos/{id}` — 409 si tiene reservas.
  Future<void> eliminar(int recursoId) async {
    await _dio.delete<void>('/recursos/$recursoId');
  }
}

final recursosRepositoryProvider = Provider<RecursosRepository>((ref) {
  return RecursosRepository(ref.watch(dioProvider));
});
