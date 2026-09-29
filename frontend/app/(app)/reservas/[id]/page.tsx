import { redirect } from "next/navigation";
import { GestionReservaClient } from "@/src/components/reservas/GestionReservaClient";
import { obtenerSesionActual } from "@/src/lib/auth";

// WF-RES-02 + WF-RES-03 + WF-RES-04 — specs/modules/reservations/wireframes.md
export default async function PaginaDetalleReserva() {
  const sesion = await obtenerSesionActual();
  if (!sesion) redirect("/login?motivo=sesion_vencida");
  return <GestionReservaClient sesion={sesion} />;
}
