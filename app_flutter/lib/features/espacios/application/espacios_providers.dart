import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../auth/application/auth_provider.dart';
import '../../auth/domain/auth_user.dart';
import '../data/espacios_repository.dart';
import '../domain/espacio.dart';

part 'espacios_providers.g.dart';

@riverpod
Future<List<Espacio>> espaciosList(Ref ref, {int? laboratorioId}) {
  return ref.read(espaciosRepositoryProvider).listar(laboratorioId: laboratorioId);
}

/// Espacios para la pantalla de gestión (`GestionEspaciosScreen`).
///
/// El filtro por laboratorio se aplica **desde el cliente** a propósito: al
/// contrario de lo que decía el comentario anterior aquí, `GET /espacios`
/// NO acota al laboratorio gestionado — `backend/app/api/espacios.py` solo
/// filtra por estado, así que gestor y admin reciben las espacios de todos
/// los laboratorios. Sin este filtro, un gestor veía espacios ajenas en la
/// lista y podía elegirlas por error.
@riverpod
Future<List<Espacio>> espaciosGestion(Ref ref) {
  final usuario = ref.watch(authProvider).value;
  final laboratorioId = usuario?.rol == RolUsuario.gestor ? usuario?.laboratorio?.id : null;
  return ref.read(espaciosRepositoryProvider).listar(laboratorioId: laboratorioId);
}
