import 'package:flutter/material.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../theme/app_spacing.dart';

/// Marca de la app (ícono + wordmark) — reutilizada en las `AppBar` del
/// shell y en la pantalla de login para que la identidad visual se sienta
/// consistente en toda la app.
class BrandMark extends StatelessWidget {
  const BrandMark({this.compact = false, super.key});

  final bool compact;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          padding: const EdgeInsets.all(AppSpacing.xs),
          decoration: BoxDecoration(
            gradient: LinearGradient(colors: [scheme.primary, scheme.tertiary]),
            borderRadius: BorderRadius.circular(AppSpacing.sm),
          ),
          child: const Icon(LucideIcons.calendarCheck, color: Colors.white, size: 18),
        ),
        const SizedBox(width: AppSpacing.sm),
        Text(
          'Reservas Parquei',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
        ),
      ],
    );
  }
}
