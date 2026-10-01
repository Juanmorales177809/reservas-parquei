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
  numero,
  plana = false,
  children,
}: {
  titulo: string;
  descripcion?: string;
  destacada?: boolean;
  /** Número del paso, cuando los pasos forman una secuencia (un formulario por pasos). */
  numero?: number;
  /** Dentro de un modal: sin tarjeta, separada de la anterior por una línea. */
  plana?: boolean;
  children: ReactNode;
}) {
  const encabezado = (
    <div className="mb-4 flex items-start gap-3">
      {numero !== undefined && (
        <span
          aria-hidden="true"
          className="mt-0.5 flex h-7 w-7 flex-none items-center justify-center rounded-full bg-primary-tint font-display text-sm font-bold text-primary-2"
        >
          {numero}
        </span>
      )}
      <div className="flex flex-col gap-0.5">
        <h2 className="text-lg font-bold text-text">{titulo}</h2>
        {descripcion && <p className="text-sm text-muted">{descripcion}</p>}
      </div>
    </div>
  );
  if (plana) {
    return (
      <div className="animate-aparecer border-t border-border pt-5 first:border-t-0 first:pt-0">
        {encabezado}
        <div className="flex flex-col gap-4">{children}</div>
      </div>
    );
  }
  return (
    <div className="relative animate-aparecer rounded-card border border-border bg-surface p-5 shadow-card md:p-6">
      {destacada && <span aria-hidden="true" className="absolute left-0 top-6 h-9 w-1 rounded-r bg-sky" />}
      {encabezado}
      <div className="flex flex-col gap-4">{children}</div>
    </div>
  );
}

/** Barra de acciones del formulario: se queda a la vista aunque el formulario sea largo. */
export function BarraAcciones({ children, plana = false }: { children: ReactNode; plana?: boolean }) {
  if (plana) {
    // Dentro del modal: pegada al pie del área que se desplaza, con el ancho completo del modal.
    return (
      <div className="sticky -bottom-5 z-10 -mx-6 -mb-5 flex flex-wrap items-center justify-end gap-3 border-t border-border bg-surface px-6 py-4">
        {children}
      </div>
    );
  }
  return (
    <div className="sticky bottom-4 z-10 flex flex-wrap items-center gap-3 rounded-card border border-border bg-[color-mix(in_srgb,var(--color-surface)_92%,transparent)] p-3 shadow-card backdrop-blur">
      {children}
    </div>
  );
}
