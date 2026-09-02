import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:app_flutter/core/domain/enums.dart';
import 'package:app_flutter/core/router/app_routes.dart';
import 'package:app_flutter/core/widgets/brand_mark.dart';
import 'package:app_flutter/features/auth/application/auth_provider.dart';
import 'package:app_flutter/features/auth/domain/auth_user.dart';
import 'package:app_flutter/features/espacios/application/espacios_providers.dart';
import 'package:app_flutter/features/laboratorios/application/laboratorios_providers.dart';
import 'package:app_flutter/features/laboratorios/domain/configuracion_laboratorio.dart';
import 'package:app_flutter/features/laboratorios/domain/laboratorio.dart';
import 'package:app_flutter/features/laboratorios/presentation/configuracion_laboratorio_screen.dart';
import 'package:app_flutter/features/laboratorios/presentation/laboratorio_detalle_screen.dart';
import 'package:app_flutter/features/recursos/application/recursos_providers.dart';
import 'package:app_flutter/shell/app_shell.dart';

/// Fase 6 (~/.claude/plans/dazzling-wobbling-zebra.md): entrar al detalle
/// de un laboratorio (o a la pantalla de configuración del gestor) hacía
/// desaparecer la barra de navegación, porque esas rutas vivían fuera del
/// `ShellRoute`. El fix las movió DENTRO del `ShellRoute` y les quitó su
/// `Scaffold`/`AppBar` propio para no duplicar el del shell activo.
///
/// Este test no monta el router real (evita tirar de la red a través de
/// `laboratorioProvider`/`espaciosGestionProvider` reales) -- monta
/// `AppShell` directamente con la pantalla como `child`, igual patrón que
/// `session_menu_test.dart`, y confirma que el chrome del shell (acá,
/// `NavigationBar` en ancho compacto) sigue presente alrededor.
class _AuthFalsa extends Auth {
  _AuthFalsa(this._user);

  final AuthUser? _user;

  @override
  Future<AuthUser?> build() async => _user;
}

const _gestor = AuthUser(
  id: 7,
  username: 'gestor_flutter',
  email: 'gestor_flutter@example.com',
  rol: RolUsuario.gestor,
  laboratorio: LaboratorioResumen(id: 1, nombre: 'Auditorio Principal', ubicacion: 'Bloque A'),
);

final _laboratorio = Laboratorio(
  id: 1,
  nombre: 'Auditorio Principal',
  ubicacion: 'Bloque A',
  capacidad: 50,
  estado: EstadoEntidad.activo,
  diasAtencion: const [0, 1, 2, 3, 4],
  horaApertura: '08:00:00',
  horaCierre: '18:00:00',
  horarioAtencion: const {'0': [8, 9, 10]},
  horasAntelacion: 0,
);

const _configuracion = ConfiguracionLaboratorio(
  laboratorioId: 1,
  laboratorioNombre: 'Auditorio Principal',
  diasAtencion: [0, 1, 2, 3, 4],
  horaApertura: '08:00:00',
  horaCierre: '18:00:00',
  horarioAtencion: {'0': [8, 9, 10]},
  horasAntelacion: 0,
  aprobacionAutomatica: false,
);

Future<void> _montar(WidgetTester tester, Widget pantalla, String currentPath, {double ancho = 375}) async {
  tester.view.physicalSize = Size(ancho, 900);
  tester.view.devicePixelRatio = 1.0;
  addTearDown(tester.view.reset);

  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        authProvider.overrideWith(() => _AuthFalsa(_gestor)),
        laboratorioProvider(1).overrideWith((ref) async => _laboratorio),
        recursosPorLaboratorioProvider(1).overrideWith((ref) => const []),
        espaciosGestionProvider.overrideWith((ref) async => []),
        configuracionLaboratorioGestionProvider.overrideWith((ref) async => _configuracion),
      ],
      child: MaterialApp(
        // `flutter test` no carga fuentes reales (ver
        // `configuracion_laboratorio_screen_test.dart`): el glifo de
        // reemplazo es más ancho que Inter y desborda la grilla de
        // `HorarioEditor`, que este test monta indirectamente al renderizar
        // `ConfiguracionLaboratorioScreen` completa -- mismo workaround ya
        // establecido ahí, no un cambio al widget de producción.
        builder: (context, child) => MediaQuery(
          data: MediaQuery.of(context).copyWith(textScaler: const TextScaler.linear(0.5)),
          child: child!,
        ),
        home: AppShell(currentPath: currentPath, child: pantalla),
      ),
    ),
  );
  await tester.pumpAndSettle();
}

void main() {
  testWidgets('el detalle de un laboratorio mantiene la barra de navegación visible', (tester) async {
    await _montar(
      tester,
      const LaboratorioDetalleScreen(laboratorioId: 1),
      AppRoutes.laboratorioDetalle(1),
    );

    // La barra de navegación del shell (BottomNavShell en este ancho) sigue
    // visible -- antes del fix, esta ruta vivía fuera del ShellRoute y
    // `NavigationBar` no aparecía en absoluto acá.
    expect(find.byType(NavigationBar), findsOneWidget);
    expect(find.byType(BrandMark), findsOneWidget);
    expect(find.text('Auditorio Principal'), findsWidgets);
    // El `SliverAppBar` de la pantalla de detalle sigue existiendo (es el
    // header con la imagen de fondo, no un `Scaffold`/`AppBar` propio que
    // compita con el del shell): coexiste con el `AppBar` del shell sin
    // que la pantalla haya vuelto a envolverse en su propio `Scaffold`.
    expect(find.byType(SliverAppBar), findsOneWidget);
  });

  testWidgets('la configuración del laboratorio mantiene la barra de navegación visible', (tester) async {
    // Ancho "medio" (RailNavShell): a 375px el `HorarioEditor` (grilla de
    // 112 celdas) desborda -- no es parte de lo que este test verifica
    // (persistencia del chrome del shell), así que se monta en un ancho
    // donde el contenido de la pantalla real entra sin desbordar.
    await _montar(
      tester,
      const ConfiguracionLaboratorioScreen(),
      AppRoutes.adminConfiguracion,
      ancho: 900,
    );

    // Antes del fix, esta ruta vivía fuera del ShellRoute y `NavigationRail`
    // no aparecía en absoluto acá.
    expect(find.byType(NavigationRail), findsOneWidget);
    expect(find.byType(BrandMark), findsOneWidget);
    expect(find.text('Configuración del laboratorio'), findsOneWidget);
    // Una sola AppBar en pantalla: la del shell -- esta pantalla ya no trae
    // la suya (era la causa de la duplicación).
    expect(find.byType(AppBar), findsOneWidget);
    expect(find.byType(BackButton), findsOneWidget);
  });
}
