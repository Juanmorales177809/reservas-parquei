import { apiFetch } from './api';
import type { ControlCambio } from '@/types/control-cambio';

export function listarControlCambios(): Promise<ControlCambio[]> {
  return apiFetch<ControlCambio[]>('/admin/control-cambios');
}
