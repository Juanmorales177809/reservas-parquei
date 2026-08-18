import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { apiFetch } from './api';

/** Respuesta JSON simulada del backend. Devuelve el mock de fetch para
 * poder inspeccionar cómo se llamó (headers, credentials). */
function mockFetch(status: number, body: unknown) {
  const fetchMock = vi.fn().mockResolvedValue(
    new Response(JSON.stringify(body), {
      status,
      headers: { 'Content-Type': 'application/json' },
    }),
  );
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

beforeEach(() => {
  // jsdom no implementa navegación real: sustituir location para poder
  // observar el redirect sin errores de navegación.
  Object.defineProperty(window, 'location', {
    configurable: true,
    writable: true,
    value: { href: '' },
  });
});

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
  window.localStorage.clear();
});

describe('apiFetch: sesión por cookie, no por localStorage (Fase 9F-B)', () => {
  it('envía credentials: same-origin en cada request', async () => {
    const fetchMock = mockFetch(200, { ok: true });

    await apiFetch('/algo');

    const init = fetchMock.mock.calls[0][1] as RequestInit;
    expect(init.credentials).toBe('same-origin');
  });

  it('no agrega el header Authorization', async () => {
    const fetchMock = mockFetch(200, { ok: true });

    await apiFetch('/algo');

    const init = fetchMock.mock.calls[0][1] as RequestInit;
    const headers = new Headers(init.headers);
    expect(headers.has('Authorization')).toBe(false);
  });

  it('ignora cualquier valor en localStorage.token: nunca lo lee ni lo usa', async () => {
    window.localStorage.setItem('token', 'valor-que-nunca-deberia-usarse');
    const fetchMock = mockFetch(200, { ok: true });

    await apiFetch('/algo');

    const init = fetchMock.mock.calls[0][1] as RequestInit;
    const headers = new Headers(init.headers);
    expect(headers.has('Authorization')).toBe(false);
  });
});

describe('apiFetch: 401 en login', () => {
  it('no redirige automáticamente', async () => {
    mockFetch(401, { detail: 'Credenciales inválidas' });
    await expect(apiFetch('/auth/login', { method: 'POST' })).rejects.toThrow(
      'Credenciales inválidas',
    );
    expect(window.location.href).toBe('');
  });

  it('muestra el mensaje esperado del backend', async () => {
    mockFetch(401, { detail: 'Credenciales inválidas' });
    const error = await apiFetch('/auth/login', { method: 'POST' }).catch(
      (e: Error) => e.message,
    );
    expect(error).toBe('Credenciales inválidas');
  });
});

describe('apiFetch: 401 en /usuarios/me (sondeo pasivo de sesión al montar AuthContext)', () => {
  it('no redirige: un visitante anónimo en una página pública recibe 401 aquí y es normal', async () => {
    mockFetch(401, { detail: 'No se pudo validar la autenticación' });

    await expect(apiFetch('/usuarios/me')).rejects.toThrow();

    expect(window.location.href).toBe('');
  });

  it('propaga el error para que AuthContext lo capture y trate como sesión ausente', async () => {
    mockFetch(401, { detail: 'No se pudo validar la autenticación' });

    await expect(apiFetch('/usuarios/me')).rejects.toThrow(
      'No se pudo validar la autenticación',
    );
  });
});

describe('apiFetch: 401 en endpoint protegido distinto de /usuarios/me (sesión expirada)', () => {
  it('redirige a /login', async () => {
    mockFetch(401, { detail: 'No se pudo validar la autenticación' });
    await expect(apiFetch('/reservas/mis-reservas')).rejects.toThrow('Sesión expirada');
    expect(window.location.href).toBe('/login');
  });

  it('no intenta leer ni escribir localStorage: la cookie HttpOnly no es manipulable desde JS', async () => {
    const getItemSpy = vi.spyOn(Storage.prototype, 'getItem');
    const removeItemSpy = vi.spyOn(Storage.prototype, 'removeItem');
    mockFetch(401, { detail: 'No se pudo validar la autenticación' });

    await expect(apiFetch('/reservas/mis-reservas')).rejects.toThrow();

    expect(removeItemSpy).not.toHaveBeenCalled();
    expect(getItemSpy).not.toHaveBeenCalled();
  });
});

describe('apiFetch: 403 en endpoint protegido', () => {
  it('no se trata como sesión expirada: no redirige', async () => {
    mockFetch(403, { detail: 'Solo un administrador puede realizar esta acción' });
    await expect(apiFetch('/usuarios', { method: 'POST' })).rejects.toThrow(
      'Solo un administrador puede realizar esta acción',
    );
    expect(window.location.href).toBe('');
  });
});

describe('apiFetch: login exitoso', () => {
  it('devuelve la respuesta sin alterar el flujo actual', async () => {
    mockFetch(200, { access_token: 'token-del-backend', token_type: 'bearer', user: { id: 1 } });
    const respuesta = await apiFetch('/auth/login', { method: 'POST' });
    expect(respuesta).toEqual({
      access_token: 'token-del-backend',
      token_type: 'bearer',
      user: { id: 1 },
    });
    expect(window.location.href).toBe('');
  });

  it('no guarda el access_token de la respuesta en localStorage', async () => {
    mockFetch(200, { access_token: 'token-del-backend', token_type: 'bearer', user: { id: 1 } });

    await apiFetch('/auth/login', { method: 'POST' });

    expect(window.localStorage.getItem('token')).toBeNull();
  });
});

describe('apiFetch: logout', () => {
  it('POST /auth/logout con 204 no intenta redirigir ni tocar localStorage', async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
    vi.stubGlobal('fetch', fetchMock);

    const respuesta = await apiFetch('/auth/logout', { method: 'POST' });

    expect(respuesta).toBeUndefined();
    expect(window.location.href).toBe('');
  });
});
