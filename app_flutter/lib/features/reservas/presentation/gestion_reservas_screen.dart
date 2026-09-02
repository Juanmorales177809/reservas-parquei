import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../../../core/domain/enums.dart';
import '../../../core/network/api_exception.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/app_typography.dart';
import '../../recursos/application/recursos_providers.dart';
import '../../espacios/application/espacios_providers.dart';
import '../../espacios/domain/espacio.dart';
import '../../../core/widgets/empty_view.dart';
import '../../../core/widgets/error_view.dart';
import '../../../core/widgets/loading_spinner.dart';
import '../../../core/widgets/staggered_entrance.dart';
import '../../laboratorios/domain/laboratorio.dart' show formatearHora;
import '../application/reservas_providers.dart';
import '../data/reservas_repository.dart';
import '../domain/reserva.dart';
import 'estado_reserva_badge.dart';

/// Espejo de la gestión de reservas de `frontend/src/app/admin/reservas/page.tsx`
/// (gestor/admin) — acotada a esta Fase 4 a: aprobar, rechazar, cancelar y
/// marcar asistencia. El backend ya filtra al laboratorio del gestor
/// (`get_managed_space_id`); esta pantalla no replica ese filtro.
class GestionReservasScreen extends ConsumerWidget {
  const GestionReservasScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final reservasAsync = ref.watch(reservasGestionProvider);

    return reservasAsync.when(
      loading: () => const LoadingSpinner(),
      error: (error, _) => ErrorView(
        message: apiErrorMessage(error, fallback: 'No se pudieron cargar las reservas.'),
        onRetry: () => ref.invalidate(reservasGestionProvider),
      ),
      data: (reservas) {
        if (reservas.isEmpty) {
          return const EmptyView(icon: LucideIcons.calendarDays, message: 'No hay reservas para gestionar.');
        }
        final ordenadas = [...reservas]..sort((a, b) {
            final prioridad = _prioridad(a.estado).compareTo(_prioridad(b.estado));
            if (prioridad != 0) return prioridad;
            return b.fecha.compareTo(a.fecha);
          });
        return RefreshIndicator(
          onRefresh: () => ref.refresh(reservasGestionProvider.future),
          child: ListView.separated(
            padding: const EdgeInsets.all(AppSpacing.lg),
            itemCount: ordenadas.length,
            separatorBuilder: (_, _) => const SizedBox(height: AppSpacing.md),
            itemBuilder: (context, index) => _GestionReservaCard(reserva: ordenadas[index]).staggerEntrance(index),
          ),
        );
      },
    );
  }

  static int _prioridad(EstadoReserva estado) => switch (estado) {
        EstadoReserva.esperando => 0,
        EstadoReserva.aprobada => 1,
        EstadoReserva.rechazada => 2,
        EstadoReserva.cancelada => 3,
      };
}

class _GestionReservaCard extends ConsumerStatefulWidget {
  const _GestionReservaCard({required this.reserva});

  final Reserva reserva;

  @override
  ConsumerState<_GestionReservaCard> createState() => _GestionReservaCardState();
}

class _GestionReservaCardState extends ConsumerState<_GestionReservaCard> {
  bool _enviando = false;

