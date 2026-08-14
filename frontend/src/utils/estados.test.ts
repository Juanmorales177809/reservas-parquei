import { describe, expect, it } from 'vitest';

import {
  BADGE_ESTADO_ENTIDAD,
  BADGE_ESTADO_RESERVA,
  LABEL_ESTADO_RESERVA,
  badgeEstadoEntidad,
  badgeEstadoReserva,
  labelEstadoReserva,
} from './estados';

describe('estados: reservas', () => {
  it('conserva los labels visibles actuales', () => {
    expect(LABEL_ESTADO_RESERVA).toEqual({
      esperando: 'Pendiente',
      aprobada: 'Aprobada',
      rechazada: 'Rechazada',
      cancelada: 'Cancelada',
    });
  });

  it('conserva las variantes visuales actuales', () => {
    expect(BADGE_ESTADO_RESERVA).toEqual({
      esperando: 'badge-warning',
      aprobada: 'badge-success',
      rechazada: 'badge-danger',
      cancelada: 'badge-neutral',
    });
  });

  it('conserva los valores serializados del backend como claves', () => {
    expect(Object.keys(BADGE_ESTADO_RESERVA)).toEqual([
      'esperando',
      'aprobada',
      'rechazada',
      'cancelada',
    ]);
  });

  it('labelEstadoReserva devuelve el valor crudo para estados desconocidos', () => {
    expect(labelEstadoReserva('desconocido')).toBe('desconocido');
  });

  it('badgeEstadoReserva devuelve badge-neutral para estados desconocidos', () => {
    expect(badgeEstadoReserva('desconocido')).toBe('badge-neutral');
  });

  it('no lanza errores con valores inesperados', () => {
    expect(() => badgeEstadoReserva('')).not.toThrow();
    expect(() => labelEstadoReserva('')).not.toThrow();
  });
});

describe('estados: entidades', () => {
  it('conserva las variantes visuales de espacios/recursos', () => {
    expect(BADGE_ESTADO_ENTIDAD).toEqual({
      activo: 'badge-success',
      inactivo: 'badge-neutral',
      mantenimiento: 'badge-warning',
    });
  });

  it('badgeEstadoEntidad devuelve badge-neutral para estados desconocidos', () => {
    expect(badgeEstadoEntidad('desconocido')).toBe('badge-neutral');
  });
});
