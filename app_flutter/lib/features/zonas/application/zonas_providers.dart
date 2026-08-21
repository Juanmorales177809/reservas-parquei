import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../data/zonas_repository.dart';
import '../domain/zona.dart';

part 'zonas_providers.g.dart';

@riverpod
Future<List<Zona>> zonasList(Ref ref, {int? espacioId}) {
  return ref.read(zonasRepositoryProvider).listar(espacioId: espacioId);
}

@riverpod
Future<List<Zona>> zonasGestion(Ref ref) {
  // Para gestor, el backend ya filtra al espacio gestionado; para admin
  // sin filtro devuelve todas. Usamos listar sin espacioId.
  return ref.read(zonasRepositoryProvider).listar();
}
