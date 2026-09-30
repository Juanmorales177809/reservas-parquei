"use client";

import type { InputHTMLAttributes } from "react";

/**
 * Campo de formulario mínimo (label + input + error en línea), construido
 * sobre los tokens de FE-02. `components.md` todavía no especifica un
 * componente de campo — esto es andamiaje pragmático de `FE-07`, no una
 * entrada nueva en el catálogo de componentes cerrados.
 */
export interface FieldProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, "id" | "className"> {
  id: string;
  label: string;
  error?: string;
  hint?: string;
}

// FE-32: el campo responde al puntero y al teclado — el borde se enciende en verde al pasar y al enfocar,
// y la etiqueta toma el color de marca mientras se escribe.
export const CLASES_CONTROL =
  "h-12 w-full rounded-control border bg-surface px-4 text-[15px] text-text " +
  "placeholder:text-muted transition-[border-color,box-shadow,background-color] duration-150 " +
  "hover:border-primary-1 focus:border-primary-1 " +
  "focus-visible:outline-none focus-visible:ring-4 " +
  "focus-visible:ring-[color-mix(in_srgb,var(--color-sky)_55%,transparent)] " +
  "disabled:cursor-not-allowed disabled:bg-disabled-bg disabled:text-disabled-text disabled:hover:border-border";

export const CLASES_ETIQUETA = "text-sm font-medium text-text transition-colors group-focus-within:text-primary-2";

export function MensajeError({ id, children }: { id?: string; children: React.ReactNode }) {
  return (
    <p id={id} className="flex items-start gap-1.5 text-sm text-error-2">
      <svg aria-hidden="true" viewBox="0 0 20 20" className="mt-0.5 h-4 w-4 flex-none" fill="currentColor">
        <path d="M10 2a8 8 0 100 16 8 8 0 000-16zm-.75 4.25a.75.75 0 011.5 0v4a.75.75 0 01-1.5 0v-4zM10 14.5a1 1 0 110-2 1 1 0 010 2z" />
      </svg>
      <span>{children}</span>
    </p>
  );
}

export function Field({ id, label, error, hint, ...rest }: FieldProps) {
  const hintId = hint ? `${id}-hint` : undefined;
  const errorId = error ? `${id}-error` : undefined;

  return (
    <div className="group flex flex-col gap-1.5">
      <label htmlFor={id} className={CLASES_ETIQUETA}>
        {label}
      </label>
      <input
        id={id}
        {...rest}
        aria-invalid={error ? true : undefined}
        aria-describedby={[hintId, errorId].filter(Boolean).join(" ") || undefined}
        className={`${CLASES_CONTROL} ${error ? "border-error-2 bg-[color-mix(in_srgb,var(--color-error-1)_6%,var(--color-surface))]" : "border-border"}`}
      />
      {hint && !error && (
        <p id={hintId} className="text-sm text-muted">
          {hint}
        </p>
      )}
      {error && <MensajeError id={errorId}>{error}</MensajeError>}
    </div>
  );
}
