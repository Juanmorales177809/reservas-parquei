import { redirect } from "next/navigation";
import { InicioClient } from "@/src/components/inicio/InicioClient";
import { obtenerSesionActual } from "@/src/lib/auth";

// SCR-REP-04 — specs/modules/reports/screens.md
export default async function PaginaInicio() {
  const sesion = await obtenerSesionActual();
  if (!sesion) redirect("/login?motivo=sesion_vencida");
  return <InicioClient sesion={sesion} />;
}
