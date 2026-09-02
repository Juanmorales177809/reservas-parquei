import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:app_flutter/core/domain/enums.dart';
import 'package:app_flutter/core/theme/app_colors.dart';
import 'package:app_flutter/features/laboratorios/presentation/slot_chip.dart';

/// Devuelve el color de fondo del `Container` decorado que pinta el chip.
Color? _fondoDe(WidgetTester tester) {
  final contenedor = tester.widget<Container>(
    find.descendant(of: find.byType(SlotChip), matching: find.byType(Container)).first,
  );
  return (contenedor.decoration as BoxDecoration?)?.color;
}

void main() {
  Widget envolver(Widget child) => MaterialApp(home: Scaffold(body: child));

  group('SlotChip', () {
    testWidgets('una franja libre se pinta con el tinte positivo', (tester) async {
      await tester.pumpWidget(
        envolver(const SlotChip(estado: EstadoSlot.libre, etiqueta: '08:00–09:00')),
      );

      expect(find.text('08:00–09:00'), findsOneWidget);
      expect(_fondoDe(tester), AppEstados.positivo.tinte);
    });

    testWidgets('una franja seleccionada usa el color de marca, no el de estado', (tester) async {
      await tester.pumpWidget(
        envolver(const SlotChip(estado: EstadoSlot.libre, etiqueta: '08:00–09:00', seleccionado: true)),
      );

      expect(_fondoDe(tester), AppColors.marca);
    });

    testWidgets(
      'mantenimiento se distingue de ocupado por PATRÓN, no solo por color',
      (tester) async {
        // Requisito 1.4.1 de WCAG: la información no puede transmitirse solo
        // con color. "Ya está reservado" y "el equipo no está operativo" son
        // cosas distintas para quien reserva, y comparten color de fondo, así
        // que mantenimiento agrega rayas diagonales (un `CustomPaint`).
        await tester.pumpWidget(
          envolver(const SlotChip(estado: EstadoSlot.mantenimiento, etiqueta: '10:00–11:00')),
        );
        final conPatron = find.descendant(
          of: find.byType(SlotChip),
          matching: find.byType(CustomPaint),
        );
        expect(conPatron, findsWidgets);

        await tester.pumpWidget(
          envolver(const SlotChip(estado: EstadoSlot.ocupado, etiqueta: '10:00–11:00')),
        );
        // `ocupado` no lleva rayas: si este chip también las tuviera, el
        // patrón dejaría de distinguir un estado del otro.
        expect(
          find.descendant(of: find.byType(SlotChip), matching: find.byType(CustomPaint)),
          findsNothing,
        );
      },
    );

    testWidgets('sin onTap no es interactivo', (tester) async {
      await tester.pumpWidget(
        envolver(const SlotChip(estado: EstadoSlot.ocupado, etiqueta: '10:00–11:00')),
      );
      expect(find.byType(InkWell), findsNothing);
    });
  });
}
