"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { fechaHora } from "@/src/lib/formato";
import { bandeja, marcarLectura } from "@/src/lib/notificaciones-api";
import type { NotificacionItem } from "@/src/lib/notificaciones-types";

const CADA_CUANTO_MS = 60_000;
const DURACION_AVISO_MS = 9_000;
const MAXIMO_AVISOS = 3;
const MAXIMO_EN_PANEL = 8;
const CLAVE_VISTAS = "rp_alertas_vistas";

const ANILLO_FOCO =
  "focus-visible:outline-none focus-visible:ring-4 " +
  "focus-visible:ring-[color-mix(in_srgb,var(--color-sky)_55%,transparent)]";

// El navegador puede negar el almacenamiento (ventana privada, datos bloqueados): sin él solo se repiten avisos.
function leerVistas(): number[] {
  try {
    const crudo = window.sessionStorage.getItem(CLAVE_VISTAS);
    return crudo ? (JSON.parse(crudo) as number[]) : [];
  } catch {
    return [];
  }
}

function guardarVistas(ids: Iterable<number>) {
  try {
    window.sessionStorage.setItem(CLAVE_VISTAS, JSON.stringify(Array.from(ids).slice(-200)));
  } catch {
    /* sin almacenamiento: se pueden repetir avisos, nada más */
  }
}

function destino(n: NotificacionItem): string {
  return n.reserva_id ? `/reservas/${n.reserva_id}` : "/notificaciones";
}

function Campana({ className }: { className?: string }) {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" className={className} fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M6 8a6 6 0 0112 0c0 7 3 8 3 8H3s3-1 3-8" />
      <path d="M10 21a2 2 0 004 0" />
    </svg>
  );
}

