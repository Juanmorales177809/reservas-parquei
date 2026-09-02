import 'package:flutter/material.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';

const _diasSemana = [
  (valor: 0, label: 'Lun'),
  (valor: 1, label: 'Mar'),
  (valor: 2, label: 'Mié'),
  (valor: 3, label: 'Jue'),
  (valor: 4, label: 'Vie'),
  (valor: 5, label: 'Sáb'),
  (valor: 6, label: 'Dom'),
];

/// Horas mostradas en el editor — 06:00–22:00 (16 franjas), igual que
/// `frontend/src/app/admin/configuracion/page.tsx` (Array.from 6..21).
const _horas = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21];

/// Notifica un cambio del horario. [operacionMasiva] trae una descripción
/// legible ("Se activó todo el Lun") cuando el cambio afectó a más de una
/// celda — la pantalla contenedora la usa para ofrecer "Deshacer", que es
/// lo que hace que una grilla de 112 celdas sea usable sin miedo.
typedef HorarioChanged = void Function(Map<int, List<int>> nuevo, {String? operacionMasiva});

/// Editor de `horario_atencion` día×hora.
///
/// **Fase 6**: 7 días × 16 horas = 112 celdas. Configurar un laboratorio a mano
/// eran 112 toques y no había forma de revertir un error. Ahora hay tres
/// caminos, y el toque celda por celda es solo el último recurso:
///
/// - **Arrastrar** (mantener presionado y deslizar) pinta un rango entero.
///   El primer toque decide la operación: si la celda inicial estaba
///   activa, el arrastre DESACTIVA todo lo que toca; si estaba inactiva,
///   activa. Es el mismo modelo mental que seleccionar celdas en una hoja
///   de cálculo.
/// - **Encabezado de día** activa/desactiva la columna completa.
/// - **Etiqueta de hora** activa/desactiva la fila completa.
///
/// El arrastre se dispara con *long press* y no con `onPan`, a propósito:
/// la tabla vive dentro de un `SingleChildScrollView` horizontal, y un
/// `onPanUpdate` competiría con ese scroll en el gesture arena — el usuario
/// intentaría desplazar la tabla para ver el domingo y en su lugar pintaría
/// franjas.
class HorarioEditor extends StatefulWidget {
  const HorarioEditor({
    required this.horario,
    required this.onChanged,
    super.key,
  });

  /// Mapa actual `dia (0-6) -> horas seleccionadas`. Las claves faltantes se
  /// tratan como listas vacías (igual que el backend: `horario['$dia'] ?? []`).
  final Map<int, List<int>> horario;

  final HorarioChanged onChanged;

  @override
  State<HorarioEditor> createState() => _HorarioEditorState();
}

class _HorarioEditorState extends State<HorarioEditor> {
  /// Una key por celda para poder resolver qué celda está bajo el dedo
  /// durante el arrastre (una `Table` no expone índices al hit-test).
  late final Map<(int, int), GlobalKey> _keys = {
    for (final d in _diasSemana)
      for (final h in _horas) (d.valor, h): GlobalKey(),
  };

  /// Valor que está pintando el arrastre en curso: `true` = activando,
  /// `false` = desactivando. `null` = no hay arrastre.
  bool? _pintando;

  bool _activa(int dia, int hora) => (widget.horario[dia] ?? const []).contains(hora);

  Map<int, List<int>> _conValor(Map<int, List<int>> base, int dia, int hora, bool activa) {
    final horasDia = List<int>.from(base[dia] ?? const []);
    if (activa) {
      if (!horasDia.contains(hora)) horasDia.add(hora);
    } else {
      horasDia.remove(hora);
    }
    horasDia.sort();
    return Map<int, List<int>>.from(base)..[dia] = horasDia;
  }

  void _toggleCelda(int dia, int hora) {
    widget.onChanged(_conValor(widget.horario, dia, hora, !_activa(dia, hora)));
  }

  void _toggleDia(int dia, String label) {
    final todasActivas = _horas.every((h) => _activa(dia, h));
    var nuevo = widget.horario;
    for (final h in _horas) {
      nuevo = _conValor(nuevo, dia, h, !todasActivas);
    }
    widget.onChanged(
      nuevo,
      operacionMasiva: todasActivas ? 'Se vació el $label' : 'Se activó todo el $label',
    );
  }

