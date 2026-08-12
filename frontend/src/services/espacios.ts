import { apiFetch } from './api';
import type {
  ConfiguracionEspacio,
  ConfiguracionEspacioUpdate,
  DisponibilidadSlot,
  Espacio,
  EspacioCreate,
  EspacioUpdate,
} from '@/types/espacio';

export function listarEspacios(): Promise<Espacio[]> {
  return apiFetch<Espacio[]>('/espacios');
}

export function crearEspacio(data: EspacioCreate): Promise<Espacio> {
  return apiFetch<Espacio>('/espacios', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export function actualizarEspacio(id: number, data: EspacioUpdate): Promise<Espacio> {
  return apiFetch<Espacio>(`/espacios/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export function eliminarEspacio(id: number): Promise<void> {
  return apiFetch<void>(`/espacios/${id}`, {
    method: 'DELETE',
  });
}

export function getDisponibilidad(espacioId: number, fecha: string): Promise<DisponibilidadSlot[]> {
  return apiFetch<DisponibilidadSlot[]>(`/espacios/${espacioId}/disponibilidad?fecha=${fecha}`);
}

export function obtenerConfiguracionEspacio(): Promise<ConfiguracionEspacio> {
  return apiFetch<ConfiguracionEspacio>('/espacios/gestion/configuracion');
}

export function actualizarConfiguracionEspacio(
  data: ConfiguracionEspacioUpdate,
): Promise<ConfiguracionEspacio> {
  return apiFetch<ConfiguracionEspacio>('/espacios/gestion/configuracion', {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}
