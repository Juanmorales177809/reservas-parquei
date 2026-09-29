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

const ANILLO_FOCO =
  "focus-visible:outline-none focus-visible:ring-4 " +
  "focus-visible:ring-[color-mix(in_srgb,var(--color-sky)_55%,transparent)]";

export function Field({ id, label, error, hint, ...rest }: FieldProps) {
  const hintId = hint ? `${id}-hint` : undefined;
  const errorId = error ? `${id}-error` : undefined;

  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={id} className="text-sm font-bold text-text">
        {label}
      </label>
      <input
        id={id}
        {...rest}
        aria-invalid={error ? true : undefined}
        aria-describedby={[hintId, errorId].filter(Boolean).join(" ") || undefined}
        className={`h-11 rounded-control border bg-surface px-4 text-[14px] text-text ${ANILLO_FOCO} ${
          error ? "border-error-2" : "border-border"
        }`}
      />
      {hint && !error && (
        <p id={hintId} className="text-sm text-muted">
          {hint}
        </p>
      )}
      {error && (
        <p id={errorId} className="text-sm text-error-2">
          {error}
        </p>
      )}
    </div>
  );
}