  void _toggleHora(int hora) {
    final todosActivos = _diasSemana.every((d) => _activa(d.valor, hora));
    var nuevo = widget.horario;
    for (final d in _diasSemana) {
      nuevo = _conValor(nuevo, d.valor, hora, !todosActivos);
    }
    final etiqueta = '${hora.toString().padLeft(2, '0')}:00';
    widget.onChanged(
      nuevo,
      operacionMasiva: todosActivos ? 'Se vació la franja de $etiqueta' : 'Se activó la franja de $etiqueta',
    );
  }

  (int, int)? _celdaEn(Offset posicionGlobal) {
    for (final entrada in _keys.entries) {
      final contexto = entrada.value.currentContext;
      if (contexto == null) continue;
      final caja = contexto.findRenderObject() as RenderBox?;
      if (caja == null || !caja.hasSize) continue;
      if ((caja.localToGlobal(Offset.zero) & caja.size).contains(posicionGlobal)) {
        return entrada.key;
      }
    }
    return null;
  }

  void _iniciarPintado(LongPressStartDetails d) {
    final celda = _celdaEn(d.globalPosition);
    if (celda == null) return;
    final destino = !_activa(celda.$1, celda.$2);
    _pintando = destino;
    widget.onChanged(_conValor(widget.horario, celda.$1, celda.$2, destino));
  }

  void _continuarPintado(LongPressMoveUpdateDetails d) {
    final destino = _pintando;
    if (destino == null) return;
    final celda = _celdaEn(d.globalPosition);
    if (celda == null) return;
    if (_activa(celda.$1, celda.$2) == destino) return;
    widget.onChanged(_conValor(widget.horario, celda.$1, celda.$2, destino));
  }

