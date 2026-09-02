// ignore_for_file: prefer_final_fields, curly_braces_in_flow_control_structures
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

// `TipoReserva`/`tipoReservaLabel`/`tipoReservaToJson` ocultos: este sheet ya
// no usa el enum viejo para crear reservas (Fase 7, ver
// `features/tipos_reserva/`) -- sin el `hide`, el nombre `TipoReserva`
// colisionaría con la clase del catálogo real importada más abajo.
import '../../../core/domain/enums.dart' hide TipoReserva, tipoReservaLabel, tipoReservaToJson;
import '../../tipos_reserva/domain/tipo_reserva.dart';
import '../../../core/network/api_exception.dart';
import '../../../core/router/app_routes.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';
import '../../../core/widgets/empty_view.dart';
import '../../../core/widgets/error_view.dart';
import '../../../core/widgets/loading_spinner.dart';
import '../../../core/widgets/success_burst.dart';
import '../../auth/application/auth_provider.dart';
import '../../laboratorios/domain/disponibilidad_slot.dart';
import '../../laboratorios/domain/laboratorio.dart';
import '../../laboratorios/presentation/disponibilidad_slot_grid.dart';
import '../../laboratorios/presentation/slot_chip.dart';
import '../../lista_espera/data/lista_espera_repository.dart';
import '../../recursos/application/recursos_providers.dart';
import '../../espacios/application/espacios_providers.dart';
import '../../tipos_reserva/application/tipos_reserva_providers.dart';
import '../../motivos_solicitud/application/motivos_solicitud_providers.dart';
import '../application/reservas_providers.dart';
import '../data/reservas_repository.dart';
import 'selectable_slot_grid.dart';

/// Sheet multi-eje para crear una reserva completa (Fase P2).
/// Cubre `recurso_ids`/`espacio_ids`/`tipo` y deja preparado `acompanantes` (paridad con `frontend/src/app/laboratorios/page.tsx:246`).
/// Se abre desde `LaboratorioDetalleScreen` con el `Laboratorio` completo, no con un solo `Recurso`.
class LaboratorioReservaSheet extends ConsumerStatefulWidget {
  const LaboratorioReservaSheet({
    required this.laboratorio,
    this.tipoSolicitud = TipoSolicitud.reservaEnLaboratorio,
    super.key,
  });
  final Laboratorio laboratorio;
  // Fase B: motivo elegido en `_MotivoSolicitudDialog` (LaboratorioDetalleScreen)
  // antes de abrir este sheet. Default al motivo de siempre para no romper
  // los callers existentes (ninguno lo pasaba antes de la Fase B).
  final TipoSolicitud tipoSolicitud;
  @override
  ConsumerState<LaboratorioReservaSheet> createState() => _LaboratorioReservaSheetState();
}

class _LaboratorioReservaSheetState extends ConsumerState<LaboratorioReservaSheet> {
  late DateTime _fecha;
  Set<int> _recursoIds = {};
  Set<int> _espacioIds = {};
  final List<Map<String, String>> _acompanantes = [];
  final _nombreCtrl = TextEditingController();
  final _correoCtrl = TextEditingController();
  final _descripcionCtrl = TextEditingController();
  final _ubicacionUsoCtrl = TextEditingController();
  Set<int> _seleccion = {};
  int _asistentes = 1;
  // Fase 7: catálogo real por laboratorio (reemplaza el enum fijo viejo,
  // ver `features/tipos_reserva/`) -- `null` si no se elige ninguno.
  int? _tipoReservaId;
  int? _motivoSolicitudId;
  bool _requiereApoyoAuxiliar = false;
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
    _ubicacionUsoCtrl.dispose();
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

  int _capacidadMax(List<dynamic> recursos, List<dynamic> espacios) {
    final caps = <int>[];
    caps.add(widget.laboratorio.capacidad);
    for (final r in recursos) { if (_recursoIds.contains(r.id)) caps.add(r.capacidad); }
    for (final z in espacios) { if (_espacioIds.contains(z.id) && z.capacidad != null) caps.add(z.capacidad as int); }
    if (caps.isEmpty) return 999;
    return caps.reduce((a, b) => a < b ? a : b);
  }

