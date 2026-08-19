import { apiFetch } from './api';
import type { Ensayo } from '@/types/ensayo';

export function listarEnsayos(zonaId?: number): Promise<Ensayo[]> {
  const params = zonaId ? `?zona_id=${zonaId}` : '';
  return apiFetch<Ensayo[]>(`/ensayos${params}`);
}
