import 'package:dio/dio.dart';

import 'api_exception.dart';

/// Rutas donde un 401 NO dispara la sesión-expirada global (equivalente a
/// `RUTAS_SIN_REDIRECT_401` en `frontend/src/services/api.ts`):
/// - `/auth/supabase/sesion`: un 401 aquí es un JWT de Supabase inválido
///   (típicamente un intento de login que está en curso, no una sesión
///   nuestra que expiró) — debe llegar tal cual a la pantalla de login.
/// - `/usuarios/me`: sondeo pasivo de sesión al arrancar la app; un 401 ahí
///   sin sesión previa es el resultado normal de "no hay sesión", no debe
///   forzar la navegación global a /login (el guard de go_router ya cubre
///   ese caso al entrar a una ruta protegida).
const kRutasSinRedirect401 = {'/auth/supabase/sesion', '/usuarios/me'};

/// Traduce cualquier error de dio a [ApiException] y notifica sesión
/// expirada en el resto de rutas — equivalente al interceptor de 401 de
/// `apiFetch`. Sin manejo global de 403 (cada pantalla lo maneja, igual que
/// hoy en el frontend Next.js).
class AuthInterceptor extends Interceptor {
  AuthInterceptor({required this.onSessionExpired});

  final void Function() onSessionExpired;

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    final statusCode = err.response?.statusCode;
    final path = err.requestOptions.path;

    if (statusCode == 401 && !kRutasSinRedirect401.contains(path)) {
      onSessionExpired();
      handler.next(
        err.copyWith(
          error: const ApiException('Sesión expirada. Por favor, inicia sesión nuevamente.', statusCode: 401),
        ),
      );
      return;
    }

    final message = parseApiErrorMessage(err.response?.data, statusCode: statusCode);
    handler.next(err.copyWith(error: ApiException(message, statusCode: statusCode)));
  }
}
