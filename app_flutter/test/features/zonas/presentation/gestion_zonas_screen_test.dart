import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:app_flutter/core/domain/enums.dart';
import 'package:app_flutter/core/network/api_exception.dart';
import 'package:app_flutter/features/auth/application/auth_provider.dart';
import 'package:app_flutter/features/auth/domain/auth_user.dart';
import 'package:app_flutter/features/espacios/application/espacios_providers.dart';
import 'package:app_flutter/features/espacios/domain/espacio.dart';
import 'package:app_flutter/features/recursos/application/recursos_providers.dart';
import 'package:app_flutter/features/recursos/domain/recurso.dart';
import 'package:app_flutter/features/recursos/domain/tipo_recurso.dart';
import 'package:app_flutter/features/zonas/application/zonas_providers.dart';
import 'package:app_flutter/features/zonas/data/zonas_repository.dart';
import 'package:app_flutter/features/zonas/domain/zona.dart';
import 'package:app_flutter/features/zonas/presentation/gestion_zonas_screen.dart';

/// Sesión falsa: `Auth` es un `@riverpod class`, así que se sobreescribe
/// extendiéndolo y devolviendo el usuario ya resuelto en `build()`.
class _AuthFake extends Auth {
  _AuthFake(this._usuario);

  final AuthUser? _usuario;

  @override
  Future<AuthUser?> build() async => _usuario;
}

Espacio _espacio(int id, String nombre) => Espacio(
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
      modalidadReserva: ModalidadEspacio.zonas,
    );

AuthUser _usuario(RolUsuario rol, {EspacioResumen? espacio}) => AuthUser(
      id: 1,
      username: rol.name,
      email: '${rol.name}@example.com',
      rol: rol,
      espacio: espacio,
    );

Future<void> _abrirFormularioNuevaZona(WidgetTester tester, AuthUser usuario) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        authProvider.overrideWith(() => _AuthFake(usuario)),
        // Sin zonas: el formulario es lo único bajo prueba.
        zonasGestionProvider.overrideWith((ref) async => []),
        espaciosListProvider.overrideWith(
          (ref) async => [_espacio(1, 'Auditorio Principal'), _espacio(2, 'Laboratorio')],
        ),
      ],
      child: const MaterialApp(home: GestionZonasScreen()),
    ),
  );
  await tester.pumpAndSettle();

  await tester.tap(find.text('Nueva'));
  await tester.pumpAndSettle();
}

Zona _zona(int id, String nombre, {int espacioId = 1, List<int> recursoIds = const []}) => Zona(
      id: id,
      nombre: nombre,
      espacioId: espacioId,
      estado: EstadoEntidad.activo,
      createdAt: '2026-01-01T00:00:00',
      updatedAt: '2026-01-01T00:00:00',
      createdBy: 1,
      updatedBy: 1,
      recursoIds: recursoIds,
    );

Recurso _recurso(int id, String nombre, {int espacioId = 1}) => Recurso(
      id: id,
      nombre: nombre,
      espacioId: espacioId,
      tipoRecursoId: 1,
      capacidad: 1,
      estado: EstadoEntidad.activo,
      espacio: _espacio(espacioId, 'Espacio $espacioId'),
      tipo: const TipoRecurso(id: 1, nombre: 'Equipo', descripcion: '', activo: 'activo'),
      esPrestacionServicio: false,
    );

/// Fake por subclase (mismo patrón que `_AuthRepositoryFalso` en otras
/// pantallas): `reemplazarRecursos` es lo único bajo prueba, así que se
/// reemplaza por un doble que nunca toca la red.
class _ZonasRepositoryFalso extends ZonasRepository {
  _ZonasRepositoryFalso() : super(Dio());

  int? ultimaZonaId;
  List<int>? ultimosRecursoIds;
  Object? errorParaLanzar;

  @override
  Future<List<int>> reemplazarRecursos(int zonaId, List<int> recursoIds) async {
    if (errorParaLanzar != null) throw errorParaLanzar!;
    ultimaZonaId = zonaId;
    ultimosRecursoIds = recursoIds;
    return recursoIds;
  }
}

