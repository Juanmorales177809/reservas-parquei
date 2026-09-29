import { redirect } from "next/navigation";
import { ReporteClient } from "@/src/components/reportes/ReporteClient";
import { obtenerSesionActual } from "@/src/lib/auth";

// SCR-REP-02 — specs/modules/reports/screens.md
export default async function PaginaSolicitudes() {
  const sesion = await obtenerSesionActual();
  if (!sesion) redirect("/login?motivo=sesion_vencida");
  return <ReporteClient tipo="solicitudes" unidadesAutorizadas={sesion.unidades_autorizadas} />;
}
