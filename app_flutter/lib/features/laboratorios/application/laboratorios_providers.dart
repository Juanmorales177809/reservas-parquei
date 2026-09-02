import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../data/laboratorios_repository.dart';
import '../domain/configuracion_laboratorio.dart';
import '../domain/laboratorio.dart';

part 'laboratorios_providers.g.dart';

@riverpod
Future<List<Laboratorio>> laboratoriosList(Ref ref) {
  return ref.read(laboratoriosRepositoryProvider).listar();
}

@riverpod
Future<Laboratorio> laboratorio(Ref ref, int laboratorioId) {
  return ref.read(laboratoriosRepositoryProvider).obtener(laboratorioId);
}

/// Configuración del laboratorio del gestor (`GestionLaboratorioScreen`).
@riverpod
Future<ConfiguracionLaboratorio> configuracionLaboratorioGestion(Ref ref) {
  return ref.read(laboratoriosRepositoryProvider).obtenerConfiguracionGestion();
}
