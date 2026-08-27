import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:app_flutter/core/domain/enums.dart';
import 'package:app_flutter/features/auth/application/auth_provider.dart';
import 'package:app_flutter/features/auth/domain/auth_user.dart';
import 'package:app_flutter/features/espacios/domain/espacio.dart';
import 'package:app_flutter/features/recursos/application/recursos_providers.dart';
import 'package:app_flutter/features/recursos/domain/recurso.dart';
import 'package:app_flutter/features/recursos/domain/tipo_recurso.dart';
import 'package:app_flutter/features/reservas/presentation/espacio_reserva_sheet.dart';
import 'package:app_flutter/features/zonas/application/zonas_providers.dart';
import 'package:app_flutter/features/zonas/domain/zona.dart';

class _AuthFake extends Auth {
  _AuthFake(this._usuario);
  final AuthUser? _usuario;
  @override
  Future<AuthUser?> build() async => _usuario;
}

AuthUser _usuario(RolUsuario rol, {EspacioResumen? espacio}) => AuthUser(
      id: 1,
      username: rol.name,
      email: '${rol.name}@example.com',
      rol: rol,
      espacio: espacio,
    );

Espacio _espacio(int id, ModalidadEspacio modalidad) => Espacio(
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
      modalidadReserva: modalidad,
    );

Zona _zona(int id, String nombre, {int espacioId = 1, List<int> recursoIds = const [], String? descripcion, int? capacidad}) => Zona(
      id: id,
      nombre: nombre,
      espacioId: espacioId,
      descripcion: descripcion,
      capacidad: capacidad,
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
      capacidad: 5,
      estado: EstadoEntidad.activo,
      espacio: _espacio(espacioId, ModalidadEspacio.equipos),
      tipo: const TipoRecurso(id: 1, nombre: 'Equipo', descripcion: '', activo: 'activo'),
      esPrestacionServicio: false,
    );

Widget _montarSheet({
  required Espacio espacio,
  required List<Recurso> recursos,
  required List<Zona> zonas,
  AuthUser? usuario,
}) {
  return ProviderScope(
    overrides: [
      authProvider.overrideWith(() => _AuthFake(usuario)),
      recursosActivosProvider.overrideWith((ref) async => recursos),
      zonasGestionProvider.overrideWith((ref) async => zonas),
      // ensayosGestion por defecto vacío para no romper el expand de ensayos
      // ref.watch(ensayosGestionProvider) dentro del sheet se evalúa por zona,
      // pero si no lo sobreescribimos devuelve un Future que intenta ir a la red.
      // Lo dejamos sin override: no se usa si _zonaIds está vacío al inicio.
    ],
    child: MaterialApp(
      home: Scaffold(
        body: SingleChildScrollView(child: EspacioReservaSheet(espacio: espacio)),
      ),
    ),
  );
}