  Future<void> _reservar(List<DisponibilidadSlot> slots) async {
    if (_recursoIds.isEmpty && _espacioIds.isEmpty) { setState(() => _error = 'Seleccioná al menos un recurso o un espacio.'); return; }
    final tipoSolicitudActual = _motivoSolicitudId != null ? widget.tipoSolicitud : widget.tipoSolicitud;
    // Si hay motivo seleccionado, usar su codigo para determinar si requiere ubicacion
    // Por ahora mantenemos la validacion original con el enum del widget
    if (tipoSolicitudActual == TipoSolicitud.reservaFueraLaboratorio && _ubicacionUsoCtrl.text.trim().isEmpty) {
      setState(() => _error = 'Indicá dónde se va a usar el equipo.');
      return;
    }
    final minIdx = _seleccion.reduce((a, b) => a < b ? a : b);
    final maxIdx = _seleccion.reduce((a, b) => a > b ? a : b);
    setState(() { _enviando = true; _error = null; });
    try {
      await ref.read(reservasRepositoryProvider).crear(
            recursoIds: _recursoIds.toList(),
            espacioIds: _espacioIds.toList(),
            acompanantes: List.of(_acompanantes),
            fecha: _fecha,
            horaInicio: slots[minIdx].horaInicio,
            horaFin: slots[maxIdx].horaFin,
            asistentes: _asistentes,
            tipoReservaId: _tipoReservaId,
            motivoSolicitudId: _motivoSolicitudId,
            descripcion: _descripcionCtrl.text.trim().isEmpty ? null : _descripcionCtrl.text.trim(),
            tipoSolicitud: widget.tipoSolicitud,
            ubicacionUso: widget.tipoSolicitud == TipoSolicitud.reservaFueraLaboratorio
                ? _ubicacionUsoCtrl.text.trim()
                : null,
            requiereApoyoAuxiliar: _requiereApoyoAuxiliar,
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
      if (esConflicto) {
        for (final id in _recursoIds) { ref.invalidate(recursoDisponibilidadProvider(id, _fecha)); }
        if (_recursoIds.isNotEmpty && mounted) {
          _ofrecerListaEspera(horaInicio: slots[minIdx].horaInicio, horaFin: slots[maxIdx].horaFin);
        }
      }
    } finally { if (mounted) setState(() => _enviando = false); }
  }

  /// Solo a nivel de recurso (no de espacio) -- mismo alcance que
  /// `ListaEspera` en el backend (ver `backend/CLAUDE.md`).
  void _ofrecerListaEspera({required String horaInicio, required String horaFin}) {
    ScaffoldMessenger.of(context)
      ..removeCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: const Text('¿Querés que te avisemos si se libera?'),
          duration: const Duration(seconds: 8),
          // Mismo motivo que en `configuracion_laboratorio_screen.dart`: un
          // SnackBar con `action` persiste por defecto y no se autocierra.
          persist: false,
          action: SnackBarAction(
            label: 'Lista de espera',
            onPressed: () => _anotarseListaEspera(horaInicio: horaInicio, horaFin: horaFin),
          ),
        ),
      );
  }

  Future<void> _anotarseListaEspera({required String horaInicio, required String horaFin}) async {
    final repo = ref.read(listaEsperaRepositoryProvider);
    var exitosas = 0;
    for (final recursoId in _recursoIds) {
      try {
        await repo.crear(recursoId: recursoId, fecha: _fecha, horaInicio: horaInicio, horaFin: horaFin);
        exitosas++;
      } catch (_) {
        // Mejor esfuerzo: si un recurso falla (ya anotado, etc.) no bloquea
        // los demás -- se informa el resultado agregado al final.
      }
    }
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          exitosas > 0 ? 'Te anotamos en la lista de espera. Te avisamos por correo si se libera.' : 'No se pudo anotar en la lista de espera.',
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final laboratorio = widget.laboratorio;
    final recursosAsync = ref.watch(recursosPorLaboratorioProvider(laboratorio.id));
    final espaciosAsync = ref.watch(espaciosGestionProvider);
    final tiposReserva = ref.watch(tiposReservaProvider(laboratorio.id)).value ?? const [];
    final motivos = ref.watch(motivosSolicitudProvider(laboratorio.id)).value ?? const [];
    final isAuthenticated = ref.watch(isAuthenticatedProvider);
    final scheme = Theme.of(context).colorScheme;

    // filtrar espacios del laboratorio actual (espaciosGestion trae todas si admin, pero gestor ya filtra por laboratorio)
    List<dynamic> espaciosDelLaboratorio = [];
    final espaciosVal = espaciosAsync.value;
    if (espaciosVal != null) espaciosDelLaboratorio = espaciosVal.where((z) => z.laboratorioId == laboratorio.id).toList();

    // Feature A: recursos ya cubiertos por los espacios seleccionados.
    // Si un espacio marcado incluye ciertos recursos, esos recursos ya vienen
    // con el espacio y no hace falta marcarlos de nuevo en "Equipos adicionales".
    final recursosCubiertosPorEspacios = <int>{};
    for (final z in espaciosDelLaboratorio) {
      if (_espacioIds.contains(z.id as int)) {
        recursosCubiertosPorEspacios.addAll((z.recursoIds as List<int>));
      }
    }
    final recursoNombrePorId = <int, String>{
      for (final r in recursosAsync) r.id: r.nombre,
    };

    return SafeArea(
      child: Padding(
        padding: EdgeInsets.only(left: AppSpacing.lg, right: AppSpacing.lg, top: AppSpacing.sm, bottom: MediaQuery.of(context).viewInsets.bottom + AppSpacing.lg),
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(child: Container(width: 36, height: 4, margin: const EdgeInsets.only(bottom: AppSpacing.lg), decoration: BoxDecoration(color: scheme.outlineVariant, borderRadius: BorderRadius.circular(999)))),
              Text('Reservar en ${laboratorio.nombre}', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: AppSpacing.xs),
              if (motivos.isNotEmpty) ...[
                DropdownButtonFormField<int?>(
                  initialValue: _motivoSolicitudId,
                  decoration: const InputDecoration(labelText: 'Motivo de solicitud'),
                  items: [
                    const DropdownMenuItem(value: null, child: Text('Seleccionar motivo')),
                    for (final m in motivos) DropdownMenuItem(value: m.id, child: Text(m.nombre)),
                  ],
                  onChanged: (v) => setState(() => _motivoSolicitudId = v),
                ),
                const SizedBox(height: AppSpacing.md),
              ] else
                Text(tipoSolicitudLabel(widget.tipoSolicitud), style: Theme.of(context).textTheme.bodySmall?.copyWith(color: scheme.onSurfaceVariant)),
              const SizedBox(height: AppSpacing.md),
              OutlinedButton.icon(onPressed: _elegirFecha, icon: const Icon(LucideIcons.calendar, size: 18), label: Text('${_fecha.day}/${_fecha.month}/${_fecha.year}')),
              const SizedBox(height: AppSpacing.lg),
              // ── Feature A: Espacios (incluye sus equipos) ──
              // Sin ModalidadLaboratorio (removido, ver Fase 3 de
              // ~/.claude/plans/dazzling-wobbling-zebra.md): la sección se
              // muestra si el laboratorio efectivamente tiene espacios definidas,
              // en vez de por una configuración explícita.
              if (espaciosDelLaboratorio.isNotEmpty) ...[
                Row(
                  children: [
                    const Icon(LucideIcons.mapPinned, size: 16, color: AppColors.marca),
                    const SizedBox(width: AppSpacing.sm),
                    Text('ZONAS — INCLUYE SUS EQUIPOS', style: AppText.overline(color: AppColors.marca)),
                  ],
                ),
                const SizedBox(height: AppSpacing.xs),
                Text(
                  'Elegí el espacio donde vas a trabajar. Los equipos asignados a ese espacio ya están incluidos en tu reserva.',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppColors.textoTerciario),
                ),
                const SizedBox(height: AppSpacing.sm),
                ...espaciosDelLaboratorio.map((z) {
                  final ids = (z.recursoIds as List<int>);
                  final desc = z.descripcion as String?;
                  String subtitulo;
                  if (ids.isEmpty) {
                    final base = (desc != null && desc.isNotEmpty) ? '$desc · ' : '';
                    subtitulo = '${base}Sin equipos asignados';
                    if (z.capacidad != null) subtitulo = 'Cap. ${z.capacidad} · $subtitulo';
                  } else {
                    final nombres = ids.map((id) => recursoNombrePorId[id] ?? 'Recurso $id').join(', ');
                    final base = (desc != null && desc.isNotEmpty) ? '$desc · ' : '';
                    final incluye = 'Incluye: $nombres';
                    subtitulo = z.capacidad != null ? 'Cap. ${z.capacidad} · $base$incluye' : '$base$incluye';
                  }
                    return CheckboxListTile(
                      contentPadding: EdgeInsets.zero,
                      title: Text(z.nombre as String),
                      subtitle: Text(subtitulo, style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppColors.textoTerciario)),
                      value: _espacioIds.contains(z.id as int),
                      onChanged: (v) => setState(() {
                        final ids = (z.recursoIds as List<int>);
                        if (v == true) {
                          _espacioIds.add(z.id as int);
                          // Pre-seleccionar recursos del espacio pero dejarlos editables
                          _recursoIds.addAll(ids);
                        } else {
                          _espacioIds.remove(z.id as int);
                          // Al destildar espacio, quitar solo sus recursos si no están compartidos con otro espacio tildado
                          final otrosRecursos = <int>{};
                          for (final otro in espaciosDelLaboratorio) {
                            if (_espacioIds.contains(otro.id as int)) otrosRecursos.addAll(otro.recursoIds as List<int>);
                          }
                          for (final rid in ids) {
                            if (!otrosRecursos.contains(rid)) _recursoIds.remove(rid);
                          }
                        }
                        _seleccion = {};
                      }),
                  );
                }),
                const SizedBox(height: AppSpacing.lg),
              ],
              // ── Feature A: Equipos adicionales de este laboratorio ──
              if (recursosAsync.isNotEmpty) ...[
                Row(
                  children: [
                    const Icon(LucideIcons.boxes, size: 16, color: AppColors.marca),
                    const SizedBox(width: AppSpacing.sm),
                    Expanded(
                      child: Text(
                        espaciosDelLaboratorio.isNotEmpty
                            ? 'EQUIPOS ADICIONALES DE ESTE LABORATORIO'
                            : 'EQUIPOS DE ESTE LABORATORIO',
                        style: AppText.overline(color: AppColors.marca),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: AppSpacing.xs),
                Text(
                  _espacioIds.isNotEmpty
                      ? '¿Necesitás algo más que lo que ya trae el espacio seleccionado? Podés sumar equipos sueltos del mismo laboratorio.'
                      : 'Seleccioná los equipos que necesitás para tu reserva. Podés combinarlos con espacios si el laboratorio lo permite.',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppColors.textoTerciario),
                ),
                const SizedBox(height: AppSpacing.sm),
                ...recursosAsync.map((r) {
                  final estaCubierto = recursosCubiertosPorEspacios.contains(r.id);
                  final estaSeleccionado = _recursoIds.contains(r.id);
                  if (estaCubierto && !estaSeleccionado) {
                    // Pre-seleccionado por el espacio pero aún no en _recursoIds — mostrar como incluido pero editable
                    final espaciosQueCubren = espaciosDelLaboratorio
                        .where((z) => _espacioIds.contains(z.id as int) && (z.recursoIds as List<int>).contains(r.id))
                        .map((z) => z.nombre as String)
                        .toList();
                    final espacioTxt = espaciosQueCubren.join(', ');
                    return CheckboxListTile(
                      contentPadding: EdgeInsets.zero,
                      title: Text(r.nombre),
                      subtitle: Text(
                        '${r.tipo.nombre} · cap. ${r.capacidad} — Incluido en ${espaciosQueCubren.length == 1 ? "espacio" : "espacios"} $espacioTxt (podés quitarlo)',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppColors.textoTerciario),
                      ),
                      value: false,
                      onChanged: (v) => setState(() {
                        if (v == true) {
                          _recursoIds.add(r.id);
                        } else {
                          _recursoIds.remove(r.id);
                        }
                        _seleccion = {};
                      }),
                      activeColor: AppEstados.positivo.borde,
                      controlAffinity: ListTileControlAffinity.leading,
                    );
                  }
                  if (estaCubierto && estaSeleccionado) {
                    final espaciosQueCubren = espaciosDelLaboratorio
                        .where((z) => _espacioIds.contains(z.id as int) && (z.recursoIds as List<int>).contains(r.id))
                        .map((z) => z.nombre as String)
                        .toList();
                    final espacioTxt = espaciosQueCubren.join(', ');
                    return CheckboxListTile(
                      contentPadding: EdgeInsets.zero,
                      title: Text(r.nombre),
                      subtitle: Text(
                        '${r.tipo.nombre} · cap. ${r.capacidad} — Incluido en ${espaciosQueCubren.length == 1 ? "espacio" : "espacios"} $espacioTxt',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppColors.textoTerciario),
                      ),
                      value: true,
                      onChanged: (v) => setState(() {
                        if (v == true) {
                          _recursoIds.add(r.id);
                        } else {
                          _recursoIds.remove(r.id);
                        }
                        _seleccion = {};
                      }),
                      activeColor: AppEstados.positivo.borde,
                      controlAffinity: ListTileControlAffinity.leading,
                    );
                  }
                  return CheckboxListTile(
                    contentPadding: EdgeInsets.zero,
                    title: Text(r.nombre),
                    subtitle: Text('${r.tipo.nombre} · cap. ${r.capacidad}'),
                    value: _recursoIds.contains(r.id),
                    onChanged: (v) => setState(() {
                      if (v == true) {
                        _recursoIds.add(r.id);
                      } else {
                        _recursoIds.remove(r.id);
                      }
                      _seleccion = {};
                    }),
                  );
                }),
                if (recursosCubiertosPorEspacios.isNotEmpty) ...[
                  const SizedBox(height: AppSpacing.xs),
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Icon(LucideIcons.info, size: 14, color: AppColors.textoTerciario),
                      const SizedBox(width: AppSpacing.xs),
                      Expanded(
                        child: Text(
                          'Los equipos marcados como "Incluido" ya vienen con el espacio seleccionado, no hace falta agregarlos de nuevo.',
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppColors.textoTerciario, fontSize: 11),
                        ),
                      ),
                    ],
                  ),
                ],
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
              if (widget.tipoSolicitud == TipoSolicitud.reservaFueraLaboratorio) ...[
                const SizedBox(height: AppSpacing.md),
                Text('¿Dónde se va a usar el equipo?', style: Theme.of(context).textTheme.titleSmall),
                const SizedBox(height: AppSpacing.sm),
                TextField(
                  controller: _ubicacionUsoCtrl,
                  decoration: const InputDecoration(hintText: 'Ej. Auditorio del bloque 5', isDense: true),
                ),
              ],
              SwitchListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('¿Requiere apoyo del auxiliar del laboratorio?'),
                value: _requiereApoyoAuxiliar,
                onChanged: (v) => setState(() => _requiereApoyoAuxiliar = v),
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
                      return _FormularioMulti(slots: slots, seleccion: _seleccion, capacidadMax: _capacidadMax(recursosAsync, espaciosDelLaboratorio), asistentes: _asistentes, tiposReserva: tiposReserva, tipoReservaId: _tipoReservaId, enviando: _enviando, error: _error, onToggle: (i) => _alternarSlot(slots, i), onRango: _seleccionarRango, onAsistentesChanged: (v) => setState(() => _asistentes = v), onTipoReservaIdChanged: (v) => setState(() => _tipoReservaId = v), onConfirmar: () => _reservar(slots));
                    },
                  );
                }
                // Si solo espacios, usar slots desde horario (sin endpoint)
                if (_espacioIds.isNotEmpty) {
                  // horario local: usar slotsDesdeHorario si existiera, por ahora mostrar mensaje y permitir seleccionar horario fijo 08-10 como demo
                  final fakeSlots = List.generate(12, (i) => DisponibilidadSlot(horaInicio: '${7 + i}:00'.padLeft(5,'0'), horaFin: '${8 + i}:00'.padLeft(5,'0'), estado: EstadoSlot.libre));
                  if (!isAuthenticated) return Column(children: [DisponibilidadSlotGrid(slots: fakeSlots), const SizedBox(height: AppSpacing.lg), FilledButton.icon(onPressed: () { Navigator.of(context).pop(); context.go(AppRoutes.login); }, icon: const Icon(LucideIcons.logIn, size: 18), label: const Text('Iniciá sesión para reservar'))]);
                  return _FormularioMulti(slots: fakeSlots, seleccion: _seleccion, capacidadMax: _capacidadMax(recursosAsync, espaciosDelLaboratorio), asistentes: _asistentes, tiposReserva: tiposReserva, tipoReservaId: _tipoReservaId, enviando: _enviando, error: _error, onToggle: (i) => _alternarSlot(fakeSlots, i), onRango: _seleccionarRango, onAsistentesChanged: (v) => setState(() => _asistentes = v), onTipoReservaIdChanged: (v) => setState(() => _tipoReservaId = v), onConfirmar: () => _reservar(fakeSlots));
                }
                return const EmptyView(icon: LucideIcons.info, message: 'Seleccioná al menos un recurso o un espacio para ver disponibilidad.');
              }),
            ],
          ),
        ),
      ),
    );
  }
}

