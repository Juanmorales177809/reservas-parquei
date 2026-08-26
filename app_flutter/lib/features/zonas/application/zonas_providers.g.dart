// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'zonas_providers.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(zonasList)
final zonasListProvider = ZonasListFamily._();

final class ZonasListProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<Zona>>,
          List<Zona>,
          FutureOr<List<Zona>>
        >
    with $FutureModifier<List<Zona>>, $FutureProvider<List<Zona>> {
  ZonasListProvider._({
    required ZonasListFamily super.from,
    required int? super.argument,
  }) : super(
         retry: null,
         name: r'zonasListProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$zonasListHash();

  @override
  String toString() {
    return r'zonasListProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<List<Zona>> $createElement($ProviderPointer pointer) =>
      $FutureProviderElement(pointer);

  @override
  FutureOr<List<Zona>> create(Ref ref) {
    final argument = this.argument as int?;
    return zonasList(ref, espacioId: argument);
  }

  @override
  bool operator ==(Object other) {
    return other is ZonasListProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$zonasListHash() => r'fc02d09b9488f3cf0b9857ce358dddf4140d5dac';

final class ZonasListFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<List<Zona>>, int?> {
  ZonasListFamily._()
    : super(
        retry: null,
        name: r'zonasListProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  ZonasListProvider call({int? espacioId}) =>
      ZonasListProvider._(argument: espacioId, from: this);

  @override
  String toString() => r'zonasListProvider';
}

/// Zonas para las pantallas de gestión (`GestionZonasScreen` y el
/// desplegable de zona de `GestionEnsayosScreen`).
///
/// El filtro por espacio se aplica **desde el cliente** a propósito: al
/// contrario de lo que decía el comentario anterior aquí, `GET /zonas`
/// NO acota al espacio gestionado — `backend/app/api/zonas.py` solo
/// filtra por estado, así que gestor y admin reciben las zonas de todos
/// los espacios. Sin este filtro, un gestor veía zonas ajenas en la
/// lista y podía elegir una en el formulario de ensayos, que el backend
/// después rechazaba con 403.

@ProviderFor(zonasGestion)
final zonasGestionProvider = ZonasGestionProvider._();

/// Zonas para las pantallas de gestión (`GestionZonasScreen` y el
/// desplegable de zona de `GestionEnsayosScreen`).
///
/// El filtro por espacio se aplica **desde el cliente** a propósito: al
/// contrario de lo que decía el comentario anterior aquí, `GET /zonas`
/// NO acota al espacio gestionado — `backend/app/api/zonas.py` solo
/// filtra por estado, así que gestor y admin reciben las zonas de todos
/// los espacios. Sin este filtro, un gestor veía zonas ajenas en la
/// lista y podía elegir una en el formulario de ensayos, que el backend
/// después rechazaba con 403.

final class ZonasGestionProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<Zona>>,
          List<Zona>,
          FutureOr<List<Zona>>
        >
    with $FutureModifier<List<Zona>>, $FutureProvider<List<Zona>> {
  /// Zonas para las pantallas de gestión (`GestionZonasScreen` y el
  /// desplegable de zona de `GestionEnsayosScreen`).
  ///
  /// El filtro por espacio se aplica **desde el cliente** a propósito: al
  /// contrario de lo que decía el comentario anterior aquí, `GET /zonas`
  /// NO acota al espacio gestionado — `backend/app/api/zonas.py` solo
  /// filtra por estado, así que gestor y admin reciben las zonas de todos
  /// los espacios. Sin este filtro, un gestor veía zonas ajenas en la
  /// lista y podía elegir una en el formulario de ensayos, que el backend
  /// después rechazaba con 403.
  ZonasGestionProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'zonasGestionProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$zonasGestionHash();

  @$internal
  @override
  $FutureProviderElement<List<Zona>> $createElement($ProviderPointer pointer) =>
      $FutureProviderElement(pointer);

  @override
  FutureOr<List<Zona>> create(Ref ref) {
    return zonasGestion(ref);
  }
}

String _$zonasGestionHash() => r'6834d7dd8a403a2350b59afa5abd228d63dfc5c9';
