import { redirect } from "next/navigation";
import type { ReactNode } from "react";
import { obtenerSesionActual } from "@/src/lib/auth";

/**
 * FE-17: todo `/api/investigacion/*` exige `usuarios.administrar` global,
 * lecturas incluidas. Sin permiso granular en sesión, `rol ===
 * "ADMINISTRADOR"` es la aproximación disponible (mismo criterio que
 * `administracion/layout.tsx` de FE-07); el servidor autoriza cada
 * operación real.
 */
export default async function InvestigacionLayout({
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
