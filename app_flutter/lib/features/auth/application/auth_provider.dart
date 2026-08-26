import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../../core/config/supabase_config.dart';
import '../../../core/network/api_exception.dart';
import '../data/auth_repository.dart';
import '../data/supabase_auth_repository.dart';
import '../domain/auth_user.dart';

part 'auth_provider.g.dart';

/// Espejo de `frontend/src/context/AuthContext.tsx`. Fuente única de verdad
/// de la sesión: `null` = anónimo, cargando = sondeo en curso, error =
/// fallo de red real (no un 401 de "no hay sesión", que se traduce a
/// `null`).
@riverpod
class Auth extends _$Auth {
  @override
  Future<AuthUser?> build() async {
    // Sondeo pasivo al arrancar (equivalente al `GET /usuarios/me` que
    // dispara `AuthContext.tsx` al montar): 200 = autenticado, 401 =
    // anónimo, no es un error visible.
    try {
      return await ref.read(authRepositoryProvider).getProfile();
    } on DioException catch (e) {
      if (apiErrorStatusCode(e) == 401) return null;
      rethrow;
    }
  }

  Future<void> login({required String username, required String password}) async {
    // Hybrid: si Supabase está configurado, el usuario puede estar logueándose
    // con email (Supabase) en vez de username clásico. Heurística simple:
    // si contiene '@' y Supabase está activo, usar flujo Supabase (email),
    // si no, flujo clásico (username). Mantiene compatibilidad total cuando
    // SUPABASE_ENABLED=false.
    if (SupabaseConfig.isConfigured && username.contains('@')) {
      final user = await ref.read(supabaseAuthRepositoryProvider).login(email: username, password: password);
      state = AsyncData(user);
      return;
    }
    final user = await ref.read(authRepositoryProvider).login(username: username, password: password);
    state = AsyncData(user);
  }

  /// Igual que `AuthContext.tsx`: siempre limpia el estado en `finally`
  /// aunque falle la red, porque quien llama (el botón de logout del
  /// shell) no espera la promesa.
  Future<void> logout() async {
    try {
      if (SupabaseConfig.isConfigured) {
        await ref.read(supabaseAuthRepositoryProvider).logout();
      } else {
        await ref.read(authRepositoryProvider).logout();
      }
    } catch (_) {
      // Fallo de red al cerrar sesión: se ignora a propósito, mismo
      // comportamiento que hoy en Navbar.tsx.
    } finally {
      state = const AsyncData(null);
    }
  }

  /// Invocado por [AuthInterceptor.onSessionExpired] cuando cualquier
  /// request autenticado recibe un 401 fuera de `kRutasSinRedirect401`.
  void handleSessionExpired() {
    state = const AsyncData(null);
  }

  /// Cubre el cambio obligatorio tras recibir una contraseña temporal
  /// (alta de usuario o recuperación) y el autoservicio voluntario.
  ///
  /// Actualiza `debeCambiarPassword` en el estado local en vez de volver a
  /// pedir `/usuarios/me`: el backend ya confirmó el cambio (si tirara
  /// excepción no llegaríamos a esta línea), y es exactamente el mismo dato
  /// que acabamos de fijar — un round-trip extra no cambiaría el resultado.
  /// Este método es lo que hace que el guard de `app_router.dart` deje de
  /// forzar `CambiarPasswordTemporalScreen` (reevalúa `redirect` en cada
  /// cambio de este estado, vía `refreshListenable`).
  Future<void> cambiarPassword({required String passwordActual, required String passwordNueva}) async {
    await ref.read(authRepositoryProvider).cambiarPassword(
          passwordActual: passwordActual,
          passwordNueva: passwordNueva,
        );
    final actual = state.value;
    if (actual != null) {
      state = AsyncData(actual.copyWith(debeCambiarPassword: false));
    }
  }
}

@riverpod
bool isAuthenticated(Ref ref) => ref.watch(authProvider).value != null;

@riverpod
bool isAdmin(Ref ref) => ref.watch(authProvider).value?.isAdmin ?? false;

@riverpod
bool canManageResources(Ref ref) => ref.watch(authProvider).value?.canManageResources ?? false;
