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

  /// `POST /auth/cambiar-password` — exige la contraseña actual (aunque sea
  /// la temporal recién recibida por correo) como confirmación. Un 401 aquí
  /// es "contraseña actual incorrecta", no una sesión expirada — ver
  /// `kRutasSinRedirect401`.
  Future<void> cambiarPassword({required String passwordActual, required String passwordNueva}) async {
    await _dio.post<void>(
      '/auth/cambiar-password',
      data: {'password_actual': passwordActual, 'password_nueva': passwordNueva},
    );
  }

  /// `POST /auth/recuperar` — público, siempre 204 exista o no el
  /// identificador (anti-enumeración, ver backend/app/api/auth.py).
  Future<void> solicitarRecuperacion({required String identificador}) async {
    await _dio.post<void>('/auth/recuperar', data: {'identificador': identificador});
  }

  /// `POST /auth/restablecer` — público. 400 = código inválido o vencido,
  /// 429 = demasiados intentos.
  Future<void> restablecerPassword({
    required String identificador,
    required String codigo,
    required String passwordNueva,
  }) async {
    await _dio.post<void>(
      '/auth/restablecer',
      data: {'identificador': identificador, 'codigo': codigo, 'password_nueva': passwordNueva},
    );
  }
}

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(ref.watch(dioProvider));
});
