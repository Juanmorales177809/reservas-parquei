// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'auditoria_providers.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(controlCambiosList)
final controlCambiosListProvider = ControlCambiosListProvider._();

final class ControlCambiosListProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<ControlCambio>>,
          List<ControlCambio>,
          FutureOr<List<ControlCambio>>
        >
    with
        $FutureModifier<List<ControlCambio>>,
        $FutureProvider<List<ControlCambio>> {
  ControlCambiosListProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'controlCambiosListProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$controlCambiosListHash();

  @$internal
  @override
  $FutureProviderElement<List<ControlCambio>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<ControlCambio>> create(Ref ref) {
    return controlCambiosList(ref);
  }
}

String _$controlCambiosListHash() =>
    r'ede409df9e9fdd808a583811aff0d88c07d06477';
