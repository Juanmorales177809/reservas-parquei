import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../../../core/domain/enums.dart';
import '../../../core/network/api_exception.dart';
import '../../../core/router/app_routes.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/widgets/empty_view.dart';
import '../../../core/widgets/error_view.dart';
import '../../../core/widgets/loading_spinner.dart';
import '../../../core/widgets/success_burst.dart';
import '../../auth/application/auth_provider.dart';
import '../../espacios/domain/disponibilidad_slot.dart';
import '../../espacios/presentation/disponibilidad_slot_grid.dart';
import '../../espacios/presentation/slot_chip.dart';
import '../../recursos/application/recursos_providers.dart';
import '../../recursos/domain/recurso.dart';
import '../application/reservas_providers.dart';
import '../data/reservas_repository.dart';
import 'selectable_slot_grid.dart';

/// Abierto al tocar un recurso en `EspacioDetalleScreen`. Anónimo: solo
/// lectura (Fase 1) + botón "Iniciá sesión para reservar". Autenticado
/// (Fase 2): selección de un rango de franjas `libre` consecutivas +
/// formulario mínimo (asistentes, tipo opcional) + `POST /reservas`.
/// Alcance acotado a `recurso_ids` (modalidad "equipos") — zonas/ensayos/
/// acompañantes quedan fuera, ver plan de migración.
class RecursoDisponibilidadSheet extends ConsumerStatefulWidget {
  const RecursoDisponibilidadSheet({required this.recurso, super.key});

  final Recurso recurso;

  @override
  ConsumerState<RecursoDisponibilidadSheet> createState() => _RecursoDisponibilidadSheetState();
}

