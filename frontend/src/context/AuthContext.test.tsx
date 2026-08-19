import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useState } from 'react';

import { AuthProvider, useAuth } from './AuthContext';
import type { AuthUser } from '@/types/auth';

const { loginMock, logoutMock, getProfileMock } = vi.hoisted(() => ({
  loginMock: vi.fn(),
  logoutMock: vi.fn(),
  getProfileMock: vi.fn(),
}));

vi.mock('@/services/auth', () => ({
  login: loginMock,
  logout: logoutMock,
  getProfile: getProfileMock,
}));

function usuarioDePrueba(rol: AuthUser['rol'] = 'usuario'): AuthUser {
  return { id: 1, username: 'ana', email: 'ana@example.com', rol, espacio: null };
}

/** Componente sonda: expone el estado de AuthContext como texto para
 * poder hacer aserciones simples, y captura el error de login (el
 * botón real de login/page.tsx hace lo mismo con try/catch). */
function Sonda() {
  const { user, isAuthenticated, loading, login, logout } = useAuth();
  const [error, setError] = useState<string | null>(null);

  async function handleLogin() {
    setError(null);
    try {
      await login('ana', 'secret123');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'error desconocido');
    }
  }

  return (
    <div>
      <span data-testid="loading">{String(loading)}</span>
      <span data-testid="autenticado">{String(isAuthenticated)}</span>
      <span data-testid="usuario">{user?.username ?? 'ninguno'}</span>
      <span data-testid="error">{error ?? ''}</span>
      <button onClick={handleLogin}>login</button>
      <button onClick={() => logout()}>logout</button>
    </div>
  );
}

beforeEach(() => {
  loginMock.mockReset();
  logoutMock.mockReset();
  getProfileMock.mockReset();
});

describe('AuthProvider: sesión existente al montar (Fase 9F-B)', () => {
  it('usa GET /usuarios/me para autenticar, con loading correcto durante la consulta', async () => {
    getProfileMock.mockResolvedValue(usuarioDePrueba());

    render(
      <AuthProvider>
        <Sonda />
      </AuthProvider>,
    );

    expect(screen.getByTestId('loading').textContent).toBe('true');
    expect(screen.getByTestId('autenticado').textContent).toBe('false');

    await waitFor(() => expect(screen.getByTestId('loading').textContent).toBe('false'));

    expect(screen.getByTestId('autenticado').textContent).toBe('true');
    expect(screen.getByTestId('usuario').textContent).toBe('ana');
    expect(getProfileMock).toHaveBeenCalledTimes(1);
  });
});

describe('AuthProvider: sesión ausente al montar', () => {
  it('un 401 de /usuarios/me deja al visitante como anónimo, sin redirigir por sí mismo', async () => {
    getProfileMock.mockRejectedValue(new Error('No se pudo validar la autenticación'));

    render(
      <AuthProvider>
        <Sonda />
      </AuthProvider>,
    );

    await waitFor(() => expect(screen.getByTestId('loading').textContent).toBe('false'));
    expect(screen.getByTestId('autenticado').textContent).toBe('false');
    expect(screen.getByTestId('usuario').textContent).toBe('ninguno');
  });
});

describe('AuthProvider: login', () => {
  it('login exitoso guarda el usuario de la respuesta, sin tocar localStorage', async () => {
    getProfileMock.mockRejectedValue(new Error('sin sesión'));
    loginMock.mockResolvedValue(usuarioDePrueba('admin'));
    const usuario = userEvent.setup();

    render(
      <AuthProvider>
        <Sonda />
      </AuthProvider>,
    );
    await waitFor(() => expect(screen.getByTestId('loading').textContent).toBe('false'));

    await usuario.click(screen.getByText('login'));

    await waitFor(() => expect(screen.getByTestId('autenticado').textContent).toBe('true'));
    expect(screen.getByTestId('usuario').textContent).toBe('ana');
    expect(loginMock).toHaveBeenCalledWith('ana', 'secret123');
    expect(window.localStorage.getItem('token')).toBeNull();
    expect(window.localStorage.getItem('user')).toBeNull();
  });

  it('login fallido no autentica y propaga el error del backend', async () => {
    getProfileMock.mockRejectedValue(new Error('sin sesión'));
    loginMock.mockRejectedValue(new Error('Credenciales inválidas'));
    const usuario = userEvent.setup();

    render(
      <AuthProvider>
        <Sonda />
      </AuthProvider>,
    );
    await waitFor(() => expect(screen.getByTestId('loading').textContent).toBe('false'));

    await usuario.click(screen.getByText('login'));

    await waitFor(() => expect(screen.getByTestId('error').textContent).toBe('Credenciales inválidas'));
    expect(screen.getByTestId('autenticado').textContent).toBe('false');
  });
});

describe('AuthProvider: logout', () => {
  it('llama POST /auth/logout (vía authService.logout) y limpia el estado local', async () => {
    getProfileMock.mockResolvedValue(usuarioDePrueba());
    logoutMock.mockResolvedValue(undefined);
    const usuario = userEvent.setup();

    render(
      <AuthProvider>
        <Sonda />
      </AuthProvider>,
    );
    await waitFor(() => expect(screen.getByTestId('autenticado').textContent).toBe('true'));

    await usuario.click(screen.getByText('logout'));

    await waitFor(() => expect(screen.getByTestId('autenticado').textContent).toBe('false'));
    expect(logoutMock).toHaveBeenCalledTimes(1);
    expect(screen.getByTestId('usuario').textContent).toBe('ninguno');
  });

  it('limpia el estado local aunque la llamada de red de logout falle', async () => {
    getProfileMock.mockResolvedValue(usuarioDePrueba());
    logoutMock.mockRejectedValue(new Error('network error'));
    const usuario = userEvent.setup();

    render(
      <AuthProvider>
        <Sonda />
      </AuthProvider>,
    );
    await waitFor(() => expect(screen.getByTestId('autenticado').textContent).toBe('true'));

    await usuario.click(screen.getByText('logout'));

    await waitFor(() => expect(screen.getByTestId('autenticado').textContent).toBe('false'));
  });
});

describe('AuthProvider: sin fuente de verdad paralela en localStorage', () => {
  it('nunca escribe token ni user en localStorage durante todo el ciclo login → logout', async () => {
    getProfileMock.mockRejectedValue(new Error('sin sesión'));
    loginMock.mockResolvedValue(usuarioDePrueba('gestor'));
    logoutMock.mockResolvedValue(undefined);
    const usuario = userEvent.setup();

    render(
      <AuthProvider>
        <Sonda />
      </AuthProvider>,
    );
    await waitFor(() => expect(screen.getByTestId('loading').textContent).toBe('false'));

    await usuario.click(screen.getByText('login'));
    await waitFor(() => expect(screen.getByTestId('autenticado').textContent).toBe('true'));

    await usuario.click(screen.getByText('logout'));
    await waitFor(() => expect(screen.getByTestId('autenticado').textContent).toBe('false'));

    expect(window.localStorage.getItem('token')).toBeNull();
    expect(window.localStorage.getItem('user')).toBeNull();
  });
});
