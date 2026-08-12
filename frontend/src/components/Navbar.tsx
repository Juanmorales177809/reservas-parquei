'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { useState } from 'react';
import NotificationBell from './NotificationBell';

export default function Navbar() {
  const router = useRouter();
  const { isAuthenticated, isAdmin, canManageResources, user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const homeHref = canManageResources ? '/admin' : '/dashboard';
  const resourcesHref = canManageResources ? '/admin/recursos' : '/espacios';
  const reservationsHref = canManageResources ? '/admin/reservas' : '/reservas/mis-reservas';

  function handleLogout() {
    logout();
    router.push('/');
  }

  function closeMenu() {
    setMenuOpen(false);
  }

  const desktopPublicLinks = (
    <>
      <Link href="/espacios" className="text-sm font-medium text-text-secondary hover:text-primary-600 transition-colors">
        Recursos
      </Link>
      <Link href="/login" className="btn btn-primary btn-sm">
        Iniciar Sesión
      </Link>
    </>
  );

  const desktopUserLinks = (
    <>
      <Link
        href={homeHref}
        className="text-sm font-medium text-text-secondary hover:text-primary-600 transition-colors"
      >
        Inicio
      </Link>
      {isAdmin && (
        <Link href="/usuarios" className="text-sm font-medium text-text-secondary hover:text-primary-600 transition-colors">
          Usuarios
        </Link>
      )}
      {canManageResources && (
        <Link href={resourcesHref} className="text-sm font-medium text-text-secondary hover:text-primary-600 transition-colors">
          Recursos
        </Link>
      )}
      {!isAdmin && canManageResources && (
        <Link href="/admin/configuracion" className="text-sm font-medium text-text-secondary hover:text-primary-600 transition-colors">
          Configuración
        </Link>
      )}
      {isAdmin && (
        <Link href="/admin/espacios" className="text-sm font-medium text-text-secondary hover:text-primary-600 transition-colors">
          Espacios
        </Link>
      )}
      {isAdmin && (
        <Link href="/admin/control-cambios" className="text-sm font-medium text-text-secondary hover:text-primary-600 transition-colors">
          Cambios
        </Link>
      )}
      <Link
        href={reservationsHref}
        className="text-sm font-medium text-text-secondary hover:text-primary-600 transition-colors"
      >
        Reservas
      </Link>
      <NotificationBell />
      <span className="text-sm font-medium text-text-muted">{user?.username}</span>
      <button className="btn btn-secondary btn-sm" onClick={handleLogout} type="button">
        Cerrar sesión
      </button>
    </>
  );

  return (
    <nav className="sticky top-0 z-50 bg-surface-card border-b border-border">
      <div className="mx-auto hidden h-16 max-w-7xl items-center justify-between px-4 sm:flex sm:px-6 lg:px-8">
        <Link href={isAuthenticated ? homeHref : '/'} className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary-600 text-xs font-bold text-white">
            IC
          </div>
          <span className="text-lg font-bold text-text-primary">Reservas IC</span>
        </Link>

        <div className="flex items-center gap-4">
          {isAuthenticated ? desktopUserLinks : desktopPublicLinks}
        </div>
      </div>

      <div className="mx-auto grid h-16 max-w-7xl grid-cols-[2.5rem_1fr_2.5rem] items-center px-4 sm:hidden">
        <button
          className="flex h-10 w-10 items-center justify-center rounded-md text-text-secondary hover:bg-surface-hover"
          onClick={() => setMenuOpen((open) => !open)}
          type="button"
          aria-label={menuOpen ? 'Cerrar menú' : 'Abrir menú'}
          aria-expanded={menuOpen}
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            {menuOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>

        <Link
          href={isAuthenticated ? homeHref : '/'}
          className="flex min-w-0 items-center justify-self-center gap-2"
          onClick={closeMenu}
        >
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary-600 text-xs font-bold text-white">
            IC
          </div>
          <span className="truncate text-lg font-bold text-text-primary">Reservas IC</span>
        </Link>

        <div className="justify-self-end">
          {isAuthenticated && <NotificationBell />}
        </div>
      </div>

      {menuOpen && (
        <div className="flex flex-col gap-2 border-t border-border bg-surface-card px-4 pb-4 pt-2 sm:hidden">
          {isAuthenticated ? (
            <>
              <Link
                href={homeHref}
                className="rounded-md px-3 py-2 text-sm font-medium text-text-secondary transition-colors hover:bg-surface-hover hover:text-primary-600"
                onClick={closeMenu}
              >
                Inicio
              </Link>
              <Link
                href={resourcesHref}
                className="rounded-md px-3 py-2 text-sm font-medium text-text-secondary transition-colors hover:bg-surface-hover hover:text-primary-600"
                onClick={closeMenu}
              >
                Recursos
              </Link>
              <Link
                href={reservationsHref}
                className="rounded-md px-3 py-2 text-sm font-medium text-text-secondary transition-colors hover:bg-surface-hover hover:text-primary-600"
                onClick={closeMenu}
              >
                Reservas
              </Link>
              <button
                className="mt-2 border-t border-border px-3 pt-4 text-left text-sm font-medium text-text-secondary transition-colors hover:text-primary-600"
                type="button"
                onClick={() => {
                  closeMenu();
                  handleLogout();
                }}
              >
                Cerrar sesión
              </button>
            </>
          ) : (
            <>
              <Link
                href="/espacios"
                className="rounded-md px-3 py-2 text-sm font-medium text-text-secondary transition-colors hover:bg-surface-hover hover:text-primary-600"
                onClick={closeMenu}
              >
                Recursos
              </Link>
              <Link
                href="/login"
                className="rounded-md px-3 py-2 text-sm font-medium text-text-secondary transition-colors hover:bg-surface-hover hover:text-primary-600"
                onClick={closeMenu}
              >
                Iniciar sesión
              </Link>
            </>
          )}
        </div>
      )}
    </nav>
  );
}
