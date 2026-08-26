import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import '../../../core/config/supabase_config.dart';
import '../../../core/network/dio_client.dart';
import '../domain/auth_user.dart';

/// Repositorio Supabase Auth hybrid (institucional sin recursos extra).
///
/// Con `SUPABASE_ENABLED=false` (default) este repositorio no se usa y el
/// flujo clásico `AuthRepository.login(username,password)` sigue intacto.
/// Con true: `signInWithPassword` contra Supabase Cloud (free tier
/// recomendado) y luego `POST /auth/supabase/sesion` para fijar la cookie
/// `access_token` del backend (ver `backend/app/api/auth.py`).
///
/// Mantiene `AuthUser.rol/espacio` en nuestra tabla (fuente única, ver
/// plan), no en `user_metadata` de Supabase.
class SupabaseAuthRepository {
  SupabaseAuthRepository(this._dio);

  final Dio _dio;

  bool get enabled => SupabaseConfig.isConfigured;

  /// Inicia sesión en Supabase y vincula la sesión en el backend.
  ///
  /// 1. `supabase.auth.signInWithPassword(email: email, password: password)`
  /// 2. Extrae `session.accessToken` (JWT con sub=UUID)
  /// 3. `POST /auth/supabase/sesion {supabase_token}` → fija cookie HttpOnly
  ///    y devuelve `AuthUser` (nuestra tabla, rol/espacio reales).
  Future<AuthUser> login({required String email, required String password}) async {
    if (!enabled) throw StateError('Supabase Auth no habilitado (SUPABASE_ENABLED=false)');
    final supa = Supabase.instance.client;
    final res = await supa.auth.signInWithPassword(email: email, password: password);
    final token = res.session?.accessToken;
    if (token == null || token.isEmpty) {
      throw Exception('Supabase no devolvió sesión');
    }
    final resp = await _dio.post<Map<String, dynamic>>(
      '/auth/supabase/sesion',
      data: {'supabase_token': token},
    );
    return LoginResponse.fromJson(resp.data!).user;
  }

  Future<void> logout() async {
    if (enabled) {
      try {
        await Supabase.instance.client.auth.signOut();
      } catch (_) {}
    }
    await _dio.post<void>('/auth/logout');
  }

  Future<AuthUser> getProfile() async {
    final resp = await _dio.get<Map<String, dynamic>>('/usuarios/me');
    return AuthUser.fromJson(resp.data!);
  }
}

final supabaseAuthRepositoryProvider = Provider<SupabaseAuthRepository>((ref) {
  return SupabaseAuthRepository(ref.watch(dioProvider));
});
