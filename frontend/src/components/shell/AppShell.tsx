"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { Button } from "@/src/components/ui/Button";
import { ETIQUETA_ROL, type ContextoSesion } from "@/src/lib/auth-types";
import { apiRequest, renovarSesion } from "@/src/lib/http";
import { CentroDeAlertas } from "./CentroDeAlertas";
import { destinosVisiblesPara, type DestinoNav } from "./nav-items";

export interface AppShellProps {
  sesion: ContextoSesion;
  children: ReactNode;
}

const ANILLO_FOCO =
  "focus-visible:outline-none focus-visible:ring-4 " +
  "focus-visible:ring-[color-mix(in_srgb,var(--color-sky)_55%,transparent)]";

// Iconos de trazo, uno por destino del menú (FE-32). Decorativos: el texto del enlace es el nombre accesible.
const ICONOS: Record<string, ReactNode> = {
  "/inicio": (
    <>
      <path d="M3 11l9-8 9 8" />
      <path d="M5 10v10h5v-6h4v6h5V10" />
    </>
  ),
  "/reservas": (
    <>
      <rect x="3" y="4" width="18" height="18" rx="2" />
      <path d="M16 2v4M8 2v4M3 10h18" />
    </>
  ),
  "/recursos": (
    <>
      <path d="M21 8l-9-5-9 5 9 5 9-5z" />
      <path d="M3 8v8l9 5 9-5V8M12 13v8" />
    </>
  ),
  "/espacios": (
    <>
      <path d="M3 21h18M5 21V5a2 2 0 012-2h10a2 2 0 012 2v16" />
      <path d="M9 7h2M13 7h2M9 11h2M13 11h2M10 21v-4h4v4" />
    </>
  ),
  "/investigacion": (
    <>
      <path d="M9 3h6M10 3v6L4.5 19a1.5 1.5 0 001.3 2h12.4a1.5 1.5 0 001.3-2L14 9V3" />
      <path d="M7.5 15h9" />
    </>
  ),
  "/usuarios": (
    <>
      <circle cx="9" cy="8" r="3.5" />
      <path d="M2.5 20a6.5 6.5 0 0113 0M16 4.5a3.5 3.5 0 010 7M18 14.5a6.5 6.5 0 013.5 5.5" />
    </>
  ),
  "/administracion": (
    <>
      <path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0" />
      <circle cx="16" cy="6" r="2" />
      <circle cx="10" cy="12" r="2" />
      <circle cx="18" cy="18" r="2" />
    </>
  ),
  "/notificaciones": (
    <>
      <path d="M6 8a6 6 0 0112 0c0 7 3 8 3 8H3s3-1 3-8" />
      <path d="M10 21a2 2 0 004 0" />
    </>
  ),
  "/reportes": <path d="M4 20V10M10 20V4M16 20v-8M22 20H2" />,
};

function Icono({ href }: { href: string }) {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      className="h-[18px] w-[18px] flex-none"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {ICONOS[href]}
    </svg>
  );
}

function Marca() {
  return (
    <div className="flex items-center gap-3 px-5 py-6">
      <span
        aria-hidden="true"
        className="flex h-9 w-9 items-center justify-center rounded-control bg-primary-1 font-display text-lg font-bold text-white"
      >
        R
      </span>
      <div className="flex flex-col leading-tight">
        <span className="font-display text-[15px] font-bold text-white">Reservas Parquei</span>
        <span className="text-xs text-ink-text">Parque i · ITM</span>
      </div>
    </div>
  );
}