function AvisoEmergente({ n, onAbrir, onCerrar }: { n: NotificacionItem; onAbrir: () => void; onCerrar: () => void }) {
  useEffect(() => {
    const t = window.setTimeout(onCerrar, DURACION_AVISO_MS);
    return () => window.clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  return (
    <div className="pointer-events-auto flex w-full animate-aparecer items-start gap-3 rounded-card border border-border border-l-4 border-l-primary-1 bg-surface p-4 shadow-[0_14px_36px_-14px_rgba(7,19,12,0.45)]">
      <button type="button" onClick={onAbrir} className={`flex min-w-0 flex-1 flex-col gap-0.5 rounded-control text-left ${ANILLO_FOCO}`}>
        <span className="font-display text-[15px] font-bold text-text">{n.titulo}</span>
        <span className="line-clamp-2 text-sm text-muted">{n.cuerpo}</span>
      </button>
      <button
        type="button"
        onClick={onCerrar}
        className={`flex h-7 w-7 flex-none items-center justify-center rounded-control text-muted hover:bg-primary-tint hover:text-primary-2 ${ANILLO_FOCO}`}
      >
        <span className="sr-only">Cerrar aviso</span>
        <svg aria-hidden="true" viewBox="0 0 20 20" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          <path d="M5 5l10 10M15 5L5 15" />
        </svg>
      </button>
    </div>
  );
}

/**
 * La campanita de la cabecera: cuenta lo que falta por leer, abre un panel con lo último y, al entrar y cuando
 * llega algo nuevo, muestra avisos emergentes abajo a la derecha. Reemplaza al destino «Notificaciones» del menú;
 * el historial completo sigue en `/notificaciones`.
 */
export function CentroDeAlertas() {
  const router = useRouter();
  const [items, setItems] = useState<NotificacionItem[]>([]);
  const [abierto, setAbierto] = useState(false);
  const [avisos, setAvisos] = useState<NotificacionItem[]>([]);
  const vistas = useRef<Set<number>>(new Set());
  const contenedor = useRef<HTMLDivElement>(null);

  const cargar = useCallback(async () => {
    try {
      const r = await bandeja();
      const datos = r?.datos ?? [];
      setItems(datos);
      // Cada notificación sin leer avisa una sola vez por sesión del navegador; se muestran las más nuevas.
      const nuevas = datos.filter((n) => n.leida_at === null && !vistas.current.has(n.id));
      if (nuevas.length > 0) {
        nuevas.forEach((n) => vistas.current.add(n.id));
        guardarVistas(vistas.current);
        setAvisos((previos) => [...nuevas.slice(0, MAXIMO_AVISOS), ...previos].slice(0, MAXIMO_AVISOS));
      }
    } catch {
      // Sin red o sesión vencida: la campanita se queda como estaba; la sesión la maneja el resto de la aplicación.
    }
  }, []);

  useEffect(() => {
    vistas.current = new Set(leerVistas());
    void cargar();
    const t = window.setInterval(() => {
      if (!document.hidden) void cargar();
    }, CADA_CUANTO_MS);
    return () => window.clearInterval(t);
  }, [cargar]);

  useEffect(() => {
    if (!abierto) return;
    function fuera(e: MouseEvent) {
      if (contenedor.current && !contenedor.current.contains(e.target as Node)) setAbierto(false);
    }
    function tecla(e: KeyboardEvent) {
      if (e.key === "Escape") setAbierto(false);
    }
    document.addEventListener("mousedown", fuera);
    document.addEventListener("keydown", tecla);
    return () => {
      document.removeEventListener("mousedown", fuera);
      document.removeEventListener("keydown", tecla);
    };
  }, [abierto]);

  const sinLeer = items.filter((n) => n.leida_at === null);

  async function leer(n: NotificacionItem) {
    if (n.leida_at !== null) return;
    setItems((previos) => previos.map((x) => (x.id === n.id ? { ...x, leida_at: new Date().toISOString() } : x)));
    try {
      await marcarLectura(n.id);
    } catch {
      void cargar(); // no se pudo marcar: el panel vuelve a lo que dice el servidor
    }
  }

  async function abrir(n: NotificacionItem) {
    setAbierto(false);
    setAvisos((previos) => previos.filter((a) => a.id !== n.id));
    router.push(destino(n));
    await leer(n);
  }

  async function marcarTodas() {
    const pendientes = sinLeer;
    setItems((previos) => previos.map((x) => (x.leida_at === null ? { ...x, leida_at: new Date().toISOString() } : x)));
    setAvisos([]);
    try {
      await Promise.all(pendientes.map((n) => marcarLectura(n.id)));
    } catch {
      void cargar();
    }
  }

  return (
    <>
      <div ref={contenedor} className="relative">
        <button
          type="button"
          aria-haspopup="true"
          aria-expanded={abierto}
          onClick={() => setAbierto((v) => !v)}
          className={`relative flex h-10 w-10 items-center justify-center rounded-full text-muted transition-colors hover:bg-primary-tint hover:text-primary-2 ${ANILLO_FOCO}`}
        >
          <Campana className="h-[22px] w-[22px]" />
          <span className="sr-only">
            Notificaciones{sinLeer.length > 0 ? `, ${sinLeer.length} sin leer` : ""}
          </span>
          {sinLeer.length > 0 && (
            <span
              aria-hidden="true"
              className="absolute -right-0.5 -top-0.5 flex h-[18px] min-w-[18px] items-center justify-center rounded-full bg-error-2 px-1 text-[11px] font-bold leading-none text-white"
            >
              {sinLeer.length > 9 ? "9+" : sinLeer.length}
            </span>
          )}
        </button>

        {abierto && (
          <div
            role="region"
            aria-label="Últimas notificaciones"
            className="absolute right-0 top-full z-40 mt-2 flex w-[min(380px,calc(100vw-2rem))] animate-aparecer flex-col overflow-hidden rounded-card border border-border bg-surface shadow-[0_18px_44px_-16px_rgba(7,19,12,0.5)]"
          >
            <div className="flex items-center justify-between gap-3 border-b border-border px-4 py-3">
              <h2 className="font-display text-base font-bold text-text">Notificaciones</h2>
              {sinLeer.length > 0 && (
                <button type="button" onClick={() => void marcarTodas()} className={`rounded-control text-sm font-medium text-primary-2 underline-offset-4 hover:underline ${ANILLO_FOCO}`}>
                  Marcar todas como leídas
                </button>
              )}
            </div>
            {items.length === 0 ? (
              <p className="px-4 py-8 text-center text-sm text-muted">No tienes notificaciones.</p>
            ) : (
              <ul className="max-h-[22rem] overflow-y-auto">
                {items.slice(0, MAXIMO_EN_PANEL).map((n) => (
                  <li key={n.id} className="border-b border-border last:border-b-0">
                    <button
                      type="button"
                      onClick={() => void abrir(n)}
                      className={`flex w-full items-start gap-3 px-4 py-3 text-left transition-colors hover:bg-primary-tint ${ANILLO_FOCO}`}
                    >
                      <span
                        aria-hidden="true"
                        className={`mt-1.5 h-2.5 w-2.5 flex-none rounded-full ${n.leida_at === null ? "bg-primary-1" : "bg-transparent"}`}
                      />
                      <span className="flex min-w-0 flex-1 flex-col gap-0.5">
                        <span className={`text-sm text-text ${n.leida_at === null ? "font-bold" : "font-medium"}`}>{n.titulo}</span>
                        <span className="text-sm text-muted">{n.cuerpo}</span>
                        <span className="text-xs text-muted">{fechaHora(n.created_at)}</span>
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
            <div className="border-t border-border px-4 py-3">
              <Link href="/notificaciones" onClick={() => setAbierto(false)} className={`rounded-control text-sm font-bold text-primary-2 underline-offset-4 hover:underline ${ANILLO_FOCO}`}>
                Ver todas las notificaciones
              </Link>
            </div>
          </div>
        )}
      </div>

      {/* Avisos al entrar y cuando llega algo nuevo: abajo a la derecha, sin tapar el contenido principal. */}
      <div aria-live="polite" className="pointer-events-none fixed bottom-5 right-5 z-50 flex w-[min(380px,calc(100vw-2.5rem))] flex-col gap-3">
        {avisos.map((n) => (
          <AvisoEmergente
            key={n.id}
            n={n}
            onAbrir={() => void abrir(n)}
            onCerrar={() => setAvisos((previos) => previos.filter((a) => a.id !== n.id))}
          />
        ))}
      </div>
    </>
  );
}
