import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:app_flutter/core/domain/enums.dart';
import 'package:app_flutter/features/auth/application/auth_provider.dart';
import 'package:app_flutter/features/auth/domain/auth_user.dart';
import 'package:app_flutter/features/laboratorios/domain/laboratorio.dart';
import 'package:app_flutter/features/recursos/application/recursos_providers.dart';
import 'package:app_flutter/features/recursos/domain/recurso.dart';
import 'package:app_flutter/features/recursos/domain/tipo_recurso.dart';
import 'package:app_flutter/features/recursos/presentation/gestion_recursos_screen.dart';

/// Búsqueda + tabla ordenable en `GestionRecursosScreen` (2026-08-31),
/// mismo patrón que `gestion_espacios_screen_test.dart`.
class _AuthFake extends Auth {
  _AuthFake(this._usuario);

  final AuthUser? _usuario;

  @override
  Future<AuthUser?> build() async => _usuario;
}

Laboratorio _laboratorio(int id, String nombre) => Laboratorio(
      id: id,
      nombre: nombre,
      ubicacion: 'Bloque $id',
      capacidad: 50,
      estado: EstadoEntidad.activo,
      diasAtencion: const [0, 1, 2, 3, 4],
      horaApertura: '08:00:00',
      horaCierre: '18:00:00',
      horarioAtencion: const {'0': [8, 9, 10]},
      horasAntelacion: 0,
    );

Recurso _recurso(int id, String nombre, {int laboratorioId = 1, String laboratorioNombre = 'Auditorio'}) => Recurso(
      id: id,
      nombre: nombre,
      laboratorioId: laboratorioId,
      tipoRecursoId: 1,
      capacidad: 1,
      estado: EstadoEntidad.activo,
      laboratorio: _laboratorio(laboratorioId, laboratorioNombre),
      tipo: const TipoRecurso(id: 1, nombre: 'Equipo', descripcion: '', activo: 'activo'),
      esPrestacionServicio: false,
    );

void main() {
  Future<void> montar(WidgetTester tester, List<Recurso> recursos) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authProvider.overrideWith(() => _AuthFake(AuthUser(id: 1, username: 'admin', email: 'admin@example.com', rol: RolUsuario.admin))),
          recursosGestionProvider.overrideWith((ref) async => recursos),
          tiposRecursosProvider.overrideWith(
            (ref) async => const [TipoRecurso(id: 1, nombre: 'Equipo', descripcion: '', activo: 'activo')],
          ),
        ],
        child: const MaterialApp(home: GestionRecursosScreen()),
      ),
    );
    await tester.pumpAndSettle();
  }

  group('GestionRecursosScreen — búsqueda y orden (2026-08-31)', () {
    testWidgets('buscar por nombre filtra la lista', (tester) async {
      await montar(tester, [_recurso(1, 'Proyector'), _recurso(2, 'Cámara')]);

      expect(find.text('Proyector'), findsOneWidget);
      expect(find.text('Cámara'), findsOneWidget);

      // "Proye" (no el nombre completo): si se buscara el texto exacto del
      // recurso, el propio TextField con ese valor también matchearía
      // find.text('Proyector'), dando un falso "2 widgets encontrados".
      await tester.enterText(find.byType(TextField), 'Proye');
      await tester.pumpAndSettle();

      expect(find.text('Proyector'), findsOneWidget);
      expect(find.text('Cámara'), findsNothing);
    });

    testWidgets('buscar por laboratorio también filtra', (tester) async {
      await montar(tester, [
        _recurso(1, 'Proyector', laboratorioId: 1, laboratorioNombre: 'Auditorio'),
        _recurso(2, 'Cámara', laboratorioId: 2, laboratorioNombre: 'Laboratorio'),
      ]);

      await tester.enterText(find.byType(TextField), 'Laboratorio');
      await tester.pumpAndSettle();

      expect(find.text('Cámara'), findsOneWidget);
      expect(find.text('Proyector'), findsNothing);
    });

    testWidgets('buscar algo que no matchea nada muestra el mensaje de sin resultados', (tester) async {
      await montar(tester, [_recurso(1, 'Proyector')]);

      await tester.enterText(find.byType(TextField), 'inexistente');
      await tester.pumpAndSettle();

      expect(find.textContaining('No se encontraron resultados'), findsOneWidget);
      expect(find.text('Proyector'), findsNothing);
    });

    testWidgets('tocar el header de una columna reordena las filas', (tester) async {
      await montar(tester, [_recurso(1, 'Zeta'), _recurso(2, 'Alfa')]);

      final zetaAntes = tester.getTopLeft(find.text('Zeta')).dy;
      final alfaAntes = tester.getTopLeft(find.text('Alfa')).dy;
      expect(zetaAntes, lessThan(alfaAntes));

      await tester.tap(find.text('NOMBRE'));
      await tester.pumpAndSettle();

      final zetaDespues = tester.getTopLeft(find.text('Zeta')).dy;
      final alfaDespues = tester.getTopLeft(find.text('Alfa')).dy;
      expect(alfaDespues, lessThan(zetaDespues));
    });
  });
}
