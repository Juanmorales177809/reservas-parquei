// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'laboratorios_providers.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(laboratoriosList)
final laboratoriosListProvider = LaboratoriosListProvider._();

final class LaboratoriosListProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<Laboratorio>>,
          List<Laboratorio>,
          FutureOr<List<Laboratorio>>
        >
    with
        $FutureModifier<List<Laboratorio>>,
        $FutureProvider<List<Laboratorio>> {
  LaboratoriosListProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'laboratoriosListProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$laboratoriosListHash();

  @$internal
  @override
  $FutureProviderElement<List<Laboratorio>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<Laboratorio>> create(Ref ref) {
    return laboratoriosList(ref);
  }
}

String _$laboratoriosListHash() => r'5c864b4d4b7a6c0968a3905b5775d067bfce47df';

@ProviderFor(laboratorio)
final laboratorioProvider = LaboratorioFamily._();

final class LaboratorioProvider
    extends
        $FunctionalProvider<
          AsyncValue<Laboratorio>,
          Laboratorio,
          FutureOr<Laboratorio>
        >
    with $FutureModifier<Laboratorio>, $FutureProvider<Laboratorio> {
  LaboratorioProvider._({
    required LaboratorioFamily super.from,
    required int super.argument,
  }) : super(
         retry: null,
         name: r'laboratorioProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$laboratorioHash();

  @override
  String toString() {
    return r'laboratorioProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<Laboratorio> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<Laboratorio> create(Ref ref) {
    final argument = this.argument as int;
    return laboratorio(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is LaboratorioProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$laboratorioHash() => r'08d162c10c259247bcad09d5104fd354cc730280';

final class LaboratorioFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<Laboratorio>, int> {
  LaboratorioFamily._()
    : super(
        retry: null,
        name: r'laboratorioProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  LaboratorioProvider call(int laboratorioId) =>
      LaboratorioProvider._(argument: laboratorioId, from: this);

  @override
  String toString() => r'laboratorioProvider';
}

/// Configuración del laboratorio del gestor (`GestionLaboratorioScreen`).

@ProviderFor(configuracionLaboratorioGestion)
final configuracionLaboratorioGestionProvider =
    ConfiguracionLaboratorioGestionProvider._();

/// Configuración del laboratorio del gestor (`GestionLaboratorioScreen`).

final class ConfiguracionLaboratorioGestionProvider
    extends
        $FunctionalProvider<
          AsyncValue<ConfiguracionLaboratorio>,
          ConfiguracionLaboratorio,
          FutureOr<ConfiguracionLaboratorio>
        >
    with
        $FutureModifier<ConfiguracionLaboratorio>,
        $FutureProvider<ConfiguracionLaboratorio> {
  /// Configuración del laboratorio del gestor (`GestionLaboratorioScreen`).
  ConfiguracionLaboratorioGestionProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'configuracionLaboratorioGestionProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$configuracionLaboratorioGestionHash();

  @$internal
  @override
  $FutureProviderElement<ConfiguracionLaboratorio> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<ConfiguracionLaboratorio> create(Ref ref) {
    return configuracionLaboratorioGestion(ref);
  }
}

String _$configuracionLaboratorioGestionHash() =>
    r'850827057a2246f6c549d5c28207433cdddd1fa5';