class _RecursoDisponibilidadSheetState extends ConsumerState<RecursoDisponibilidadSheet> {
  late DateTime _fecha;
  Set<int> _seleccion = {};
  int _asistentes = 1;
  TipoReserva? _tipo;
  bool _enviando = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    final ahora = DateTime.now();
    _fecha = DateTime(ahora.year, ahora.month, ahora.day);
  }

  Future<void> _elegirFecha() async {
    final elegida = await showDatePicker(
      context: context,
      initialDate: _fecha,
      firstDate: DateTime(_fecha.year - 1),
      lastDate: DateTime(_fecha.year + 1),
    );
    if (elegida != null) {
      setState(() {
        _fecha = DateTime(elegida.year, elegida.month, elegida.day);
        _seleccion = {};
        _error = null;
      });
    }
  }

  /// Selección producida por un arrastre sobre la grilla. El rango ya
  /// viene validado como contiguo y todo `libre` por `SelectableSlotGrid`.
  void _seleccionarRango(int desde, int hasta) {
    setState(() {
      _error = null;
      _seleccion = {for (var i = desde; i <= hasta; i++) i};
    });
  }

  void _alternarSlot(List<DisponibilidadSlot> slots, int index) {
    setState(() {
      _error = null;
      if (_seleccion.isEmpty) {
        _seleccion = {index};
        return;
      }
      if (_seleccion.length == 1 && _seleccion.contains(index)) {
        _seleccion = {};
        return;
      }
      final minIdx = _seleccion.reduce((a, b) => a < b ? a : b);
      final maxIdx = _seleccion.reduce((a, b) => a > b ? a : b);
      Iterable<int> rango;
      if (index < minIdx) {
        rango = Iterable.generate(maxIdx - index + 1, (i) => index + i);
      } else if (index > maxIdx) {
        rango = Iterable.generate(index - minIdx + 1, (i) => minIdx + i);
      } else {
        _seleccion = {index};
        return;
      }
      final todasLibres = rango.every((i) => slots[i].estado == EstadoSlot.libre);
      _seleccion = todasLibres ? rango.toSet() : {index};
    });
  }

  Future<void> _reservar(List<DisponibilidadSlot> slots) async {
    final minIdx = _seleccion.reduce((a, b) => a < b ? a : b);
    final maxIdx = _seleccion.reduce((a, b) => a > b ? a : b);
    setState(() {
      _enviando = true;
      _error = null;
    });
    try {
      await ref.read(reservasRepositoryProvider).crear(
            recursoIds: [widget.recurso.id],
            fecha: _fecha,
            horaInicio: slots[minIdx].horaInicio,
            horaFin: slots[maxIdx].horaFin,
            asistentes: _asistentes,
            tipo: _tipo,
          );
      ref.invalidate(recursoDisponibilidadProvider(widget.recurso.id, _fecha));
      ref.invalidate(misReservasProvider);
      if (mounted) {
        await SuccessBurst.show(context, message: 'Reserva enviada. Quedó pendiente de aprobación.');
        if (mounted) Navigator.of(context).pop();
      }
    } on Object catch (e) {
      final esConflicto = apiErrorStatusCode(e) == 409;
      setState(() {
        _error = esConflicto
            ? 'Ese horario ya no está disponible. Actualizá la disponibilidad e intentá de nuevo.'
            : apiErrorMessage(e, fallback: 'No se pudo crear la reserva. Intentá de nuevo.');
      });
      if (esConflicto) ref.invalidate(recursoDisponibilidadProvider(widget.recurso.id, _fecha));
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final disponibilidadAsync = ref.watch(recursoDisponibilidadProvider(widget.recurso.id, _fecha));
    final isAuthenticated = ref.watch(isAuthenticatedProvider);
    final scheme = Theme.of(context).colorScheme;

    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(AppSpacing.lg, AppSpacing.sm, AppSpacing.lg, AppSpacing.lg),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 36,
                height: 4,
                margin: const EdgeInsets.only(bottom: AppSpacing.lg),
                decoration: BoxDecoration(
                  color: scheme.outlineVariant,
                  borderRadius: BorderRadius.circular(999),
                ),
              ),
            ),
            Text(widget.recurso.nombre, style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: AppSpacing.md),
            OutlinedButton.icon(
              onPressed: _elegirFecha,
              icon: const Icon(LucideIcons.calendar, size: 18),
              label: Text('${_fecha.day}/${_fecha.month}/${_fecha.year}'),
            ),
            const SizedBox(height: AppSpacing.lg),
            disponibilidadAsync.when(
              loading: () => const Padding(padding: EdgeInsets.symmetric(vertical: 24), child: LoadingSpinner()),
              error: (error, _) => ErrorView(
                message: apiErrorMessage(error, fallback: 'No se pudo cargar la disponibilidad.'),
                onRetry: () => ref.invalidate(recursoDisponibilidadProvider(widget.recurso.id, _fecha)),
              ),
              data: (slots) {
                if (slots.isEmpty) {
                  return const EmptyView(
                    icon: LucideIcons.calendarX,
                    message: 'No hay franjas disponibles para esta fecha.',
                  );
                }
                if (!isAuthenticated) {
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      DisponibilidadSlotGrid(slots: slots),
                      const SizedBox(height: AppSpacing.lg),
                      FilledButton.icon(
                        onPressed: () {
                          Navigator.of(context).pop();
                          // `go`, no `push`: ver comentario en
                          // `top_nav_shell.dart` — con `push` el guard de
                          // `app_router.dart` no detecta `/login` como
                          // ubicación y no redirige tras autenticarse.
                          context.go(AppRoutes.login);
                        },
                        icon: const Icon(LucideIcons.logIn, size: 18),
                        label: const Text('Iniciá sesión para reservar'),
                      ),
                    ],
                  );
                }
                return _FormularioReserva(
                  slots: slots,
                  seleccion: _seleccion,
                  recurso: widget.recurso,
                  asistentes: _asistentes,
                  tipo: _tipo,
                  enviando: _enviando,
                  error: _error,
                  onToggle: (i) => _alternarSlot(slots, i),
                  onRango: _seleccionarRango,
                  onAsistentesChanged: (v) => setState(() => _asistentes = v),
                  onTipoChanged: (v) => setState(() => _tipo = v),
                  onConfirmar: () => _reservar(slots),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}

class _FormularioReserva extends StatelessWidget {
  const _FormularioReserva({
    required this.slots,
    required this.seleccion,
    required this.recurso,
    required this.asistentes,
    required this.tipo,
    required this.enviando,
    required this.error,
    required this.onToggle,
    required this.onRango,
    required this.onAsistentesChanged,
    required this.onTipoChanged,
    required this.onConfirmar,
  });

  final List<DisponibilidadSlot> slots;
  final Set<int> seleccion;
  final Recurso recurso;
  final int asistentes;
  final TipoReserva? tipo;
  final bool enviando;
  final String? error;
  final ValueChanged<int> onToggle;
  final void Function(int desde, int hasta) onRango;
  final ValueChanged<int> onAsistentesChanged;
  final ValueChanged<TipoReserva?> onTipoChanged;
  final VoidCallback onConfirmar;

