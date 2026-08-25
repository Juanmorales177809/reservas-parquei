import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../../core/network/api_exception.dart';
import '../../auth/application/auth_provider.dart';
import '../../auth/domain/auth_user.dart';
import '../data/dashboard_repository.dart';
import '../domain/dashboard_summary.dart';

part 'dashboard_providers.g.dart';

@riverpod
Future<DashboardSummary> dashboardSummary(Ref ref) async {
  final user = ref.watch(authProvider).value;
  // `user == null` es un estado transitorio real, no solo teórico: si la
  // sesión expira mientras el usuario está en `/admin` (dashboard), este
  // provider reacciona al cambio de `authProvider` ANTES de que el guard
  // del router (que corre en un frame aparte, vía `refreshListenable`)
  // alcance a redirigir a `/login`. Sin este chequeo, el `else` de abajo
  // pegaba sin sesión a `GET /admin/dashboard/summary` — el endpoint de
  // ADMIN, sin importar el rol real — devolviendo un 401 espurio que no
  // aporta nada (el guard va a sacar de esta pantalla en el próximo
  // frame de todas formas). Encontrado en producción, no en pruebas.
  if (user == null) {
    throw const ApiException('Sesión expirada.', statusCode: 401);
  }
  final repo = ref.read(dashboardRepositoryProvider);
  if (user.rol == RolUsuario.gestor) {
    return repo.resumenGestion();
  }
  return repo.resumenAdmin();
}
