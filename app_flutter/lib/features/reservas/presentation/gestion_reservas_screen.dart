import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../../../core/domain/enums.dart';
import '../../../core/network/api_exception.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/widgets/empty_view.dart';
import '../../../core/widgets/error_view.dart';
import '../../../core/widgets/loading_spinner.dart';
import '../../../core/widgets/staggered_entrance.dart';
import '../../espacios/domain/espacio.dart' show formatearHora;
import '../application/reservas_providers.dart';
import '../data/reservas_repository.dart';
import '../domain/reserva.dart';
import 'estado_reserva_badge.dart';

/// Espejo de la gestión de reservas de `frontend/src/app/admin/reservas/page.tsx`
/// (gestor/admin) — acotada a esta Fase 4 a: aprobar, rechazar, cancelar y
/// marcar asistencia. El backend ya filtra al espacio del gestor
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

  Future<void> _pedirMotivoYRechazar() async {
    final controller = TextEditingController();
    final formKey = GlobalKey<FormState>();
    final motivo = await showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Rechazar reserva'),
        content: Form(
          key: formKey,
          child: TextFormField(
            controller: controller,
            autofocus: true,
            maxLength: 500,
            maxLines: 3,
            decoration: const InputDecoration(
              labelText: 'Motivo *',
              hintText: 'Explicá por qué se rechaza',
              border: OutlineInputBorder(),
            ),
            validator: (v) {
              if (v == null || v.trim().isEmpty) return 'El motivo es obligatorio';
              if (v.trim().length > 500) return 'Máx. 500 caracteres';
              return null;
            },
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
          FilledButton(
            onPressed: () {
              if (formKey.currentState!.validate()) Navigator.pop(ctx, controller.text.trim());
            },
            child: const Text('Rechazar'),
          ),
        ],
      ),
    );
    if (motivo == null) return;
    await _cambiarEstado(EstadoReserva.rechazada, motivo: motivo);
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
                    '${reserva.usuario.username} · ${reserva.espacio.nombre}',
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
              ],
            ),
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
                      if (v == 'rechazar') _pedirMotivoYRechazar();
                    },
                    itemBuilder: (context) => [
                      const PopupMenuItem(
                        value: 'rechazar',
                        child: Row(
                          children: [
                            Icon(LucideIcons.x, size: 16, color: AppColors.textoSecundario),
                            SizedBox(width: AppSpacing.sm),
                            Text('Rechazar'),
                          ],
                        ),
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
