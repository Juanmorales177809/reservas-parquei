import 'package:freezed_annotation/freezed_annotation.dart';

import '../../../core/domain/enums.dart';
import '../../auth/domain/auth_user.dart';

part 'reserva.freezed.dart';
part 'reserva.g.dart';

/// Espejo de `UsuarioReservaResponse` (`backend/app/schemas/reserva.py`) —
/// subset mínimo del usuario, no confundir con `AuthUser`.
@freezed
abstract class UsuarioReserva with _$UsuarioReserva {
  const factory UsuarioReserva({
    required int id,
    required String username,
    required String email,
    required RolUsuario rol,
  }) = _UsuarioReserva;

  factory UsuarioReserva.fromJson(Map<String, dynamic> json) => _$UsuarioReservaFromJson(json);
}

/// Espejo de `EspacioReservaResponse` — subset mínimo, no el `Espacio`
/// completo de la feature `espacios` (sin `ubicacion`/`horario_atencion`).
@freezed
abstract class EspacioReserva with _$EspacioReserva {
  const factory EspacioReserva({
    required int id,
    required String nombre,
    int? capacidad,
    required EstadoEntidad estado,
  }) = _EspacioReserva;

  factory EspacioReserva.fromJson(Map<String, dynamic> json) => _$EspacioReservaFromJson(json);
}

/// Espejo de `RecursoReservaResponse` — subset mínimo.
@freezed
abstract class RecursoReserva with _$RecursoReserva {
  const factory RecursoReserva({
    required int id,
    required String nombre,
    int? capacidad,
    required EstadoEntidad estado,
    required EspacioReserva espacio,
  }) = _RecursoReserva;

  factory RecursoReserva.fromJson(Map<String, dynamic> json) => _$RecursoReservaFromJson(json);
}

/// Espejo de `ZonaReservaResponse`. La Fase 2 no expone selección de zonas
/// en el formulario todavía (ver alcance documentado en el plan) — este
/// modelo existe para poder parsear reservas existentes que sí las tengan
/// sin romper.
@freezed
abstract class ZonaReserva with _$ZonaReserva {
  const factory ZonaReserva({
    required int id,
    required String nombre,
    required int espacioId,
    String? descripcion,
    int? capacidad,
    required EstadoEntidad estado,
  }) = _ZonaReserva;

  factory ZonaReserva.fromJson(Map<String, dynamic> json) => _$ZonaReservaFromJson(json);
}

/// Espejo de `EnsayoReservaResponse`. Mismo motivo que `ZonaReserva`: solo
/// para parseo, sin UI de selección todavía.
@freezed
abstract class EnsayoReserva with _$EnsayoReserva {
  const factory EnsayoReserva({
    required int id,
    required String nombre,
    required int zonaId,
    required EstadoEntidad estado,
  }) = _EnsayoReserva;

  factory EnsayoReserva.fromJson(Map<String, dynamic> json) => _$EnsayoReservaFromJson(json);
}

/// Espejo de `ReservaAcompananteResponse`.
@freezed
abstract class ReservaAcompanante with _$ReservaAcompanante {
  const factory ReservaAcompanante({
    required int id,
    required String nombre,
    required String correo,
  }) = _ReservaAcompanante;

  factory ReservaAcompanante.fromJson(Map<String, dynamic> json) => _$ReservaAcompananteFromJson(json);
}

/// Espejo de `ReservaResponse`. `fecha`/`horaInicio`/`horaFin`/`createdAt`/
/// `updatedAt` quedan como texto crudo (mismo criterio que `Espacio` en la
/// Fase 1) — nunca se parsean a `DateTime` por el riesgo de zona horaria
/// documentado en el plan de migración (el backend devuelve naive en
/// `America/Bogota`).
@freezed
abstract class Reserva with _$Reserva {
  const factory Reserva({
    required int id,
    required int usuarioId,
    required int espacioId,
    required String fecha,
    required String horaInicio,
    required String horaFin,
    required EstadoReserva estado,
    required int asistentes,
    TipoReserva? tipo,
    bool? asistio,
    String? motivoRechazo,
    // Fase A3: texto libre opcional -- "Actividad a realizar".
    String? descripcion,
    // Fase B: siempre tiene valor (NOT NULL con default en el backend).
    @Default(TipoSolicitud.reservaEnLaboratorio) TipoSolicitud tipoSolicitud,
    String? ubicacionUso,
    @Default(false) bool requiereApoyoAuxiliar,
    required String createdAt,
    required String updatedAt,
    required UsuarioReserva usuario,
    required EspacioReserva espacio,
    @Default([]) List<int> recursoIds,
    @Default([]) List<RecursoReserva> recursos,
    @Default([]) List<int> zonaIds,
    @Default([]) List<ZonaReserva> zonas,
    @Default([]) List<int> ensayoIds,
    @Default([]) List<EnsayoReserva> ensayos,
    @Default([]) List<ReservaAcompanante> acompanantes,
  }) = _Reserva;

  const Reserva._();

  factory Reserva.fromJson(Map<String, dynamic> json) => _$ReservaFromJson(json);

  /// Espejo exacto de `cancelar_reserva_usuario`
  /// (`backend/app/services/reservas.py:739`): el endpoint
  /// `PUT /reservas/{id}/cancelar` solo acepta reservas ya `aprobada` — una
  /// reserva `esperando` (pendiente de revisión) no puede cancelarse por
  /// esta vía; el usuario debe esperar a que gestor/admin la apruebe o
  /// rechace. (Nombre distinto a propósito de `ESTADOS_RESERVA_BLOQUEANTES`
  /// del backend, que es una regla no relacionada — de solapamiento, no de
  /// cancelación.)
  bool get puedeCancelarse => estado == EstadoReserva.aprobada;
}

/// Espejo de `OcurrenciaOmitida` (`backend/app/schemas/reserva.py`) --
/// una fecha de una reserva recurrente que no se pudo crear (2026-08-29).
@freezed
abstract class OcurrenciaOmitida with _$OcurrenciaOmitida {
  const factory OcurrenciaOmitida({
    required String fecha,
    required String motivo,
  }) = _OcurrenciaOmitida;

  factory OcurrenciaOmitida.fromJson(Map<String, dynamic> json) => _$OcurrenciaOmitidaFromJson(json);
}

/// Espejo de `ReservaSerieResponse` -- solo la respuesta de `POST /reservas`
/// cuando se pidió `repetirSemanas` (ver `ReservasRepository.crearRecurrente`).
@freezed
abstract class ReservaSerieResultado with _$ReservaSerieResultado {
  const factory ReservaSerieResultado({
    required List<Reserva> creadas,
    required List<OcurrenciaOmitida> omitidas,
  }) = _ReservaSerieResultado;

  factory ReservaSerieResultado.fromJson(Map<String, dynamic> json) => _$ReservaSerieResultadoFromJson(json);
}