void main() {
  group('EspacioReservaSheet — Feature A: agrupación visual', () {
    testWidgets('modalidad mixto muestra ambos encabezados agrupados', (tester) async {
      final espacio = _espacio(1, ModalidadEspacio.mixto);
      await tester.pumpWidget(
        _montarSheet(
          espacio: espacio,
          recursos: [_recurso(1, 'Proyector')],
          zonas: [_zona(10, 'Zona A', recursoIds: [1])],
          usuario: _usuario(RolUsuario.usuario),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('ZONAS — INCLUYE SUS EQUIPOS'), findsOneWidget);
      // En mixto con zonas, el segundo grupo es "adicionales"
      expect(find.text('EQUIPOS ADICIONALES DE ESTE LABORATORIO'), findsOneWidget);
      expect(
        find.text('Elegí la zona donde vas a trabajar. Los equipos asignados a esa zona ya están incluidos en tu reserva.'),
        findsOneWidget,
      );
    });

    testWidgets('zona muestra qué equipos incluye en el subtítulo', (tester) async {
      final espacio = _espacio(1, ModalidadEspacio.mixto);
      final recursos = [_recurso(1, 'Proyector'), _recurso(2, 'Cámara')];
      final zonas = [_zona(10, 'Estudio 5.1', recursoIds: [1, 2], descripcion: 'Sala de mezcla')];
      await tester.pumpWidget(
        _montarSheet(espacio: espacio, recursos: recursos, zonas: zonas, usuario: _usuario(RolUsuario.usuario)),
      );
      await tester.pumpAndSettle();

      expect(find.text('Estudio 5.1'), findsOneWidget);
      expect(find.textContaining('Incluye: Proyector, Cámara'), findsOneWidget);
      expect(find.textContaining('Sala de mezcla'), findsOneWidget);
    });

    testWidgets('zona sin equipos muestra "Sin equipos asignados"', (tester) async {
      final espacio = _espacio(1, ModalidadEspacio.zonas);
      await tester.pumpWidget(
        _montarSheet(
          espacio: espacio,
          recursos: [],
          zonas: [_zona(10, 'Zona Vacía', recursoIds: [])],
          usuario: _usuario(RolUsuario.usuario),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.textContaining('Sin equipos asignados'), findsOneWidget);
    });

    testWidgets('modalidad equipos solo muestra equipos, sin zonas', (tester) async {
      final espacio = _espacio(1, ModalidadEspacio.equipos);
      await tester.pumpWidget(
        _montarSheet(
          espacio: espacio,
          recursos: [_recurso(1, 'Micrófono')],
          zonas: [_zona(10, 'Zona A', recursoIds: [1])],
          usuario: _usuario(RolUsuario.usuario),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('ZONAS — INCLUYE SUS EQUIPOS'), findsNothing);
      expect(find.text('EQUIPOS DE ESTE LABORATORIO'), findsOneWidget);
      expect(find.text('EQUIPOS ADICIONALES DE ESTE LABORATORIO'), findsNothing);
      expect(find.text('Micrófono'), findsOneWidget);
    });

    testWidgets('recurso cubierto por zona seleccionada aparece como Incluido y deshabilitado', (tester) async {
      final espacio = _espacio(1, ModalidadEspacio.mixto);
      final recursos = [_recurso(1, 'Proyector'), _recurso(2, 'Cámara')];
      final zonas = [_zona(10, 'Zona A', recursoIds: [1])];
      await tester.pumpWidget(
        _montarSheet(espacio: espacio, recursos: recursos, zonas: zonas, usuario: _usuario(RolUsuario.usuario)),
      );
      await tester.pumpAndSettle();

      // Al inicio, ambos recursos son seleccionables (checkbox habilitado, sin "Incluido")
      expect(find.text('Proyector'), findsOneWidget);
      expect(find.textContaining('Incluido en zona'), findsNothing);

      // Marcar la zona que cubre Proyector
      await tester.tap(find.text('Zona A'));
      await tester.pumpAndSettle();

      // Ahora Proyector debe aparecer como incluido y deshabilitado
      expect(find.textContaining('Incluido en zona Zona A'), findsOneWidget);
      // Cámara sigue seleccionable, sin etiqueta de incluido
      expect(find.text('Cámara'), findsOneWidget);
      // El hint explicativo aparece cuando hay cubiertos
      expect(find.textContaining('ya vienen con la zona seleccionada'), findsOneWidget);

      // Desmarcar la zona → vuelve a ser seleccionable normal
      await tester.tap(find.text('Zona A'));
      await tester.pumpAndSettle();
      expect(find.textContaining('Incluido en zona'), findsNothing);
    });

    testWidgets('no sugiere marcar dos veces: cubierto aparece tildado y no se puede destildar', (tester) async {
      final espacio = _espacio(1, ModalidadEspacio.mixto);
      final recursos = [_recurso(1, 'Proyector')];
      final zonas = [_zona(10, 'Zona A', recursoIds: [1])];
      await tester.pumpWidget(
        _montarSheet(espacio: espacio, recursos: recursos, zonas: zonas, usuario: _usuario(RolUsuario.usuario)),
      );
      await tester.pumpAndSettle();

      await tester.tap(find.text('Zona A'));
      await tester.pumpAndSettle();

      final tileCubierto = tester.widgetList<CheckboxListTile>(find.byType(CheckboxListTile)).firstWhere(
            (w) => (w.title as Text).data == 'Proyector',
          );
      expect(tileCubierto.value, isTrue);
      expect(tileCubierto.onChanged, isNull);
    });

    testWidgets('recurso cubierto por múltiples zonas lista todas las zonas que lo cubren', (tester) async {
      final espacio = _espacio(1, ModalidadEspacio.mixto);
      final recursos = [_recurso(1, 'Proyector')];
      final zonas = [
        _zona(10, 'Zona A', recursoIds: [1]),
        _zona(11, 'Zona B', recursoIds: [1]),
      ];
      await tester.pumpWidget(
        _montarSheet(espacio: espacio, recursos: recursos, zonas: zonas, usuario: _usuario(RolUsuario.usuario)),
      );
      await tester.pumpAndSettle();

      await tester.tap(find.text('Zona A'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Zona B'));
      await tester.pumpAndSettle();

      // Debe decir "zonas Zona A, Zona B" en plural
      expect(find.textContaining('zonas Zona A, Zona B'), findsOneWidget);
    });
  });
}
