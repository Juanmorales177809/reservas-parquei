import 'package:flutter/gestures.dart' show DragStartBehavior;
import 'package:flutter/material.dart';

import '../../../core/domain/enums.dart';
import '../../../core/theme/app_spacing.dart';
import '../../espacios/domain/disponibilidad_slot.dart';
import '../../espacios/presentation/slot_chip.dart';

/// Grilla interactiva: permite elegir un rango de franjas `libre`
/// consecutivas. Las `ocupado`/`mantenimiento` se muestran pero no son
/// tocables.
///
/// Dos formas de seleccionar, a propósito:
/// - **Tocar** el inicio y luego el fin (la de siempre, y la única viable
///   con lector de pantalla o teclado).
/// - **Arrastrar** horizontalmente sobre las franjas: convierte "tocar
///   cinco celdas" en un solo gesto y comunica visualmente que lo que se
///   está eligiendo es un bloque continuo, no cinco cosas sueltas.
///
/// El arrastre es **horizontal** y no libre: este widget vive dentro de un
/// `showModalBottomSheet` scrolleable, y un `onPanUpdate` competiría con el
/// scroll vertical del sheet en el gesture arena — el usuario intentaría
/// desplazar la hoja y en su lugar pintaría franjas.
class SelectableSlotGrid extends StatefulWidget {
  const SelectableSlotGrid({
    required this.slots,
    required this.selectedIndices,
    required this.onToggle,
    this.onRango,
    super.key,
  });

  final List<DisponibilidadSlot> slots;
  final Set<int> selectedIndices;
  final ValueChanged<int> onToggle;

  /// Selección contigua `[desde, hasta]` producida por un arrastre. Si es
  /// `null`, el arrastre queda deshabilitado y solo funciona el toque.
  final void Function(int desde, int hasta)? onRango;

  @override
  State<SelectableSlotGrid> createState() => _SelectableSlotGridState();
}

class _SelectableSlotGridState extends State<SelectableSlotGrid> {
  List<GlobalKey> _keys = const [];
  int? _ancla;

  @override
  void initState() {
    super.initState();
    _sincronizarKeys();
  }

  @override
  void didUpdateWidget(SelectableSlotGrid oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.slots.length != widget.slots.length) _sincronizarKeys();
  }

  void _sincronizarKeys() {
    _keys = List.generate(widget.slots.length, (_) => GlobalKey(), growable: false);
  }

  /// Qué franja está bajo el puntero. Se resuelve por geometría (rectángulo
  /// global de cada chip) porque un `Wrap` no expone índices al hit-test.
  int? _indiceEn(Offset posicionGlobal) {
    for (var i = 0; i < _keys.length; i++) {
      final contexto = _keys[i].currentContext;
      if (contexto == null) continue;
      final caja = contexto.findRenderObject() as RenderBox?;
      if (caja == null || !caja.hasSize) continue;
      final origen = caja.localToGlobal(Offset.zero);
      if ((origen & caja.size).contains(posicionGlobal)) return i;
    }
    return null;
  }

  bool _rangoTodoLibre(int desde, int hasta) {
    for (var i = desde; i <= hasta; i++) {
      if (widget.slots[i].estado != EstadoSlot.libre) return false;
    }
    return true;
  }

  void _iniciarArrastre(DragStartDetails d) {
    final idx = _indiceEn(d.globalPosition);
    if (idx == null || widget.slots[idx].estado != EstadoSlot.libre) return;
    _ancla = idx;
    widget.onRango!(idx, idx);
  }

  void _actualizarArrastre(DragUpdateDetails d) {
    final ancla = _ancla;
    if (ancla == null) return;
    final idx = _indiceEn(d.globalPosition);
    if (idx == null) return;
    final desde = idx < ancla ? idx : ancla;
    final hasta = idx < ancla ? ancla : idx;
    // Un rango que cruza una franja ocupada no es reservable: se ignora el
    // movimiento en vez de partir la selección en dos.
    if (!_rangoTodoLibre(desde, hasta)) return;
    widget.onRango!(desde, hasta);
  }

  @override
  Widget build(BuildContext context) {
    final grilla = Wrap(
      spacing: AppSpacing.sm,
      runSpacing: AppSpacing.sm,
      children: [
        for (var i = 0; i < widget.slots.length; i++)
          KeyedSubtree(
            key: _keys[i],
            child: SlotChip(
              estado: widget.slots[i].estado,
              etiqueta: '${widget.slots[i].horaInicio}–${widget.slots[i].horaFin}',
              seleccionado: widget.selectedIndices.contains(i),
              onTap: widget.slots[i].estado == EstadoSlot.libre ? () => widget.onToggle(i) : null,
            ),
          ),
      ],
    );

    if (widget.onRango == null) return grilla;

    return GestureDetector(
      // `DragStartBehavior.start` (el default) reporta el inicio del
      // arrastre en la posición donde el gesto fue RECONOCIDO, es decir
      // después de recorrer el umbral táctil (~18px). Para cuando llega el
      // callback, el dedo ya suele estar sobre la franja siguiente, así que
      // el ancla quedaba en la franja equivocada y la franja donde el
      // usuario realmente empezó nunca entraba en la selección.
      // `.down` reporta la posición del contacto inicial, que es la que el
      // usuario tenía en mente. (Bug encontrado por el test de arrastre.)
      dragStartBehavior: DragStartBehavior.down,
      onHorizontalDragStart: _iniciarArrastre,
      onHorizontalDragUpdate: _actualizarArrastre,
      onHorizontalDragEnd: (_) => _ancla = null,
      onHorizontalDragCancel: () => _ancla = null,
      child: grilla,
    );
  }
}
