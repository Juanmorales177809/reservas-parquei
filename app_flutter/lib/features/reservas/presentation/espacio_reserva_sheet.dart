// ignore_for_file: prefer_final_fields, curly_braces_in_flow_control_structures
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
import '../../ensayos/application/ensayos_providers.dart';
import '../../espacios/domain/disponibilidad_slot.dart';
import '../../espacios/domain/espacio.dart';
import '../../espacios/presentation/disponibilidad_slot_grid.dart';
import '../../espacios/presentation/slot_chip.dart';
import '../../recursos/application/recursos_providers.dart';
import '../../zonas/application/zonas_providers.dart';
import '../application/reservas_providers.dart';
import '../data/reservas_repository.dart';
import 'selectable_slot_grid.dart';

/// Sheet multi-eje para crear una reserva completa (Fase P2).
/// Cubre `recurso_ids`/`zona_ids`/`tipo` y deja preparado `ensayo_ids`/`acompanantes` (paridad con `frontend/src/app/espacios/page.tsx:246`).
/// Se abre desde `EspacioDetalleScreen` con el `Espacio` completo, no con un solo `Recurso`.
class EspacioReservaSheet extends ConsumerStatefulWidget {
  const EspacioReservaSheet({required this.espacio, super.key});
  final Espacio espacio;
  @override
  ConsumerState<EspacioReservaSheet> createState() => _EspacioReservaSheetState();
}

class _EspacioReservaSheetState extends ConsumerState<EspacioReservaSheet> {
  late DateTime _fecha;
  Set<int> _recursoIds = {};
  Set<int> _zonaIds = {};
  Set<int> _ensayoIds = {};
  final List<Map<String, String>> _acompanantes = [];
  final _nombreCtrl = TextEditingController();
  final _correoCtrl = TextEditingController();
  final _descripcionCtrl = TextEditingController();
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

  @override
  void dispose() {
    _nombreCtrl.dispose();
    _correoCtrl.dispose();
    _descripcionCtrl.dispose();
    super.dispose();
  }

  Future<void> _elegirFecha() async {
    final elegida = await showDatePicker(context: context, initialDate: _fecha, firstDate: DateTime(_fecha.year - 1), lastDate: DateTime(_fecha.year + 1));
    if (elegida != null) setState(() { _fecha = DateTime(elegida.year, elegida.month, elegida.day); _seleccion = {}; _error = null; });
  }

  void _seleccionarRango(int desde, int hasta) => setState(() { _error = null; _seleccion = {for (var i = desde; i <= hasta; i++) i}; });

  void _alternarSlot(List<DisponibilidadSlot> slots, int index) {
    setState(() {
      _error = null;
      if (_seleccion.isEmpty) { _seleccion = {index}; return; }
      if (_seleccion.length == 1 && _seleccion.contains(index)) { _seleccion = {}; return; }
      final minIdx = _seleccion.reduce((a, b) => a < b ? a : b);
      final maxIdx = _seleccion.reduce((a, b) => a > b ? a : b);
      Iterable<int> rango;
      if (index < minIdx) rango = Iterable.generate(maxIdx - index + 1, (i) => index + i);
      else if (index > maxIdx) rango = Iterable.generate(index - minIdx + 1, (i) => minIdx + i);
      else { _seleccion = {index}; return; }
      final todasLibres = rango.every((i) => slots[i].estado == EstadoSlot.libre);
      _seleccion = todasLibres ? rango.toSet() : {index};
    });
  }

  int _capacidadMax(List<dynamic> recursos, List<dynamic> zonas) {
    final caps = <int>[];
    caps.add(widget.espacio.capacidad);
    for (final r in recursos) { if (_recursoIds.contains(r.id)) caps.add(r.capacidad); }
    for (final z in zonas) { if (_zonaIds.contains(z.id) && z.capacidad != null) caps.add(z.capacidad as int); }
    if (caps.isEmpty) return 999;
    return caps.reduce((a, b) => a < b ? a : b);
  }

