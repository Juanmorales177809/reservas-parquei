import type { ReactNode } from "react";

/** Shell centrado de las pantallas públicas de auth — specs/modules/auth/wireframes.md. */
export function AuthCard({
  titulo,
  children,
}: {
  titulo: string;
  children: ReactNode;
}) {
  return (
    <div className="w-full max-w-[420px] rounded-card border border-border bg-surface p-8 shadow-card">
      <h1 className="mb-6 font-display text-2xl font-bold tracking-tight text-text">{titulo}</h1>
      {children}
    </div>
  );
}
