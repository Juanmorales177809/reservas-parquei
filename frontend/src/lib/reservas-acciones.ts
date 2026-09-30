import type { ContextoSesion } from "./auth-types";
import type { ReservaResumen } from "./reservas-types";

/** Qué parte de la gestión de una reserva se muestra en el modal (`GestionReservaContenido`). */
export type VistaGestion =
  | "todo"
  | "revision"
  | "propuestas"
  | "ejecucion"
  | "finalizacion"
  | "cancelacion"
  | "editar"
  | "recursos"
  | "lista";

export interface AccionReserva {
  vista: VistaGestion;
  etiqueta: string;
  variante: "primary" | "success" | "danger" | "secondary" | "ghost";
}

/**
 * Las acciones que este actor puede hacer sobre una reserva, deducidas del resumen del listado. Es el mismo
 * criterio que el detalle (`GestionReservaClient`): la pantalla solo ofrece lo que corresponde al rol, y el
 * servidor sigue autorizando cada operación.
 */
export function accionesDe(r: ReservaResumen, sesion: ContextoSesion): AccionReserva[] {
  const puedeGestionar =
    sesion.rol !== "USUARIO" &&
    (sesion.unidades_autorizadas === "GLOBAL" || sesion.unidades_autorizadas.includes(r.id_unidad));
  const esPropietario = r.id_cuenta === sesion.id_cuenta;
  const esLista = r.tipo_reserva === "LISTA_ESPERA";
  const esEspacioInterno = r.tipo_reserva === "ESPACIO" || r.tipo_reserva === "RECURSO_INTERNO";
  const admitePropuesta = !esLista;
  const acciones: AccionReserva[] = [];

  if (r.estado === "SOLICITADA") {
    if (puedeGestionar && !esLista) acciones.push({ vista: "revision", etiqueta: "Aprobar", variante: "success" });
    if (puedeGestionar) acciones.push({ vista: "revision", etiqueta: "Rechazar", variante: "danger" });
    if (esPropietario && !esLista) acciones.push({ vista: "editar", etiqueta: "Editar", variante: "secondary" });
  }
  if (r.estado === "APROBADA" && puedeGestionar && !esEspacioInterno) {
    acciones.push({
      vista: "ejecucion",
      etiqueta: esLista ? "Iniciar" : "Registrar entrega",
      variante: "primary",
    });
  }
  if (r.estado === "EN_EJECUCION" && puedeGestionar && !esEspacioInterno) {
    acciones.push({ vista: "finalizacion", etiqueta: "Finalizar", variante: "success" });
  }
  if ((r.estado === "SOLICITADA" || r.estado === "APROBADA") && puedeGestionar && admitePropuesta) {
    acciones.push({ vista: "propuestas", etiqueta: "Proponer otro periodo", variante: "secondary" });
  }
  if (puedeGestionar && esEspacioInterno && ["SOLICITADA", "APROBADA", "EN_EJECUCION"].includes(r.estado)) {
    acciones.push({ vista: "recursos", etiqueta: "Recursos", variante: "secondary" });
  }
  if (esLista && (puedeGestionar || esPropietario) && ["SOLICITADA", "APROBADA", "EN_EJECUCION"].includes(r.estado)) {
    acciones.push({ vista: "lista", etiqueta: "Gestionar solicitud", variante: "secondary" });
  }
  if ((esPropietario || puedeGestionar) && (r.estado === "SOLICITADA" || r.estado === "APROBADA")) {
    acciones.push({ vista: "cancelacion", etiqueta: "Cancelar", variante: "ghost" });
  }
  return acciones;
}
