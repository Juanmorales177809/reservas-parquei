import type { ReservaResumen } from "./reservas-types";

export const NOMBRE_TIPO_RESERVA: Record<string, string> = {
  ESPACIO: "Espacio",
  RECURSO_INTERNO: "Recurso interno",
  RECURSO_CAMPUS: "Recurso en campus",
  RECURSO_EXTERNO: "Recurso fuera del campus",
  LISTA_ESPERA: "Lista de espera",
};

export const NOMBRE_ESTADO_RESERVA: Record<string, string> = {
  SOLICITADA: "Solicitada",
  APROBADA: "Aprobada",
  RECHAZADA: "Rechazada",
  EN_EJECUCION: "En ejecución",
  FINALIZADA: "Finalizada",
  CANCELADA: "Cancelada",
};

export const NOMBRE_ROL_RECURSO: Record<string, string> = { PRINCIPAL: "principal", ADICIONAL: "adicional" };

/** «2026-10-14» → «14 oct 2026», sin pasar por la zona horaria (una fecha civil no tiene hora). */
export function fechaCorta(iso: string | null | undefined): string {
  if (!iso) return "";
  const [a, m, d] = iso.slice(0, 10).split("-").map(Number);
  if (!a || !m || !d) return iso;
  return new Date(a, m - 1, d).toLocaleDateString("es-CO", { day: "numeric", month: "short", year: "numeric" });
}

const hora = (t: string | null | undefined) => (t ? t.slice(0, 5) : "");

/** Cuándo es una reserva, según la forma de su periodo (contrato reservations §3.1). */
export function periodoLegible(periodo: ReservaResumen["periodo"]): string {
  if (!periodo) return "Sin fecha";
  if ("fecha" in periodo && periodo.fecha) {
    return `${fechaCorta(periodo.fecha)}, ${hora(periodo.hora_inicio)}–${hora(periodo.hora_fin)}`;
  }
  if ("fecha_salida" in periodo) {
    return `Sale ${fechaCorta(periodo.fecha_salida)} · devuelve ${fechaCorta(periodo.fecha_devolucion_estimada)}`;
  }
  return "Sin fecha";
}
