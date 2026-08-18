import { apiFetch } from './api';
import type { Zona } from '@/types/zona';

export function listarZonas(espacioId?: number): Promise<Zona[]> {
  const query = espacioId !== undefined ? `?espacio_id=${espacioId}` : '';
  return apiFetch<Zona[]>(`/zonas${query}`);
}