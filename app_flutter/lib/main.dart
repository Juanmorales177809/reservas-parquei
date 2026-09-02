import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_web_plugins/url_strategy.dart';

import 'app.dart';
import 'core/config/app_config.dart';
import 'core/config/supabase_config.dart';
import 'core/network/dio_client.dart';
import 'core/router/app_router.dart';
import 'core/router/app_routes.dart';
import 'core/storage/supabase_secure_storage.dart';
import 'features/auth/application/auth_provider.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // No-op fuera de Web. En Web, evita URLs con "#" (http://host/#/laboratorios)
  // para que las rutas limpias (http://host/laboratorios/3) funcionen al
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

  // Un link de invitación (o de recuperación de contraseña) trae el token
  // de sesión en la propia URL; `detectSessionInUri` (activo por defecto)
  // lo detecta al arrancar y dispara este evento con una sesión temporal
  // ya establecida -- Supabase trata invitación y recuperación igual del
  // lado del cliente, ambas como `passwordRecovery`. Redirige a la
  // pantalla donde la persona fija su contraseña real (ver
  // CompletarCuentaScreen); sin este listener el link no lleva a ningún
  // lado útil, aunque la URL de redirect esté bien configurada en
  // Supabase.
  Supabase.instance.client.auth.onAuthStateChange.listen((data) {
    if (data.event == AuthChangeEvent.passwordRecovery) {
      container.read(goRouterProvider).go(AppRoutes.completarCuenta);
    }
  });

  runApp(UncontrolledProviderScope(container: container, child: const ReservasApp()));
}
