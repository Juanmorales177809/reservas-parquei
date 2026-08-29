// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'usuarios_providers.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(usuariosList)
final usuariosListProvider = UsuariosListProvider._();

final class UsuariosListProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<AuthUser>>,
          List<AuthUser>,
          FutureOr<List<AuthUser>>
        >
    with $FutureModifier<List<AuthUser>>, $FutureProvider<List<AuthUser>> {
  UsuariosListProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'usuariosListProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$usuariosListHash();

  @$internal
  @override
  $FutureProviderElement<List<AuthUser>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<AuthUser>> create(Ref ref) {
    return usuariosList(ref);
  }
}

String _$usuariosListHash() => r'e2a8c947d613586d957042413bccd44206bc4e4d';

/// Personal institucional (admin/gestor) -- tabla separada de `usuarios`
/// desde 2026-08-28, ver `backend/CLAUDE.md` y
/// `usuarios_repository.dart::listarPersonal`.

@ProviderFor(personalList)
final personalListProvider = PersonalListProvider._();

/// Personal institucional (admin/gestor) -- tabla separada de `usuarios`
/// desde 2026-08-28, ver `backend/CLAUDE.md` y
/// `usuarios_repository.dart::listarPersonal`.

final class PersonalListProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<AuthUser>>,
          List<AuthUser>,
          FutureOr<List<AuthUser>>
        >
    with $FutureModifier<List<AuthUser>>, $FutureProvider<List<AuthUser>> {
  /// Personal institucional (admin/gestor) -- tabla separada de `usuarios`
  /// desde 2026-08-28, ver `backend/CLAUDE.md` y
  /// `usuarios_repository.dart::listarPersonal`.
  PersonalListProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'personalListProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$personalListHash();

  @$internal
  @override
  $FutureProviderElement<List<AuthUser>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<AuthUser>> create(Ref ref) {
    return personalList(ref);
  }
}

String _$personalListHash() => r'8db52696ce20f986ff48e1ab48f88adfe488fbf6';
