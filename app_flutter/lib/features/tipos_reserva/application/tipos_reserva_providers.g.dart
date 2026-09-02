// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'tipos_reserva_providers.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Tipos de reserva de un laboratorio puntual -- usado por el dropdown
/// dinámico del formulario de reserva (`laboratorio_reserva_sheet.dart`,
/// `recurso_disponibilidad_sheet.dart`, Fase 7).

@ProviderFor(tiposReserva)
final tiposReservaProvider = TiposReservaFamily._();

/// Tipos de reserva de un laboratorio puntual -- usado por el dropdown
/// dinámico del formulario de reserva (`laboratorio_reserva_sheet.dart`,
/// `recurso_disponibilidad_sheet.dart`, Fase 7).

final class TiposReservaProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<TipoReserva>>,
          List<TipoReserva>,
          FutureOr<List<TipoReserva>>
        >
    with
        $FutureModifier<List<TipoReserva>>,
        $FutureProvider<List<TipoReserva>> {
  /// Tipos de reserva de un laboratorio puntual -- usado por el dropdown
  /// dinámico del formulario de reserva (`laboratorio_reserva_sheet.dart`,
  /// `recurso_disponibilidad_sheet.dart`, Fase 7).
  TiposReservaProvider._({
    required TiposReservaFamily super.from,
    required int super.argument,
  }) : super(
         retry: null,
         name: r'tiposReservaProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$tiposReservaHash();

  @override
  String toString() {
    return r'tiposReservaProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<List<TipoReserva>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<TipoReserva>> create(Ref ref) {
    final argument = this.argument as int;
    return tiposReserva(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is TiposReservaProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$tiposReservaHash() => r'fcb59ed4bef2ca9ce0410aa7b070c4bb7fcac81c';

/// Tipos de reserva de un laboratorio puntual -- usado por el dropdown
/// dinámico del formulario de reserva (`laboratorio_reserva_sheet.dart`,
/// `recurso_disponibilidad_sheet.dart`, Fase 7).

final class TiposReservaFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<List<TipoReserva>>, int> {
  TiposReservaFamily._()
    : super(
        retry: null,
        name: r'tiposReservaProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// Tipos de reserva de un laboratorio puntual -- usado por el dropdown
  /// dinámico del formulario de reserva (`laboratorio_reserva_sheet.dart`,
  /// `recurso_disponibilidad_sheet.dart`, Fase 7).

  TiposReservaProvider call(int laboratorioId) =>
      TiposReservaProvider._(argument: laboratorioId, from: this);

  @override
  String toString() => r'tiposReservaProvider';
}

/// Tipos de reserva para la pantalla de gestión (`GestionTiposReservaScreen`)
/// -- mismo criterio de filtro cliente-side que `espaciosGestionProvider`:
/// un gestor solo ve/gestiona los de su propio laboratorio.

@ProviderFor(tiposReservaGestion)
final tiposReservaGestionProvider = TiposReservaGestionProvider._();

/// Tipos de reserva para la pantalla de gestión (`GestionTiposReservaScreen`)
/// -- mismo criterio de filtro cliente-side que `espaciosGestionProvider`:
/// un gestor solo ve/gestiona los de su propio laboratorio.

final class TiposReservaGestionProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<TipoReserva>>,
          List<TipoReserva>,
          FutureOr<List<TipoReserva>>
        >
    with
        $FutureModifier<List<TipoReserva>>,
        $FutureProvider<List<TipoReserva>> {
  /// Tipos de reserva para la pantalla de gestión (`GestionTiposReservaScreen`)
  /// -- mismo criterio de filtro cliente-side que `espaciosGestionProvider`:
  /// un gestor solo ve/gestiona los de su propio laboratorio.
  TiposReservaGestionProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'tiposReservaGestionProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$tiposReservaGestionHash();

  @$internal
  @override
  $FutureProviderElement<List<TipoReserva>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<TipoReserva>> create(Ref ref) {
    return tiposReservaGestion(ref);
  }
}

String _$tiposReservaGestionHash() =>
    r'a76415268e844f28ccc7c0a1a41881461d48b277';
