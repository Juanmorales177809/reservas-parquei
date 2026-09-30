"use client";

import { useEffect, useId, useRef, type ReactNode } from "react";

const ENFOCABLES =
  'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

/**
 * Diálogo modal: se cierra con Escape, con el fondo o con su botón; devuelve el foco a quien lo abrió y no
 * deja que Tab salga de él. Bloquea el desplazamiento de la página mientras está abierto.
 */
export function Modal({
  titulo,
  subtitulo,
  onClose,
  children,
}: {
  titulo: string;
  subtitulo?: ReactNode;
  onClose: () => void;
  children: ReactNode;
}) {
  const idTitulo = useId();
  const panel = useRef<HTMLDivElement>(null);
  const onCloseRef = useRef(onClose);
  onCloseRef.current = onClose;

  useEffect(() => {
    const previo = document.activeElement as HTMLElement | null;
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    panel.current?.focus();

    function alTeclear(e: KeyboardEvent) {
      if (e.key === "Escape") {
        e.stopPropagation();
        onCloseRef.current();
        return;
      }
      if (e.key !== "Tab" || !panel.current) return;
      const items = Array.from(panel.current.querySelectorAll<HTMLElement>(ENFOCABLES));
      if (items.length === 0) return;
      const primero = items[0];
      const ultimo = items[items.length - 1];
      const activo = document.activeElement;
      if (e.shiftKey && (activo === primero || activo === panel.current)) {
        e.preventDefault();
        ultimo.focus();
      } else if (!e.shiftKey && activo === ultimo) {
        e.preventDefault();
        primero.focus();
      }
    }
    document.addEventListener("keydown", alTeclear);
    return () => {
      document.removeEventListener("keydown", alTeclear);
      document.body.style.overflow = overflow;
      previo?.focus?.();
    };
  }, []);

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center sm:items-center sm:p-6">
      <button
        type="button"
        aria-label="Cerrar ventana"
        tabIndex={-1}
        className="absolute inset-0 cursor-default bg-[rgba(7,19,12,0.55)] backdrop-blur-[2px]"
        onClick={onClose}
      />
      <div
        ref={panel}
        role="dialog"
        aria-modal="true"
        aria-labelledby={idTitulo}
        tabIndex={-1}
        className="relative flex max-h-[92vh] w-full max-w-[640px] animate-aparecer flex-col overflow-hidden rounded-t-card border border-border bg-surface shadow-[0_24px_60px_-20px_rgba(7,19,12,0.5)] focus:outline-none sm:rounded-card"
      >
        <div className="flex items-start justify-between gap-4 border-b border-border px-6 py-4">
          <div className="flex min-w-0 flex-col gap-1">
            <h2 id={idTitulo} className="truncate font-display text-xl font-bold text-text">
              {titulo}
            </h2>
            {subtitulo && <div className="text-sm text-muted">{subtitulo}</div>}
          </div>
          <button
            type="button"
            onClick={onClose}
            className="flex h-9 w-9 flex-none items-center justify-center rounded-control text-muted transition-colors hover:bg-primary-tint hover:text-primary-2 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-[color-mix(in_srgb,var(--color-sky)_55%,transparent)]"
          >
            <span className="sr-only">Cerrar</span>
            <svg aria-hidden="true" viewBox="0 0 20 20" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <path d="M5 5l10 10M15 5L5 15" />
            </svg>
          </button>
        </div>
        <div className="overflow-y-auto px-6 py-5">{children}</div>
      </div>
    </div>
  );
}
