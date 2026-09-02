import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../laboratorios/domain/disponibilidad_slot.dart';
import '../data/recursos_repository.dart';
import '../domain/recurso.dart';
import '../domain/tipo_recurso.dart';

part 'recursos_providers.g.dart';

/// Carga una sola vez todos los recursos activos (sin filtrar por laboratorio)
/// y se agrupa client-side por `laboratorioId` — evita N+1 llamadas al abrir
/// cada laboratorio, igual que hoy hace `frontend/src/app/laboratorios/page.tsx`.
@riverpod
Future<List<Recurso>> recursosActivos(Ref ref) {
  return ref.read(recursosRepositoryProvider).listar(soloActivos: true);
}

@riverpod
List<Recurso> recursosPorLaboratorio(Ref ref, int laboratorioId) {
  final todos = ref.watch(recursosActivosProvider).value ?? const [];
  return todos.where((r) => r.laboratorioId == laboratorioId).toList(growable: false);
}

@riverpod
Future<List<DisponibilidadSlot>> recursoDisponibilidad(Ref ref, int recursoId, DateTime fecha) {
  return ref.read(recursosRepositoryProvider).disponibilidad(recursoId, fecha);
}

@riverpod
Future<List<Recurso>> recursosGestion(Ref ref) {
  return ref.read(recursosRepositoryProvider).listarGestion();
}

@riverpod
Future<List<TipoRecurso>> tiposRecursos(Ref ref) {
  return ref.read(recursosRepositoryProvider).listarTipos();
}
