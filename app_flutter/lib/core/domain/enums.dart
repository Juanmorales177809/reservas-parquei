import 'package:json_annotation/json_annotation.dart';

/// Enums de dominio compartidos entre features — espejo de
/// `backend/app/domain/enums.py`. Los valores JSON son los que el backend
/// ya serializa; no reordenar ni renombrar sin verificar contra el backend.

enum EstadoEntidad {
  @JsonValue('activo')
  activo,
  @JsonValue('inactivo')
  inactivo,
  @JsonValue('mantenimiento')
  mantenimiento,
}

enum ModalidadEspacio {
  @JsonValue('equipos')
  equipos,
  @JsonValue('zonas')
  zonas,
  @JsonValue('mixto')
  mixto,
}

enum EstadoSlot {
  @JsonValue('libre')
  libre,
  @JsonValue('ocupado')
  ocupado,
  @JsonValue('mantenimiento')
  mantenimiento,
}

/// Estados del ciclo de vida de una reserva. Transiciones válidas:
/// `esperando -> aprobada|rechazada|cancelada`, `aprobada -> cancelada`.
/// `rechazada`/`cancelada` son terminales (backend/app/domain/enums.py).
enum EstadoReserva {
  @JsonValue('esperando')
  esperando,
  @JsonValue('aprobada')
  aprobada,
  @JsonValue('rechazada')
  rechazada,
  @JsonValue('cancelada')
  cancelada,
}

const _kEstadoReservaJson = {
  EstadoReserva.esperando: 'esperando',
  EstadoReserva.aprobada: 'aprobada',
  EstadoReserva.rechazada: 'rechazada',
  EstadoReserva.cancelada: 'cancelada',
};

/// Codifica un [EstadoReserva] al string que espera el backend — mismo
/// motivo que `tipoReservaToJson` (armado manual del body de
/// `PUT /reservas/{id}/estado`).
String estadoReservaToJson(EstadoReserva estado) => _kEstadoReservaJson[estado]!;

/// Tipo de reserva académica (RN-012/RN-015). Opcional: una reserva puede
/// no declarar tipo. `servicioDeEnsayo` es el único valor que habilita
/// recursos de "prestación de servicio" para gestor/admin.
enum TipoReserva {
  @JsonValue('trabajo_investigacion')
  trabajoInvestigacion,
  @JsonValue('trabajo_grado')
  trabajoGrado,
  @JsonValue('servicio_de_ensayo')
  servicioDeEnsayo,
}

const _kTipoReservaJson = {
  TipoReserva.trabajoInvestigacion: 'trabajo_investigacion',
  TipoReserva.trabajoGrado: 'trabajo_grado',
  TipoReserva.servicioDeEnsayo: 'servicio_de_ensayo',
};

/// Codifica un [TipoReserva] al string que espera el backend — usado por
/// los repositorios que arman el body de una request a mano (POST/PATCH),
/// donde no aplica el `fromJson`/`toJson` generado de un modelo de
/// respuesta.
String tipoReservaToJson(TipoReserva tipo) => _kTipoReservaJson[tipo]!;

/// Etiqueta en español para mostrar en la UI (formularios, listados).
String tipoReservaLabel(TipoReserva tipo) => switch (tipo) {
      TipoReserva.trabajoInvestigacion => 'Trabajo de investigación',
      TipoReserva.trabajoGrado => 'Trabajo de grado',
      TipoReserva.servicioDeEnsayo => 'Servicio de ensayo',
    };

/// Vinculación institucional de la persona con el ITM (Fase A2, perfil de
/// usuario) — cinco categorías estables del formulario real de solicitud
/// de laboratorios. Distinto de `RolUsuario` (rol funcional dentro de esta
/// app: usuario/gestor/admin), un concepto no relacionado.
enum VinculacionUsuario {
  @JsonValue('docente')
  docente,
  @JsonValue('estudiante')
  estudiante,
  @JsonValue('contratista_empleado')
  contratistaEmpleado,
  @JsonValue('extension')
  extension,
  @JsonValue('otra')
  otra,
}

const _kVinculacionUsuarioJson = {
  VinculacionUsuario.docente: 'docente',
  VinculacionUsuario.estudiante: 'estudiante',
  VinculacionUsuario.contratistaEmpleado: 'contratista_empleado',
  VinculacionUsuario.extension: 'extension',
  VinculacionUsuario.otra: 'otra',
};

/// Codifica un [VinculacionUsuario] al string que espera el backend —
/// usado por `UsuariosRepository.actualizarMiPerfil`, que arma el body a
/// mano (no pasa por el `fromJson`/`toJson` de un modelo de respuesta).
String vinculacionUsuarioToJson(VinculacionUsuario vinculacion) => _kVinculacionUsuarioJson[vinculacion]!;

/// Etiqueta en español para mostrar en el formulario de perfil.
String vinculacionUsuarioLabel(VinculacionUsuario vinculacion) => switch (vinculacion) {
      VinculacionUsuario.docente => 'Docente',
      VinculacionUsuario.estudiante => 'Estudiante',
      VinculacionUsuario.contratistaEmpleado => 'Contratista/Empleado',
      VinculacionUsuario.extension => 'Extensión',
      VinculacionUsuario.otra => 'Otra',
    };

/// Tipo de notificación — OJO: valores capitalizados en el backend
/// (`notificaciones_tipo_check`, constraint de base de datos), a
/// diferencia del resto de enums del dominio que van en minúscula.
enum TipoNotificacion {
  @JsonValue('Pendiente')
  pendiente,
  @JsonValue('Aprobada')
  aprobada,
  @JsonValue('Rechazada')
  rechazada,
  @JsonValue('Cancelada')
  cancelada,
}
