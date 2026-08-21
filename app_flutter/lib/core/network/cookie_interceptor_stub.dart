import 'package:dio/dio.dart';

/// Rama Web (sin `dart:library.io`): el navegador maneja la cookie
/// `HttpOnly` de sesión por sí mismo — no hay nada que hacer aquí. Ver
/// `cookie_interceptor_io.dart` para la rama nativa.
Future<Interceptor?> createCookieInterceptor() async => null;
