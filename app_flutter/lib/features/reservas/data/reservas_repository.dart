import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../core/domain/enums.dart';
import '../../../core/network/dio_client.dart';
import '../domain/reserva.dart';

final _formatoFecha = DateFormat('yyyy-MM-dd');

/// Espejo de `frontend/src/services/reservas.ts`, acotado al alcance de la
/// Fase 2 (ver plan de migración): creación por `recurso_ids` (modalidad
/// "equipos"), sin selección de espacios/acompañantes todavía —
/// `espacio_ids`/`acompanantes` siempre se envían vacíos, el
/// contrato del backend los acepta igual (`default_factory=list`).
class ReservasRepository {
  ReservasRepository(this._dio);

  final Dio _dio;

  /// `POST /reservas`. `horaInicio`/`horaFin` en formato `"HH:MM"`.
  /// Fase P2: ahora soporta todos los ejes (`recurso_ids`/`espacio_ids`/`acompanantes`/`tipo`),
  /// según las validaciones de `services/reservas.py`.
  Future<Reserva> crear({
    required List<int> recursoIds,
    required DateTime fecha,
    required String horaInicio,
    required String horaFin,
    required int asistentes,
    TipoReserva? tipo,
    int? tipoReservaId,
    int? motivoSolicitudId,
    List<int> espacioIds = const [],
    List<Map<String, String>> acompanantes = const [],
    String? descripcion,
    TipoSolicitud? tipoSolicitud,
    String? ubicacionUso,
    bool? requiereApoyoAuxiliar,
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/reservas',
      data: _payloadCrear(
        recursoIds: recursoIds,
        fecha: fecha,
        horaInicio: horaInicio,
        horaFin: horaFin,
        asistentes: asistentes,
        tipo: tipo,
        tipoReservaId: tipoReservaId,
        motivoSolicitudId: motivoSolicitudId,
        espacioIds: espacioIds,
        acompanantes: acompanantes,
        descripcion: descripcion,
        tipoSolicitud: tipoSolicitud,
        ubicacionUso: ubicacionUso,
        requiereApoyoAuxiliar: requiereApoyoAuxiliar,
      ),
    );
    return Reserva.fromJson(response.data!);
  }

  Map<String, dynamic> _payloadCrear({
    required List<int> recursoIds,
    required DateTime fecha,
    required String horaInicio,
    required String horaFin,
    required int asistentes,
    TipoReserva? tipo,
    int? tipoReservaId,
    int? motivoSolicitudId,
    List<int> espacioIds = const [],
    List<Map<String, String>> acompanantes = const [],
    String? descripcion,
    TipoSolicitud? tipoSolicitud,
    String? ubicacionUso,
    bool? requiereApoyoAuxiliar,
  }) {
    final tipoJson = tipo == null ? null : tipoReservaToJson(tipo);
    final tipoSolicitudJson = tipoSolicitud == null ? null : tipoSolicitudToJson(tipoSolicitud);
    return {
      'recurso_ids': recursoIds,
      'espacio_ids': espacioIds,
      'acompanantes': acompanantes,
      'fecha': _formatoFecha.format(fecha),
      'hora_inicio': horaInicio,
      'hora_fin': horaFin,
      'asistentes': asistentes,
      'tipo': ?tipoJson,
      // Fase 7: catálogo real por laboratorio (reemplaza `tipo` hacia
      // adelante, ver backend/CLAUDE.md) -- `tipo` se conserva sin tocar
      // por compatibilidad de lectura de reservas históricas.
      'tipo_reserva_id': ?tipoReservaId,
      'motivo_solicitud_id': ?motivoSolicitudId,
      'descripcion': ?descripcion,
      'tipo_solicitud': ?tipoSolicitudJson,
      'ubicacion_uso': ?ubicacionUso,
      'requiere_apoyo_auxiliar': ?requiereApoyoAuxiliar,
    };
  }

  /// `POST /reservas/grupo` -- reservas multi-día agrupadas (2026-09-03).
  /// Mismos ejes compartidos que `crear` MENOS `fecha`/`hora_inicio`/
  /// `hora_fin` (esos viven en cada `OcurrenciaInput`) -- un solo equipo/
  /// espacio para todas las ocurrencias del grupo. Método separado, no una
  /// sobrecarga de `crear`: Dart no tiene equivalente ergonómico a la unión
  /// de tipos que usaría Pydantic acá.
  Future<ReservaGrupoResultado> crearGrupo({
    required List<int> recursoIds,
    required List<OcurrenciaInput> ocurrencias,
    required int asistentes,
    TipoReserva? tipo,
    int? tipoReservaId,
    int? motivoSolicitudId,
    List<int> espacioIds = const [],
    List<Map<String, String>> acompanantes = const [],
    String? descripcion,
    TipoSolicitud? tipoSolicitud,
    String? ubicacionUso,
    bool? requiereApoyoAuxiliar,
  }) async {
    final tipoJson = tipo == null ? null : tipoReservaToJson(tipo);
    final tipoSolicitudJson = tipoSolicitud == null ? null : tipoSolicitudToJson(tipoSolicitud);
    final response = await _dio.post<Map<String, dynamic>>(
      '/reservas/grupo',
      data: {
        'recurso_ids': recursoIds,
        'espacio_ids': espacioIds,
        'acompanantes': acompanantes,
        'asistentes': asistentes,
        'ocurrencias': ocurrencias
            .map((o) => {
                  'fecha': _formatoFecha.format(o.fecha),
                  'hora_inicio': o.horaInicio,
                  'hora_fin': o.horaFin,
                })
            .toList(),
        'tipo': ?tipoJson,
        'tipo_reserva_id': ?tipoReservaId,
        'motivo_solicitud_id': ?motivoSolicitudId,
        'descripcion': ?descripcion,
        'tipo_solicitud': ?tipoSolicitudJson,
        'ubicacion_uso': ?ubicacionUso,
        'requiere_apoyo_auxiliar': ?requiereApoyoAuxiliar,
      },
    );
    return ReservaGrupoResultado.fromJson(response.data!);
  }

