import { redirect } from "next/navigation";
import type { ReactNode } from "react";
import { obtenerSesionActual } from "@/src/lib/auth";

/**
 * Decisión 2026-10-01: el usuario solo reserva. Esta pantalla es de quien gestiona (técnico y administrador);
 * si el usuario llega por la dirección, vuelve a sus reservas. El servidor sigue autorizando cada operación:
 * el formulario de reserva lee estos catálogos por la API, no por esta pantalla.
 */
export default async function Layout({ children }: { children: ReactNode }) {
  const sesion = await obtenerSesionActual();
  if (!sesion) redirect("/login?motivo=sesion_vencida");
  if (sesion.rol === "USUARIO") redirect("/reservas");
  return <>{children}</>;
}
