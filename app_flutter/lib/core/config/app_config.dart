import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Entorno de ejecución de la app, resuelto vía `--dart-define-from-file`
/// (ver `env/*.json`). Nunca se hardcodea una URL de backend en código.
enum Environment { dev, prod }

class AppConfig {
  const AppConfig({required this.baseUrl, required this.environment});

  /// Fase 0: en Móvil/Escritorio apunta directo al backend
  /// (`http://localhost:8000`, o `http://10.0.2.2:8000` en el emulador
  /// Android). En Web, siempre debe ser una ruta relativa (`/api`) servida
  /// por el proxy same-origin de la Fase 6-Web — nunca una URL absoluta al
  /// backend, por el mismo motivo que hoy `frontend/CLAUDE.md` lo prohíbe
  /// en el cliente Next.js.
  final String baseUrl;
  final Environment environment;

  bool get isProduction => environment == Environment.prod;

  factory AppConfig.fromEnvironment() {
    const baseUrl = String.fromEnvironment(
      'BASE_URL',
      defaultValue: 'http://localhost:8000',
    );
    const environmentName = String.fromEnvironment(
      'ENVIRONMENT',
      defaultValue: 'dev',
    );
    return AppConfig(
      baseUrl: baseUrl,
      environment: environmentName == 'prod' ? Environment.prod : Environment.dev,
    );
  }
}

/// Se sobreescribe en `main()` con `AppConfig.fromEnvironment()` antes de
/// `runApp`. Lanza si algo intenta leerlo sin esa sobreescritura.
final appConfigProvider = Provider<AppConfig>((ref) {
  throw UnimplementedError('appConfigProvider debe sobreescribirse en main().');
});
