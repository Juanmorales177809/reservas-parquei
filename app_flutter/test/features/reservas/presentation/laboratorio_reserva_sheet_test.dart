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
import 'package:app_flutter/features/reservas/presentation/laboratorio_reserva_sheet.dart';
import 'package:app_flutter/features/espacios/application/espacios_providers.dart';
import 'package:app_flutter/features/espacios/domain/espacio.dart';

class _AuthFake extends Auth {
  _AuthFake(this._usuario);
  final AuthUser? _usuario;
  @override
  Future<AuthUser?> build() async => _usuario;
}

AuthUser _usuario(RolUsuario rol, {LaboratorioResumen? laboratorio}) => AuthUser(
      id: 1,
      username: rol.name,
      email: '${rol.name}@example.com',
      rol: rol,
      laboratorio: laboratorio,
    );

Laboratorio _laboratorio(int id) => Laboratorio(
      id: id,
      nombre: 'Laboratorio $id',
      ubicacion: 'Bloque $id',
      capacidad: 20,
      estado: EstadoEntidad.activo,
      diasAtencion: const [0, 1, 2, 3, 4],
      horaApertura: '08:00:00',
      horaCierre: '18:00:00',
      horarioAtencion: const {'0': [8, 9, 10]},
      horasAntelacion: 0,
    );

Espacio _espacio(int id, String nombre, {int laboratorioId = 1, List<int> recursoIds = const [], String? descripcion, int? capacidad}) => Espacio(
      id: id,
      nombre: nombre,
      laboratorioId: laboratorioId,
      descripcion: descripcion,
      capacidad: capacidad,
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
      capacidad: 5,
      estado: EstadoEntidad.activo,
      laboratorio: _laboratorio(laboratorioId),
      tipo: const TipoRecurso(id: 1, nombre: 'Equipo', descripcion: '', activo: 'activo'),
      esPrestacionServicio: false,
    );

Widget _montarSheet({
  required Laboratorio laboratorio,
  required List<Recurso> recursos,
  required List<Espacio> espacios,
  AuthUser? usuario,
}) {
  return ProviderScope(
    overrides: [
      authProvider.overrideWith(() => _AuthFake(usuario)),
      recursosActivosProvider.overrideWith((ref) async => recursos),
      espaciosGestionProvider.overrideWith((ref) async => espacios),
    ],
    child: MaterialApp(
      home: Scaffold(
        body: SingleChildScrollView(child: LaboratorioReservaSheet(laboratorio: laboratorio)),
      ),
    ),
  );
}

