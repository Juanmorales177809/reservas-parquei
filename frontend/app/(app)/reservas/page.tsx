import { redirect } from "next/navigation";
import { ListadoReservas } from "@/src/components/reservas/ListadoReservas";
import { obtenerSesionActual } from "@/src/lib/auth";

// WF-RES-04 (listado) — specs/modules/reservations/wireframes.md
export default async function PaginaReservas() {
  const sesion = await obtenerSesionActual();
  if (!sesion) redirect("/login?motivo=sesion_vencida");
  return <ListadoReservas sesion={sesion} />;
}
