import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { apiFetch } from './api';

/** Respuesta JSON simulada del backend. */
function mockFetch(status: number, body: unknown) {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue(
      new Response(JSON.stringify(body), {
        status,
        headers: { 'Content-Type': 'application/json' },
      }),
    ),
  );
}

beforeEach(() => {
  // jsdom no implementa navegación real: sustituir location para poder
  // observar el redirect sin errores de navegación.
  Object.defineProperty(window, 'location', {
    configurable: true,
    writable: true,
    value: { href: '' },
  });
  window.localStorage.setItem('token', 'token-existente');
  window.localStorage.setItem('user', '{"id":1}');
  vi.spyOn(Storage.prototype, 'removeItem');
});

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
  window.localStorage.clear();
});

describe('apiFetch: 401 en login', () => {
  it('no redirige automáticamente', async () => {
    mockFetch(401, { detail: 'Credenciales inválidas' });
    await expect(apiFetch('/auth/login', { method: 'POST' })).rejects.toThrow(
      'Credenciales inválidas',
    );
    expect(window.location.href).toBe('');
  });

  it('no limpia la sesión existente (no deja una sesión parcial)', async () => {
    mockFetch(401, { detail: 'Credenciales inválidas' });
    await expect(apiFetch('/auth/login', { method: 'POST' })).rejects.toThrow();
    expect(Storage.prototype.removeItem).not.toHaveBeenCalled();
    expect(window.localStorage.getItem('token')).toBe('token-existente');
  });

  it('muestra el mensaje esperado del backend', async () => {
    mockFetch(401, { detail: 'Credenciales inválidas' });
    const error = await apiFetch('/auth/login', { method: 'POST' }).catch(
      (e: Error) => e.message,
    );
    expect(error).toBe('Credenciales inválidas');
  });
});

describe('apiFetch: 401 en endpoint protegido (sesión expirada)', () => {
  it('limpia token y usuario', async () => {
    mockFetch(401, { detail: 'No se pudo validar la autenticación' });
    await expect(apiFetch('/reservas/mis-reservas')).rejects.toThrow('Sesión expirada');
    expect(Storage.prototype.removeItem).toHaveBeenCalledWith('token');
    expect(Storage.prototype.removeItem).toHaveBeenCalledWith('user');
  });

  it('redirige a /login', async () => {
    mockFetch(401, { detail: 'No se pudo validar la autenticación' });
    await expect(apiFetch('/reservas/mis-reservas')).rejects.toThrow();
    expect(window.location.href).toBe('/login');
  });
});

describe('apiFetch: 403 en endpoint protegido', () => {
  it('no se trata como logout: no limpia la sesión', async () => {
    mockFetch(403, { detail: 'Solo un administrador puede realizar esta acción' });
    await expect(apiFetch('/usuarios', { method: 'POST' })).rejects.toThrow(
      'Solo un administrador puede realizar esta acción',
    );
    expect(Storage.prototype.removeItem).not.toHaveBeenCalled();
    expect(window.localStorage.getItem('token')).toBe('token-existente');
  });
});

describe('apiFetch: login exitoso', () => {
  it('devuelve la respuesta sin alterar el flujo actual', async () => {
    mockFetch(200, { access_token: 'nuevo-token', token_type: 'bearer', user: { id: 1 } });
    const respuesta = await apiFetch('/auth/login', { method: 'POST' });
    expect(respuesta).toEqual({ access_token: 'nuevo-token', token_type: 'bearer', user: { id: 1 } });
    expect(window.location.href).toBe('');
  });
});
