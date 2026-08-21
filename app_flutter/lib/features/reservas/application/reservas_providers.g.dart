// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'reservas_providers.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(misReservas)
final misReservasProvider = MisReservasProvider._();

final class MisReservasProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<Reserva>>,
          List<Reserva>,
          FutureOr<List<Reserva>>
        >
    with $FutureModifier<List<Reserva>>, $FutureProvider<List<Reserva>> {
  MisReservasProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'misReservasProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$misReservasHash();

  @$internal
  @override
  $FutureProviderElement<List<Reserva>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<Reserva>> create(Ref ref) {
    return misReservas(ref);
  }
}

String _$misReservasHash() => r'38a9709053056b3f3a254ed6cce457b606ba9329';

/// `GET /reservas` — gestión, gestor/admin (ver `GestionReservasScreen`).

@ProviderFor(reservasGestion)
final reservasGestionProvider = ReservasGestionProvider._();

/// `GET /reservas` — gestión, gestor/admin (ver `GestionReservasScreen`).

final class ReservasGestionProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<Reserva>>,
          List<Reserva>,
          FutureOr<List<Reserva>>
        >
    with $FutureModifier<List<Reserva>>, $FutureProvider<List<Reserva>> {
  /// `GET /reservas` — gestión, gestor/admin (ver `GestionReservasScreen`).
  ReservasGestionProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'reservasGestionProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$reservasGestionHash();

  @$internal
  @override
  $FutureProviderElement<List<Reserva>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<Reserva>> create(Ref ref) {
    return reservasGestion(ref);
  }
}

String _$reservasGestionHash() => r'7510e7864bc88a483c1e69c1c77c554a01b3a1cc';