  Future<void> _reservar(List<DisponibilidadSlot> slots) async {
    if (_recursoIds.isEmpty && _zonaIds.isEmpty) { setState(() => _error = 'Seleccioná al menos un recurso o una zona.'); return; }
    final minIdx = _seleccion.reduce((a, b) => a < b ? a : b);
    final maxIdx = _seleccion.reduce((a, b) => a > b ? a : b);
    setState(() { _enviando = true; _error = null; });
    try {
      await ref.read(reservasRepositoryProvider).crear(
            recursoIds: _recursoIds.toList(),
            zonaIds: _zonaIds.toList(),
            ensayoIds: _ensayoIds.toList(),
            acompanantes: List.of(_acompanantes),
            fecha: _fecha,
            horaInicio: slots[minIdx].horaInicio,
            horaFin: slots[maxIdx].horaFin,
            asistentes: _asistentes,
            tipo: _tipo,
            descripcion: _descripcionCtrl.text.trim().isEmpty ? null : _descripcionCtrl.text.trim(),
          );
      // invalidar disponibilidades de recursos afectados y mis reservas
      for (final id in _recursoIds) { ref.invalidate(recursoDisponibilidadProvider(id, _fecha)); }
      ref.invalidate(misReservasProvider);
      if (mounted) {
        await SuccessBurst.show(context, message: 'Reserva enviada. Quedó pendiente de aprobación.');
        if (mounted) Navigator.of(context).pop();
      }
    } on Object catch (e) {
      final esConflicto = apiErrorStatusCode(e) == 409;
      setState(() => _error = esConflicto ? 'Ese horario ya no está disponible. Actualizá la disponibilidad e intentá de nuevo.' : apiErrorMessage(e, fallback: 'No se pudo crear la reserva. Intentá de nuevo.'));
      if (esConflicto) { for (final id in _recursoIds) ref.invalidate(recursoDisponibilidadProvider(id, _fecha)); }
    } finally { if (mounted) setState(() => _enviando = false); }
  }