  Future<void> _cambiarEstado(EstadoReserva nuevo, {String? motivo}) async {
    setState(() => _enviando = true);
    try {
      await ref.read(reservasRepositoryProvider).cambiarEstado(widget.reserva.id, nuevo, motivo: motivo);
      ref.invalidate(reservasGestionProvider);
    } on Object catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(apiErrorMessage(e, fallback: 'No se pudo actualizar la reserva.'))),
        );
      }
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  Future<void> _proponerHorarios() async {
    final motivoCtrl = TextEditingController();
    final horariosCtrl = TextEditingController();
    final formKey = GlobalKey<FormState>();
    final result = await showDialog<Map<String, String>>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Proponer horarios alternativos'),
        content: Form(
          key: formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: motivoCtrl,
                autofocus: true,
                maxLength: 500,
                maxLines: 2,
                decoration: const InputDecoration(labelText: 'Motivo *', hintText: 'Ej. Sala ocupada en ese horario', border: OutlineInputBorder()),
                validator: (v) => (v == null || v.trim().isEmpty) ? 'Requerido' : null,
              ),
              const SizedBox(height: AppSpacing.md),
              TextFormField(
                controller: horariosCtrl,
                maxLength: 1000,
                maxLines: 3,
                decoration: const InputDecoration(labelText: 'Horarios disponibles *', hintText: 'Ej. 12/09 14:00-16:00; 13/09 08:00-10:00', border: OutlineInputBorder()),
                validator: (v) => (v == null || v.trim().isEmpty) ? 'Requerido' : null,
              ),
              const SizedBox(height: AppSpacing.xs),
              Text('La reserva quedará pendiente y el usuario recibirá un correo con estos horarios.', style: Theme.of(ctx).textTheme.bodySmall?.copyWith(color: AppColors.textoTerciario)),
            ],
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
          FilledButton(onPressed: () { if (formKey.currentState!.validate()) Navigator.pop(ctx, {'motivo': motivoCtrl.text.trim(), 'horarios': horariosCtrl.text.trim()}); }, child: const Text('Enviar propuesta')),
        ],
      ),
    );
    if (result == null) return;
    setState(() => _enviando = true);
    try {
      await ref.read(reservasRepositoryProvider).proponerHorarios(widget.reserva.id, motivo: result['motivo']!, horarios: result['horarios']!);
      ref.invalidate(reservasGestionProvider);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Propuesta enviada. El usuario fue notificado por correo.')));
    } on Object catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(apiErrorMessage(e, fallback: 'No se pudo enviar la propuesta.'))));
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  Future<void> _aceptarContrapropuesta() async {
    final reserva = widget.reserva;
    if (reserva.propuestaHorarios == null) return;
    // Pedir fecha/hora para aceptar: el técnico elige uno de los horarios contrapropuestos o ingresa manual
    final fechaCtrl = TextEditingController(text: reserva.fecha);
    final inicioCtrl = TextEditingController(text: reserva.horaInicio.substring(0, 5));
    final finCtrl = TextEditingController(text: reserva.horaFin.substring(0, 5));
    final formKey = GlobalKey<FormState>();
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Aceptar contrapropuesta'),
        content: Form(
          key: formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('Contrapropuesta: ${reserva.propuestaHorarios}', style: Theme.of(ctx).textTheme.bodySmall),
              const SizedBox(height: AppSpacing.md),
              TextFormField(controller: fechaCtrl, decoration: const InputDecoration(labelText: 'Fecha (YYYY-MM-DD)'), readOnly: true, onTap: () async { final ini = DateTime.tryParse(fechaCtrl.text) ?? DateTime.now(); final p = await showDatePicker(context: ctx, initialDate: ini, firstDate: DateTime(2020), lastDate: DateTime(2030)); if (p != null) fechaCtrl.text = '${p.year.toString().padLeft(4, '0')}-${p.month.toString().padLeft(2, '0')}-${p.day.toString().padLeft(2, '0')}'; }, validator: (v) => (v == null || v.isEmpty) ? 'Requerido' : null),
              const SizedBox(height: AppSpacing.md),
              TextFormField(controller: inicioCtrl, decoration: const InputDecoration(labelText: 'Hora inicio (HH:MM)'), validator: (v) => (v == null || !RegExp(r'^\d{2}:\d{2}$').hasMatch(v)) ? 'HH:MM' : null),
              const SizedBox(height: AppSpacing.md),
              TextFormField(controller: finCtrl, decoration: const InputDecoration(labelText: 'Hora fin (HH:MM)'), validator: (v) => (v == null || !RegExp(r'^\d{2}:\d{2}$').hasMatch(v)) ? 'HH:MM' : null),
            ],
          ),
        ),
        actions: [TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancelar')), FilledButton(onPressed: () => {if (formKey.currentState!.validate()) Navigator.pop(ctx, true)}, child: const Text('Aceptar'))],
      ),
    );
    if (ok != true) return;
    setState(() => _enviando = true);
    try {
      await ref.read(reservasRepositoryProvider).aceptarPropuesta(widget.reserva.id, fecha: DateTime.parse(fechaCtrl.text), horaInicio: inicioCtrl.text, horaFin: finCtrl.text);
      ref.invalidate(reservasGestionProvider);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Contrapropuesta aceptada y reserva re-agendada.')));
    } on Object catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(apiErrorMessage(e, fallback: 'No se pudo aceptar.'))));
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  Future<void> _rechazarContrapropuesta() async {
    final confirmar = await showDialog<bool>(context: context, builder: (ctx) => AlertDialog(title: const Text('Rechazar contrapropuesta'), content: const Text('¿Rechazar la contrapropuesta? La reserva seguirá pendiente.'), actions: [TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancelar')), FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Rechazar'))]));
    if (confirmar != true) return;
    setState(() => _enviando = true);
    try {
      await ref.read(reservasRepositoryProvider).rechazarPropuesta(widget.reserva.id);
      ref.invalidate(reservasGestionProvider);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Contrapropuesta rechazada.')));
    } on Object catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(apiErrorMessage(e, fallback: 'No se pudo rechazar.'))));
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  Future<void> _marcarAsistencia(bool asistio) async {
    setState(() => _enviando = true);
    try {
      await ref.read(reservasRepositoryProvider).marcarAsistencia(widget.reserva.id, asistio);
      ref.invalidate(reservasGestionProvider);
    } on Object catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(apiErrorMessage(e, fallback: 'No se pudo registrar la asistencia.'))),
        );
      }
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  Future<void> _editarReserva() async {
    final actualizado = await showDialog<bool>(
      context: context,
      builder: (_) => _EditarReservaDialog(reserva: widget.reserva),
    );
    if (actualizado == true) {
      ref.invalidate(reservasGestionProvider);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Reserva actualizada.')));
    }
  }

  Future<void> _eliminarReserva() async {
    final confirmar = await showDialog<bool>(context: context, builder: (ctx) => AlertDialog(title: const Text('Eliminar reserva'), content: Text('¿Eliminar la reserva #${widget.reserva.id}?'), actions: [TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancelar')), FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Eliminar'))]));
    if (confirmar != true) return;
    setState(() => _enviando = true);
    try {
      await ref.read(reservasRepositoryProvider).eliminar(widget.reserva.id);
      ref.invalidate(reservasGestionProvider);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Reserva eliminada.')));
    } on Object catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(apiErrorMessage(e, fallback: 'No se pudo eliminar la reserva.'))));
    } finally { if (mounted) setState(() => _enviando = false); }
  }

  @override
  Widget build(BuildContext context) {
    final reserva = widget.reserva;
    final textTheme = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;
    final nombresRecursos = reserva.recursos.map((r) => r.nombre).join(', ');

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    '${reserva.usuario.username} · ${reserva.laboratorio.nombre}',
                    style: textTheme.titleMedium,
                  ),
                ),
                EstadoReservaBadge(estado: reserva.estado),
              ],
            ),
            if (nombresRecursos.isNotEmpty) ...[
              const SizedBox(height: AppSpacing.xs),
              Text(nombresRecursos, style: textTheme.bodySmall?.copyWith(color: scheme.onSurfaceVariant)),
            ],
            const SizedBox(height: AppSpacing.sm),
            Wrap(
              spacing: AppSpacing.md,
              runSpacing: AppSpacing.xs,
              children: [
                _InfoChip(icon: LucideIcons.calendarDays, text: _formatearFecha(reserva.fecha)),
                _InfoChip(
                  icon: LucideIcons.clock,
                  text: '${formatearHora(reserva.horaInicio)}–${formatearHora(reserva.horaFin)}',
                ),
                _InfoChip(icon: LucideIcons.users, text: '${reserva.asistentes} asistentes'),
                if (reserva.tipo != null) _InfoChip(icon: LucideIcons.tag, text: tipoReservaLabel(reserva.tipo!)),
                if (reserva.tipoSolicitud != TipoSolicitud.reservaEnLaboratorio)
                  _InfoChip(icon: LucideIcons.mapPin, text: tipoSolicitudLabel(reserva.tipoSolicitud)),
                if (reserva.requiereApoyoAuxiliar)
                  const _InfoChip(icon: LucideIcons.userCog, text: 'Requiere auxiliar'),
              ],
            ),
            if (reserva.ubicacionUso != null && reserva.ubicacionUso!.isNotEmpty) ...[
              const SizedBox(height: AppSpacing.xs),
              Text(
                'Uso: ${reserva.ubicacionUso}',
                style: textTheme.bodySmall?.copyWith(color: scheme.onSurfaceVariant),
              ),
            ],
            if (reserva.descripcion != null && reserva.descripcion!.isNotEmpty) ...[
              const SizedBox(height: AppSpacing.xs),
              Text(
                reserva.descripcion!,
                style: textTheme.bodySmall?.copyWith(color: scheme.onSurfaceVariant),
              ),
            ],
            if (reserva.estado == EstadoReserva.rechazada && reserva.motivoRechazo != null) ...[
              const SizedBox(height: AppSpacing.sm),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(AppSpacing.sm),
                decoration: BoxDecoration(
                  color: AppEstados.negativo.tinte,
                  borderRadius: BorderRadius.circular(AppRadius.sm),
                  border: Border.all(color: AppEstados.negativo.borde.withValues(alpha: 0.4)),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(LucideIcons.info, size: 14, color: AppEstados.negativo.sobreTinte),
                    const SizedBox(width: AppSpacing.xs),
                    Expanded(
                      child: Text(
                        'Motivo: ${reserva.motivoRechazo}',
                        style: textTheme.bodySmall?.copyWith(color: AppEstados.negativo.sobreTinte),
                      ),
                    ),
                  ],
                ),
              ),
            ],
            // Fase C: propuesta del técnico o contrapropuesta del usuario (queda `esperando` con bloque activo)
            if (reserva.propuestaHorarios != null && reserva.propuestaPor != null) ...[
              const SizedBox(height: AppSpacing.sm),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(AppSpacing.sm),
                decoration: BoxDecoration(
                  color: reserva.propuestaPor == 'usuario' ? const Color(0xFFDBEAFE) : const Color(0xFFFEF3C7),
                  borderRadius: BorderRadius.circular(AppRadius.sm),
                  border: Border.all(color: reserva.propuestaPor == 'usuario' ? const Color(0xFF93C5FD) : const Color(0xFFFCD34D)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(reserva.propuestaPor == 'usuario' ? LucideIcons.reply : LucideIcons.clockArrowDown, size: 14, color: reserva.propuestaPor == 'usuario' ? const Color(0xFF1E40AF) : const Color(0xFF92400E)),
                        const SizedBox(width: AppSpacing.xs),
                        Text(reserva.propuestaPor == 'usuario' ? 'Contrapropuesta del usuario' : 'Propuesta enviada (esperando usuario)', style: Theme.of(context).textTheme.bodySmall?.copyWith(fontWeight: FontWeight.w700, color: reserva.propuestaPor == 'usuario' ? const Color(0xFF1E40AF) : const Color(0xFF92400E))),
                      ],
                    ),
                    if (reserva.propuestaMotivo != null) ...[const SizedBox(height: AppSpacing.xs), Text('Motivo: ${reserva.propuestaMotivo}', style: textTheme.bodySmall)],
                    const SizedBox(height: AppSpacing.xs),
                    Text('Horarios: ${reserva.propuestaHorarios}', style: textTheme.bodySmall?.copyWith(fontWeight: FontWeight.w600)),
                  ],
                ),
              ),
              if (reserva.propuestaPor == 'usuario') ...[
                const SizedBox(height: AppSpacing.sm),
                Row(
                  children: [
                    Expanded(child: FilledButton.icon(onPressed: _enviando ? null : _aceptarContrapropuesta, icon: const Icon(LucideIcons.check, size: 16), label: const Text('Aceptar contrapropuesta'))),
                    const SizedBox(width: AppSpacing.sm),
                    Expanded(child: OutlinedButton.icon(onPressed: _enviando ? null : _rechazarContrapropuesta, icon: const Icon(LucideIcons.x, size: 16), label: const Text('Rechazar'))),
                  ],
                ),
                const SizedBox(height: AppSpacing.xs),
                SizedBox(width: double.infinity, child: OutlinedButton.icon(onPressed: _enviando ? null : _proponerHorarios, icon: const Icon(LucideIcons.clock, size: 16), label: const Text('Proponer otros horarios'))),
              ] else ...[
                const SizedBox(height: AppSpacing.sm),
                SizedBox(width: double.infinity, child: OutlinedButton.icon(onPressed: _enviando ? null : _proponerHorarios, icon: const Icon(LucideIcons.clock, size: 16), label: const Text('Re-enviar propuesta'))),
              ],
            ],
            if (reserva.estado == EstadoReserva.esperando) ...[
              const SizedBox(height: AppSpacing.md),
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  FilledButton.icon(
                    onPressed: _enviando ? null : () => _cambiarEstado(EstadoReserva.aprobada),
                    icon: const Icon(LucideIcons.check, size: 16),
                    label: const Text('Aprobar'),
                  ),
                  const SizedBox(width: AppSpacing.sm),
                  PopupMenuButton<String>(
                    enabled: !_enviando,
                    tooltip: 'Más acciones',
                    icon: Icon(LucideIcons.ellipsisVertical, size: 18, color: AppColors.textoSecundario),
                    onSelected: (v) {
                      if (v == 'proponer') _proponerHorarios();
                      if (v == 'editar') _editarReserva();
                      if (v == 'eliminar') _eliminarReserva();
                    },
                    itemBuilder: (context) => [
                      const PopupMenuItem(
                        value: 'proponer',
                        child: Row(
                          children: [
                            Icon(LucideIcons.clock, size: 16, color: AppColors.textoSecundario),
                            SizedBox(width: AppSpacing.sm),
                            Text('Proponer horarios'),
                          ],
                        ),
                      ),
                      const PopupMenuItem(
                        value: 'editar',
                        child: Row(children: [Icon(LucideIcons.pencil, size: 16, color: AppColors.textoSecundario), SizedBox(width: AppSpacing.sm), Text('Editar')]),
                      ),
                      const PopupMenuItem(
                        value: 'eliminar',
                        child: Row(children: [Icon(LucideIcons.trash2, size: 16, color: AppColors.textoSecundario), SizedBox(width: AppSpacing.sm), Text('Eliminar')]),
                      ),
                    ],
                  ),
                ],
              ),
            ] else if (reserva.estado == EstadoReserva.aprobada) ...[
              const SizedBox(height: AppSpacing.md),
              Row(
                children: [
                  Text('Asistencia:', style: textTheme.bodySmall),
                  const SizedBox(width: AppSpacing.sm),
                  ChoiceChip(
                    label: const Text('Sí'),
                    selected: reserva.asistio == true,
                    onSelected: _enviando ? null : (_) => _marcarAsistencia(true),
                  ),
                  const SizedBox(width: AppSpacing.xs),
                  ChoiceChip(
                    label: const Text('No'),
                    selected: reserva.asistio == false,
                    onSelected: _enviando ? null : (_) => _marcarAsistencia(false),
                  ),
                  const Spacer(),
                  PopupMenuButton<String>(
                    enabled: !_enviando,
                    tooltip: 'Más acciones',
                    icon: Icon(LucideIcons.ellipsisVertical, size: 18, color: AppColors.textoSecundario),
                    onSelected: (v) {
                      if (v == 'cancelar') _cambiarEstado(EstadoReserva.cancelada);
                      if (v == 'editar') _editarReserva();
                      if (v == 'eliminar') _eliminarReserva();
                    },
                    itemBuilder: (context) => [
                      const PopupMenuItem(
                        value: 'cancelar',
                        child: Row(
                          children: [
                            Icon(LucideIcons.x, size: 16, color: AppColors.textoSecundario),
                            SizedBox(width: AppSpacing.sm),
                            Text('Cancelar'),
                          ],
                        ),
                      ),
                      const PopupMenuItem(
                        value: 'editar',
                        child: Row(children: [Icon(LucideIcons.pencil, size: 16, color: AppColors.textoSecundario), SizedBox(width: AppSpacing.sm), Text('Editar')]),
                      ),
                      const PopupMenuItem(
                        value: 'eliminar',
                        child: Row(children: [Icon(LucideIcons.trash2, size: 16, color: AppColors.textoSecundario), SizedBox(width: AppSpacing.sm), Text('Eliminar')]),
                      ),
                    ],
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _EditarReservaDialog extends ConsumerStatefulWidget {
  const _EditarReservaDialog({required this.reserva});
  final Reserva reserva;
  @override
  ConsumerState<_EditarReservaDialog> createState() => _EditarReservaDialogState();
}

class _EditarReservaDialogState extends ConsumerState<_EditarReservaDialog> {
  late final GlobalKey<FormState> _formKey;
  late final TextEditingController _fechaCtrl;
  late final TextEditingController _inicioCtrl;
  late final TextEditingController _finCtrl;
  late final TextEditingController _asistCtrl;
  late Set<int> _recursoIds;
  late Set<int> _espacioIds;
  bool _guardando = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _formKey = GlobalKey<FormState>();
    _fechaCtrl = TextEditingController(text: widget.reserva.fecha);
    _inicioCtrl = TextEditingController(text: widget.reserva.horaInicio.substring(0, 5));
    _finCtrl = TextEditingController(text: widget.reserva.horaFin.substring(0, 5));
    _asistCtrl = TextEditingController(text: '${widget.reserva.asistentes}');
    _recursoIds = widget.reserva.recursoIds.toSet();
    _espacioIds = widget.reserva.espacioIds.toSet();
  }

  @override
  void dispose() {
    _fechaCtrl.dispose();
    _inicioCtrl.dispose();
    _finCtrl.dispose();
    _asistCtrl.dispose();
    super.dispose();
  }

  Future<void> _guardar() async {
    if (!_formKey.currentState!.validate()) return;
    if (_recursoIds.isEmpty && _espacioIds.isEmpty) {
      setState(() => _error = 'Seleccioná al menos un recurso o un espacio.');
      return;
    }
    setState(() {
      _guardando = true;
      _error = null;
    });
    try {
      final parsed = DateTime.parse(_fechaCtrl.text);
      await ref.read(reservasRepositoryProvider).actualizar(
            widget.reserva.id,
            fecha: parsed,
            horaInicio: _inicioCtrl.text,
            horaFin: _finCtrl.text,
            asistentes: int.parse(_asistCtrl.text),
            recursoIds: _recursoIds.toList(),
            espacioIds: _espacioIds.toList(),
          );
      if (mounted) Navigator.pop(context, true);
    } on Object catch (e) {
      setState(() => _error = apiErrorMessage(e, fallback: 'No se pudo actualizar la reserva.'));
    } finally {
      if (mounted) setState(() => _guardando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final laboratorioId = widget.reserva.laboratorioId;
    final recursos = ref.watch(recursosPorLaboratorioProvider(laboratorioId));
    final espaciosAsync = ref.watch(espaciosGestionProvider);
    final espaciosDelLaboratorio = (espaciosAsync.value ?? <Espacio>[]).where((z) => z.laboratorioId == laboratorioId).toList();

    final cubiertos = <int>{};
    for (final z in espaciosDelLaboratorio) {
      if (_espacioIds.contains(z.id)) cubiertos.addAll(z.recursoIds);
    }
    final nombrePorId = <int, String>{for (final r in recursos) r.id: r.nombre};

    return AlertDialog(
      title: Text('Editar reserva #${widget.reserva.id}'),
      content: SizedBox(
        width: double.maxFinite,
        child: SingleChildScrollView(
          child: Form(
            key: _formKey,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                TextFormField(
                  controller: _fechaCtrl,
                  decoration: const InputDecoration(labelText: 'Fecha (YYYY-MM-DD)'),
                  readOnly: true,
                  onTap: () async {
                    final ini = DateTime.tryParse(_fechaCtrl.text) ?? DateTime.now();
                    final picked = await showDatePicker(context: context, initialDate: ini, firstDate: DateTime(2020), lastDate: DateTime(2030));
                    if (picked != null) {
                      setState(() => _fechaCtrl.text = '${picked.year.toString().padLeft(4, '0')}-${picked.month.toString().padLeft(2, '0')}-${picked.day.toString().padLeft(2, '0')}');
                    }
                  },
                  validator: (v) => (v == null || v.isEmpty) ? 'Requerido' : null,
                ),
                const SizedBox(height: AppSpacing.md),
                TextFormField(controller: _inicioCtrl, decoration: const InputDecoration(labelText: 'Hora inicio (HH:MM)'), validator: (v) => (v == null || !RegExp(r'^\d{2}:\d{2}$').hasMatch(v)) ? 'HH:MM' : null),
                const SizedBox(height: AppSpacing.md),
                TextFormField(controller: _finCtrl, decoration: const InputDecoration(labelText: 'Hora fin (HH:MM)'), validator: (v) => (v == null || !RegExp(r'^\d{2}:\d{2}$').hasMatch(v)) ? 'HH:MM' : null),
                const SizedBox(height: AppSpacing.md),
                TextFormField(controller: _asistCtrl, decoration: const InputDecoration(labelText: 'Asistentes'), keyboardType: TextInputType.number, validator: (v) { final n = int.tryParse(v ?? ''); if (n == null || n <=0) return '>0'; return null; }),
                const SizedBox(height: AppSpacing.lg),
                if (espaciosDelLaboratorio.isNotEmpty) ...[
                  Row(children: [const Icon(LucideIcons.mapPinned, size: 14, color: AppColors.marca), const SizedBox(width: AppSpacing.xs), Text('ZONAS', style: AppText.overline(color: AppColors.marca))]),
                  const SizedBox(height: AppSpacing.xs),
                  ...espaciosDelLaboratorio.map((z) {
                    final ids = z.recursoIds;
                    String subtitulo;
                    if (ids.isEmpty) {
                      final base = (z.descripcion != null && z.descripcion!.isNotEmpty) ? '${z.descripcion} · ' : '';
                      subtitulo = '${base}Sin equipos asignados';
                      if (z.capacidad != null) subtitulo = 'Cap. ${z.capacidad} · $subtitulo';
                    } else {
                      final nombres = ids.map((id) => nombrePorId[id] ?? 'Recurso $id').join(', ');
                      final base = (z.descripcion != null && z.descripcion!.isNotEmpty) ? '${z.descripcion} · ' : '';
                      subtitulo = z.capacidad != null ? 'Cap. ${z.capacidad} · $base Incluye: $nombres' : '$base Incluye: $nombres';
                    }
                    return CheckboxListTile(
                      contentPadding: EdgeInsets.zero,
                      dense: true,
                      title: Text(z.nombre, style: Theme.of(context).textTheme.bodyMedium),
                      subtitle: Text(subtitulo, style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppColors.textoTerciario)),
                      value: _espacioIds.contains(z.id),
                      onChanged: (v) => setState(() {
                        if (v == true) {
                          _espacioIds.add(z.id);
                        } else {
                          _espacioIds.remove(z.id);
                        }
                      }),
                    );
                  }),
                  const SizedBox(height: AppSpacing.md),
                ],
                if (recursos.isNotEmpty) ...[
                  Row(children: [const Icon(LucideIcons.boxes, size: 14, color: AppColors.marca), const SizedBox(width: AppSpacing.xs), Text(espaciosDelLaboratorio.isNotEmpty ? 'EQUIPOS ADICIONALES' : 'EQUIPOS', style: AppText.overline(color: AppColors.marca))]),
                  const SizedBox(height: AppSpacing.xs),
                  ...recursos.map((r) {
                    final cubierto = cubiertos.contains(r.id);
                    if (cubierto) {
                      final espaciosQueCubren = espaciosDelLaboratorio.where((z) => _espacioIds.contains(z.id) && z.recursoIds.contains(r.id)).map((z) => z.nombre).toList();
                      final espacioTxt = espaciosQueCubren.join(', ');
                      return CheckboxListTile(
                        contentPadding: EdgeInsets.zero,
                        dense: true,
                        title: Text(r.nombre, style: const TextStyle(color: AppColors.textoTerciario)),
                        subtitle: Text('${r.tipo.nombre} · cap. ${r.capacidad} — Incluido en ${espaciosQueCubren.length == 1 ? "espacio" : "espacios"} $espacioTxt', style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppColors.textoTerciario)),
                        value: true,
                        onChanged: null,
                        activeColor: AppEstados.positivo.borde,
                      );
                    }
                    return CheckboxListTile(
                      contentPadding: EdgeInsets.zero,
                      dense: true,
                      title: Text(r.nombre),
                      subtitle: Text('${r.tipo.nombre} · cap. ${r.capacidad}'),
                      value: _recursoIds.contains(r.id),
                      onChanged: (v) => setState(() {
                        if (v == true) {
                          _recursoIds.add(r.id);
                        } else {
                          _recursoIds.remove(r.id);
                        }
                      }),
                    );
                  }),
                  if (cubiertos.isNotEmpty) ...[
                    const SizedBox(height: AppSpacing.xs),
                    Row(crossAxisAlignment: CrossAxisAlignment.start, children: [const Icon(LucideIcons.info, size: 12, color: AppColors.textoTerciario), const SizedBox(width: AppSpacing.xs), Expanded(child: Text('Los equipos marcados como "Incluido" ya vienen con el espacio seleccionado.', style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppColors.textoTerciario, fontSize: 11)))]),
                  ],
                  const SizedBox(height: AppSpacing.md),
                ],
                if (_error != null) ...[
                  Container(width: double.infinity, padding: const EdgeInsets.all(AppSpacing.sm), decoration: BoxDecoration(color: AppEstados.negativo.tinte, borderRadius: BorderRadius.circular(AppRadius.sm), border: Border.all(color: AppEstados.negativo.borde.withValues(alpha: 0.4))), child: Text(_error!, style: TextStyle(color: AppEstados.negativo.sobreTinte))),
                  const SizedBox(height: AppSpacing.sm),
                ],
              ],
            ),
          ),
        ),
      ),
      actions: [
        TextButton(onPressed: _guardando ? null : () => Navigator.pop(context, false), child: const Text('Cancelar')),
        FilledButton(onPressed: _guardando ? null : _guardar, child: _guardando ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2)) : const Text('Guardar')),
      ],
    );
  }
}

class _InfoChip extends StatelessWidget {
  const _InfoChip({required this.icon, required this.text});

  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 14, color: scheme.onSurfaceVariant),
        const SizedBox(width: AppSpacing.xs),
        Text(text, style: Theme.of(context).textTheme.bodySmall),
      ],
    );
  }
}

/// `"YYYY-MM-DD"` -> `"DD/MM/YYYY"` — mismo criterio que
/// `mis_reservas_screen.dart` (texto plano, sin `DateTime`).
String _formatearFecha(String fechaIso) {
  final partes = fechaIso.split('-');
  if (partes.length != 3) return fechaIso;
  return '${partes[2]}/${partes[1]}/${partes[0]}';
}
