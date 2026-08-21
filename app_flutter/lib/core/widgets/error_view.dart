import 'package:flutter/material.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../theme/app_colors.dart';
import '../theme/app_spacing.dart';

/// Vista de error, reutilizada por todas las features. Muestra el mensaje
/// que devuelve `ApiException` tal cual (sin reescribirlo) — mismo criterio
/// que sigue el frontend Next.js.
///
/// **Deliberadamente NO se parece a `EmptyView`.** "No hay nada todavía" y
/// "no se pudo cargar" son situaciones distintas y requieren acciones
/// distintas; cuando ambas se dibujan como un icono gris centrado, el
/// usuario no sabe si tiene que crear algo o reintentar. Este estado usa el
/// tinte negativo, un panel acotado y un botón de reintento explícito.
class ErrorView extends StatelessWidget {
  const ErrorView({required this.message, this.onRetry, super.key});

  final String message;
  final VoidCallback? onRetry;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(AppSpacing.xxl),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 420),
          child: Container(
            padding: const EdgeInsets.all(AppSpacing.xl),
            decoration: BoxDecoration(
              color: AppEstados.negativo.tinte,
              borderRadius: BorderRadius.circular(AppRadius.xl),
              border: Border.all(color: AppEstados.negativo.borde.withValues(alpha: 0.35)),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(LucideIcons.wifiOff, size: 20, color: AppEstados.negativo.sobreTinte),
                    const SizedBox(width: AppSpacing.sm),
                    Text(
                      'No se pudo cargar',
                      style: textTheme.titleMedium?.copyWith(color: AppEstados.negativo.sobreTinte),
                    ),
                  ],
                ),
                const SizedBox(height: AppSpacing.sm),
                Text(
                  message,
                  style: textTheme.bodyMedium?.copyWith(color: AppEstados.negativo.sobreTinte),
                ),
                if (onRetry != null) ...[
                  const SizedBox(height: AppSpacing.lg),
                  OutlinedButton.icon(
                    onPressed: onRetry,
                    icon: const Icon(LucideIcons.refreshCw, size: 16),
                    label: const Text('Reintentar'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: AppEstados.negativo.sobreTinte,
                      side: BorderSide(color: AppEstados.negativo.borde.withValues(alpha: 0.5)),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}
