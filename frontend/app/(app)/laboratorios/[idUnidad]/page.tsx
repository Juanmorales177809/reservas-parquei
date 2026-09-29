import { redirect } from "next/navigation";
import { LaboratorioClient } from "@/src/components/recursos/LaboratorioClient";
import { obtenerSesionActual } from "@/src/lib/auth";

// WF-REC-03 — specs/modules/resources/wireframes.md
export default async function PaginaLaboratorio({
  params,
}: {
  params: { idUnidad: string };
}) {
  const sesion = await obtenerSesionActual();
  if (!sesion) redirect("/login?motivo=sesion_vencida");
  return <LaboratorioClient idUnidad={Number(params.idUnidad)} puedeGestionar={sesion.rol !== "USUARIO"} />;
}
