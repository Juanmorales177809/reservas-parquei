import type { InputHTMLAttributes, ReactNode } from "react";

/**
 * Casilla presentada como una ficha que se enciende al elegirla. Conserva la estructura de siempre
 * (`<label>` que envuelve un `<input type="checkbox">`), así que el nombre accesible es el mismo.
 */
export function CasillaTarjeta({
  children,
  ...entrada
}: Omit<InputHTMLAttributes<HTMLInputElement>, "type" | "className"> & { children: ReactNode }) {
  return (
    <label
      className={
        "flex cursor-pointer items-center gap-3 rounded-control border border-border bg-surface px-4 py-3 text-sm text-text " +
        "transition-[border-color,background-color,box-shadow] duration-150 hover:border-primary-1 " +
        "has-[:checked]:border-primary-1 has-[:checked]:bg-primary-tint " +
        "has-[:disabled]:cursor-not-allowed has-[:disabled]:opacity-60 has-[:disabled]:hover:border-border " +
        "has-[:focus-visible]:ring-4 has-[:focus-visible]:ring-[color-mix(in_srgb,var(--color-sky)_55%,transparent)]"
      }
    >
      <input type="checkbox" {...entrada} />
      <span className="flex flex-wrap items-center gap-x-2 gap-y-0.5">{children}</span>
    </label>
  );
}

/** Grupo de fichas con su leyenda. */
export function GrupoCasillas({ leyenda, children }: { leyenda: string; children: ReactNode }) {
  return (
    <fieldset className="flex flex-col gap-2">
      <legend className="mb-1 text-sm font-medium text-text">{leyenda}</legend>
      {children}
    </fieldset>
  );
}
