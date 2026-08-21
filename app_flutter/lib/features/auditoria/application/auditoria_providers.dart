import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../data/auditoria_repository.dart';
import '../domain/control_cambio.dart';

part 'auditoria_providers.g.dart';

@riverpod
Future<List<ControlCambio>> controlCambiosList(Ref ref) {
  return ref.read(auditoriaRepositoryProvider).listar();
}
