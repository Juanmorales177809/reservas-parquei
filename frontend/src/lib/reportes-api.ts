import { apiRequest, renovarSesion } from "./http";

export type Dimension = "laboratorio" | "espacio" | "recurso" | "proyecto" | "semillero";
export type TipoReporte = "ocupacion" | "solicitudes" | "lista-espera";

export interface FiltrosReporte {
  dimension?: Dimension;
  desde?: string;
  hasta?: string;
  id_unidad?: string;
  espacio_id?: string;
  recurso_id?: string;
  proyecto_id?: string;
  semillero_id?: string;
}

export interface FilaReporte {
  nombre: string;
  id_unidad?: number;
  espacio_id?: number;
  recurso_id?: number;
  proyecto_id?: number;
  semillero_id?: number;
  horas_reservadas?: number;
  horas_disponibles?: number | null;
  horas_uso?: number | null;
  porcentaje_ocupacion?: number | null;
  solicitada?: number;
  aprobada?: number;
  rechazada?: number;
  en_ejecucion?: number;
  finalizada?: number;
  cancelada?: number;
  reservas?: number;
  horas_ejecucion?: number;
}

export interface RespuestaReporte {
  resumen: { dimension?: Dimension; desde: string | null; hasta: string | null; filtros: Record<string, number> };
  datos: FilaReporte[];
  paginacion: { pagina: number; tamano: number; total: number; paginas: number };
}

function parametros(filtros: FiltrosReporte, extra: Record<string, string> = {}): string {
  const params = new URLSearchParams();
  for (const [clave, valor] of Object.entries({ ...filtros, ...extra })) {
    if (valor) params.set(clave, valor);
  }
  return params.toString();
}

export function consultarReporte(tipo: TipoReporte, filtros: FiltrosReporte, pagina = 1) {
  return apiRequest<RespuestaReporte>(
    `/api/reportes/${tipo}?${parametros(filtros, { pagina: String(pagina), tamano: "20" })}`
  );
}

// Contrato §3.4 (API-20): agregado del periodo para la pantalla «Inicio».
export interface ResumenPeriodo {
  desde: string;
  hasta: string;
  desde_previo: string;
  hasta_previo: string;
  filtros: Record<string, number>;
}

export interface ResumenRespuesta {
  resumen: ResumenPeriodo;
  indicadores: {
    reservas: { actual: number; previo: number };
    solicitadas: number;
    horas_reservadas: { actual: number; previo: number };
    porcentaje_ocupacion: { actual: number | null; previo: number | null };
  };
  por_estado: Record<string, number>;
  por_fecha: { fecha: string; reservas: number }[];
  por_laboratorio: {
    id_unidad: number;
    nombre: string;
    reservas: number;
    horas_reservadas: number;
    porcentaje_ocupacion: number | null;
  }[];
  recursos_mas_reservados: { recurso_id: number; nombre: string; reservas: number }[];
  ocupacion_dia_hora: { dia: number; hora: number; cantidad: number }[];
}

export function consultarResumen(filtros: Pick<FiltrosReporte, "desde" | "hasta" | "id_unidad">) {
  return apiRequest<ResumenRespuesta>(`/api/reportes/resumen?${parametros(filtros)}`);
}

/**
 * §4.1. Descarga el archivo con los filtros de la última consulta. Va por `fetch` y no por un enlace para
 * poder mostrar el error del servidor en la pantalla en lugar de una página de JSON.
 */
export async function exportarReporte(tipo: TipoReporte, filtros: FiltrosReporte, formato: "csv" | "excel"): Promise<void> {
  const base = process.env.NEXT_PUBLIC_API_URL ?? "";
  const url = `${base}/api/reportes/${tipo}/exportacion?${parametros(filtros, { formato })}`;
  let respuesta = await fetch(url, { credentials: "include", cache: "no-store" });
  if (respuesta.status === 401 && (await renovarSesion())) {
    respuesta = await fetch(url, { credentials: "include", cache: "no-store" });
  }
  if (!respuesta.ok) {
    const cuerpo = await respuesta.json().catch(() => null);
    throw new Error(cuerpo?.error?.mensaje ?? "No se pudo preparar el archivo.");
  }
  const nombreCabecera = /filename="?([^";]+)"?/.exec(respuesta.headers.get("Content-Disposition") ?? "")?.[1];
  const blob = await respuesta.blob();
  const enlace = document.createElement("a");
  enlace.href = URL.createObjectURL(blob);
  enlace.download = nombreCabecera ?? `reporte-${tipo}.${formato === "csv" ? "csv" : "xlsx"}`;
  document.body.appendChild(enlace);
  enlace.click();
  enlace.remove();
  URL.revokeObjectURL(enlace.href);
}
