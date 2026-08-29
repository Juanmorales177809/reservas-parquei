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
    return _intercambiarSesion(token);
  }

  /// Completa una invitación (o una recuperación de contraseña): en ese
  /// momento ya existe una sesión "temporal" de Supabase (la estableció el
  /// link del correo, procesado por `detectSessionInUri` al arrancar la
  /// app — ver `main.dart`), pero la persona todavía no tiene contraseña
  /// propia. `updateUser` la fija y la sesión pasa a ser una normal, sin
  /// pedir un login aparte -- se canjea directo con el mismo endpoint que
  /// usa [login].
  Future<AuthUser> completarCuenta({required String password}) async {
    if (Supabase.instance.client.auth.currentSession == null) {
      throw Exception(
        'No hay una sesión de invitación activa. Volvé a abrir el link del correo.',
      );
    }
    await Supabase.instance.client.auth.updateUser(UserAttributes(password: password));
    final token = Supabase.instance.client.auth.currentSession?.accessToken;
    if (token == null || token.isEmpty) {
      throw Exception('Supabase no devolvió una sesión válida');
    }
    final user = await _intercambiarSesion(token);
    // Aviso de seguridad best-effort ("tu contraseña fue actualizada") --
    // el cambio de contraseña en sí ya ocurrió (líneas arriba, contra
    // Supabase); si el correo de confirmación falla no tiene sentido
    // bloquear el login con una sesión ya válida por eso.
    try {
      await _dio.post<void>('/auth/confirmar-cambio-password');
    } catch (_) {}
    return user;
  }

  /// `POST /auth/registro` (autoregistro abierto, sin aprobación de un
  /// admin -- ver `backend/CLAUDE.md`): crea la cuenta con rol `usuario` y
  /// la contraseña ya elegida, y de una vez inicia sesión con las mismas
  /// credenciales reusando [login] -- no hay ningún paso de invitación ni
  /// confirmación de por medio, la cuenta ya queda lista para usar.
  Future<AuthUser> registrarse({
    required String username,
    required String email,
    required String password,
  }) async {
    await _dio.post<Map<String, dynamic>>(
      '/auth/registro',
      data: {'username': username, 'email': email, 'password': password},
    );
    return login(email: email, password: password);
  }

  /// `POST /auth/recuperar` -- el backend genera el link de recuperación
  /// (`generar_link_recuperacion`, vía Supabase Admin API) y lo encola por
  /// nuestro propio outbox (Graph/SMTP según `EMAIL_TRANSPORT`), en vez del
  /// envío propio de Supabase que usaba este método antes
  /// (`resetPasswordForEmail`, 100% client-side). El backend responde 204
  /// exista o no una cuenta con ese email -- la pantalla que llama esto debe
  /// seguir mostrando siempre el mismo mensaje, sin importar el resultado,
  /// para no revelar qué emails existen. El link que llega por correo
  /// establece la misma sesión temporal `passwordRecovery` que un link de
  /// invitación (ver `main.dart`) y termina en [completarCuenta] -- mismo
  /// mecanismo, dos formas de llegar ahí.
  Future<void> solicitarRecuperacion({required String email}) async {
    await _dio.post<void>('/auth/recuperar', data: {'email': email});
  }

  Future<AuthUser> _intercambiarSesion(String supabaseToken) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/auth/supabase/sesion',
      data: {'supabase_token': supabaseToken},
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
