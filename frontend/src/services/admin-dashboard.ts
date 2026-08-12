import { apiFetch } from './api';
import type { AdminDashboardSummary } from '@/types/admin-dashboard';

export function obtenerResumenAdmin(): Promise<AdminDashboardSummary> {
  return apiFetch<AdminDashboardSummary>('/admin/dashboard/summary');
}

export function obtenerResumenGestor(): Promise<AdminDashboardSummary> {
  return apiFetch<AdminDashboardSummary>('/gestion/dashboard/summary');
}
