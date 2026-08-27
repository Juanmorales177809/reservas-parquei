import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../../core/network/api_exception.dart';
import '../data/auth_repository.dart';
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

  Future<void> login({required String email, required String password}) async {
    final user = await ref.read(authRepositoryProvider).login(email: email, password: password);
    state = AsyncData(user);
  }

  /// Igual que `AuthContext.tsx`: siempre limpia el estado en `finally`
  /// aunque falle la red, porque quien llama (el botón de logout del
  /// shell) no espera la promesa.
  Future<void> logout() async {
    try {
      await ref.read(authRepositoryProvider).logout();
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
}

@riverpod
bool isAuthenticated(Ref ref) => ref.watch(authProvider).value != null;

@riverpod
bool isAdmin(Ref ref) => ref.watch(authProvider).value?.isAdmin ?? false;

@riverpod
bool canManageResources(Ref ref) => ref.watch(authProvider).value?.canManageResources ?? false;
