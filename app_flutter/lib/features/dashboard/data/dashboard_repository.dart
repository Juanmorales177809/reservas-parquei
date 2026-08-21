import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/dio_client.dart';
import '../domain/dashboard_summary.dart';

/// Espejo de `frontend/src/services/admin-dashboard.ts` (si existe) — dos
/// endpoints: `/admin/dashboard/summary` (admin) y `/gestion/dashboard/summary` (gestor).
class DashboardRepository {
  DashboardRepository(this._dio);

  final Dio _dio;

  Future<DashboardSummary> resumenAdmin({int periodoDias = 30}) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/admin/dashboard/summary',
      queryParameters: {'periodo_dias': periodoDias},
    );
    return DashboardSummary.fromJson(response.data!);
  }

  Future<DashboardSummary> resumenGestion({int periodoDias = 30}) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/gestion/dashboard/summary',
      queryParameters: {'periodo_dias': periodoDias},
    );
    return DashboardSummary.fromJson(response.data!);
  }
}

final dashboardRepositoryProvider = Provider<DashboardRepository>((ref) {
  return DashboardRepository(ref.watch(dioProvider));
});
