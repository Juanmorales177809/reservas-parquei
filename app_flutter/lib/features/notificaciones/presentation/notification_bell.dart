import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

import '../application/notificaciones_providers.dart';
import 'notificaciones_sheet.dart';

/// Campana con contador de no leídas — vive en el `AppBar` de ambos shells
/// (bottom nav y top nav), no en la barra de navegación misma. Espejo de
/// `frontend/src/components/NotificationBell.tsx`.
class NotificationBell extends ConsumerWidget {
  const NotificationBell({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final count = ref.watch(notificacionesUnreadCountProvider).value ?? 0;

    return IconButton(
      tooltip: 'Notificaciones',
      onPressed: () => showModalBottomSheet(
        context: context,
        isScrollControlled: true,
        builder: (context) => const NotificacionesSheet(),
      ),
      icon: Badge(
        label: Text('$count'),
        isLabelVisible: count > 0,
        child: const Icon(LucideIcons.bell),
      ),
    );
  }
}
