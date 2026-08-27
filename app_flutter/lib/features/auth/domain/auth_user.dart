import 'package:freezed_annotation/freezed_annotation.dart';

import '../../../core/domain/enums.dart';

part 'auth_user.freezed.dart';
part 'auth_user.g.dart';

/// Roles del sistema (ver CLAUDE.md raíz, tabla "Roles del sistema").
enum RolUsuario {
  @JsonValue('usuario')
  usuario,
  @JsonValue('gestor')
  gestor,
  @JsonValue('admin')
  admin,
}

@freezed
abstract class EspacioResumen with _$EspacioResumen {
  const factory EspacioResumen({
    required int id,
    required String nombre,
    required String ubicacion,
  }) = _EspacioResumen;

  factory EspacioResumen.fromJson(Map<String, dynamic> json) => _$EspacioResumenFromJson(json);
}

/// Espejo de `AuthUser` en `frontend/src/types/auth.ts`. `espacio` es
/// explícitamente nullable (un usuario/admin sin espacio asignado, o un
/// gestor con su único espacio) — nunca se reemplaza por un objeto vacío.
@freezed
abstract class AuthUser with _$AuthUser {
  const factory AuthUser({
    required int id,
    required String username,
    required String email,
    required RolUsuario rol,
    EspacioResumen? espacio,
    // Fase A2: perfil de usuario -- se completan una vez en `/perfil`,
    // nunca en cada reserva. Nullable: sin backfill para cuentas viejas.
    String? documentoIdentificacion,
    String? telefono,
    String? institucion,
    VinculacionUsuario? vinculacion,
    String? dependencia,
  }) = _AuthUser;

  const AuthUser._();

  factory AuthUser.fromJson(Map<String, dynamic> json) => _$AuthUserFromJson(json);

  /// Espejo de `isAdmin`/`canManageResources` en
  /// `frontend/src/context/AuthContext.tsx` — única fuente de verdad para
  /// estas dos reglas, reutilizada por guards de navegación y widgets.
  bool get isAdmin => rol == RolUsuario.admin;
  bool get canManageResources => rol == RolUsuario.admin || rol == RolUsuario.gestor;
}

/// El body de `POST /auth/supabase/sesion` (`LoginResponse`) solo trae
/// `{user}` — nunca un token, la sesión vive en la cookie HttpOnly.
@freezed
abstract class LoginResponse with _$LoginResponse {
  const factory LoginResponse({required AuthUser user}) = _LoginResponse;

  factory LoginResponse.fromJson(Map<String, dynamic> json) => _$LoginResponseFromJson(json);
}
