import { redirect } from "next/navigation";
import { EspacioDetalleClient } from "@/src/components/espacios/EspacioDetalleClient";
import { obtenerSesionActual } from "@/src/lib/auth";

// WF-ESP-02 + WF-ESP-03 — specs/modules/espacios/wireframes.md
export default async function PaginaDetalleEspacio() {
  const sesion = await obtenerSesionActual();
  if (!sesion) redirect("/login?motivo=sesion_vencida");
  return <EspacioDetalleClient puedeGestionar={sesion.rol !== "USUARIO"} />;
}