void main() {
  group('LaboratorioReservaSheet — Feature A: agrupación visual', () {
    testWidgets('con espacios y equipos propios muestra ambos encabezados agrupados', (tester) async {
      final laboratorio = _laboratorio(1);
      await tester.pumpWidget(
        _montarSheet(
          laboratorio: laboratorio,
          recursos: [_recurso(1, 'Proyector')],
          espacios: [_espacio(10, 'Espacio A', recursoIds: [1])],
          usuario: _usuario(RolUsuario.usuario),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('ZONAS — INCLUYE SUS EQUIPOS'), findsOneWidget);
      // Con espacios Y recursos propios, el segundo grupo es "adicionales"
      expect(find.text('EQUIPOS ADICIONALES DE ESTE LABORATORIO'), findsOneWidget);
      expect(
        find.text('Elegí el espacio donde vas a trabajar. Los equipos asignados a ese espacio ya están incluidos en tu reserva.'),
        findsOneWidget,
      );
    });

    testWidgets('espacio muestra qué equipos incluye en el subtítulo', (tester) async {
      final laboratorio = _laboratorio(1);
      final recursos = [_recurso(1, 'Proyector'), _recurso(2, 'Cámara')];
      final espacios = [_espacio(10, 'Estudio 5.1', recursoIds: [1, 2], descripcion: 'Sala de mezcla')];
      await tester.pumpWidget(
        _montarSheet(laboratorio: laboratorio, recursos: recursos, espacios: espacios, usuario: _usuario(RolUsuario.usuario)),
      );
      await tester.pumpAndSettle();

      expect(find.text('Estudio 5.1'), findsOneWidget);
      expect(find.textContaining('Incluye: Proyector, Cámara'), findsOneWidget);
      expect(find.textContaining('Sala de mezcla'), findsOneWidget);
    });

    testWidgets('espacio sin equipos muestra "Sin equipos asignados"', (tester) async {
      final laboratorio = _laboratorio(1);
      await tester.pumpWidget(
        _montarSheet(
          laboratorio: laboratorio,
          recursos: [],
          espacios: [_espacio(10, 'Espacio Vacía', recursoIds: [])],
          usuario: _usuario(RolUsuario.usuario),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.textContaining('Sin equipos asignados'), findsOneWidget);
    });

    testWidgets('sin espacios definidas no muestra la sección de espacios', (tester) async {
      final laboratorio = _laboratorio(1);
      await tester.pumpWidget(
        _montarSheet(
          laboratorio: laboratorio,
          recursos: [_recurso(1, 'Micrófono')],
          espacios: const [],
          usuario: _usuario(RolUsuario.usuario),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('ZONAS — INCLUYE SUS EQUIPOS'), findsNothing);
      expect(find.text('EQUIPOS DE ESTE LABORATORIO'), findsOneWidget);
      expect(find.text('EQUIPOS ADICIONALES DE ESTE LABORATORIO'), findsNothing);
      expect(find.text('Micrófono'), findsOneWidget);
    });

    testWidgets('recurso cubierto por espacio seleccionada aparece como Incluido y deshabilitado', (tester) async {
      final laboratorio = _laboratorio(1);
      final recursos = [_recurso(1, 'Proyector'), _recurso(2, 'Cámara')];
      final espacios = [_espacio(10, 'Espacio A', recursoIds: [1])];
      await tester.pumpWidget(
        _montarSheet(laboratorio: laboratorio, recursos: recursos, espacios: espacios, usuario: _usuario(RolUsuario.usuario)),
      );
      await tester.pumpAndSettle();

      // Al inicio, ambos recursos son seleccionables (checkbox habilitado, sin "Incluido")
      expect(find.text('Proyector'), findsOneWidget);
      expect(find.textContaining('Incluido en espacio'), findsNothing);

      // Marcar la espacio que cubre Proyector
      await tester.tap(find.text('Espacio A'));
      await tester.pumpAndSettle();

      // Ahora Proyector debe aparecer como incluido y deshabilitado
      expect(find.textContaining('Incluido en espacio Espacio A'), findsOneWidget);
      // Cámara sigue seleccionable, sin etiqueta de incluido
      expect(find.text('Cámara'), findsOneWidget);
      // El hint explicativo aparece cuando hay cubiertos
      expect(find.textContaining('ya vienen con el espacio seleccionado'), findsOneWidget);

      // Desmarcar la espacio → vuelve a ser seleccionable normal
      await tester.tap(find.text('Espacio A'));
      await tester.pumpAndSettle();
      expect(find.textContaining('Incluido en espacio'), findsNothing);
    });

    testWidgets('cubierto aparece tildado y se puede destildar (editable al reservar)', (tester) async {
      final laboratorio = _laboratorio(1);
      final recursos = [_recurso(1, 'Proyector')];
      final espacios = [_espacio(10, 'Espacio A', recursoIds: [1])];
      await tester.pumpWidget(
        _montarSheet(laboratorio: laboratorio, recursos: recursos, espacios: espacios, usuario: _usuario(RolUsuario.usuario)),
      );
      await tester.pumpAndSettle();

      await tester.tap(find.text('Espacio A'));
      await tester.pumpAndSettle();

      final tileCubierto = tester.widgetList<CheckboxListTile>(find.byType(CheckboxListTile)).firstWhere(
            (w) => (w.title as Text).data == 'Proyector',
          );
      expect(tileCubierto.value, isTrue);
      expect(tileCubierto.onChanged, isNotNull);
      // Destildar debe ser posible (requisito: recursos de espacio editables)
      await tester.tap(find.byWidget(tileCubierto));
      await tester.pumpAndSettle();
      final tileDespues = tester.widgetList<CheckboxListTile>(find.byType(CheckboxListTile)).firstWhere(
            (w) => (w.title as Text).data == 'Proyector',
          );
      expect(tileDespues.value, isFalse);
    });

    testWidgets('recurso cubierto por múltiples espacios lista todas las espacios que lo cubren', (tester) async {
      final laboratorio = _laboratorio(1);
      final recursos = [_recurso(1, 'Proyector')];
      final espacios = [
        _espacio(10, 'Espacio A', recursoIds: [1]),
        _espacio(11, 'Espacio B', recursoIds: [1]),
      ];
      await tester.pumpWidget(
        _montarSheet(laboratorio: laboratorio, recursos: recursos, espacios: espacios, usuario: _usuario(RolUsuario.usuario)),
      );
      await tester.pumpAndSettle();

      await tester.tap(find.text('Espacio A'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Espacio B'));
      await tester.pumpAndSettle();

      // Debe decir "espacios Espacio A, Espacio B" en plural
      expect(find.textContaining('espacios Espacio A, Espacio B'), findsOneWidget);
    });
  });
}
