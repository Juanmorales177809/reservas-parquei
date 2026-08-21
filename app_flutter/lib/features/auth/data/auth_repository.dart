import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/dio_client.dart';
import '../domain/auth_user.dart';

/// Espejo de `frontend/src/services/auth.ts` + el uso de `GET /usuarios/me`
/// en `AuthContext.tsx`. Sin estado propio: solo llama `dio` y devuelve/
/// lanza modelos tipados (`ApiException`, ver `auth_interceptor.dart`).
class AuthRepository {
  AuthRepository(this._dio);

  final Dio _dio;

  /// `POST /auth/login` — el backend fija la cookie `access_token` vía
  /// `Set-Cookie`; el body de respuesta solo trae `{user}` (Fase 9G, sin
  /// token). Un 401 aquí son credenciales inválidas (ver
  /// `kRutasSinRedirect401`), no una sesión expirada.
  Future<AuthUser> login({required String username, required String password}) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/auth/login',
      data: {'username': username, 'password': password},
    );
    return LoginResponse.fromJson(response.data!).user;
  }

  /// `POST /auth/logout` — borra la cookie en el backend. Público,
  /// idempotente.
  Future<void> logout() async {
    await _dio.post<void>('/auth/logout');
  }

  /// `GET /usuarios/me` — sondeo pasivo de sesión: 200 = autenticado, 401 =
  /// anónimo (no es un error a mostrar, ver `authProvider`).
  Future<AuthUser> getProfile() async {
    final response = await _dio.get<Map<String, dynamic>>('/usuarios/me');
    return AuthUser.fromJson(response.data!);
  }
}

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(ref.watch(dioProvider));
});
