import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:app_flutter/core/domain/enums.dart';
import 'package:app_flutter/core/network/api_exception.dart';
import 'package:app_flutter/features/auth/application/auth_provider.dart';
import 'package:app_flutter/features/auth/domain/auth_user.dart';
import 'package:app_flutter/features/laboratorios/application/laboratorios_providers.dart';
import 'package:app_flutter/features/laboratorios/domain/laboratorio.dart';
import 'package:app_flutter/features/recursos/application/recursos_providers.dart';
import 'package:app_flutter/features/recursos/domain/recurso.dart';
import 'package:app_flutter/features/recursos/domain/tipo_recurso.dart';
import 'package:app_flutter/features/espacios/application/espacios_providers.dart';
import 'package:app_flutter/features/espacios/data/espacios_repository.dart';
import 'package:app_flutter/features/espacios/domain/espacio.dart';
import 'package:app_flutter/features/espacios/presentation/gestion_espacios_screen.dart';

/// Sesión falsa: `Auth` es un `@riverpod class`, así que se sobreescribe
/// extendiéndolo y devolviendo el usuario ya resuelto en `build()`.
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

AuthUser _usuario(RolUsuario rol, {LaboratorioResumen? laboratorio}) => AuthUser(
      id: 1,
      username: rol.name,
      email: '${rol.name}@example.com',
      rol: rol,
      laboratorio: laboratorio,
    );

Future<void> _abrirFormularioNuevaEspacio(WidgetTester tester, AuthUser usuario) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        authProvider.overrideWith(() => _AuthFake(usuario)),
        // Sin espacios: el formulario es lo único bajo prueba.
        espaciosGestionProvider.overrideWith((ref) async => []),
        laboratoriosListProvider.overrideWith(
          (ref) async => [_laboratorio(1, 'Auditorio Principal'), _laboratorio(2, 'Laboratorio')],
        ),
      ],
      child: const MaterialApp(home: GestionEspaciosScreen()),
    ),
  );
  await tester.pumpAndSettle();

  await tester.tap(find.text('Nueva'));
  await tester.pumpAndSettle();
}

Espacio _espacio(int id, String nombre, {int laboratorioId = 1, List<int> recursoIds = const []}) => Espacio(
      id: id,
      nombre: nombre,
      laboratorioId: laboratorioId,
      estado: EstadoEntidad.activo,
      createdAt: '2026-01-01T00:00:00',
      updatedAt: '2026-01-01T00:00:00',
      createdBy: 1,
      updatedBy: 1,
      recursoIds: recursoIds,
    );

Recurso _recurso(int id, String nombre, {int laboratorioId = 1}) => Recurso(
      id: id,
      nombre: nombre,
      laboratorioId: laboratorioId,
      tipoRecursoId: 1,
      capacidad: 1,
      estado: EstadoEntidad.activo,
      laboratorio: _laboratorio(laboratorioId, 'Laboratorio $laboratorioId'),
      tipo: const TipoRecurso(id: 1, nombre: 'Equipo', descripcion: '', activo: 'activo'),
      esPrestacionServicio: false,
    );

/// Fake por subclase (mismo patrón que `_AuthRepositoryFalso` en otras
/// pantallas): `reemplazarRecursos` es lo único bajo prueba, así que se
/// reemplaza por un doble que nunca toca la red.
class _EspaciosRepositoryFalso extends EspaciosRepository {
  _EspaciosRepositoryFalso() : super(Dio());

  int? ultimaEspacioId;
  List<int>? ultimosRecursoIds;
  Object? errorParaLanzar;

  @override
  Future<List<int>> reemplazarRecursos(int espacioId, List<int> recursoIds) async {
    if (errorParaLanzar != null) throw errorParaLanzar!;
    ultimaEspacioId = espacioId;
    ultimosRecursoIds = recursoIds;
    return recursoIds;
  }
}

