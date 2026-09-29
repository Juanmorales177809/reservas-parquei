"use client";

import type { SelectHTMLAttributes } from "react";

/** Mismo criterio que Field.tsx: andamiaje pragmático de FE-07, no un componente cerrado. */
export interface SelectProps
  extends Omit<SelectHTMLAttributes<HTMLSelectElement>, "id" | "className"> {
  id: string;
  label: string;
  error?: string;
}

const ANILLO_FOCO =
  "focus-visible:outline-none focus-visible:ring-4 " +
  "focus-visible:ring-[color-mix(in_srgb,var(--color-sky)_55%,transparent)]";

export function Select({ id, label, error, children, ...rest }: SelectProps) {
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={id} className="text-sm font-bold text-text">
        {label}
      </label>
      <select
        id={id}
        {...rest}
        className={`h-11 rounded-control border bg-surface px-4 text-[14px] text-text ${ANILLO_FOCO} ${
          error ? "border-error-2" : "border-border"
        }`}
      >
        {children}
      </select>
      {error && (
        <p className="text-sm text-error-2">{error}</p>
      )}
    </div>
  );
}
