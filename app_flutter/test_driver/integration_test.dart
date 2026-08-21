import 'package:integration_test/integration_test_driver.dart';

/// Puente estándar del paquete `integration_test` para `flutter drive`.
/// Sin este archivo, `flutter drive --driver=test_driver/integration_test.dart`
/// no tiene con qué comunicarse; el contenido real de las pruebas vive en
/// `integration_test/*.dart` (ver `app_flutter/CLAUDE.md`, sección E2E).
Future<void> main() => integrationDriver();
