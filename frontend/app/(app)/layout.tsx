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
    redirect("/login");
  }

  return <AppShell sesion={sesion}>{children}</AppShell>;
}
