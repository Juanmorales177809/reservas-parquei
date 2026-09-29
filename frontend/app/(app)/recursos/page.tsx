import { redirect } from "next/navigation";
import { RecursosClient } from "@/src/components/recursos/RecursosClient";
import { obtenerSesionActual } from "@/src/lib/auth";

// WF-REC-01 — specs/modules/resources/wireframes.md
export default async function PaginaRecursos() {
  const sesion = await obtenerSesionActual();
  if (!sesion) redirect("/login?motivo=sesion_vencida");
  return <RecursosClient puedeGestionar={sesion.rol !== "USUARIO"} />;
}
