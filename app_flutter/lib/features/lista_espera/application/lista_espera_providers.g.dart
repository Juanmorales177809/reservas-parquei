// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'lista_espera_providers.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(misEntradasListaEspera)
final misEntradasListaEsperaProvider = MisEntradasListaEsperaProvider._();

final class MisEntradasListaEsperaProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<ListaEsperaEntrada>>,
          List<ListaEsperaEntrada>,
          FutureOr<List<ListaEsperaEntrada>>
        >
    with
        $FutureModifier<List<ListaEsperaEntrada>>,
        $FutureProvider<List<ListaEsperaEntrada>> {
  MisEntradasListaEsperaProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'misEntradasListaEsperaProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$misEntradasListaEsperaHash();

  @$internal
  @override
  $FutureProviderElement<List<ListaEsperaEntrada>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<ListaEsperaEntrada>> create(Ref ref) {
    return misEntradasListaEspera(ref);
  }
}

String _$misEntradasListaEsperaHash() =>
    r'0d51fdddee72453b5b8483ab98368c6af2aa6a3d';
