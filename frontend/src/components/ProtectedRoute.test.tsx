import { render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import ProtectedRoute from './ProtectedRoute';
import type { AuthUser } from '@/types/auth';

const { replaceMock, useAuthMock } = vi.hoisted(() => ({
  replaceMock: vi.fn(),
  useAuthMock: vi.fn(),
}));

vi.mock('next/navigation', () => ({
  useRouter: () => ({ replace: replaceMock, push: vi.fn(), back: vi.fn(), forward: vi.fn() }),
}));

vi.mock('@/context/AuthContext', () => ({
  useAuth: useAuthMock,
}));

function usuarioDePrueba(rol: AuthUser['rol'] = 'usuario'): AuthUser {
  return {
    id: 1,
    username: 'usuario-prueba',
    email: 'usuario-prueba@test.com',
    rol,
    espacio: null,
  };
}

function estadoAuth({
  loading = false,
  autenticado = true,
  rol = 'usuario' as AuthUser['rol'],
} = {}) {
  useAuthMock.mockReturnValue({
    user: autenticado ? usuarioDePrueba(rol) : null,
    token: autenticado ? 'token-de-prueba' : null,
    isAdmin: rol === 'admin',
    canManageResources: rol === 'admin' || rol === 'gestor',
    isAuthenticated: autenticado,
    loading,
    login: vi.fn(),
    logout: vi.fn(),
  });
}

const CONTENIDO = 'CONTENIDO-PROTEGIDO';

beforeEach(() => {
  replaceMock.mockClear();
  useAuthMock.mockReset();
});

describe('ProtectedRoute', () => {
  it('redirige a /login cuando no hay sesión y no renderiza el contenido', async () => {
    estadoAuth({ autenticado: false });
    render(<ProtectedRoute><p>{CONTENIDO}</p></ProtectedRoute>);
    await waitFor(() => expect(replaceMock).toHaveBeenCalledWith('/login'));
    expect(screen.queryByText(CONTENIDO)).not.toBeInTheDocument();
  });

  it('muestra el spinner durante la hidratación de la sesión', () => {
    estadoAuth({ loading: true, autenticado: false });
    render(<ProtectedRoute><p>{CONTENIDO}</p></ProtectedRoute>);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('renderiza el contenido para un usuario autenticado sin restricción de rol', () => {
    estadoAuth();
    render(<ProtectedRoute><p>{CONTENIDO}</p></ProtectedRoute>);
    expect(screen.getByText(CONTENIDO)).toBeInTheDocument();
    expect(replaceMock).not.toHaveBeenCalled();
  });

  it('renderiza el contenido cuando el rol está permitido', () => {
    estadoAuth({ rol: 'gestor' });
    render(
      <ProtectedRoute roles={['admin', 'gestor']}><p>{CONTENIDO}</p></ProtectedRoute>,
    );
    expect(screen.getByText(CONTENIDO)).toBeInTheDocument();
  });

  it('redirige con redirectForbidden como string cuando el rol no está permitido', async () => {
    estadoAuth();
    render(
      <ProtectedRoute roles={['admin', 'gestor']} redirectForbidden="/dashboard">
        <p>{CONTENIDO}</p>
      </ProtectedRoute>,
    );
    await waitFor(() => expect(replaceMock).toHaveBeenCalledWith('/dashboard'));
    expect(screen.queryByText(CONTENIDO)).not.toBeInTheDocument();
  });

  it('redirige con redirectForbidden como función según el rol', async () => {
    estadoAuth({ rol: 'admin' });
    render(
      <ProtectedRoute
        roles={['gestor']}
        redirectForbidden={(usuario) => (usuario.rol === 'admin' ? '/admin' : '/dashboard')}
      >
        <p>{CONTENIDO}</p>
      </ProtectedRoute>,
    );
    await waitFor(() => expect(replaceMock).toHaveBeenCalledWith('/admin'));
  });

  it('adminOnly permite solo al rol admin', async () => {
    estadoAuth({ rol: 'gestor' });
    render(<ProtectedRoute adminOnly><p>{CONTENIDO}</p></ProtectedRoute>);
    await waitFor(() => expect(replaceMock).toHaveBeenCalledWith('/'));
    expect(screen.queryByText(CONTENIDO)).not.toBeInTheDocument();
  });

  it('respeta redirectNoAuth personalizado', async () => {
    estadoAuth({ autenticado: false });
    render(
      <ProtectedRoute redirectNoAuth="/entrar"><p>{CONTENIDO}</p></ProtectedRoute>,
    );
    await waitFor(() => expect(replaceMock).toHaveBeenCalledWith('/entrar'));
  });

  it('no genera loops: una sola redirección tras estabilizarse', async () => {
    estadoAuth({ autenticado: false });
    render(<ProtectedRoute><p>{CONTENIDO}</p></ProtectedRoute>);
    await waitFor(() => expect(replaceMock).toHaveBeenCalledTimes(1));
    await new Promise((resolve) => setTimeout(resolve, 10));
    expect(replaceMock).toHaveBeenCalledTimes(1);
  });

  it('no realiza peticiones de red ni sustituye la autorización del backend', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch');
    estadoAuth();
    render(<ProtectedRoute roles={['admin']}><p>{CONTENIDO}</p></ProtectedRoute>);
    await waitFor(() => expect(replaceMock).toHaveBeenCalledWith('/'));
    expect(fetchSpy).not.toHaveBeenCalled();
  });
});
