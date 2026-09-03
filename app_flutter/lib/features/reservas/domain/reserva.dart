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

/// Espejo de `LaboratorioReservaResponse` — subset mínimo, no el `Laboratorio`
/// completo de la feature `laboratorios` (sin `ubicacion`/`horario_atencion`).
@freezed
abstract class LaboratorioReserva with _$LaboratorioReserva {
  const factory LaboratorioReserva({
    required int id,
    required String nombre,
    int? capacidad,
    required EstadoEntidad estado,
  }) = _LaboratorioReserva;

  factory LaboratorioReserva.fromJson(Map<String, dynamic> json) => _$LaboratorioReservaFromJson(json);
}

/// Espejo de `RecursoReservaResponse` — subset mínimo.
@freezed
abstract class RecursoReserva with _$RecursoReserva {
  const factory RecursoReserva({
    required int id,
    required String nombre,
    int? capacidad,
    required EstadoEntidad estado,
    required LaboratorioReserva laboratorio,
  }) = _RecursoReserva;

  factory RecursoReserva.fromJson(Map<String, dynamic> json) => _$RecursoReservaFromJson(json);
}

/// Espejo de `EspacioReservaResponse`. La Fase 2 no expone selección de espacios
/// en el formulario todavía (ver alcance documentado en el plan) — este
/// modelo existe para poder parsear reservas existentes que sí las tengan
/// sin romper.
@freezed
abstract class EspacioReserva with _$EspacioReserva {
  const factory EspacioReserva({
    required int id,
    required String nombre,
    required int laboratorioId,
    String? descripcion,
    int? capacidad,
    required EstadoEntidad estado,
  }) = _EspacioReserva;

  factory EspacioReserva.fromJson(Map<String, dynamic> json) => _$EspacioReservaFromJson(json);
}

/// Espejo de `TipoReservaReservaResponse` (Fase 7) -- subset mínimo del
/// catálogo real `tipos_reserva`, no confundir con el enum viejo
/// [TipoReserva] (campo `tipo`, conservado por compatibilidad histórica).
@freezed
abstract class TipoReservaReserva with _$TipoReservaReserva {
  const factory TipoReservaReserva({
    required int id,
    required int laboratorioId,
    required String nombre,
    required String estado,
  }) = _TipoReservaReserva;

  factory TipoReservaReserva.fromJson(Map<String, dynamic> json) => _$TipoReservaReservaFromJson(json);
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
/// `updatedAt` quedan como texto crudo (mismo criterio que `Laboratorio` en la
/// Fase 1) — nunca se parsean a `DateTime` por el riesgo de espacio horaria
/// documentado en el plan de migración (el backend devuelve naive en
/// `America/Bogota`).
@freezed
abstract class Reserva with _$Reserva {
  const factory Reserva({
    required int id,
    required int usuarioId,
    required int laboratorioId,
    required String fecha,
    required String horaInicio,
    required String horaFin,
    required EstadoReserva estado,
    required int asistentes,
    TipoReserva? tipo,
    // Fase 7: catálogo real por laboratorio, reemplaza `tipo` hacia
    // adelante (ver backend/CLAUDE.md) -- `tipo` se conserva sin tocar por
    // compatibilidad de lectura de reservas históricas.
    int? tipoReservaId,
    TipoReservaReserva? tipoReserva,
    int? motivoSolicitudId,
    // MotivoSolicitud denormalizado para mostrar sin JOIN extra
    String? motivoSolicitudCodigo,
    String? motivoSolicitudNombre,
    bool? asistio,
    String? motivoRechazo,
    // Fase C: propuesta del técnico/usuario sin cambiar estado (queda
    // `esperando` con bloque activo). Todo nullable: sin propuesta no hay dato.
    String? propuestaMotivo,
    String? propuestaHorarios,
    String? propuestaPor,
    String? propuestaEn,
    // Fase A3: texto libre opcional -- "Actividad a realizar".
    String? descripcion,
    // Fase B: siempre tiene valor (NOT NULL con default en el backend).
    @Default(TipoSolicitud.reservaEnLaboratorio) TipoSolicitud tipoSolicitud,
    String? ubicacionUso,
    @Default(false) bool requiereApoyoAuxiliar,
    required String createdAt,
    required String updatedAt,
    required UsuarioReserva usuario,
    required LaboratorioReserva laboratorio,
    @Default([]) List<int> recursoIds,
    @Default([]) List<RecursoReserva> recursos,
    @Default([]) List<int> espacioIds,
    @Default([]) List<EspacioReserva> espacios,
    @Default([]) List<ReservaAcompanante> acompanantes,
    // Reservas multi-día agrupadas (2026-09-03): `null` para la inmensa
    // mayoría de las reservas (las que no pertenecen a ningún grupo). UUID
    // como texto crudo, mismo criterio que fecha/hora -- nunca se parsea.
    String? grupoId,
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

/// Reservas multi-día agrupadas (2026-09-03): una entrada de la lista que
/// arma `LaboratorioReservaSheet` antes de confirmar -- espejo de
/// `OcurrenciaInput` (`backend/app/schemas/reserva.py`). Solo se envía,
/// nunca se recibe -- sin `fromJson`.
@freezed
abstract class OcurrenciaInput with _$OcurrenciaInput {
  const factory OcurrenciaInput({
    required DateTime fecha,
    required String horaInicio,
    required String horaFin,
  }) = _OcurrenciaInput;
}

/// Espejo de `OcurrenciaOmitida` -- una ocurrencia del grupo que no se pudo
/// crear/cancelar ("mejor esfuerzo"), con el motivo que dio el backend.
@freezed
abstract class OcurrenciaOmitida with _$OcurrenciaOmitida {
  const factory OcurrenciaOmitida({
    required String fecha,
    required String horaInicio,
    required String horaFin,
    required String motivo,
  }) = _OcurrenciaOmitida;

  factory OcurrenciaOmitida.fromJson(Map<String, dynamic> json) => _$OcurrenciaOmitidaFromJson(json);
}

/// Espejo de `ReservaGrupoResponse` -- respuesta de `POST /reservas/grupo`.
@freezed
abstract class ReservaGrupoResultado with _$ReservaGrupoResultado {
  const factory ReservaGrupoResultado({
    required String grupoId,
    required List<Reserva> creadas,
    required List<OcurrenciaOmitida> omitidas,
  }) = _ReservaGrupoResultado;

  factory ReservaGrupoResultado.fromJson(Map<String, dynamic> json) => _$ReservaGrupoResultadoFromJson(json);
}

/// Espejo de `ReservaGrupoCancelResponse` -- respuesta de
/// `PUT /reservas/grupo/{id}/cancelar`.
@freezed
abstract class ReservaGrupoCancelResultado with _$ReservaGrupoCancelResultado {
  const factory ReservaGrupoCancelResultado({
    required List<int> canceladas,
    required List<OcurrenciaOmitida> omitidas,
  }) = _ReservaGrupoCancelResultado;

  factory ReservaGrupoCancelResultado.fromJson(Map<String, dynamic> json) => _$ReservaGrupoCancelResultadoFromJson(json);
}
