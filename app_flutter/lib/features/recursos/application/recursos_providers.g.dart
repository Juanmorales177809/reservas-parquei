// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'recursos_providers.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Carga una sola vez todos los recursos activos (sin filtrar por laboratorio)
/// y se agrupa client-side por `laboratorioId` — evita N+1 llamadas al abrir
/// cada laboratorio, igual que hoy hace `frontend/src/app/laboratorios/page.tsx`.

@ProviderFor(recursosActivos)
final recursosActivosProvider = RecursosActivosProvider._();

/// Carga una sola vez todos los recursos activos (sin filtrar por laboratorio)
/// y se agrupa client-side por `laboratorioId` — evita N+1 llamadas al abrir
/// cada laboratorio, igual que hoy hace `frontend/src/app/laboratorios/page.tsx`.

final class RecursosActivosProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<Recurso>>,
          List<Recurso>,
          FutureOr<List<Recurso>>
        >
    with $FutureModifier<List<Recurso>>, $FutureProvider<List<Recurso>> {
  /// Carga una sola vez todos los recursos activos (sin filtrar por laboratorio)
  /// y se agrupa client-side por `laboratorioId` — evita N+1 llamadas al abrir
  /// cada laboratorio, igual que hoy hace `frontend/src/app/laboratorios/page.tsx`.
  RecursosActivosProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'recursosActivosProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$recursosActivosHash();

  @$internal
  @override
  $FutureProviderElement<List<Recurso>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<Recurso>> create(Ref ref) {
    return recursosActivos(ref);
  }
}

String _$recursosActivosHash() => r'e7848e14830e007211eea30fa19ecc8bcef928f2';

@ProviderFor(recursosPorLaboratorio)
final recursosPorLaboratorioProvider = RecursosPorLaboratorioFamily._();

final class RecursosPorLaboratorioProvider
    extends $FunctionalProvider<List<Recurso>, List<Recurso>, List<Recurso>>
    with $Provider<List<Recurso>> {
  RecursosPorLaboratorioProvider._({
    required RecursosPorLaboratorioFamily super.from,
    required int super.argument,
  }) : super(
         retry: null,
         name: r'recursosPorLaboratorioProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$recursosPorLaboratorioHash();

  @override
  String toString() {
    return r'recursosPorLaboratorioProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $ProviderElement<List<Recurso>> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  List<Recurso> create(Ref ref) {
    final argument = this.argument as int;
    return recursosPorLaboratorio(ref, argument);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(List<Recurso> value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<List<Recurso>>(value),
    );
  }

  @override
  bool operator ==(Object other) {
    return other is RecursosPorLaboratorioProvider &&
        other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$recursosPorLaboratorioHash() =>
    r'64c8844de3db9244098be9020e424147d2a85e0c';

final class RecursosPorLaboratorioFamily extends $Family
    with $FunctionalFamilyOverride<List<Recurso>, int> {
  RecursosPorLaboratorioFamily._()
    : super(
        retry: null,
        name: r'recursosPorLaboratorioProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  RecursosPorLaboratorioProvider call(int laboratorioId) =>
      RecursosPorLaboratorioProvider._(argument: laboratorioId, from: this);

  @override
  String toString() => r'recursosPorLaboratorioProvider';
}

@ProviderFor(recursoDisponibilidad)
final recursoDisponibilidadProvider = RecursoDisponibilidadFamily._();

final class RecursoDisponibilidadProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<DisponibilidadSlot>>,
          List<DisponibilidadSlot>,
          FutureOr<List<DisponibilidadSlot>>
        >
    with
        $FutureModifier<List<DisponibilidadSlot>>,
        $FutureProvider<List<DisponibilidadSlot>> {
  RecursoDisponibilidadProvider._({
    required RecursoDisponibilidadFamily super.from,
    required (int, DateTime) super.argument,
  }) : super(
         retry: null,
         name: r'recursoDisponibilidadProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$recursoDisponibilidadHash();

  @override
  String toString() {
    return r'recursoDisponibilidadProvider'
        ''
        '$argument';
  }

  @$internal
  @override
  $FutureProviderElement<List<DisponibilidadSlot>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<DisponibilidadSlot>> create(Ref ref) {
    final argument = this.argument as (int, DateTime);
    return recursoDisponibilidad(ref, argument.$1, argument.$2);
  }

  @override
  bool operator ==(Object other) {
    return other is RecursoDisponibilidadProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$recursoDisponibilidadHash() =>
    r'2d33de1b70be03e1b1aa05724dcfb1db483b3f3f';

final class RecursoDisponibilidadFamily extends $Family
    with
        $FunctionalFamilyOverride<
          FutureOr<List<DisponibilidadSlot>>,
          (int, DateTime)
        > {
  RecursoDisponibilidadFamily._()
    : super(
        retry: null,
        name: r'recursoDisponibilidadProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  RecursoDisponibilidadProvider call(int recursoId, DateTime fecha) =>
      RecursoDisponibilidadProvider._(argument: (recursoId, fecha), from: this);

  @override
  String toString() => r'recursoDisponibilidadProvider';
}

@ProviderFor(recursosGestion)
final recursosGestionProvider = RecursosGestionProvider._();

final class RecursosGestionProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<Recurso>>,
          List<Recurso>,
          FutureOr<List<Recurso>>
        >
    with $FutureModifier<List<Recurso>>, $FutureProvider<List<Recurso>> {
  RecursosGestionProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'recursosGestionProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$recursosGestionHash();

  @$internal
  @override
  $FutureProviderElement<List<Recurso>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<Recurso>> create(Ref ref) {
    return recursosGestion(ref);
  }
}

String _$recursosGestionHash() => r'08206cb9b3e667c8383a05a7a90247c6d86a4299';

@ProviderFor(tiposRecursos)
final tiposRecursosProvider = TiposRecursosProvider._();

final class TiposRecursosProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<TipoRecurso>>,
          List<TipoRecurso>,
          FutureOr<List<TipoRecurso>>
        >
    with
        $FutureModifier<List<TipoRecurso>>,
        $FutureProvider<List<TipoRecurso>> {
  TiposRecursosProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'tiposRecursosProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$tiposRecursosHash();

  @$internal
  @override
  $FutureProviderElement<List<TipoRecurso>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<TipoRecurso>> create(Ref ref) {
    return tiposRecursos(ref);
  }
}

String _$tiposRecursosHash() => r'566d657a32e0a0565be4f89627cf7d10184177c5';
