// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'ensayos_providers.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(ensayosList)
final ensayosListProvider = EnsayosListFamily._();

final class EnsayosListProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<Ensayo>>,
          List<Ensayo>,
          FutureOr<List<Ensayo>>
        >
    with $FutureModifier<List<Ensayo>>, $FutureProvider<List<Ensayo>> {
  EnsayosListProvider._({
    required EnsayosListFamily super.from,
    required int? super.argument,
  }) : super(
         retry: null,
         name: r'ensayosListProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$ensayosListHash();

  @override
  String toString() {
    return r'ensayosListProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<List<Ensayo>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<Ensayo>> create(Ref ref) {
    final argument = this.argument as int?;
    return ensayosList(ref, zonaId: argument);
  }

  @override
  bool operator ==(Object other) {
    return other is EnsayosListProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$ensayosListHash() => r'ef99edec82afcc22af73466c8482393b0860f112';

final class EnsayosListFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<List<Ensayo>>, int?> {
  EnsayosListFamily._()
    : super(
        retry: null,
        name: r'ensayosListProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  EnsayosListProvider call({int? zonaId}) =>
      EnsayosListProvider._(argument: zonaId, from: this);

  @override
  String toString() => r'ensayosListProvider';
}

@ProviderFor(ensayosGestion)
final ensayosGestionProvider = EnsayosGestionProvider._();

final class EnsayosGestionProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<Ensayo>>,
          List<Ensayo>,
          FutureOr<List<Ensayo>>
        >
    with $FutureModifier<List<Ensayo>>, $FutureProvider<List<Ensayo>> {
  EnsayosGestionProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'ensayosGestionProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$ensayosGestionHash();

  @$internal
  @override
  $FutureProviderElement<List<Ensayo>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<Ensayo>> create(Ref ref) {
    return ensayosGestion(ref);
  }
}

String _$ensayosGestionHash() => r'd311ed247b3593d7d234350bfd63100d4acd5f4d';
