// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'espacios_providers.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(espaciosList)
final espaciosListProvider = EspaciosListFamily._();

final class EspaciosListProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<Espacio>>,
          List<Espacio>,
          FutureOr<List<Espacio>>
        >
    with $FutureModifier<List<Espacio>>, $FutureProvider<List<Espacio>> {
  EspaciosListProvider._({
    required EspaciosListFamily super.from,
    required int? super.argument,
  }) : super(
         retry: null,
         name: r'espaciosListProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$espaciosListHash();

  @override
  String toString() {
    return r'espaciosListProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<List<Espacio>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<Espacio>> create(Ref ref) {
    final argument = this.argument as int?;
    return espaciosList(ref, laboratorioId: argument);
  }

  @override
  bool operator ==(Object other) {
    return other is EspaciosListProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$espaciosListHash() => r'5e55d294735d01c602176cb9b564d4e6ebf0736b';

final class EspaciosListFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<List<Espacio>>, int?> {
  EspaciosListFamily._()
    : super(
        retry: null,
        name: r'espaciosListProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  EspaciosListProvider call({int? laboratorioId}) =>
      EspaciosListProvider._(argument: laboratorioId, from: this);

  @override
  String toString() => r'espaciosListProvider';
}

/// Espacios para la pantalla de gestión (`GestionEspaciosScreen`).
///
/// El filtro por laboratorio se aplica **desde el cliente** a propósito: al
/// contrario de lo que decía el comentario anterior aquí, `GET /espacios`
/// NO acota al laboratorio gestionado — `backend/app/api/espacios.py` solo
/// filtra por estado, así que gestor y admin reciben las espacios de todos
/// los laboratorios. Sin este filtro, un gestor veía espacios ajenas en la
/// lista y podía elegirlas por error.

@ProviderFor(espaciosGestion)
final espaciosGestionProvider = EspaciosGestionProvider._();

/// Espacios para la pantalla de gestión (`GestionEspaciosScreen`).
///
/// El filtro por laboratorio se aplica **desde el cliente** a propósito: al
/// contrario de lo que decía el comentario anterior aquí, `GET /espacios`
/// NO acota al laboratorio gestionado — `backend/app/api/espacios.py` solo
/// filtra por estado, así que gestor y admin reciben las espacios de todos
/// los laboratorios. Sin este filtro, un gestor veía espacios ajenas en la
/// lista y podía elegirlas por error.

final class EspaciosGestionProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<Espacio>>,
          List<Espacio>,
          FutureOr<List<Espacio>>
        >
    with $FutureModifier<List<Espacio>>, $FutureProvider<List<Espacio>> {
  /// Espacios para la pantalla de gestión (`GestionEspaciosScreen`).
  ///
  /// El filtro por laboratorio se aplica **desde el cliente** a propósito: al
  /// contrario de lo que decía el comentario anterior aquí, `GET /espacios`
  /// NO acota al laboratorio gestionado — `backend/app/api/espacios.py` solo
  /// filtra por estado, así que gestor y admin reciben las espacios de todos
  /// los laboratorios. Sin este filtro, un gestor veía espacios ajenas en la
  /// lista y podía elegirlas por error.
  EspaciosGestionProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'espaciosGestionProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$espaciosGestionHash();

  @$internal
  @override
  $FutureProviderElement<List<Espacio>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<Espacio>> create(Ref ref) {
    return espaciosGestion(ref);
  }
}

String _$espaciosGestionHash() => r'b89f08033d1b7a70d64c3c4ea3061c49e27c3975';