  @override
  Widget build(BuildContext context) {
    final espacio = widget.espacio;
    final modalidad = espacio.modalidadReserva;
    final recursosAsync = ref.watch(recursosPorEspacioProvider(espacio.id));
    final zonasAsync = ref.watch(zonasGestionProvider);
    final isAuthenticated = ref.watch(isAuthenticatedProvider);
    final scheme = Theme.of(context).colorScheme;

    // filtrar zonas del espacio actual (zonasGestion trae todas si admin, pero gestor ya filtra por espacio)
    List<dynamic> zonasDelEspacio = [];
    final zonasVal = zonasAsync.value;
    if (zonasVal != null) zonasDelEspacio = zonasVal.where((z) => z.espacioId == espacio.id).toList();

    return SafeArea(
      child: Padding(
        padding: EdgeInsets.only(left: AppSpacing.lg, right: AppSpacing.lg, top: AppSpacing.sm, bottom: MediaQuery.of(context).viewInsets.bottom + AppSpacing.lg),
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(child: Container(width: 36, height: 4, margin: const EdgeInsets.only(bottom: AppSpacing.lg), decoration: BoxDecoration(color: scheme.outlineVariant, borderRadius: BorderRadius.circular(999)))),
              Text('Reservar en ${espacio.nombre}', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: AppSpacing.xs),
              Text('Modalidad: ${modalidad.name}', style: Theme.of(context).textTheme.bodySmall?.copyWith(color: scheme.onSurfaceVariant)),
              const SizedBox(height: AppSpacing.md),
              OutlinedButton.icon(onPressed: _elegirFecha, icon: const Icon(LucideIcons.calendar, size: 18), label: Text('${_fecha.day}/${_fecha.month}/${_fecha.year}')),
              const SizedBox(height: AppSpacing.lg),
              // Recursos
              if (modalidad != ModalidadEspacio.zonas) ...[
                Text('Recursos', style: Theme.of(context).textTheme.titleSmall),
                const SizedBox(height: AppSpacing.sm),
                if (recursosAsync.isEmpty) const Text('No hay recursos activos.', style: TextStyle(fontSize: 12)),
                ...recursosAsync.map((r) => CheckboxListTile(
                      contentPadding: EdgeInsets.zero,
                      title: Text(r.nombre),
                      subtitle: Text('${r.tipo.nombre} · cap. ${r.capacidad}'),
                      value: _recursoIds.contains(r.id),
                      onChanged: (v) => setState(() { if (v == true) _recursoIds.add(r.id); else _recursoIds.remove(r.id); _seleccion = {}; }),
                    )),
                const SizedBox(height: AppSpacing.md),
              ],
              // Zonas
              if (modalidad != ModalidadEspacio.equipos) ...[
                Text('Zonas', style: Theme.of(context).textTheme.titleSmall),
                const SizedBox(height: AppSpacing.sm),
                if (zonasDelEspacio.isEmpty) const Text('No hay zonas en este espacio.', style: TextStyle(fontSize: 12)),
                ...zonasDelEspacio.map((z) => CheckboxListTile(
                      contentPadding: EdgeInsets.zero,
                      title: Text(z.nombre),
                      subtitle: Text(z.descripcion ?? ''),
                      value: _zonaIds.contains(z.id),
                      onChanged: (v) => setState(() { if (v == true) _zonaIds.add(z.id); else { _zonaIds.remove(z.id); _ensayoIds.removeWhere((eid) => false); } _seleccion = {}; }),
                    )),
                const SizedBox(height: AppSpacing.md),
              ],
              // Ensayos (si hay zonas seleccionadas)
              if (_zonaIds.isNotEmpty) ...[
                Text('Ensayos (opcional)', style: Theme.of(context).textTheme.titleSmall),
                const SizedBox(height: AppSpacing.sm),
                ..._zonaIds.expand((zid) {
                  final ensayosAsync = ref.watch(ensayosGestionProvider);
                  final lista = ensayosAsync.value?.where((e) => e.zonaId == zid).toList() ?? [];
                  return lista.map((e) => CheckboxListTile(
                        contentPadding: EdgeInsets.zero,
                        title: Text(e.nombre),
                        subtitle: Text('Zona $zid'),
                        value: _ensayoIds.contains(e.id),
                        onChanged: (v) => setState(() { if (v == true) _ensayoIds.add(e.id); else _ensayoIds.remove(e.id); }),
                      ));
                }),
                const SizedBox(height: AppSpacing.md),
              ],
              // Acompañantes
              Text('Acompañantes (opcional)', style: Theme.of(context).textTheme.titleSmall),
              const SizedBox(height: AppSpacing.sm),
              ..._acompanantes.asMap().entries.map((e) => ListTile(
                    contentPadding: EdgeInsets.zero,
                    title: Text(e.value['nombre'] ?? ''),
                    subtitle: Text(e.value['correo'] ?? ''),
                    trailing: IconButton(icon: const Icon(LucideIcons.x, size: 16), onPressed: () => setState(() => _acompanantes.removeAt(e.key))),
                  )),
              Row(children: [
                Expanded(child: TextField(controller: _nombreCtrl, decoration: const InputDecoration(hintText: 'Nombre', isDense: true))),
                const SizedBox(width: AppSpacing.sm),
                Expanded(child: TextField(controller: _correoCtrl, decoration: const InputDecoration(hintText: 'correo@ej.com', isDense: true))),
                IconButton(icon: const Icon(LucideIcons.plus, size: 18), onPressed: () {
                  final n = _nombreCtrl.text.trim(); final c = _correoCtrl.text.trim();
                  if (n.isEmpty || c.isEmpty || !c.contains('@')) return;
                  setState(() { _acompanantes.add({'nombre': n, 'correo': c}); _nombreCtrl.clear(); _correoCtrl.clear(); });
                }),
              ]),
              const SizedBox(height: AppSpacing.lg),
              Text('Actividad a realizar (opcional)', style: Theme.of(context).textTheme.titleSmall),
              const SizedBox(height: AppSpacing.sm),
              TextField(
                controller: _descripcionCtrl,
                decoration: const InputDecoration(hintText: 'Ej. Grabación del podcast semanal', isDense: true),
                maxLines: 2,
              ),
              const SizedBox(height: AppSpacing.lg),
              // Disponibilidad
              Builder(builder: (context) {
                // Si hay recurso seleccionado, usar disponibilidad real del primer recurso
                if (_recursoIds.isNotEmpty) {
                  final rid = _recursoIds.first;
                  final dispAsync = ref.watch(recursoDisponibilidadProvider(rid, _fecha));
                  return dispAsync.when(
                    loading: () => const Padding(padding: EdgeInsets.symmetric(vertical: 24), child: LoadingSpinner()),
                    error: (error, _) => ErrorView(message: apiErrorMessage(error, fallback: 'No se pudo cargar la disponibilidad.'), onRetry: () => ref.invalidate(recursoDisponibilidadProvider(rid, _fecha))),
                    data: (slots) {
                      if (slots.isEmpty) return const EmptyView(icon: LucideIcons.calendarX, message: 'No hay franjas disponibles para esta fecha.');
                      if (!isAuthenticated) return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [DisponibilidadSlotGrid(slots: slots), const SizedBox(height: AppSpacing.lg), FilledButton.icon(onPressed: () { Navigator.of(context).pop(); context.go(AppRoutes.login); }, icon: const Icon(LucideIcons.logIn, size: 18), label: const Text('Iniciá sesión para reservar'))]);
                      return _FormularioMulti(slots: slots, seleccion: _seleccion, capacidadMax: _capacidadMax(recursosAsync, zonasDelEspacio), asistentes: _asistentes, tipo: _tipo, enviando: _enviando, error: _error, onToggle: (i) => _alternarSlot(slots, i), onRango: _seleccionarRango, onAsistentesChanged: (v) => setState(() => _asistentes = v), onTipoChanged: (v) => setState(() => _tipo = v), onConfirmar: () => _reservar(slots));
                    },
                  );
                }
                // Si solo zonas, usar slots desde horario (sin endpoint)
                if (_zonaIds.isNotEmpty) {
                  // horario local: usar slotsDesdeHorario si existiera, por ahora mostrar mensaje y permitir seleccionar horario fijo 08-10 como demo
                  final fakeSlots = List.generate(12, (i) => DisponibilidadSlot(horaInicio: '${7 + i}:00'.padLeft(5,'0'), horaFin: '${8 + i}:00'.padLeft(5,'0'), estado: EstadoSlot.libre));
                  if (!isAuthenticated) return Column(children: [DisponibilidadSlotGrid(slots: fakeSlots), const SizedBox(height: AppSpacing.lg), FilledButton.icon(onPressed: () { Navigator.of(context).pop(); context.go(AppRoutes.login); }, icon: const Icon(LucideIcons.logIn, size: 18), label: const Text('Iniciá sesión para reservar'))]);
                  return _FormularioMulti(slots: fakeSlots, seleccion: _seleccion, capacidadMax: _capacidadMax(recursosAsync, zonasDelEspacio), asistentes: _asistentes, tipo: _tipo, enviando: _enviando, error: _error, onToggle: (i) => _alternarSlot(fakeSlots, i), onRango: _seleccionarRango, onAsistentesChanged: (v) => setState(() => _asistentes = v), onTipoChanged: (v) => setState(() => _tipo = v), onConfirmar: () => _reservar(fakeSlots));
                }
                return const EmptyView(icon: LucideIcons.info, message: 'Seleccioná al menos un recurso o una zona para ver disponibilidad.');
              }),
            ],
          ),
        ),
      ),
    );
  }
}

