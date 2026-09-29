import { redirect } from "next/navigation";
import { RecursoDetalleClient } from "@/src/components/recursos/RecursoDetalleClient";
import { obtenerSesionActual } from "@/src/lib/auth";

// WF-REC-02 — specs/modules/resources/wireframes.md
export default async function PaginaDetalleRecurso() {
  const sesion = await obtenerSesionActual();
  if (!sesion) redirect("/login?motivo=sesion_vencida");
  return <RecursoDetalleClient puedeGestionar={sesion.rol !== "USUARIO"} />;
}