void main() {
  group('GestionEspaciosScreen — selector de laboratorio al crear una espacio', () {
    testWidgets('un gestor NO ve el selector: se usa su laboratorio asignado', (tester) async {
      await _abrirFormularioNuevaEspacio(
        tester,
        _usuario(
          RolUsuario.gestor,
          laboratorio: const LaboratorioResumen(id: 1, nombre: 'Auditorio Principal', ubicacion: 'Bloque 1'),
        ),
      );

      expect(find.text('Nuevo espacio'), findsOneWidget);
      // El bug original: aquí aparecía un desplegable con TODOS los
      // laboratorios, preseleccionado en `laboratorios.first` — que para un gestor
      // suele ser uno ajeno, y el backend respondía 403 al guardar.
      expect(find.text('Laboratorio *'), findsNothing);
      expect(find.text('Laboratorio'), findsNothing);
    });

    testWidgets('un admin SÍ ve el selector con todos los laboratorios', (tester) async {
      await _abrirFormularioNuevaEspacio(tester, _usuario(RolUsuario.admin));

      expect(find.text('Nuevo espacio'), findsOneWidget);
      expect(find.text('Laboratorio *'), findsOneWidget);
    });
  });

  group('GestionEspaciosScreen — recursos de una espacio', () {
    Future<_EspaciosRepositoryFalso> abrirDialogoRecursos(
      WidgetTester tester, {
      required List<int> recursoIdsIniciales,
      required List<Recurso> recursosDelLaboratorio,
    }) async {
      final fake = _EspaciosRepositoryFalso();
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            authProvider.overrideWith(() => _AuthFake(_usuario(RolUsuario.admin))),
            espaciosGestionProvider.overrideWith(
              (ref) async => [_espacio(1, 'Espacio A', recursoIds: recursoIdsIniciales)],
            ),
            espaciosRepositoryProvider.overrideWithValue(fake),
            recursosActivosProvider.overrideWith((ref) async => recursosDelLaboratorio),
            laboratoriosListProvider.overrideWith((ref) async => [_laboratorio(1, 'Lab')]),
          ],
          child: const MaterialApp(home: GestionEspaciosScreen()),
        ),
      );
      await tester.pumpAndSettle();

      // Búsqueda + tabla ordenable (2026-08-31): en pantalla ancha (el
      // tamaño de prueba por defecto ya supera kCompactBreakpoint) la
      // acción "Recursos" es un IconButton en la tabla, sin texto visible
      // -- se ubica por su tooltip en vez de por find.text. La tabla vive
      // en un `SingleChildScrollView` horizontal (Fase 5, columna
      // "LABORATORIO" más ancha que la vieja "ESPACIO"): a diferencia de
      // un usuario real, `tester.tap` no hace scroll solo, así que hay
      // que traer el botón a la vista antes de tocarlo.
      await tester.ensureVisible(find.byTooltip('Recursos'));
      await tester.pumpAndSettle();
      await tester.tap(find.byTooltip('Recursos'));
      await tester.pumpAndSettle();
      return fake;
    }

    testWidgets('precarga la selección actual de la espacio', (tester) async {
      await abrirDialogoRecursos(
        tester,
        recursoIdsIniciales: [1],
        recursosDelLaboratorio: [_recurso(1, 'Proyector'), _recurso(2, 'Cámara')],
      );

      expect(find.text('Recursos de Espacio A'), findsOneWidget);
      final checkboxes = tester.widgetList<CheckboxListTile>(find.byType(CheckboxListTile)).toList();
      expect(checkboxes.firstWhere((c) => (c.title as Text).data == 'Proyector').value, isTrue);
      expect(checkboxes.firstWhere((c) => (c.title as Text).data == 'Cámara').value, isFalse);
    });

    testWidgets('guardar llama a reemplazarRecursos con la selección actualizada', (tester) async {
      final fake = await abrirDialogoRecursos(
        tester,
        recursoIdsIniciales: [1],
        recursosDelLaboratorio: [_recurso(1, 'Proyector'), _recurso(2, 'Cámara')],
      );

      await tester.tap(find.text('Cámara'));
      await tester.tap(find.text('Guardar'));
      await tester.pumpAndSettle();

      expect(fake.ultimaEspacioId, 1);
      expect(fake.ultimosRecursoIds, unorderedEquals([1, 2]));
      expect(find.text('Recursos del espacio actualizados.'), findsOneWidget);
    });

    testWidgets('sin recursos en el laboratorio muestra el mensaje vacío', (tester) async {
      await abrirDialogoRecursos(tester, recursoIdsIniciales: [], recursosDelLaboratorio: []);

      expect(find.text('No hay recursos en este laboratorio.'), findsOneWidget);
    });

    testWidgets('muestra el error del backend si falla el guardado', (tester) async {
      final fake = await abrirDialogoRecursos(
        tester,
        recursoIdsIniciales: [],
        recursosDelLaboratorio: [_recurso(1, 'Proyector')],
      );
      fake.errorParaLanzar = const ApiException('Los recursos [1] ya pertenecen a otra espacio', statusCode: 409);

      await tester.tap(find.text('Proyector'));
      await tester.tap(find.text('Guardar'));
      await tester.pumpAndSettle();

      expect(find.text('Los recursos [1] ya pertenecen a otra espacio'), findsOneWidget);
    });
  });

  group('GestionEspaciosScreen — búsqueda y orden (2026-08-31)', () {
    Future<void> montar(WidgetTester tester, List<Espacio> espacios, List<Laboratorio> laboratorios) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            authProvider.overrideWith(() => _AuthFake(_usuario(RolUsuario.admin))),
            espaciosGestionProvider.overrideWith((ref) async => espacios),
            laboratoriosListProvider.overrideWith((ref) async => laboratorios),
          ],
          child: const MaterialApp(home: GestionEspaciosScreen()),
        ),
      );
      await tester.pumpAndSettle();
    }

    testWidgets('buscar por nombre filtra la lista', (tester) async {
      await montar(tester, [_espacio(1, 'Sala Norte'), _espacio(2, 'Sala Sur')], [_laboratorio(1, 'Auditorio')]);

      expect(find.text('Sala Norte'), findsOneWidget);
      expect(find.text('Sala Sur'), findsOneWidget);

      await tester.enterText(find.byType(TextField), 'Norte');
      await tester.pumpAndSettle();

      expect(find.text('Sala Norte'), findsOneWidget);
      expect(find.text('Sala Sur'), findsNothing);
    });

    testWidgets('buscar algo que no matchea nada muestra el mensaje de sin resultados', (tester) async {
      await montar(tester, [_espacio(1, 'Sala Norte')], [_laboratorio(1, 'Auditorio')]);

      await tester.enterText(find.byType(TextField), 'inexistente');
      await tester.pumpAndSettle();

      expect(find.textContaining('No se encontraron resultados'), findsOneWidget);
      expect(find.text('Sala Norte'), findsNothing);
    });

    testWidgets('tocar el header de una columna reordena las filas', (tester) async {
      await montar(tester, [_espacio(1, 'Zeta'), _espacio(2, 'Alfa')], [_laboratorio(1, 'Auditorio')]);

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
