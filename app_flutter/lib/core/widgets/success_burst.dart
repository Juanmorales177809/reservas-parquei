import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../theme/app_spacing.dart';

/// Overlay breve con un ícono de check que "explota" hacia adentro (scale
/// elástico) — el momento de "listo" de una acción importante (crear una
/// reserva) se siente mejor que un `SnackBar` seco. Se cierra solo, no
/// requiere interacción del usuario.
class SuccessBurst {
  SuccessBurst._();

  static Future<void> show(BuildContext context, {required String message}) async {
    final navigator = Navigator.of(context, rootNavigator: true);
    unawaited(
      showGeneralDialog<void>(
        context: context,
        barrierDismissible: false,
        barrierColor: Colors.black.withValues(alpha: 0.35),
        transitionDuration: const Duration(milliseconds: 180),
        pageBuilder: (context, _, _) => _SuccessBurstContent(message: message),
        transitionBuilder: (context, animation, _, child) => FadeTransition(opacity: animation, child: child),
      ),
    );
    await Future.delayed(const Duration(milliseconds: 1200));
    if (navigator.mounted && navigator.canPop()) navigator.pop();
  }
}

class _SuccessBurstContent extends StatelessWidget {
  const _SuccessBurstContent({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Center(
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: AppSpacing.xxl),
        padding: const EdgeInsets.all(AppSpacing.xl),
        decoration: BoxDecoration(
          color: scheme.surface,
          borderRadius: BorderRadius.circular(AppRadius.lg),
          boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.2), blurRadius: 30, offset: const Offset(0, 12))],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 64,
              height: 64,
              decoration: BoxDecoration(color: const Color(0xFF10B981).withValues(alpha: 0.15), shape: BoxShape.circle),
              child: const Icon(LucideIcons.circleCheck, color: Color(0xFF10B981), size: 36),
            ).animate().scale(
                  begin: const Offset(0.3, 0.3),
                  end: const Offset(1, 1),
                  duration: 450.ms,
                  curve: Curves.elasticOut,
                ),
            const SizedBox(height: AppSpacing.lg),
            Text(
              message,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium,
            ).animate().fadeIn(delay: 150.ms, duration: 250.ms),
          ],
        ),
      ),
    );
  }
}
