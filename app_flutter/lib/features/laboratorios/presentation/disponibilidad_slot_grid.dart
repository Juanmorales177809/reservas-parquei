import 'package:flutter/material.dart';

import '../../../core/theme/app_spacing.dart';
import '../domain/disponibilidad_slot.dart';
import 'slot_chip.dart';

/// Grilla de solo lectura (Fase 1): pinta el estado real de cada franja,
/// sin selección ni interacción. `SelectableSlotGrid` (Fase 2) es la
/// variante interactiva; ambas comparten [SlotChip] para no divergir.
class DisponibilidadSlotGrid extends StatelessWidget {
  const DisponibilidadSlotGrid({required this.slots, this.mostrarLeyenda = true, super.key});

  final List<DisponibilidadSlot> slots;
  final bool mostrarLeyenda;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Wrap(
          spacing: AppSpacing.sm,
          runSpacing: AppSpacing.sm,
          children: [
            for (final slot in slots)
              SlotChip(estado: slot.estado, etiqueta: '${slot.horaInicio}–${slot.horaFin}'),
          ],
        ),
        if (mostrarLeyenda) ...[
          const SizedBox(height: AppSpacing.lg),
          const SlotLeyenda(),
        ],
      ],
    );
  }
}
