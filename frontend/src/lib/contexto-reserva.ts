import type { ReservaCrear } from "./reservas-types";

/** Lo elegido como contexto de una reserva (ids como texto, así viajan desde un `<select>`). */
export interface ContextoElegido {
  proyecto: string;
  semillero: string;
  pasantia: string;
  trabajo: string;
  actividad: string;
}

export const CONTEXTO_VACIO: ContextoElegido = { proyecto: "", semillero: "", pasantia: "", trabajo: "", actividad: "" };

export function hayContexto(c: ContextoElegido): boolean {
  return Object.values(c).some((v) => v !== "");
}

export function contextoParaEnviar(c: ContextoElegido): ReservaCrear["contexto"] {
  return {
    ...(c.proyecto ? { proyecto_id: Number(c.proyecto) } : {}),
    ...(c.semillero ? { semillero_id: Number(c.semillero) } : {}),
    ...(c.pasantia ? { pasantia_id: Number(c.pasantia) } : {}),
    ...(c.trabajo ? { trabajo_grado_id: Number(c.trabajo) } : {}),
    ...(c.actividad ? { actividad_institucional_id: Number(c.actividad) } : {}),
  };
}
