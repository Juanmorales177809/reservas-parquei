import 'dart:async';

import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../auth/application/auth_provider.dart';
import '../data/notificaciones_repository.dart';
import '../domain/notificacion.dart';

part 'notificaciones_providers.g.dart';

/// Espejo de `frontend/src/context/NotificationContext.tsx`: sondeo cada
/// 30s mientras haya sesión, detenido al cerrar sesión. `build()` se
/// reevalúa solo cuando cambia `isAuthenticatedProvider` (login/logout),
/// no en cada tick — el propio timer actualiza `state` directamente.
@riverpod
class NotificacionesUnreadCount extends _$NotificacionesUnreadCount {
  Timer? _timer;

  @override
  Future<int> build() async {
    ref.onDispose(() => _timer?.cancel());
    _timer?.cancel();

    final autenticado = ref.watch(isAuthenticatedProvider);
    if (!autenticado) return 0;

    _timer = Timer.periodic(const Duration(seconds: 30), (_) => _refrescar());
    return ref.read(notificacionesRepositoryProvider).contarSinLeer();
  }

  Future<void> _refrescar() async {
    final cantidad = await ref.read(notificacionesRepositoryProvider).contarSinLeer();
    state = AsyncData(cantidad);
  }

  /// Llamado tras marcar como leída/leídas, para no esperar hasta el
  /// próximo tick del polling.
  Future<void> refrescarAhora() => _refrescar();
}

@riverpod
Future<List<Notificacion>> notificacionesList(Ref ref) {
  return ref.read(notificacionesRepositoryProvider).listar();
}
