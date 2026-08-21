import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../../../core/network/api_exception.dart';
import '../../../core/router/app_routes.dart';
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

/// Espejo de la lista de "mis reservas" de `frontend/src/app/espacios/page.tsx`
/// (hoy embebida en esa página vía `GET /reservas/mis-reservas`) — acá vive
/// en su propia pantalla, coherente con el resto de la navegación de la app.
class MisReservasScreen extends ConsumerWidget {
  const MisReservasScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final reservasAsync = ref.watch(misReservasProvider);

    return reservasAsync.when(
      loading: () => const LoadingSpinner(),
      error: (error, _) => ErrorView(
        message: apiErrorMessage(error, fallback: 'No se pudieron cargar tus reservas.'),
        onRetry: () => ref.invalidate(misReservasProvider),
      ),
      data: (reservas) {
        if (reservas.isEmpty) {
          return EmptyView(
            icon: LucideIcons.calendarX,
            message: 'Todavía no tenés reservas',
            detalle: 'Elegí un espacio, mirá su disponibilidad y reservá una franja horaria.',
            accion: FilledButton.icon(
              onPressed: () => context.go(AppRoutes.espacios),
              icon: const Icon(LucideIcons.building2, size: 18),
              label: const Text('Ver espacios'),
            ),
          );
        }
        final ordenadas = [...reservas]..sort((a, b) => b.fecha.compareTo(a.fecha));
        return RefreshIndicator(
          onRefresh: () => ref.refresh(misReservasProvider.future),
          child: ListView.separated(
            padding: const EdgeInsets.all(AppSpacing.lg),
            itemCount: ordenadas.length,
            separatorBuilder: (_, _) => const SizedBox(height: AppSpacing.md),
            itemBuilder: (context, index) => _ReservaCard(reserva: ordenadas[index]).staggerEntrance(index),
          ),
        );
      },
    );
  }
}

class _ReservaCard extends ConsumerStatefulWidget {
  const _ReservaCard({required this.reserva});

  final Reserva reserva;

  @override
  ConsumerState<_ReservaCard> createState() => _ReservaCardState();
}

class _ReservaCardState extends ConsumerState<_ReservaCard> {
  bool _cancelando = false;

  Future<void> _confirmarCancelacion() async {
    final confirmar = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('¿Cancelar esta reserva?'),
        content: Text(
          '${widget.reserva.espacio.nombre} · ${_formatearFecha(widget.reserva.fecha)} · '
          '${formatearHora(widget.reserva.horaInicio)}–${formatearHora(widget.reserva.horaFin)}',
        ),
        actions: [
          TextButton(onPressed: () => Navigator.of(context).pop(false), child: const Text('Volver')),
          FilledButton.tonal(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Cancelar reserva'),
          ),
        ],
      ),
    );
    if (confirmar != true) return;

    setState(() => _cancelando = true);
    try {
      await ref.read(reservasRepositoryProvider).cancelar(widget.reserva.id);
      ref.invalidate(misReservasProvider);
    } on Object catch (e) {
      if (mounted) {
        final mensaje = apiErrorMessage(e, fallback: 'No se pudo cancelar la reserva.');
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(mensaje)));
      }
    } finally {
      if (mounted) setState(() => _cancelando = false);
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
                Expanded(child: Text(reserva.espacio.nombre, style: textTheme.titleMedium)),
                EstadoReservaBadge(estado: reserva.estado),
              ],
            ),
            if (nombresRecursos.isNotEmpty) ...[
              const SizedBox(height: AppSpacing.xs),
              Text(nombresRecursos, style: textTheme.bodySmall?.copyWith(color: scheme.onSurfaceVariant)),
            ],
            const SizedBox(height: AppSpacing.sm),
            Row(
              children: [
                Icon(LucideIcons.calendarDays, size: 16, color: scheme.onSurfaceVariant),
                const SizedBox(width: AppSpacing.xs),
                Text(_formatearFecha(reserva.fecha), style: textTheme.bodyMedium),
                const SizedBox(width: AppSpacing.md),
                Icon(LucideIcons.clock, size: 16, color: scheme.onSurfaceVariant),
                const SizedBox(width: AppSpacing.xs),
                Text(
                  '${formatearHora(reserva.horaInicio)}–${formatearHora(reserva.horaFin)}',
                  style: textTheme.bodyMedium,
                ),
              ],
            ),
            const SizedBox(height: AppSpacing.xs),
            Row(
              children: [
                Icon(LucideIcons.users, size: 16, color: scheme.onSurfaceVariant),
                const SizedBox(width: AppSpacing.xs),
                Text('${reserva.asistentes} asistentes', style: textTheme.bodyMedium),
              ],
            ),
            if (reserva.puedeCancelarse) ...[
              const SizedBox(height: AppSpacing.md),
              Align(
                alignment: Alignment.centerRight,
                child: OutlinedButton.icon(
                  onPressed: _cancelando ? null : _confirmarCancelacion,
                  icon: _cancelando
                      ? const SizedBox(height: 14, width: 14, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(LucideIcons.x, size: 16),
                  label: const Text('Cancelar'),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

/// `"YYYY-MM-DD"` -> `"DD/MM/YYYY"`, manipulación de texto pura — sin
/// pasar por `DateTime` (mismo criterio que `formatearHora`, ver riesgo de
/// fechas/horas del plan de migración).
String _formatearFecha(String fechaIso) {
  final partes = fechaIso.split('-');
  if (partes.length != 3) return fechaIso;
  return '${partes[2]}/${partes[1]}/${partes[0]}';
}
