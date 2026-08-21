import 'package:dio/dio.dart';

import 'cookie_interceptor_stub.dart' if (dart.library.io) 'cookie_interceptor_io.dart' as impl;

/// Selección en tiempo de compilación (no en runtime) entre la rama nativa
/// (`dart:io` disponible) y la rama Web (sin `dart:io`) — el patrón estándar
/// de "conditional import" de Dart. Necesario porque `cookie_jar`/
/// `path_provider` usan `dart:io`, que no compila para el target Web.
Future<Interceptor?> createCookieInterceptor() => impl.createCookieInterceptor();
