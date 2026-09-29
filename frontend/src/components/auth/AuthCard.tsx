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
    <div className="w-full max-w-[420px] rounded-[16px] border border-border bg-surface p-[30px]">
      <h1 className="mb-5 font-display text-xl font-bold text-text">{titulo}</h1>
      {children}
    </div>
  );
}
