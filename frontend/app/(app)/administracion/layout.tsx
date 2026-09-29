import { redirect } from "next/navigation";
import type { ReactNode } from "react";
import { obtenerSesionActual } from "@/src/lib/auth";

/**
 * specs/docs/tasks/frontend.md, FE-07: una pantalla de administración sin
 * el permiso `cuentas.administrar` no muestra ni parpadea contenido
 * protegido antes de redirigir. `sesiones/actual` no expone permisos
 * granulares (ver FE-06/layout.md) — `rol === "ADMINISTRADOR"` es la
 * aproximación disponible; el servidor sigue siendo quien autoriza cada
 * operación real.
 */
export default async function AdministracionLayout({
  children,
}: {
  children: ReactNode;
}) {
  const sesion = await obtenerSesionActual();

  if (!sesion) {
    redirect("/login");
  }
  if (sesion.rol !== "ADMINISTRADOR") {
    redirect("/reservas");
  }

  return <>{children}</>;
}