  /// `GET /reservas/grupo/{grupoId}` -- ownership-only, nadie ve el grupo
  /// de otra persona (el backend devuelve una lista vacía, no 403).
  Future<List<Reserva>> grupo(String grupoId) async {
    final response = await _dio.get<List<dynamic>>('/reservas/grupo/$grupoId');
    return response.data!.map((json) => Reserva.fromJson(json as Map<String, dynamic>)).toList();
  }

  /// `PUT /reservas/grupo/{grupoId}/cancelar` -- atajo de "cancelar todas
  /// de una". Una ocurrencia individual se puede seguir cancelando con
  /// [cancelar] sin afectar al resto del grupo.
  Future<ReservaGrupoCancelResultado> cancelarGrupo(String grupoId) async {
    final response = await _dio.put<Map<String, dynamic>>('/reservas/grupo/$grupoId/cancelar');
    return ReservaGrupoCancelResultado.fromJson(response.data!);
  }

  /// `GET /reservas/mis-reservas`.
  Future<List<Reserva>> misReservas() async {
    final response = await _dio.get<List<dynamic>>('/reservas/mis-reservas');
    return response.data!.map((json) => Reserva.fromJson(json as Map<String, dynamic>)).toList();
  }

  /// `GET /reservas/mis-reservas/export` (2026-08-29).
  Future<List<int>> exportarMisReservas(String formato) async {
    final response = await _dio.get<List<int>>(
      '/reservas/mis-reservas/export',
      queryParameters: {'formato': formato},
      options: Options(responseType: ResponseType.bytes),
    );
    return response.data!;
  }

  /// `PUT /reservas/{id}/cancelar` — solo el propietario, y solo si la
  /// reserva está `aprobada` (`Reserva.puedeCancelarse`).
  Future<Reserva> cancelar(int reservaId) async {
    final response = await _dio.put<Map<String, dynamic>>('/reservas/$reservaId/cancelar');
    return Reserva.fromJson(response.data!);
  }

  /// `GET /reservas` — gestión, solo gestor/admin. El backend ya filtra al
  /// laboratorio del gestor (`get_managed_space_id`); el cliente no replica
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
  /// Feature B: ahora también acepta `recursoIds`/`espacioIds` para que el gestor
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
    List<int>? espacioIds,
    int? tipoReservaId,
  }) async {
    final data = <String, dynamic>{};
    if (fecha != null) data['fecha'] = _formatoFecha.format(fecha);
    if (horaInicio != null) data['hora_inicio'] = horaInicio;
    if (horaFin != null) data['hora_fin'] = horaFin;
    if (asistentes != null) data['asistentes'] = asistentes;
    if (descripcion != null) data['descripcion'] = descripcion;
    if (tipoReservaId != null) data['tipo_reserva_id'] = tipoReservaId;
    if (tipoSolicitud != null) data['tipo_solicitud'] = tipoSolicitudToJson(tipoSolicitud);
    if (ubicacionUso != null) data['ubicacion_uso'] = ubicacionUso;
    if (requiereApoyoAuxiliar != null) data['requiere_apoyo_auxiliar'] = requiereApoyoAuxiliar;
    if (recursoIds != null) data['recurso_ids'] = recursoIds;
    if (espacioIds != null) data['espacio_ids'] = espacioIds;
    final response = await _dio.patch<Map<String, dynamic>>('/reservas/$reservaId', data: data);
    return Reserva.fromJson(response.data!);
  }

  /// Fase C: proponer horarios alternativos (técnico, queda `esperando`).
  Future<Reserva> proponerHorarios(int reservaId, {required String motivo, required String horarios}) async {
    final response = await _dio.put<Map<String, dynamic>>(
      '/reservas/$reservaId/proponer-horarios',
      data: {'motivo': motivo, 'horarios': horarios},
    );
    return Reserva.fromJson(response.data!);
  }

  /// Fase C: contraproponer (usuario, cuando hay propuesta del técnico).
  Future<Reserva> contraproponer(int reservaId, {required String motivo, required String horarios}) async {
    final response = await _dio.put<Map<String, dynamic>>(
      '/reservas/$reservaId/contraproponer',
      data: {'motivo': motivo, 'horarios': horarios},
    );
    return Reserva.fromJson(response.data!);
  }

  /// Fase C: aceptar propuesta re-agendando.
  Future<Reserva> aceptarPropuesta(int reservaId, {required DateTime fecha, required String horaInicio, required String horaFin}) async {
    final response = await _dio.put<Map<String, dynamic>>(
      '/reservas/$reservaId/aceptar-propuesta',
      data: {'fecha': _formatoFecha.format(fecha), 'hora_inicio': horaInicio, 'hora_fin': horaFin},
    );
    return Reserva.fromJson(response.data!);
  }

  /// Fase C: rechazar propuesta (limpia, queda `esperando`).
  Future<Reserva> rechazarPropuesta(int reservaId) async {
    final response = await _dio.put<Map<String, dynamic>>('/reservas/$reservaId/rechazar-propuesta');
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
