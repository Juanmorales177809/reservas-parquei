import { redirect } from "next/navigation";
import { EspaciosClient } from "@/src/components/espacios/EspaciosClient";
import { obtenerSesionActual } from "@/src/lib/auth";

// WF-ESP-04 + WF-ESP-01 — specs/modules/espacios/wireframes.md
export default async function PaginaEspacios() {
  const sesion = await obtenerSesionActual();
  if (!sesion) redirect("/login?motivo=sesion_vencida");
  return <EspaciosClient puedeGestionar={sesion.rol !== "USUARIO"} />;
}
