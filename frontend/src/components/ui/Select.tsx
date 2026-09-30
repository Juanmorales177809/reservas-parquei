"use client";

import type { SelectHTMLAttributes } from "react";
import { CLASES_CONTROL, CLASES_ETIQUETA, MensajeError } from "./Field";

/** Mismo criterio que Field.tsx: andamiaje pragmático de FE-07, no un componente cerrado. */
export interface SelectProps
  extends Omit<SelectHTMLAttributes<HTMLSelectElement>, "id" | "className"> {
  id: string;
  label: string;
  error?: string;
}

export function Select({ id, label, error, children, ...rest }: SelectProps) {
  return (
    <div className="group flex flex-col gap-1.5">
      <label htmlFor={id} className={CLASES_ETIQUETA}>
        {label}
      </label>
      <div className="relative">
        <select
          id={id}
          {...rest}
          className={`${CLASES_CONTROL} cursor-pointer appearance-none pr-11 ${
            error ? "border-error-2" : "border-border"
          }`}
        >
          {children}
        </select>
        <svg
          aria-hidden="true"
          viewBox="0 0 20 20"
          className="pointer-events-none absolute right-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted transition-colors group-focus-within:text-primary-2"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M5 8l5 5 5-5" />
        </svg>
      </div>
      {error && <MensajeError>{error}</MensajeError>}
    </div>
  );
}