void main() {
  group('GestionZonasScreen — selector de espacio al crear una zona', () {
    testWidgets('un gestor NO ve el selector: se usa su espacio asignado', (tester) async {
      await _abrirFormularioNuevaZona(
        tester,
        _usuario(
          RolUsuario.gestor,
          espacio: const EspacioResumen(id: 1, nombre: 'Auditorio Principal', ubicacion: 'Bloque 1'),
        ),
      );

      expect(find.text('Nueva zona'), findsOneWidget);
      // El bug original: aquí aparecía un desplegable con TODOS los
      // espacios, preseleccionado en `espacios.first` — que para un gestor
      // suele ser uno ajeno, y el backend respondía 403 al guardar.
      expect(find.text('Espacio *'), findsNothing);
      expect(find.text('Laboratorio'), findsNothing);
    });

    testWidgets('un admin SÍ ve el selector con todos los espacios', (tester) async {
      await _abrirFormularioNuevaZona(tester, _usuario(RolUsuario.admin));

      expect(find.text('Nueva zona'), findsOneWidget);
      expect(find.text('Espacio *'), findsOneWidget);
    });
  });

  group('GestionZonasScreen — recursos de una zona', () {
    Future<_ZonasRepositoryFalso> abrirDialogoRecursos(
      WidgetTester tester, {
      required List<int> recursoIdsIniciales,
      required List<Recurso> recursosDelEspacio,
    }) async {
      final fake = _ZonasRepositoryFalso();
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            authProvider.overrideWith(() => _AuthFake(_usuario(RolUsuario.admin))),
            zonasGestionProvider.overrideWith(
              (ref) async => [_zona(1, 'Zona A', recursoIds: recursoIdsIniciales)],
            ),
            zonasRepositoryProvider.overrideWithValue(fake),
            recursosActivosProvider.overrideWith((ref) async => recursosDelEspacio),
          ],
          child: const MaterialApp(home: GestionZonasScreen()),
        ),
      );
      await tester.pumpAndSettle();

      await tester.tap(find.text('Recursos'));
      await tester.pumpAndSettle();
      return fake;
    }

    testWidgets('precarga la selección actual de la zona', (tester) async {
      await abrirDialogoRecursos(
        tester,
        recursoIdsIniciales: [1],
        recursosDelEspacio: [_recurso(1, 'Proyector'), _recurso(2, 'Cámara')],
      );

      expect(find.text('Recursos de Zona A'), findsOneWidget);
      final checkboxes = tester.widgetList<CheckboxListTile>(find.byType(CheckboxListTile)).toList();
      expect(checkboxes.firstWhere((c) => (c.title as Text).data == 'Proyector').value, isTrue);
      expect(checkboxes.firstWhere((c) => (c.title as Text).data == 'Cámara').value, isFalse);
    });

    testWidgets('guardar llama a reemplazarRecursos con la selección actualizada', (tester) async {
      final fake = await abrirDialogoRecursos(
        tester,
        recursoIdsIniciales: [1],
        recursosDelEspacio: [_recurso(1, 'Proyector'), _recurso(2, 'Cámara')],
      );

      await tester.tap(find.text('Cámara'));
      await tester.tap(find.text('Guardar'));
      await tester.pumpAndSettle();

      expect(fake.ultimaZonaId, 1);
      expect(fake.ultimosRecursoIds, unorderedEquals([1, 2]));
      expect(find.text('Recursos de la zona actualizados.'), findsOneWidget);
    });

    testWidgets('sin recursos en el espacio muestra el mensaje vacío', (tester) async {
      await abrirDialogoRecursos(tester, recursoIdsIniciales: [], recursosDelEspacio: []);

      expect(find.text('No hay recursos en este espacio.'), findsOneWidget);
    });

    testWidgets('muestra el error del backend si falla el guardado', (tester) async {
      final fake = await abrirDialogoRecursos(
        tester,
        recursoIdsIniciales: [],
        recursosDelEspacio: [_recurso(1, 'Proyector')],
      );
      fake.errorParaLanzar = const ApiException('Los recursos [1] ya pertenecen a otra zona', statusCode: 409);

      await tester.tap(find.text('Proyector'));
      await tester.tap(find.text('Guardar'));
      await tester.pumpAndSettle();

      expect(find.text('Los recursos [1] ya pertenecen a otra zona'), findsOneWidget);
    });
  });
}
