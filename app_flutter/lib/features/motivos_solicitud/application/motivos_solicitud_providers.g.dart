// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'motivos_solicitud_providers.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(motivosSolicitud)
final motivosSolicitudProvider = MotivosSolicitudFamily._();

final class MotivosSolicitudProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<MotivoSolicitud>>,
          List<MotivoSolicitud>,
          FutureOr<List<MotivoSolicitud>>
        >
    with
        $FutureModifier<List<MotivoSolicitud>>,
        $FutureProvider<List<MotivoSolicitud>> {
  MotivosSolicitudProvider._({
    required MotivosSolicitudFamily super.from,
    required int super.argument,
  }) : super(
         retry: null,
         name: r'motivosSolicitudProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$motivosSolicitudHash();

  @override
  String toString() {
    return r'motivosSolicitudProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<List<MotivoSolicitud>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<MotivoSolicitud>> create(Ref ref) {
    final argument = this.argument as int;
    return motivosSolicitud(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is MotivosSolicitudProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$motivosSolicitudHash() => r'c375693ccac76f5128771980b220f39d56c10d90';

final class MotivosSolicitudFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<List<MotivoSolicitud>>, int> {
  MotivosSolicitudFamily._()
    : super(
        retry: null,
        name: r'motivosSolicitudProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  MotivosSolicitudProvider call(int laboratorioId) =>
      MotivosSolicitudProvider._(argument: laboratorioId, from: this);

  @override
  String toString() => r'motivosSolicitudProvider';
}
