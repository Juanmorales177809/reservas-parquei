import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../auth/application/auth_provider.dart';
import '../../auth/domain/auth_user.dart';
import '../data/dashboard_repository.dart';
import '../domain/dashboard_summary.dart';

part 'dashboard_providers.g.dart';

@riverpod
Future<DashboardSummary> dashboardSummary(Ref ref) async {
  final user = ref.watch(authProvider).value;
  final repo = ref.read(dashboardRepositoryProvider);
  if (user?.rol == RolUsuario.gestor) {
    return repo.resumenGestion();
  }
  return repo.resumenAdmin();
}
