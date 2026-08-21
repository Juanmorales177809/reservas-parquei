import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../data/ensayos_repository.dart';
import '../domain/ensayo.dart';

part 'ensayos_providers.g.dart';

@riverpod
Future<List<Ensayo>> ensayosList(Ref ref, {int? zonaId}) {
  return ref.read(ensayosRepositoryProvider).listar(zonaId: zonaId);
}

@riverpod
Future<List<Ensayo>> ensayosGestion(Ref ref) {
  return ref.read(ensayosRepositoryProvider).listar();
}