class _FormularioMulti extends StatelessWidget {
  const _FormularioMulti({required this.slots, required this.seleccion, required this.capacidadMax, required this.asistentes, required this.tiposReserva, required this.tipoReservaId, required this.enviando, required this.error, required this.onToggle, required this.onRango, required this.onAsistentesChanged, required this.onTipoReservaIdChanged, required this.onConfirmar});
  final List<DisponibilidadSlot> slots;
  final Set<int> seleccion;
  final int capacidadMax;
  final int asistentes;
  final List<TipoReserva> tiposReserva;
  final int? tipoReservaId;
  final bool enviando;
  final String? error;
  final ValueChanged<int> onToggle;
  final void Function(int, int) onRango;
  final ValueChanged<int> onAsistentesChanged;
  final ValueChanged<int?> onTipoReservaIdChanged;
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
        // Fase 7: catálogo real por laboratorio -- si no definió ninguno, el
        // campo no se muestra (es opcional, sin valores fijos que ofrecer).
        if (tiposReserva.isNotEmpty)
          DropdownButtonFormField<int?>(initialValue: tipoReservaId, decoration: const InputDecoration(labelText: 'Tipo de reserva (opcional)'), items: [const DropdownMenuItem(value: null, child: Text('Sin especificar')), for (final t in tiposReserva) DropdownMenuItem(value: t.id, child: Text(t.nombre))], onChanged: onTipoReservaIdChanged),
      ],
      if (error != null) ...[const SizedBox(height: AppSpacing.md), Container(width: double.infinity, padding: const EdgeInsets.all(AppSpacing.md), decoration: BoxDecoration(color: AppEstados.negativo.tinte, borderRadius: BorderRadius.circular(8), border: Border.all(color: AppEstados.negativo.borde.withValues(alpha: 0.4))), child: Text(error!, style: TextStyle(color: AppEstados.negativo.sobreTinte)))],
      const SizedBox(height: AppSpacing.lg),
      if (resumen != null) Container(width: double.infinity, padding: const EdgeInsets.all(AppSpacing.md), margin: const EdgeInsets.only(bottom: AppSpacing.md), decoration: BoxDecoration(color: AppColors.azul50, borderRadius: BorderRadius.circular(8)), child: Row(children: [const Icon(LucideIcons.calendarCheck, size: 16, color: AppColors.marca), const SizedBox(width: AppSpacing.sm), Expanded(child: Text(resumen, style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: AppColors.azul800, fontWeight: FontWeight.w600))) ])),
      SizedBox(width: double.infinity, child: FilledButton(onPressed: (!hay || enviando) ? null : onConfirmar, child: enviando ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Text('Reservar'))),
      if (!hay) ...[const SizedBox(height: AppSpacing.sm), Center(child: Text('Tocá una franja disponible, o arrastrá para elegir varias seguidas', style: Theme.of(context).textTheme.bodySmall, textAlign: TextAlign.center))],
    ]);
  }
}
