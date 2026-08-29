import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../data/lista_espera_repository.dart';
import '../domain/lista_espera_entrada.dart';

part 'lista_espera_providers.g.dart';

@riverpod
Future<List<ListaEsperaEntrada>> misEntradasListaEspera(Ref ref) {
  return ref.watch(listaEsperaRepositoryProvider).listarMias();
}
