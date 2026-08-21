import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_web_plugins/url_strategy.dart';

import 'app.dart';
import 'core/config/app_config.dart';
import 'core/network/dio_client.dart';
import 'features/auth/application/auth_provider.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // No-op fuera de Web. En Web, evita URLs con "#" (http://host/#/espacios)
  // para que las rutas limpias (http://host/espacios/3) funcionen al
  // compartirlas o recargar la página — depende de que el proxy same-origin
  // sirva index.html como fallback de SPA (ver Fase 6-Web).
  usePathUrlStrategy();

  final config = AppConfig.fromEnvironment();

  // `late final container`: buildDioClient necesita el callback de sesión
  // expirada antes de que exista el ProviderContainer, pero el callback
  // solo se invoca más tarde (ante un 401 real), nunca durante la
  // construcción síncrona de abajo — así que la referencia diferida es
  // segura.
  late final ProviderContainer container;
  final dio = await buildDioClient(
    config,
    onSessionExpired: () => container.read(authProvider.notifier).handleSessionExpired(),
  );

  container = ProviderContainer(
    overrides: [
      appConfigProvider.overrideWithValue(config),
      dioProvider.overrideWithValue(dio),
    ],
  );

  runApp(UncontrolledProviderScope(container: container, child: const ReservasApp()));
}
