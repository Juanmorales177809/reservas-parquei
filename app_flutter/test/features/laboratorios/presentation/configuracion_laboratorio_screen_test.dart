import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:app_flutter/features/laboratorios/application/laboratorios_providers.dart';
import 'package:app_flutter/features/laboratorios/domain/configuracion_laboratorio.dart';
import 'package:app_flutter/features/laboratorios/presentation/configuracion_laboratorio_screen.dart';

const _config = ConfiguracionLaboratorio(
  laboratorioId: 1,
  laboratorioNombre: 'Auditorio Pequeño',
  diasAtencion: [0, 1, 2, 3, 4, 5],
  horaApertura: '07:00:00',
  horaCierre: '20:00:00',
  horarioAtencion: {
    '0': [7, 8, 9],
    // Domingo con TODAS las franjas que muestra el editor (06:00–22:00):
    // así tocar el encabezado "DOM" lo vacía, que es exactamente el caso
    // reportado en producción ("Se vació el Dom" clavado en pantalla).
    '6': [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21],
  },
  horasAntelacion: 24,
  aprobacionAutomatica: false,
  notificarPorCorreo: true,
);

Future<void> _abrirConfiguracion(WidgetTester tester) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        configuracionLaboratorioGestionProvider.overrideWith((ref) async => _config),
      ],
      child: MaterialApp(
        // `flutter test` no carga fuentes reales: usa una de reemplazo donde
        // cada glifo mide exactamente el tamaño de fuente, así que
        // "06:00–07:00" ocupa ~121px donde Inter ocupa ~60 y desborda la
        // columna de 112px del editor. Es un artefacto del entorno de test,
        // no un bug de layout (en la app real esa columna entra sobrada);
        // se compensa achicando el texto solo acá, en vez de deformar el
        // widget de producción para complacer al test.
        builder: (context, child) => MediaQuery(
          data: MediaQuery.of(context).copyWith(textScaler: const TextScaler.linear(0.5)),
          child: child!,
        ),
        home: const ConfiguracionLaboratorioScreen(),
      ),
    ),
  );
  await tester.pumpAndSettle();
}

void main() {
  group('ConfiguracionLaboratorioScreen — SnackBar de "Deshacer"', () {
    // Regresión de un bug REAL de producción: el aviso "Se vació el Dom"
    // quedaba clavado en pantalla indefinidamente. La causa no era el
    // `duration` ni la forma de reemplazar el snackbar anterior, sino que
    // un `SnackBar` con `action` toma `persist = true` por defecto
    // (`snack_bar.dart`: `persist = persist ?? action != null`), y un
    // snackbar que persiste NUNCA se auto-cierra: el timer se dispara, ve
    // `persist`, y retorna sin cerrarlo. Este test falla si alguien quita
    // el `persist: false`.
    testWidgets('se cierra solo al vencer su duración', (tester) async {
      await _abrirConfiguracion(tester);

      // Vaciar la columna del domingo (tiene horas activas en la fixture):
      // es una operación masiva, así que ofrece "Deshacer".
      await tester.tap(find.text('DOM'));
      await tester.pumpAndSettle();

      expect(find.text('Se vació el Dom'), findsOneWidget);
      expect(find.text('Deshacer'), findsOneWidget);

      // Más allá de los 8s de `duration` que fija la pantalla.
      await tester.pump(const Duration(seconds: 9));
      await tester.pumpAndSettle();

      expect(
        find.text('Se vació el Dom'),
        findsNothing,
        reason: 'El SnackBar debe auto-cerrarse; con `persist` por defecto queda para siempre.',
      );
    });

    testWidgets('"Deshacer" revierte la operación masiva', (tester) async {
      await _abrirConfiguracion(tester);

      await tester.tap(find.text('DOM'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Deshacer'));
      await tester.pumpAndSettle();

      // Si el undo funciona, volver a tocar el encabezado vuelve a
      // ofrecer "vaciar" (y no "activar todo"), porque el domingo
      // recuperó las horas que la fixture traía.
      await tester.tap(find.text('DOM'));
      await tester.pumpAndSettle();
      expect(find.text('Se vació el Dom'), findsOneWidget);
    });
  });
}