  void _terminarPintado() {
    if (_pintando != null) {
      _pintando = null;
      // Un arrastre suele tocar muchas celdas: se ofrece deshacer igual que
      // en las operaciones de fila/columna.
      widget.onChanged(widget.horario, operacionMasiva: 'Se pintaron varias franjas');
    }
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Horario semanal de atención', style: textTheme.titleMedium),
        const SizedBox(height: AppSpacing.xs),
        Text(
          'Tocá una franja para activarla o desactivarla. Mantené presionado y arrastrá '
          'para pintar varias seguidas, o tocá un día / una hora para la fila o columna completa.',
          style: textTheme.bodySmall,
        ),
        const SizedBox(height: AppSpacing.md),
        GestureDetector(
          onLongPressStart: _iniciarPintado,
          onLongPressMoveUpdate: _continuarPintado,
          onLongPressEnd: (_) => _terminarPintado(),
          onLongPressCancel: _terminarPintado,
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Table(
              defaultColumnWidth: const FixedColumnWidth(76),
              columnWidths: const {0: FixedColumnWidth(112)},
              children: [
                TableRow(
                  children: [
                    const _EncabezadoEsquina(),
                    for (final d in _diasSemana)
                      _EncabezadoDia(
                        label: d.label,
                        todasActivas: _horas.every((h) => _activa(d.valor, h)),
                        onTap: () => _toggleDia(d.valor, d.label),
                      ),
                  ],
                ),
                for (final hora in _horas)
                  TableRow(
                    children: [
                      _EtiquetaHora(
                        hora: hora,
                        todosActivos: _diasSemana.every((d) => _activa(d.valor, hora)),
                        onTap: () => _toggleHora(hora),
                      ),
                      for (final dia in _diasSemana)
                        KeyedSubtree(
                          key: _keys[(dia.valor, hora)],
                          child: _SlotCell(
                            seleccionada: _activa(dia.valor, hora),
                            onTap: () => _toggleCelda(dia.valor, hora),
                            semanticsLabel: '${dia.label} de $hora:00 a ${hora + 1}:00',
                          ),
                        ),
                    ],
                  ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

class _EncabezadoEsquina extends StatelessWidget {
  const _EncabezadoEsquina();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(AppSpacing.sm),
      child: Text('FRANJA', style: AppText.overline()),
    );
  }
}

class _EncabezadoDia extends StatelessWidget {
  const _EncabezadoDia({required this.label, required this.todasActivas, required this.onTap});

  final String label;
  final bool todasActivas;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(2),
      child: Tooltip(
        message: todasActivas ? 'Vaciar $label' : 'Activar todo el $label',
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(AppRadius.xs),
          child: Container(
            padding: const EdgeInsets.symmetric(vertical: AppSpacing.sm),
            alignment: Alignment.center,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(label.toUpperCase(), style: AppText.overline(color: AppColors.texto)),
                const SizedBox(width: 2),
                Icon(
                  todasActivas ? LucideIcons.squareCheck : LucideIcons.square,
                  size: 11,
                  color: AppColors.textoDeshabilitado,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _EtiquetaHora extends StatelessWidget {
  const _EtiquetaHora({required this.hora, required this.todosActivos, required this.onTap});

  final int hora;
  final bool todosActivos;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(2),
      child: Tooltip(
        message: todosActivos ? 'Vaciar esta franja en todos los días' : 'Activar esta franja todos los días',
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(AppRadius.xs),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: AppSpacing.sm, vertical: AppSpacing.sm),
            alignment: Alignment.centerLeft,
            child: Row(
              children: [
                Icon(
                  todosActivos ? LucideIcons.squareCheck : LucideIcons.square,
                  size: 11,
                  color: AppColors.textoDeshabilitado,
                ),
                const SizedBox(width: AppSpacing.xs),
                Text(
                  '${hora.toString().padLeft(2, '0')}:00–${(hora + 1).toString().padLeft(2, '0')}:00',
                  style: AppText.numerico(fontSize: 11, color: AppColors.textoSecundario, fontWeight: FontWeight.w500),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _SlotCell extends StatelessWidget {
  const _SlotCell({required this.seleccionada, required this.onTap, required this.semanticsLabel});

  final bool seleccionada;
  final VoidCallback onTap;
  final String semanticsLabel;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(2),
      child: Semantics(
        button: true,
        label: semanticsLabel,
        toggled: seleccionada,
        // `GestureDetector` y no `InkWell`: en una grilla de 112 celdas
        // contiguas el ripple de una celda se desborda sobre las vecinas y
        // durante un arrastre quedan varios ripples solapados a la vez.
        child: GestureDetector(
          onTap: onTap,
          child: AnimatedContainer(
            // 100ms: en una grilla densa, cualquier cosa más lenta hace que
            // un arrastre sobre 20 celdas se sienta viscoso.
            duration: const Duration(milliseconds: 100),
            height: 36,
            decoration: BoxDecoration(
              // Verde y no el azul de marca, deliberadamente: en esta app el
              // verde SIGNIFICA "disponible" (ver `AppEstados.positivo`), y
              // estas celdas son exactamente las franjas que quedarán
              // disponibles para reservar. Usar el azul de "seleccionado"
              // haría que el editor no coincida con la grilla que después ve
              // quien reserva.
              color: seleccionada ? AppEstados.positivo.relleno : AppColors.superficie,
              border: Border.all(
                color: seleccionada ? AppEstados.positivo.relleno : AppColors.borde,
              ),
              borderRadius: BorderRadius.circular(AppRadius.xs),
            ),
            alignment: Alignment.center,
            child: seleccionada
                ? const Icon(LucideIcons.check, size: 14, color: Colors.white)
                : null,
          ),
        ),
      ),
    );
  }
}

/// Convierte `Map<String,List<int>>` (formato JSON del backend) a
/// `Map<int,List<int>>` para el editor.
Map<int, List<int>> horarioFromJson(Map<String, List<int>> json) {
  return {for (final e in json.entries) int.parse(e.key): List<int>.from(e.value)};
}

/// Convierte `Map<int,List<int>>` del editor a `Map<String,List<int>>` para
/// `PUT /laboratorios/gestion/configuracion`. Incluye todos los días 0-6
/// (aunque estén vacíos) para que la validación del backend sea explícita.
Map<String, List<int>> horarioToJson(Map<int, List<int>> horario) {
  return {for (var dia = 0; dia < 7; dia++) '$dia': List<int>.from(horario[dia] ?? const [])..sort()};
}
