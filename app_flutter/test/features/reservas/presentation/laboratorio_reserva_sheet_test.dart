import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:app_flutter/core/domain/enums.dart';
import 'package:app_flutter/features/auth/application/auth_provider.dart';
import 'package:app_flutter/features/auth/domain/auth_user.dart';
import 'package:app_flutter/features/laboratorios/domain/disponibilidad_slot.dart';
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

Recurso _recurso(int id, String nombre, {int laboratorioId = 1, bool requiereApoyoAuxiliar = false}) => Recurso(
      id: id,
      nombre: nombre,
      laboratorioId: laboratorioId,
      tipoRecursoId: 1,
      capacidad: 5,
      estado: EstadoEntidad.activo,
      laboratorio: _laboratorio(laboratorioId),
      tipo: const TipoRecurso(id: 1, nombre: 'Equipo', descripcion: '', activo: 'activo'),
      esPrestacionServicio: false,
      requiereApoyoAuxiliar: requiereApoyoAuxiliar,
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

  group('LaboratorioReservaSheet — acompañamiento obligatorio del auxiliar', () {
    testWidgets('recurso directo con requiereApoyoAuxiliar fuerza el toggle y lo deshabilita', (tester) async {
      final laboratorio = _laboratorio(1);
      final recursos = [_recurso(1, 'Torno CNC', requiereApoyoAuxiliar: true)];
      await tester.pumpWidget(
        _montarSheet(laboratorio: laboratorio, recursos: recursos, espacios: const [], usuario: _usuario(RolUsuario.usuario)),
      );
      await tester.pumpAndSettle();

      await tester.tap(find.text('Torno CNC'));
      await tester.pumpAndSettle();

      final toggle = tester.widget<SwitchListTile>(find.byType(SwitchListTile));
      expect(toggle.value, isTrue);
      expect(toggle.onChanged, isNull);
      expect(find.textContaining('exige acompañamiento del auxiliar'), findsOneWidget);
    });

    testWidgets('recurso cubierto por un espacio con requiereApoyoAuxiliar también fuerza el toggle', (tester) async {
      final laboratorio = _laboratorio(1);
      final recursos = [_recurso(1, 'Consola de mezcla', requiereApoyoAuxiliar: true)];
      final espacios = [_espacio(10, 'Estudio', recursoIds: [1])];
      await tester.pumpWidget(
        _montarSheet(laboratorio: laboratorio, recursos: recursos, espacios: espacios, usuario: _usuario(RolUsuario.usuario)),
      );
      await tester.pumpAndSettle();

      await tester.tap(find.text('Estudio'));
      await tester.pumpAndSettle();

      final toggle = tester.widget<SwitchListTile>(find.byType(SwitchListTile));
      expect(toggle.value, isTrue);
      expect(toggle.onChanged, isNull);
    });

    testWidgets('sin recursos obligatorios el toggle queda libre', (tester) async {
      final laboratorio = _laboratorio(1);
      final recursos = [_recurso(1, 'Proyector')];
      await tester.pumpWidget(
        _montarSheet(laboratorio: laboratorio, recursos: recursos, espacios: const [], usuario: _usuario(RolUsuario.usuario)),
      );
      await tester.pumpAndSettle();

      await tester.tap(find.text('Proyector'));
      await tester.pumpAndSettle();

      final toggle = tester.widget<SwitchListTile>(find.byType(SwitchListTile));
      expect(toggle.value, isFalse);
      expect(toggle.onChanged, isNotNull);
    });
  });

  group('LaboratorioReservaSheet — reservas multi-día agrupadas (2026-09-03)', () {
    testWidgets('agregar un día muestra el chip, abre el selector de fecha, y se puede quitar', (tester) async {
      final laboratorio = _laboratorio(1);
      final recurso = _recurso(1, 'Proyector');
      final hoy = DateTime.now();
      final fechaInicial = DateTime(hoy.year, hoy.month, hoy.day);
      final slots = [
        DisponibilidadSlot(horaInicio: '08:00', horaFin: '09:00', estado: EstadoSlot.libre),
        DisponibilidadSlot(horaInicio: '09:00', horaFin: '10:00', estado: EstadoSlot.libre),
      ];

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            authProvider.overrideWith(() => _AuthFake(_usuario(RolUsuario.usuario))),
            recursosActivosProvider.overrideWith((ref) async => [recurso]),
            espaciosGestionProvider.overrideWith((ref) async => const []),
            recursoDisponibilidadProvider(1, fechaInicial).overrideWith((ref) async => slots),
          ],
          child: MaterialApp(
            home: Scaffold(
              body: SingleChildScrollView(child: LaboratorioReservaSheet(laboratorio: laboratorio)),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Sin ocurrencias agregadas todavía: el botón dice "Reservar" a secas.
      await tester.tap(find.text('Proyector'));
      await tester.pumpAndSettle();
      expect(find.widgetWithText(FilledButton, 'Reservar'), findsOneWidget);
      expect(find.text('Agregar otro día'), findsNothing);

      await tester.tap(find.text('08:00–09:00'));
      await tester.pumpAndSettle();

      final botonAgregar = find.text('Agregar otro día');
      expect(botonAgregar, findsOneWidget);
      await tester.ensureVisible(botonAgregar);
      await tester.tap(botonAgregar);
      await tester.pumpAndSettle();

      // Se agregó la ocurrencia (chip visible) y se abrió el selector de
      // fecha para el día siguiente -- lo cerramos tocando el centro de la
      // pantalla (cae dentro del diálogo, sobre la grilla de días) sin
      // depender de qué fecha exacta arme el DatePicker.
      expect(find.textContaining('08:00–09:00'), findsWidgets);
      expect(find.byType(DatePickerDialog), findsOneWidget);
      await tester.tapAt(tester.getCenter(find.byType(DatePickerDialog)));
      await tester.pumpAndSettle();

      // Con 1 ocurrencia ya agregada (y ninguna franja elegida todavía para
      // el día vigente), el botón queda deshabilitado pero ya anticipa el total.
      final botonReservarDos = find.widgetWithText(FilledButton, 'Reservar 2 días');
      expect(botonReservarDos, findsOneWidget);
      expect(tester.widget<FilledButton>(botonReservarDos).onPressed, isNull);

      // Quitar el chip vuelve al estado de una sola reserva. Se invoca
      // `onDeleted` directo (lo mismo que dispara tocar el ícono de borrar
      // del chip) en vez de apuntarle a un ícono puntual -- más robusto.
      expect(find.byType(InputChip), findsOneWidget);
      tester.widget<InputChip>(find.byType(InputChip)).onDeleted!();
      await tester.pumpAndSettle();

      expect(find.byType(InputChip), findsNothing);
      expect(find.widgetWithText(FilledButton, 'Reservar'), findsOneWidget);
    });
  });
}
