import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart' hide AuthUser;

import '../../../core/network/dio_client.dart';
import '../domain/auth_user.dart';

/// Único repositorio de autenticación: Supabase Auth (`signInWithPassword`)
/// + intercambio con el backend para fijar la cookie de sesión de siempre.
/// Reemplaza el viejo par `AuthRepository`/`SupabaseAuthRepository` (hybrid)
/// — no hay heurística de "es un email, entonces Supabase": todo el login
/// pasa por acá.
class AuthRepository {
  AuthRepository(this._dio);

  final Dio _dio;

  /// 1. `supabase.auth.signInWithPassword` contra Supabase Cloud.
  /// 2. `POST /auth/supabase/sesion {supabase_token}` — el backend verifica
  ///    ese JWT y busca el `Usuario` por `supabase_id` ya existente (nunca
  ///    crea ni vincula nada, ver `backend/app/api/auth.py::supabase_sesion`),
  ///    fija la cookie `HttpOnly` de siempre y devuelve `{user}`.
  Future<AuthUser> login({required String email, required String password}) async {
    final sesion = await Supabase.instance.client.auth.signInWithPassword(email: email, password: password);
    final token = sesion.session?.accessToken;
    if (token == null || token.isEmpty) {
      throw Exception('Supabase no devolvió una sesión válida');
    }
    final response = await _dio.post<Map<String, dynamic>>(
      '/auth/supabase/sesion',
      data: {'supabase_token': token},
    );
    return LoginResponse.fromJson(response.data!).user;
  }

  /// Cierra la sesión de Supabase y la cookie del backend. Un fallo al
  /// cerrar la de Supabase se ignora a propósito — la cookie del backend es
  /// la fuente de verdad real de la sesión de la app.
  Future<void> logout() async {
    try {
      await Supabase.instance.client.auth.signOut();
    } catch (_) {}
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
