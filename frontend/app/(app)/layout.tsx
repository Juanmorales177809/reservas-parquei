import { redirect } from "next/navigation";
import type { ReactNode } from "react";
import { AppShell } from "@/src/components/shell/AppShell";
import { obtenerSesionActual } from "@/src/lib/auth";

export default async function AppLayout({
  children,
}: {
  children: ReactNode;
}) {
  const sesion = await obtenerSesionActual();

  if (!sesion) {
    // WF-AUTH-01: "Sesión vencida/revocada — Antes de las entradas:
    // «Debes iniciar sesión nuevamente.»". `/login` no distingue por sí
    // sola una primera visita de una sesión que dejó de ser válida.
    redirect("/login?motivo=sesion_vencida");
  }

  return <AppShell sesion={sesion}>{children}</AppShell>;
}
