'use client';

import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import type { AuthUser } from '@/types/auth';
import * as authService from '@/services/auth';

interface AuthContextValue {
  user: AuthUser | null;
  isAdmin: boolean;
  canManageResources: boolean;
  isAuthenticated: boolean;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue>({
  user: null,
  isAdmin: false,
  canManageResources: false,
  isAuthenticated: false,
  loading: true,
  login: async () => {},
  logout: async () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fase 9F-B: la sesión ya no se lee de localStorage — el JWT vive en
    // una cookie HttpOnly invisible para JS. GET /usuarios/me es el único
    // mecanismo para saber si hay sesión: 200 = autenticado, 401 = anónimo
    // (comportamiento normal en páginas públicas, no un error). api.ts
    // excluye /usuarios/me del redirect global de 401 precisamente para
    // que este sondeo no fuerce una navegación a /login por sí mismo.
    let vigente = true;
    authService
      .getProfile()
      .then((usuario) => {
        if (vigente) setUser(usuario);
      })
      .catch(() => {
        if (vigente) setUser(null);
      })
      .finally(() => {
        if (vigente) setLoading(false);
      });
    return () => {
      vigente = false;
    };
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    setLoading(true);
    try {
      const usuario = await authService.login(username, password);
      setUser(usuario);
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } catch {
      // A diferencia de login, un fallo de red en logout no debe
      // propagarse: los consumidores (Navbar.tsx) llaman logout() sin
      // esperar la promesa. El estado local igual se limpia abajo; si la
      // cookie sigue viva, expira sola por Max-Age.
    } finally {
      setUser(null);
    }
  }, []);

  const value = useMemo(
    () => ({
      user,
      isAdmin: user?.rol === 'admin',
      canManageResources: user?.rol === 'admin' || user?.rol === 'gestor',
      isAuthenticated: Boolean(user),
      loading,
      login,
      logout,
    }),
    [user, loading, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
