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
  /// Fase P2: ahora soporta todos los ejes (`recurso_ids`/`zona_ids`/`ensayo_ids`/`acompanantes`/`tipo`)
  /// según `modalidad_reserva` y validaciones de `services/reservas.py`.
  Future<Reserva> crear({
    required List<int> recursoIds,
    required DateTime fecha,
    required String horaInicio,
    required String horaFin,
    required int asistentes,
    TipoReserva? tipo,
    List<int> zonaIds = const [],
    List<int> ensayoIds = const [],
    List<Map<String, String>> acompanantes = const [],
    String? descripcion,
    TipoSolicitud? tipoSolicitud,
    String? ubicacionUso,
    bool? requiereApoyoAuxiliar,
  }) async {
    final tipoJson = tipo == null ? null : tipoReservaToJson(tipo);
    final tipoSolicitudJson = tipoSolicitud == null ? null : tipoSolicitudToJson(tipoSolicitud);
    final response = await _dio.post<Map<String, dynamic>>(
      '/reservas',
      data: {
        'recurso_ids': recursoIds,
        'zona_ids': zonaIds,
        'ensayo_ids': ensayoIds,
        'acompanantes': acompanantes,
        'fecha': _formatoFecha.format(fecha),
        'hora_inicio': horaInicio,
        'hora_fin': horaFin,
        'asistentes': asistentes,
        'tipo': ?tipoJson,
        'descripcion': ?descripcion,
        'tipo_solicitud': ?tipoSolicitudJson,
        'ubicacion_uso': ?ubicacionUso,
        'requiere_apoyo_auxiliar': ?requiereApoyoAuxiliar,
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
  /// `motivo` es obligatorio cuando `nuevoEstado == rechazada`.
  Future<Reserva> cambiarEstado(int reservaId, EstadoReserva nuevoEstado, {String? motivo}) async {
    final data = <String, dynamic>{'nuevo_estado': estadoReservaToJson(nuevoEstado)};
    if (motivo != null) data['motivo'] = motivo;
    final response = await _dio.put<Map<String, dynamic>>(
      '/reservas/$reservaId/estado',
      data: data,
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

  /// `PATCH /reservas/{id}` — editar propia (usuario si esperando) o gestor/admin.
  /// Feature B: ahora también acepta `recursoIds`/`zonaIds` para que el gestor
  /// pueda agregar equipos a una reserva ya aprobada.
  Future<Reserva> actualizar(
    int reservaId, {
    DateTime? fecha,
    String? horaInicio,
    String? horaFin,
    int? asistentes,
    String? descripcion,
    TipoSolicitud? tipoSolicitud,
    String? ubicacionUso,
    bool? requiereApoyoAuxiliar,
    List<int>? recursoIds,
    List<int>? zonaIds,
  }) async {
    final data = <String, dynamic>{};
    if (fecha != null) data['fecha'] = _formatoFecha.format(fecha);
    if (horaInicio != null) data['hora_inicio'] = horaInicio;
    if (horaFin != null) data['hora_fin'] = horaFin;
    if (asistentes != null) data['asistentes'] = asistentes;
    if (descripcion != null) data['descripcion'] = descripcion;
    if (tipoSolicitud != null) data['tipo_solicitud'] = tipoSolicitudToJson(tipoSolicitud);
    if (ubicacionUso != null) data['ubicacion_uso'] = ubicacionUso;
    if (requiereApoyoAuxiliar != null) data['requiere_apoyo_auxiliar'] = requiereApoyoAuxiliar;
    if (recursoIds != null) data['recurso_ids'] = recursoIds;
    if (zonaIds != null) data['zona_ids'] = zonaIds;
    final response = await _dio.patch<Map<String, dynamic>>('/reservas/$reservaId', data: data);
    return Reserva.fromJson(response.data!);
  }

  /// `DELETE /reservas/{id}` — solo gestor/admin (usuario no puede).
  Future<void> eliminar(int reservaId) async {
    await _dio.delete<void>('/reservas/$reservaId');
  }
}

final reservasRepositoryProvider = Provider<ReservasRepository>((ref) {
  return ReservasRepository(ref.watch(dioProvider));
});
