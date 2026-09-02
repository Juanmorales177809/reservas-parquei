import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:app_flutter/core/domain/enums.dart';
import 'package:app_flutter/features/laboratorios/domain/disponibilidad_slot.dart';
import 'package:app_flutter/features/reservas/presentation/selectable_slot_grid.dart';

DisponibilidadSlot _slot(String inicio, String fin, EstadoSlot estado) =>
    DisponibilidadSlot(horaInicio: inicio, horaFin: fin, estado: estado);

void main() {
  // Cuatro franjas seguidas; la tercera está ocupada, así que un rango que
  // la cruce no debe poder seleccionarse.
  final slots = [
    _slot('08:00', '09:00', EstadoSlot.libre),
    _slot('09:00', '10:00', EstadoSlot.libre),
    _slot('10:00', '11:00', EstadoSlot.ocupado),
    _slot('11:00', '12:00', EstadoSlot.libre),
  ];

  Future<void> montar(
    WidgetTester tester, {
    required void Function(int, int) onRango,
    Set<int> seleccion = const {},
  }) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SelectableSlotGrid(
            slots: slots,
            selectedIndices: seleccion,
            onToggle: (_) {},
            onRango: onRango,
          ),
        ),
      ),
    );
  }

  group('SelectableSlotGrid — selección por arrastre', () {
    testWidgets('arrastrar sobre franjas libres contiguas reporta el rango', (tester) async {
      final rangos = <(int, int)>[];
      await montar(tester, onRango: (d, h) => rangos.add((d, h)));

      final desde = tester.getCenter(find.text('08:00–09:00'));
      final hasta = tester.getCenter(find.text('09:00–10:00'));

      final gesto = await tester.startGesture(desde);
      await tester.pump();
      await gesto.moveTo(hasta);
      await tester.pump();
      await gesto.up();
      await tester.pumpAndSettle();

      // El primer reporte es el ancla (0,0); el último debe cubrir 0..1.
      expect(rangos.first, (0, 0));
      expect(rangos.last, (0, 1));
    });

    testWidgets('un arrastre que cruzaría una franja ocupada no extiende el rango', (tester) async {
      final rangos = <(int, int)>[];
      await montar(tester, onRango: (d, h) => rangos.add((d, h)));

      final desde = tester.getCenter(find.text('08:00–09:00'));
      final cruzando = tester.getCenter(find.text('11:00–12:00'));

      final gesto = await tester.startGesture(desde);
      await tester.pump();
      // 0..3 incluye la franja 2 (ocupada): la reserva no sería válida, así
      // que el movimiento se ignora en vez de partir la selección en dos.
      await gesto.moveTo(cruzando);
      await tester.pump();
      await gesto.up();
      await tester.pumpAndSettle();

      expect(rangos, isNot(contains((0, 3))));
    });

    testWidgets('arrastrar desde una franja no libre no inicia selección', (tester) async {
      final rangos = <(int, int)>[];
      await montar(tester, onRango: (d, h) => rangos.add((d, h)));

      final gesto = await tester.startGesture(tester.getCenter(find.text('10:00–11:00')));
      await tester.pump();
      await gesto.moveTo(tester.getCenter(find.text('11:00–12:00')));
      await tester.pump();
      await gesto.up();
      await tester.pumpAndSettle();

      expect(rangos, isEmpty);
    });

    testWidgets('sin onRango el arrastre no hace nada', (tester) async {
      var toques = 0;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SelectableSlotGrid(
              slots: slots,
              selectedIndices: const {},
              onToggle: (_) => toques++,
            ),
          ),
        ),
      );

      // No se puede afirmar `findsNothing` sobre `GestureDetector`: cada chip
      // tocable monta un `InkWell`, que internamente ES un GestureDetector.
      // Lo que se verifica es el comportamiento: arrastrar sin `onRango` no
      // debe producir ninguna selección (ni siquiera vía `onToggle`).
      final gesto = await tester.startGesture(tester.getCenter(find.text('08:00–09:00')));
      await tester.pump();
      await gesto.moveTo(tester.getCenter(find.text('09:00–10:00')));
      await tester.pump();
      await gesto.up();
      await tester.pumpAndSettle();

      expect(toques, 0);
    });
  });
}
