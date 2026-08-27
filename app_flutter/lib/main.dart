import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_web_plugins/url_strategy.dart';

import 'app.dart';
import 'core/config/app_config.dart';
import 'core/config/supabase_config.dart';
import 'core/network/dio_client.dart';
import 'core/storage/supabase_secure_storage.dart';
import 'features/auth/application/auth_provider.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // No-op fuera de Web. En Web, evita URLs con "#" (http://host/#/espacios)
  // para que las rutas limpias (http://host/espacios/3) funcionen al
  // compartirlas o recargar la página — depende de que el proxy same-origin
  // sirva index.html como fallback de SPA (ver Fase 6-Web).
  usePathUrlStrategy();

  final config = AppConfig.fromEnvironment();

  // Supabase Auth es el único mecanismo de autenticación (corte completo,
  // ver CLAUDE.md raíz): sin esto no hay forma de iniciar sesión, así que
  // se falla rápido y con un mensaje claro en vez de dejar que la app
  // arranque y recién falle en el primer intento de login.
  if (!SupabaseConfig.isConfigured) {
    throw StateError(
      'Falta configurar Supabase: SUPABASE_URL y SUPABASE_PUBLISHABLE_KEY '
      '(o SUPABASE_ANON_KEY) son obligatorias — ver env/*.json.',
    );
  }
  await Supabase.initialize(
    url: SupabaseConfig.url,
    publishableKey: SupabaseConfig.effectiveKey,
    authOptions: const FlutterAuthClientOptions(localStorage: SupabaseSecureStorage()),
  );

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
