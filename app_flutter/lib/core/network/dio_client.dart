import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../config/app_config.dart';
import 'auth_interceptor.dart';
import 'cookie_interceptor.dart';

/// Construye el cliente `dio` de la app. Se llama una vez en `main()`
/// (async, antes de `runApp`) y el resultado se inyecta vía
/// `dioProvider.overrideWithValue(...)`.
Future<Dio> buildDioClient(AppConfig config, {required void Function() onSessionExpired}) async {
  final dio = Dio(
    BaseOptions(
      baseUrl: config.baseUrl,
      contentType: 'application/json',
    ),
  );

  if (kIsWeb) {
    // En Web, dio usa el adaptador del navegador: la cookie `HttpOnly` la
    // maneja el propio navegador. `withCredentials` solo afecta a
    // peticiones cross-origin (para same-origin el navegador siempre
    // adjunta la cookie); se deja en true para el proxy same-origin de la
    // Fase 6-Web, y no tiene efecto negativo hoy porque el backend no
    // acepta credenciales cross-origin de todos modos.
    dio.options.extra['withCredentials'] = true;
  } else {
    final cookieInterceptor = await createCookieInterceptor();
    if (cookieInterceptor != null) {
      dio.interceptors.add(cookieInterceptor);
    }
  }

  dio.interceptors.add(AuthInterceptor(onSessionExpired: onSessionExpired));

  return dio;
}

/// Se sobreescribe en `main()` con el resultado de [buildDioClient]. Lanza
/// si algo intenta leerlo sin esa sobreescritura.
final dioProvider = Provider<Dio>((ref) {
  throw UnimplementedError('dioProvider debe sobreescribirse en main().');
});
