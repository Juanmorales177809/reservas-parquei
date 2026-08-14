'use client';

import { useEffect, useMemo, type ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import LoadingSpinner from './LoadingSpinner';
import type { AuthUser } from '@/types/auth';

export type RolUsuario = AuthUser['rol'];

interface Props {
  children: ReactNode;
  roles?: RolUsuario[];
  adminOnly?: boolean;
  redirectNoAuth?: string;
  redirectForbidden?: string | ((user: AuthUser) => string);
}

/**
 * Protección de rutas a nivel de UI. La autorización real sigue viviendo en
 * el backend (deps por rol); este componente solo evita renderizar páginas
 * que el usuario no debería ver y redirige de forma equivalente a los
 * guards manuales que reemplaza.
 */
export default function ProtectedRoute({
  children,
  roles,
  adminOnly,
  redirectNoAuth = '/login',
  redirectForbidden = '/',
}: Props) {
  const router = useRouter();
  const { isAuthenticated, user, loading } = useAuth();
  const rolesRequeridos: RolUsuario[] = useMemo(
    () => (adminOnly ? ['admin'] : (roles ?? [])),
    [adminOnly, roles],
  );

  useEffect(() => {
    if (loading) return;
    if (!isAuthenticated) {
      router.replace(redirectNoAuth);
      return;
    }
    if (rolesRequeridos.length > 0 && user && !rolesRequeridos.includes(user.rol)) {
      router.replace(
        typeof redirectForbidden === 'function' ? redirectForbidden(user) : redirectForbidden,
      );
    }
  }, [loading, isAuthenticated, user, rolesRequeridos, redirectNoAuth, redirectForbidden, router]);

  if (loading) return <LoadingSpinner />;
  if (!isAuthenticated) return null;
  if (rolesRequeridos.length > 0 && user && !rolesRequeridos.includes(user.rol)) return null;

  return <>{children}</>;
}
