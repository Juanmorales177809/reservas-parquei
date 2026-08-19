import { describe, expect, it } from 'vitest';

import type { Reserva } from '@/types/reserva';
import { etiquetaObjetivoReserva } from './reservaEtiqueta';

const espacio = { id: 1, nombre: 'Sala', capacidad: 10, estado: 'activo' as const };

function reservaBase(overrides: Partial<Reserva> = {}): Reserva {
  return {
    id: 1,
    usuario_id: 1,
    espacio_id: 1,
    fecha: '2026-01-01',
    hora_inicio: '08:00:00',
    hora_fin: '10:00:00',
    estado: 'esperando',
    asistentes: 1,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    usuario: { id: 1, username: 'usuario', email: 'usuario@example.com', rol: 'usuario' },
    espacio,
    ...overrides,
  };
}

describe('etiquetaObjetivoReserva', () => {
  it('usa el nombre del recurso cuando hay uno solo y ninguna zona', () => {
    const reserva = reservaBase({
      recurso_ids: [5],
      recursos: [{ id: 5, nombre: 'Proyector', capacidad: 1, estado: 'activo', espacio }],
    });
    expect(etiquetaObjetivoReserva(reserva)).toBe('Proyector');
  });

  it('junta los nombres de varios recursos directos con coma', () => {
    const reserva = reservaBase({
      recurso_ids: [5, 6],
      recursos: [
        { id: 5, nombre: 'Proyector', capacidad: 1, estado: 'activo', espacio },
        { id: 6, nombre: 'Cámara', capacidad: 1, estado: 'activo', espacio },
      ],
    });
    expect(etiquetaObjetivoReserva(reserva)).toBe('Proyector, Cámara');
  });

  it('prioriza la(s) zona(s) sobre los recursos', () => {
    const reserva = reservaBase({
      recurso_ids: [5],
      recursos: [{ id: 5, nombre: 'Proyector', capacidad: 1, estado: 'activo', espacio }],
      zona_ids: [9],
      zonas: [{ id: 9, nombre: 'Zona Norte', espacio_id: 1, descripcion: null, capacidad: null, estado: 'activo' }],
    });
    expect(etiquetaObjetivoReserva(reserva)).toBe('Zona Norte');
  });

  it('junta varios nombres de zona con coma', () => {
    const reserva = reservaBase({
      zonas: [
        { id: 9, nombre: 'Zona Norte', espacio_id: 1, descripcion: null, capacidad: null, estado: 'activo' },
        { id: 10, nombre: 'Zona Sur', espacio_id: 1, descripcion: null, capacidad: null, estado: 'activo' },
      ],
    });
    expect(etiquetaObjetivoReserva(reserva)).toBe('Zona Norte, Zona Sur');
  });

  it('recae en el ancla singular si un contrato en caché no trae "recursos" (compatibilidad)', () => {
    const reserva = reservaBase({
      recurso: { id: 5, nombre: 'Proyector', capacidad: 1, estado: 'activo', espacio },
    });
    expect(etiquetaObjetivoReserva(reserva)).toBe('Proyector');
  });

  it('devuelve cadena vacía si no hay recurso ni zona resueltos', () => {
    const reserva = reservaBase();
    expect(etiquetaObjetivoReserva(reserva)).toBe('');
  });
});