class _FormularioMulti extends StatelessWidget {
  const _FormularioMulti({required this.slots, required this.seleccion, required this.capacidadMax, required this.asistentes, required this.tipo, required this.enviando, required this.error, required this.onToggle, required this.onRango, required this.onAsistentesChanged, required this.onTipoChanged, required this.onConfirmar});
  final List<DisponibilidadSlot> slots;
  final Set<int> seleccion;
  final int capacidadMax;
  final int asistentes;
  final TipoReserva? tipo;
  final bool enviando;
  final String? error;
  final ValueChanged<int> onToggle;
  final void Function(int, int) onRango;
  final ValueChanged<int> onAsistentesChanged;
  final ValueChanged<TipoReserva?> onTipoChanged;
  final VoidCallback onConfirmar;
  @override
  Widget build(BuildContext context) {
    final hay = seleccion.isNotEmpty;
    String? resumen;
    if (hay) { final minIdx = seleccion.reduce((a, b) => a < b ? a : b); final maxIdx = seleccion.reduce((a, b) => a > b ? a : b); final h = seleccion.length; resumen = '${slots[minIdx].horaInicio}–${slots[maxIdx].horaFin} · ${h == 1 ? '1 hora' : '$h horas'} · ${asistentes == 1 ? '1 asistente' : '$asistentes asistentes'}'; }
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      SelectableSlotGrid(slots: slots, selectedIndices: seleccion, onToggle: onToggle, onRango: onRango),
      const SizedBox(height: AppSpacing.lg),
      const SlotLeyenda(),
      if (hay) ...[
        const SizedBox(height: AppSpacing.lg),
        Row(children: [Text('Asistentes', style: Theme.of(context).textTheme.bodyMedium), const Spacer(), IconButton.filledTonal(onPressed: asistentes > 1 ? () => onAsistentesChanged(asistentes - 1) : null, icon: const Icon(LucideIcons.minus, size: 16), constraints: const BoxConstraints.tightFor(width: 32, height: 32)), SizedBox(width: 32, child: Text('$asistentes', textAlign: TextAlign.center, style: Theme.of(context).textTheme.titleSmall)), IconButton.filledTonal(onPressed: asistentes < capacidadMax ? () => onAsistentesChanged(asistentes + 1) : null, icon: const Icon(LucideIcons.plus, size: 16), constraints: const BoxConstraints.tightFor(width: 32, height: 32))]),
        const SizedBox(height: AppSpacing.md),
        DropdownButtonFormField<TipoReserva?>(initialValue: tipo, decoration: const InputDecoration(labelText: 'Tipo de reserva (opcional)'), items: [const DropdownMenuItem(value: null, child: Text('Sin especificar')), for (final t in TipoReserva.values) DropdownMenuItem(value: t, child: Text(tipoReservaLabel(t)))], onChanged: onTipoChanged),
      ],
      if (error != null) ...[const SizedBox(height: AppSpacing.md), Container(width: double.infinity, padding: const EdgeInsets.all(AppSpacing.md), decoration: BoxDecoration(color: AppEstados.negativo.tinte, borderRadius: BorderRadius.circular(8), border: Border.all(color: AppEstados.negativo.borde.withValues(alpha: 0.4))), child: Text(error!, style: TextStyle(color: AppEstados.negativo.sobreTinte)))],
      const SizedBox(height: AppSpacing.lg),
      if (resumen != null) Container(width: double.infinity, padding: const EdgeInsets.all(AppSpacing.md), margin: const EdgeInsets.only(bottom: AppSpacing.md), decoration: BoxDecoration(color: AppColors.azul50, borderRadius: BorderRadius.circular(8)), child: Row(children: [const Icon(LucideIcons.calendarCheck, size: 16, color: AppColors.marca), const SizedBox(width: AppSpacing.sm), Expanded(child: Text(resumen, style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: AppColors.azul800, fontWeight: FontWeight.w600))) ])),
      SizedBox(width: double.infinity, child: FilledButton(onPressed: (!hay || enviando) ? null : onConfirmar, child: enviando ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Text('Reservar'))),
      if (!hay) ...[const SizedBox(height: AppSpacing.sm), Center(child: Text('Tocá una franja disponible, o arrastrá para elegir varias seguidas', style: Theme.of(context).textTheme.bodySmall, textAlign: TextAlign.center))],
    ]);
  }
}
