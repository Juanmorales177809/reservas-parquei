import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../../../core/domain/enums.dart';
import '../../../core/network/api_exception.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/widgets/empty_view.dart';
import '../../../core/widgets/error_view.dart';
import '../../../core/widgets/loading_spinner.dart';
import '../application/notificaciones_providers.dart';
import '../data/notificaciones_repository.dart';
import '../domain/notificacion.dart';

/// Panel de notificaciones, abierto desde la campana del `AppBar` (ambos
/// shells). Espejo de `frontend/src/components/NotificationBell.tsx`.
class NotificacionesSheet extends ConsumerWidget {
  const NotificacionesSheet({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final listaAsync = ref.watch(notificacionesListProvider);
    final scheme = Theme.of(context).colorScheme;

    return SafeArea(
      child: ConstrainedBox(
        constraints: BoxConstraints(maxHeight: MediaQuery.sizeOf(context).height * 0.75),
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
                  decoration: BoxDecoration(color: scheme.outlineVariant, borderRadius: BorderRadius.circular(999)),
                ),
              ),
              Row(
                children: [
                  Text('Notificaciones', style: Theme.of(context).textTheme.titleMedium),
                  const Spacer(),
                  TextButton(
                    onPressed: () async {
                      await ref.read(notificacionesRepositoryProvider).marcarTodasLeidas();
                      ref.invalidate(notificacionesListProvider);
                      await ref.read(notificacionesUnreadCountProvider.notifier).refrescarAhora();
                    },
                    child: const Text('Marcar todas leídas'),
                  ),
                ],
              ),
              const SizedBox(height: AppSpacing.sm),
              Flexible(
                child: listaAsync.when(
                  loading: () => const Padding(padding: EdgeInsets.all(AppSpacing.xl), child: LoadingSpinner()),
                  error: (error, _) => ErrorView(
                    message: apiErrorMessage(error, fallback: 'No se pudieron cargar las notificaciones.'),
                    onRetry: () => ref.invalidate(notificacionesListProvider),
                  ),
                  data: (lista) {
                    if (lista.isEmpty) {
                      return const Padding(
                        padding: EdgeInsets.symmetric(vertical: AppSpacing.xl),
                        child: EmptyView(icon: LucideIcons.bellOff, message: 'No tenés notificaciones.'),
                      );
                    }
                    return ListView.separated(
                      shrinkWrap: true,
                      itemCount: lista.length,
                      separatorBuilder: (_, _) => const SizedBox(height: AppSpacing.xs),
                      itemBuilder: (context, index) => _NotificacionTile(notificacion: lista[index]),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _NotificacionTile extends ConsumerWidget {
  const _NotificacionTile({required this.notificacion});

  final Notificacion notificacion;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final scheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    final (icono, color) = switch (notificacion.tipo) {
      TipoNotificacion.pendiente => (LucideIcons.clock, const Color(0xFFD97706)),
      TipoNotificacion.aprobada => (LucideIcons.circleCheck, const Color(0xFF10B981)),
      TipoNotificacion.rechazada => (LucideIcons.circleX, const Color(0xFFDC2626)),
      TipoNotificacion.cancelada => (LucideIcons.ban, const Color(0xFF6B7280)),
    };

    return InkWell(
      borderRadius: BorderRadius.circular(AppRadius.md),
      onTap: notificacion.leida
          ? null
          : () async {
              await ref.read(notificacionesRepositoryProvider).marcarLeida(notificacion.id);
              ref.invalidate(notificacionesListProvider);
              await ref.read(notificacionesUnreadCountProvider.notifier).refrescarAhora();
            },
      child: Container(
        padding: const EdgeInsets.all(AppSpacing.md),
        decoration: BoxDecoration(
          color: notificacion.leida ? null : scheme.primaryContainer.withValues(alpha: 0.25),
          borderRadius: BorderRadius.circular(AppRadius.md),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icono, size: 20, color: color),
            const SizedBox(width: AppSpacing.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    notificacion.mensaje,
                    style: textTheme.bodyMedium?.copyWith(
                      fontWeight: notificacion.leida ? FontWeight.w400 : FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: AppSpacing.xs),
                  Text(
                    _formatearFechaHora(notificacion.createdAt),
                    style: textTheme.bodySmall?.copyWith(color: scheme.onSurfaceVariant),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// `"2026-08-20T18:24:34.220196Z"` -> `"20/08/2026 18:24"` — manipulación
/// de texto pura, sin `DateTime` (mismo criterio que el resto de la app).
String _formatearFechaHora(String iso) {
  final partes = iso.split('T');
  if (partes.length < 2) return iso;
  final fechaPartes = partes[0].split('-');
  if (fechaPartes.length != 3) return iso;
  final fecha = '${fechaPartes[2]}/${fechaPartes[1]}/${fechaPartes[0]}';
  final hora = partes[1].length >= 5 ? partes[1].substring(0, 5) : partes[1];
  return '$fecha $hora';
}
