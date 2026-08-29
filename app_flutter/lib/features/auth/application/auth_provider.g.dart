// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'auth_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Espejo de `frontend/src/context/AuthContext.tsx`. Fuente única de verdad
/// de la sesión: `null` = anónimo, cargando = sondeo en curso, error =
/// fallo de red real (no un 401 de "no hay sesión", que se traduce a
/// `null`).

@ProviderFor(Auth)
final authProvider = AuthProvider._();

/// Espejo de `frontend/src/context/AuthContext.tsx`. Fuente única de verdad
/// de la sesión: `null` = anónimo, cargando = sondeo en curso, error =
/// fallo de red real (no un 401 de "no hay sesión", que se traduce a
/// `null`).
final class AuthProvider extends $AsyncNotifierProvider<Auth, AuthUser?> {
  /// Espejo de `frontend/src/context/AuthContext.tsx`. Fuente única de verdad
  /// de la sesión: `null` = anónimo, cargando = sondeo en curso, error =
  /// fallo de red real (no un 401 de "no hay sesión", que se traduce a
  /// `null`).
  AuthProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'authProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$authHash();

  @$internal
  @override
  Auth create() => Auth();
}

String _$authHash() => r'7f31e9e4d93876f857c5c10f11031cc9ef75a185';

/// Espejo de `frontend/src/context/AuthContext.tsx`. Fuente única de verdad
/// de la sesión: `null` = anónimo, cargando = sondeo en curso, error =
/// fallo de red real (no un 401 de "no hay sesión", que se traduce a
/// `null`).

abstract class _$Auth extends $AsyncNotifier<AuthUser?> {
  FutureOr<AuthUser?> build();
  @$mustCallSuper
  @override
  WhenComplete runBuild() {
    final ref = this.ref as $Ref<AsyncValue<AuthUser?>, AuthUser?>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<AuthUser?>, AuthUser?>,
              AsyncValue<AuthUser?>,
              Object?,
              Object?
            >;
    return element.handleCreate(ref, build);
  }
}

@ProviderFor(isAuthenticated)
final isAuthenticatedProvider = IsAuthenticatedProvider._();

final class IsAuthenticatedProvider
    extends $FunctionalProvider<bool, bool, bool>
    with $Provider<bool> {
  IsAuthenticatedProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'isAuthenticatedProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$isAuthenticatedHash();

  @$internal
  @override
  $ProviderElement<bool> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  bool create(Ref ref) {
    return isAuthenticated(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(bool value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<bool>(value),
    );
  }
}

String _$isAuthenticatedHash() => r'8e5cf6b7422ae78497bbc9a70fcb84497f0f5e8c';

@ProviderFor(isAdmin)
final isAdminProvider = IsAdminProvider._();

final class IsAdminProvider extends $FunctionalProvider<bool, bool, bool>
    with $Provider<bool> {
  IsAdminProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'isAdminProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$isAdminHash();

  @$internal
  @override
  $ProviderElement<bool> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  bool create(Ref ref) {
    return isAdmin(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(bool value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<bool>(value),
    );
  }
}

String _$isAdminHash() => r'e74e12df2bc63449689735af6cf91ed562656344';

@ProviderFor(canManageResources)
final canManageResourcesProvider = CanManageResourcesProvider._();

final class CanManageResourcesProvider
    extends $FunctionalProvider<bool, bool, bool>
    with $Provider<bool> {
  CanManageResourcesProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'canManageResourcesProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$canManageResourcesHash();

  @$internal
  @override
  $ProviderElement<bool> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  bool create(Ref ref) {
    return canManageResources(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(bool value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<bool>(value),
    );
  }
}

String _$canManageResourcesHash() =>
    r'1ebae91a01960c9d9933760b542d2b9de447de5a';
