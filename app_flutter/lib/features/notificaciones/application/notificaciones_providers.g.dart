// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'notificaciones_providers.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Espejo de `frontend/src/context/NotificationContext.tsx`: sondeo cada
/// 30s mientras haya sesión, detenido al cerrar sesión. `build()` se
/// reevalúa solo cuando cambia `isAuthenticatedProvider` (login/logout),
/// no en cada tick — el propio timer actualiza `state` directamente.

@ProviderFor(NotificacionesUnreadCount)
final notificacionesUnreadCountProvider = NotificacionesUnreadCountProvider._();

/// Espejo de `frontend/src/context/NotificationContext.tsx`: sondeo cada
/// 30s mientras haya sesión, detenido al cerrar sesión. `build()` se
/// reevalúa solo cuando cambia `isAuthenticatedProvider` (login/logout),
/// no en cada tick — el propio timer actualiza `state` directamente.
final class NotificacionesUnreadCountProvider
    extends $AsyncNotifierProvider<NotificacionesUnreadCount, int> {
  /// Espejo de `frontend/src/context/NotificationContext.tsx`: sondeo cada
  /// 30s mientras haya sesión, detenido al cerrar sesión. `build()` se
  /// reevalúa solo cuando cambia `isAuthenticatedProvider` (login/logout),
  /// no en cada tick — el propio timer actualiza `state` directamente.
  NotificacionesUnreadCountProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'notificacionesUnreadCountProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$notificacionesUnreadCountHash();

  @$internal
  @override
  NotificacionesUnreadCount create() => NotificacionesUnreadCount();
}

String _$notificacionesUnreadCountHash() =>
    r'a5b920cfd3b1a3d3018d1c32f8743998dc4c5029';

/// Espejo de `frontend/src/context/NotificationContext.tsx`: sondeo cada
/// 30s mientras haya sesión, detenido al cerrar sesión. `build()` se
/// reevalúa solo cuando cambia `isAuthenticatedProvider` (login/logout),
/// no en cada tick — el propio timer actualiza `state` directamente.

abstract class _$NotificacionesUnreadCount extends $AsyncNotifier<int> {
  FutureOr<int> build();
  @$mustCallSuper
  @override
  WhenComplete runBuild() {
    final ref = this.ref as $Ref<AsyncValue<int>, int>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<int>, int>,
              AsyncValue<int>,
              Object?,
              Object?
            >;
    return element.handleCreate(ref, build);
  }
}

@ProviderFor(notificacionesList)
final notificacionesListProvider = NotificacionesListProvider._();

final class NotificacionesListProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<Notificacion>>,
          List<Notificacion>,
          FutureOr<List<Notificacion>>
        >
    with
        $FutureModifier<List<Notificacion>>,
        $FutureProvider<List<Notificacion>> {
  NotificacionesListProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'notificacionesListProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$notificacionesListHash();

  @$internal
  @override
  $FutureProviderElement<List<Notificacion>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<Notificacion>> create(Ref ref) {
    return notificacionesList(ref);
  }
}

String _$notificacionesListHash() =>
    r'9bf8a5a12a93a60a34c073192404a32dbb4f4cc3';