export function AppShell({ sesion, children }: AppShellProps) {
  const [menuAbierto, setMenuAbierto] = useState(false);
  const [cerrandoSesion, setCerrandoSesion] = useState(false);
  const pathname = usePathname();
  const destinos = destinosVisiblesPara(sesion.rol);

  // FE-27: el acceso dura poco y un Server Component no puede renovarlo (no recibe `rp_refresh`).
  // Mientras la persona esté usando la aplicación se renueva antes de que venza; si está inactiva no,
  // para respetar el tiempo máximo de inactividad (SEC-SES-09).
  const huboActividad = useRef(true);
  useEffect(() => {
    const marcar = () => {
      huboActividad.current = true;
    };
    const eventos = ["pointerdown", "keydown", "focus"] as const;
    eventos.forEach((e) => window.addEventListener(e, marcar));
    const cada5Minutos = window.setInterval(() => {
      if (!huboActividad.current) return;
      huboActividad.current = false;
      void renovarSesion().then((ok) => {
        if (!ok) window.location.href = "/login?motivo=sesion_vencida";
      });
    }, 5 * 60 * 1000);
    return () => {
      eventos.forEach((e) => window.removeEventListener(e, marcar));
      window.clearInterval(cada5Minutos);
    };
  }, []);

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

  const inicial = sesion.correo.charAt(0).toUpperCase();

  return (
    <div className="flex min-h-screen bg-bg text-text">
      <nav className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col bg-ink lg:flex">
        <Marca />
        <div className="flex-1 overflow-y-auto">
          <NavList destinos={destinos} pathname={pathname} />
        </div>
      </nav>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-16 items-center justify-between border-b border-border bg-surface px-5 lg:px-10">
          <button
            type="button"
            className={`rounded-control px-2 py-1 font-display text-sm font-bold text-primary-2 lg:hidden ${ANILLO_FOCO}`}
            onClick={() => setMenuAbierto(true)}
          >
            Menú
          </button>
          <div className="ml-auto flex items-center gap-3">
          <CentroDeAlertas />
          <div className="hidden items-center gap-4 lg:flex">
            <span
              aria-hidden="true"
              className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-tint font-display text-sm font-bold text-primary-2"
            >
              {inicial}
            </span>
            <span className="text-sm text-muted">
              {sesion.correo} · {ETIQUETA_ROL[sesion.rol]}
            </span>
            <CuentaEnlaces rol={sesion.rol} />
            <Button variant="ghost" size="sm" onClick={cerrarSesion} loading={cerrandoSesion}>
              Cerrar sesión
            </Button>
          </div>
          </div>
        </header>

        {menuAbierto && (
          <div className="fixed inset-0 z-40 lg:hidden">
            <button
              type="button"
              aria-label="Cerrar menú"
              className="absolute inset-0 bg-black/50"
              onClick={() => setMenuAbierto(false)}
            />
            <nav className="relative z-50 flex h-full w-64 flex-col bg-ink">
              <Marca />
              <div className="flex-1 overflow-y-auto">
                <NavList destinos={destinos} pathname={pathname} onNavigate={() => setMenuAbierto(false)} />
              </div>
              <div className="border-t border-white/10 p-4">
                <p className="mb-2 text-sm text-ink-text">
                  {sesion.correo} · {ETIQUETA_ROL[sesion.rol]}
                </p>
                <div className="mb-2 flex flex-col gap-1" onClick={() => setMenuAbierto(false)}>
                  <CuentaEnlaces rol={sesion.rol} enOscuro />
                </div>
                <Button variant="secondary" size="sm" fullWidth onClick={cerrarSesion} loading={cerrandoSesion}>
                  Cerrar sesión
                </Button>
              </div>
            </nav>
          </div>
        )}

        <main className="w-full min-w-0 px-5 pb-[90px] pt-10 lg:px-10">
          <div className="mx-auto max-w-[1080px]">{children}</div>
        </main>
      </div>
    </div>
  );
}

/** Enlaces de la cuenta que no son un destino del menú: mi perfil (solo Usuario) y cambiar contraseña. */
function CuentaEnlaces({ rol, enOscuro = false }: { rol: ContextoSesion["rol"]; enOscuro?: boolean }) {
  const clase = `rounded-control text-sm font-medium underline-offset-4 hover:underline ${ANILLO_FOCO} ${
    enOscuro ? "text-white" : "text-primary-2"
  }`;
  return (
    <>
      {rol === "USUARIO" && (
        <Link href="/usuarios/perfil" className={clase}>
          Mi perfil
        </Link>
      )}
      <Link href="/cambiar-contrasena" className={clase}>
        Cambiar contraseña
      </Link>
    </>
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
    <ul className="flex flex-col gap-0.5 px-3 pb-4">
      {destinos.map((destino) => {
        const activo = pathname.startsWith(destino.href);
        return (
          <li key={destino.href}>
            <Link
              href={destino.href}
              onClick={onNavigate}
              aria-current={activo ? "page" : undefined}
              className={`relative flex items-center gap-3 rounded-control px-3 py-2.5 font-display text-[14.5px] font-medium transition-colors ${ANILLO_FOCO} ${
                activo
                  ? "bg-ink-hover text-white before:absolute before:-left-3 before:top-2 before:h-6 before:w-1 before:rounded-r before:bg-sky"
                  : "text-ink-text hover:bg-ink-hover hover:text-white"
              }`}
            >
              <Icono href={destino.href} />
              {destino.etiqueta}
            </Link>
          </li>
        );
      })}
    </ul>
  );
}
