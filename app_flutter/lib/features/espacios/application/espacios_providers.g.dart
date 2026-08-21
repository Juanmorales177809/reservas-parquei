// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'espacios_providers.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(espaciosList)
final espaciosListProvider = EspaciosListProvider._();

final class EspaciosListProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<Espacio>>,
          List<Espacio>,
          FutureOr<List<Espacio>>
        >
    with $FutureModifier<List<Espacio>>, $FutureProvider<List<Espacio>> {
  EspaciosListProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'espaciosListProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$espaciosListHash();

  @$internal
  @override
  $FutureProviderElement<List<Espacio>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<Espacio>> create(Ref ref) {
    return espaciosList(ref);
  }
}

String _$espaciosListHash() => r'1988a8897fc77fdf68e7ec3f39d0cf5e442a18ab';

@ProviderFor(espacio)
final espacioProvider = EspacioFamily._();

final class EspacioProvider
    extends $FunctionalProvider<AsyncValue<Espacio>, Espacio, FutureOr<Espacio>>
    with $FutureModifier<Espacio>, $FutureProvider<Espacio> {
  EspacioProvider._({
    required EspacioFamily super.from,
    required int super.argument,
  }) : super(
         retry: null,
         name: r'espacioProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$espacioHash();

  @override
  String toString() {
    return r'espacioProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<Espacio> $createElement($ProviderPointer pointer) =>
      $FutureProviderElement(pointer);

  @override
  FutureOr<Espacio> create(Ref ref) {
    final argument = this.argument as int;
    return espacio(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is EspacioProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$espacioHash() => r'1ad95ed0e7e336c551740c86d868141219f1efd2';

final class EspacioFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<Espacio>, int> {
  EspacioFamily._()
    : super(
        retry: null,
        name: r'espacioProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  EspacioProvider call(int espacioId) =>
      EspacioProvider._(argument: espacioId, from: this);

  @override
  String toString() => r'espacioProvider';
}

/// Configuración del espacio del gestor (`GestionEspacioScreen`).

@ProviderFor(configuracionEspacioGestion)
final configuracionEspacioGestionProvider =
    ConfiguracionEspacioGestionProvider._();

/// Configuración del espacio del gestor (`GestionEspacioScreen`).

final class ConfiguracionEspacioGestionProvider
    extends
        $FunctionalProvider<
          AsyncValue<ConfiguracionEspacio>,
          ConfiguracionEspacio,
          FutureOr<ConfiguracionEspacio>
        >
    with
        $FutureModifier<ConfiguracionEspacio>,
        $FutureProvider<ConfiguracionEspacio> {
  /// Configuración del espacio del gestor (`GestionEspacioScreen`).
  ConfiguracionEspacioGestionProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'configuracionEspacioGestionProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$configuracionEspacioGestionHash();

  @$internal
  @override
  $FutureProviderElement<ConfiguracionEspacio> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<ConfiguracionEspacio> create(Ref ref) {
    return configuracionEspacioGestion(ref);
  }
}

String _$configuracionEspacioGestionHash() =>
    r'b6437653a0a44fbeb54c1393b77d5d1b6132fc05';
