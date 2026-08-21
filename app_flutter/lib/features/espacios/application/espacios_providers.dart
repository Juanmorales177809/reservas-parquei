import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../data/espacios_repository.dart';
import '../domain/configuracion_espacio.dart';
import '../domain/espacio.dart';

part 'espacios_providers.g.dart';

@riverpod
Future<List<Espacio>> espaciosList(Ref ref) {
  return ref.read(espaciosRepositoryProvider).listar();
}

@riverpod
Future<Espacio> espacio(Ref ref, int espacioId) {
  return ref.read(espaciosRepositoryProvider).obtener(espacioId);
}

/// Configuración del espacio del gestor (`GestionEspacioScreen`).
@riverpod
Future<ConfiguracionEspacio> configuracionEspacioGestion(Ref ref) {
  return ref.read(espaciosRepositoryProvider).obtenerConfiguracionGestion();
}
