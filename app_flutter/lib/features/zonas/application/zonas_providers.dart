import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../auth/application/auth_provider.dart';
import '../../auth/domain/auth_user.dart';
import '../data/zonas_repository.dart';
import '../domain/zona.dart';

part 'zonas_providers.g.dart';

@riverpod
Future<List<Zona>> zonasList(Ref ref, {int? espacioId}) {
  return ref.read(zonasRepositoryProvider).listar(espacioId: espacioId);
}

/// Zonas para las pantallas de gestión (`GestionZonasScreen` y el
/// desplegable de zona de `GestionEnsayosScreen`).
///
/// El filtro por espacio se aplica **desde el cliente** a propósito: al
/// contrario de lo que decía el comentario anterior aquí, `GET /zonas`
/// NO acota al espacio gestionado — `backend/app/api/zonas.py` solo
/// filtra por estado, así que gestor y admin reciben las zonas de todos
/// los espacios. Sin este filtro, un gestor veía zonas ajenas en la
/// lista y podía elegir una en el formulario de ensayos, que el backend
/// después rechazaba con 403.
@riverpod
Future<List<Zona>> zonasGestion(Ref ref) {
  final usuario = ref.watch(authProvider).value;
  final espacioId = usuario?.rol == RolUsuario.gestor ? usuario?.espacio?.id : null;
  return ref.read(zonasRepositoryProvider).listar(espacioId: espacioId);
}
