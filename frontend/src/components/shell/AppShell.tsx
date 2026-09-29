"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, type ReactNode } from "react";
import { Button } from "@/src/components/ui/Button";
import { ETIQUETA_ROL, type ContextoSesion } from "@/src/lib/auth-types";
import { apiRequest } from "@/src/lib/http";
import { destinosVisiblesPara, type DestinoNav } from "./nav-items";

export interface AppShellProps {
  sesion: ContextoSesion;
  children: ReactNode;
}

const ANILLO_FOCO =
  "focus-visible:outline-none focus-visible:ring-4 " +
  "focus-visible:ring-[color-mix(in_srgb,var(--color-sky)_55%,transparent)]";

export function AppShell({ sesion, children }: AppShellProps) {
  const [menuAbierto, setMenuAbierto] = useState(false);
  const [cerrandoSesion, setCerrandoSesion] = useState(false);
  const pathname = usePathname();
  const destinos = destinosVisiblesPara(sesion.rol);

  async function cerrarSesion() {
    setCerrandoSesion(true);
    try {
      await apiRequest("/api/auth/sesiones/actual", { method: "DELETE" });
    } finally {
      // Navegación completa, no router.push: fuerza a que cualquier estado
      // de cliente se descarte junto con la sesión que acaba de cerrarse.
      window.location.href = "/login";
    }
  }

  return (
    <div className="min-h-screen bg-bg text-text">
      <header className="flex h-16 items-center justify-between border-b border-border bg-surface px-5">
        <button
          type="button"
          className={`text-sm font-display font-bold text-muted lg:hidden ${ANILLO_FOCO}`}
          onClick={() => setMenuAbierto(true)}
        >
          Menú
        </button>
        <div className="hidden items-center gap-4 lg:flex">
          <span className="text-sm text-muted">
            {sesion.correo} · {ETIQUETA_ROL[sesion.rol]}
          </span>
          <Button
            variant="ghost"
            size="sm"
            onClick={cerrarSesion}
            loading={cerrandoSesion}
          >
            Cerrar sesión
          </Button>
        </div>
      </header>

      <div className="flex">
        <nav className="hidden w-60 shrink-0 border-r border-border bg-surface lg:block">
          <NavList destinos={destinos} pathname={pathname} />
        </nav>

        {menuAbierto && (
          <div className="fixed inset-0 z-40 lg:hidden">
            <button
              type="button"
              aria-label="Cerrar menú"
              className="absolute inset-0 bg-black/40"
              onClick={() => setMenuAbierto(false)}
            />
            <nav className="relative z-50 flex h-full w-60 flex-col bg-surface">
              <div className="flex-1 overflow-y-auto">
                <NavList
                  destinos={destinos}
                  pathname={pathname}
                  onNavigate={() => setMenuAbierto(false)}
                />
              </div>
              <div className="border-t border-border p-4">
                <p className="mb-2 text-sm text-muted">
                  {sesion.correo} · {ETIQUETA_ROL[sesion.rol]}
                </p>
                <Button
                  variant="ghost"
                  size="sm"
                  fullWidth
                  onClick={cerrarSesion}
                  loading={cerrandoSesion}
                >
                  Cerrar sesión
                </Button>
              </div>
            </nav>
          </div>
        )}

        <main className="w-full min-w-0 px-5 pb-[90px] pt-11 lg:px-[30px]">
          <div className="mx-auto max-w-[1180px]">{children}</div>
        </main>
      </div>
    </div>
  );
}

function NavList({
  destinos,
  pathname,
  onNavigate,
}: {
  destinos: DestinoNav[];
  pathname: string;
  onNavigate?: () => void;
}) {
  return (
    <ul className="flex flex-col py-3">
      {destinos.map((destino) => {
        const activo = pathname.startsWith(destino.href);
        return (
          <li key={destino.href}>
            <Link
              href={destino.href}
              onClick={onNavigate}
              className={`block px-5 py-3 text-sm font-bold ${ANILLO_FOCO} ${
                activo
                  ? "bg-primary-tint text-primary-2"
                  : "text-muted hover:bg-primary-tint hover:text-primary-2"
              }`}
            >
              {destino.etiqueta}
            </Link>
          </li>
        );
      })}
    </ul>
  );
}