  @override
  Widget build(BuildContext context) {
    final capacidadMax = recurso.capacidad > 0 ? recurso.capacidad : 999;
    final hayseleccion = seleccion.isNotEmpty;

    String? resumen;
    if (hayseleccion) {
      final minIdx = seleccion.reduce((a, b) => a < b ? a : b);
      final maxIdx = seleccion.reduce((a, b) => a > b ? a : b);
      final horas = seleccion.length;
      resumen = '${slots[minIdx].horaInicio}–${slots[maxIdx].horaFin} · '
          '${horas == 1 ? '1 hora' : '$horas horas'} · '
          '${asistentes == 1 ? '1 asistente' : '$asistentes asistentes'}';
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SelectableSlotGrid(
          slots: slots,
          selectedIndices: seleccion,
          onToggle: onToggle,
          onRango: onRango,
        ),
        const SizedBox(height: AppSpacing.lg),
        const SlotLeyenda(),
        if (hayseleccion) ...[
          const SizedBox(height: AppSpacing.lg),
          Row(
            children: [
              Text('Asistentes', style: Theme.of(context).textTheme.bodyMedium),
              const Spacer(),
              IconButton.filledTonal(
                onPressed: asistentes > 1 ? () => onAsistentesChanged(asistentes - 1) : null,
                icon: const Icon(LucideIcons.minus, size: 16),
                constraints: const BoxConstraints.tightFor(width: 32, height: 32),
              ),
              SizedBox(
                width: 32,
                child: Text('$asistentes', textAlign: TextAlign.center, style: Theme.of(context).textTheme.titleSmall),
              ),
              IconButton.filledTonal(
                onPressed: asistentes < capacidadMax ? () => onAsistentesChanged(asistentes + 1) : null,
                icon: const Icon(LucideIcons.plus, size: 16),
                constraints: const BoxConstraints.tightFor(width: 32, height: 32),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.md),
          DropdownButtonFormField<TipoReserva?>(
            initialValue: tipo,
            decoration: const InputDecoration(labelText: 'Tipo de reserva (opcional)'),
            items: [
              const DropdownMenuItem(value: null, child: Text('Sin especificar')),
              for (final t in TipoReserva.values) DropdownMenuItem(value: t, child: Text(tipoReservaLabel(t))),
            ],
            onChanged: onTipoChanged,
          ),
        ],
        if (error != null) ...[
          const SizedBox(height: AppSpacing.md),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(AppSpacing.md),
            decoration: BoxDecoration(
              color: AppEstados.negativo.tinte,
              borderRadius: BorderRadius.circular(AppRadius.sm),
              border: Border.all(color: AppEstados.negativo.borde.withValues(alpha: 0.4)),
            ),
            child: Text(error!, style: TextStyle(color: AppEstados.negativo.sobreTinte)),
          ),
        ],
        const SizedBox(height: AppSpacing.lg),
        // Resumen persistente + botón a ancho completo: antes el usuario
        // elegía franjas y completaba el formulario sin ver nunca
        // consolidado lo que estaba por reservar.
        if (resumen != null)
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(AppSpacing.md),
            margin: const EdgeInsets.only(bottom: AppSpacing.md),
            decoration: BoxDecoration(
              color: AppColors.azul50,
              borderRadius: BorderRadius.circular(AppRadius.sm),
            ),
            child: Row(
              children: [
                const Icon(LucideIcons.calendarCheck, size: 16, color: AppColors.marca),
                const SizedBox(width: AppSpacing.sm),
                Expanded(
                  child: Text(
                    resumen,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: AppColors.azul800,
                          fontWeight: FontWeight.w600,
                        ),
                  ),
                ),
              ],
            ),
          ),
        SizedBox(
          width: double.infinity,
          child: FilledButton(
            onPressed: (!hayseleccion || enviando) ? null : onConfirmar,
            child: enviando
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                  )
                : const Text('Reservar'),
          ),
        ),
        // Un botón gris y mudo obliga a adivinar qué falta.
        if (!hayseleccion) ...[
          const SizedBox(height: AppSpacing.sm),
          Center(
            child: Text(
              'Tocá una franja disponible, o arrastrá para elegir varias seguidas',
              style: Theme.of(context).textTheme.bodySmall,
              textAlign: TextAlign.center,
            ),
          ),
        ],
      ],
    );
  }
}
