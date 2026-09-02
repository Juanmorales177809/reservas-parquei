import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../data/motivos_solicitud_repository.dart';
import '../domain/motivo_solicitud.dart';

part 'motivos_solicitud_providers.g.dart';

@riverpod
Future<List<MotivoSolicitud>> motivosSolicitud(Ref ref, int laboratorioId) {
  return ref.read(motivosSolicitudRepositoryProvider).listar(laboratorioId: laboratorioId);
}
