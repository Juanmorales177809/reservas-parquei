import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../core/domain/enums.dart';
import '../../../core/network/dio_client.dart';
import '../domain/reserva.dart';

final _formatoFecha = DateFormat('yyyy-MM-dd');

/// Espejo de `frontend/src/services/reservas.ts`, acotado al alcance de la
/// Fase 2 (ver plan de migración): creación por `recurso_ids` (modalidad
/// "equipos"), sin selección de zonas/ensayos/acompañantes todavía —
/// `zona_ids`/`ensayo_ids`/`acompanantes` siempre se envían vacíos, el
/// contrato del backend los acepta igual (`default_factory=list`).
class ReservasRepository {
  ReservasRepository(this._dio);

  final Dio _dio;

  /// `POST /reservas`. `horaInicio`/`horaFin` en formato `"HH:MM"`.
  Future<Reserva> crear({
    required List<int> recursoIds,
    required DateTime fecha,
    required String horaInicio,
    required String horaFin,
    required int asistentes,
    TipoReserva? tipo,
  }) async {
    final tipoJson = tipo == null ? null : tipoReservaToJson(tipo);
    final response = await _dio.post<Map<String, dynamic>>(
      '/reservas',
      data: {
        'recurso_ids': recursoIds,
        'zona_ids': <int>[],
        'ensayo_ids': <int>[],
        'acompanantes': <Map<String, dynamic>>[],
        'fecha': _formatoFecha.format(fecha),
        'hora_inicio': horaInicio,
        'hora_fin': horaFin,
        'asistentes': asistentes,
        'tipo': ?tipoJson,
      },
    );
    return Reserva.fromJson(response.data!);
  }

  /// `GET /reservas/mis-reservas`.
  Future<List<Reserva>> misReservas() async {
    final response = await _dio.get<List<dynamic>>('/reservas/mis-reservas');
    return response.data!.map((json) => Reserva.fromJson(json as Map<String, dynamic>)).toList();
  }

  /// `PUT /reservas/{id}/cancelar` — solo el propietario, y solo si la
  /// reserva está `aprobada` (`Reserva.puedeCancelarse`).
  Future<Reserva> cancelar(int reservaId) async {
    final response = await _dio.put<Map<String, dynamic>>('/reservas/$reservaId/cancelar');
    return Reserva.fromJson(response.data!);
  }

  /// `GET /reservas` — gestión, solo gestor/admin. El backend ya filtra al
  /// espacio del gestor (`get_managed_space_id`); el cliente no replica
  /// ese filtro.
  Future<List<Reserva>> listarGestion({int skip = 0, int limit = 100}) async {
    final response = await _dio.get<List<dynamic>>(
      '/reservas',
      queryParameters: {'skip': skip, 'limit': limit},
    );
    return response.data!.map((json) => Reserva.fromJson(json as Map<String, dynamic>)).toList();
  }

  /// `PUT /reservas/{id}/estado` — aprobar/rechazar/cancelar, solo
  /// gestor/admin. Transiciones válidas las valida el backend
  /// (`esperando -> aprobada|rechazada|cancelada`, `aprobada -> cancelada`).
  Future<Reserva> cambiarEstado(int reservaId, EstadoReserva nuevoEstado) async {
    final response = await _dio.put<Map<String, dynamic>>(
      '/reservas/$reservaId/estado',
      data: {'nuevo_estado': estadoReservaToJson(nuevoEstado)},
    );
    return Reserva.fromJson(response.data!);
  }

  /// `PUT /reservas/{id}/asistio` — solo gestor/admin.
  Future<Reserva> marcarAsistencia(int reservaId, bool asistio) async {
    final response = await _dio.put<Map<String, dynamic>>(
      '/reservas/$reservaId/asistio',
      data: {'asistio': asistio},
    );
    return Reserva.fromJson(response.data!);
  }
}

final reservasRepositoryProvider = Provider<ReservasRepository>((ref) {
  return ReservasRepository(ref.watch(dioProvider));
});
