import type { ReactNode } from "react";

/**
 * Tarjeta de un paso del formulario: un título que dice para qué sirve y los campos que le pertenecen.
 * Aparece con una entrada breve porque casi siempre lo hace como respuesta a una elección de la persona
 * (por ejemplo, al elegir el tipo de reserva). `destacada` marca la primera con el acento lima.
 */
export function Seccion({
  titulo,
  descripcion,
  destacada = false,
  children,
}: {
  titulo: string;
  descripcion?: string;
  destacada?: boolean;
  children: ReactNode;
}) {
  return (
    <div className="relative animate-aparecer rounded-card border border-border bg-surface p-5 shadow-card md:p-6">
      {destacada && <span aria-hidden="true" className="absolute left-0 top-6 h-9 w-1 rounded-r bg-sky" />}
      <div className="mb-4 flex flex-col gap-0.5">
        <h2 className="text-lg font-bold text-text">{titulo}</h2>
        {descripcion && <p className="text-sm text-muted">{descripcion}</p>}
      </div>
      <div className="flex flex-col gap-4">{children}</div>
    </div>
  );
}

/** Barra de acciones del formulario: se queda a la vista aunque el formulario sea largo. */
export function BarraAcciones({ children }: { children: ReactNode }) {
  return (
    <div className="sticky bottom-4 z-10 flex flex-wrap items-center gap-3 rounded-card border border-border bg-[color-mix(in_srgb,var(--color-surface)_92%,transparent)] p-3 shadow-card backdrop-blur">
      {children}
    </div>
  );
}
