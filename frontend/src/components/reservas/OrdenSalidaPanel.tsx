"use client";

import { useEffect, useState } from "react";
import { fechaHora } from "@/src/lib/formato";
import { ApiRequestError } from "@/src/lib/http";
import { ordenSalida, urlOrdenSalidaPdf } from "@/src/lib/reservas-api";
import { fechaCorta } from "@/src/lib/reservas-nombres";
import type { OrdenSalida } from "@/src/lib/reservas-types";

/**
 * Orden de salida FGL 030 de un préstamo (RN-TIP-RC-07, RN-TIP-RC-11): se muestra como se generó al
 * aprobar —sus datos son inmutables— y se descarga en PDF. Las firmas van a mano sobre el papel (RN-TIP-RC-14).
 */
export function OrdenSalidaPanel({ idReserva }: { idReserva: number }) {
  const [orden, setOrden] = useState<OrdenSalida | null>(null);
  const [estado, setEstado] = useState<"cargando" | "lista" | "sin_orden" | "error">("cargando");

  useEffect(() => {
    let cancelado = false;
    ordenSalida(idReserva)
      .then((o) => {
        if (cancelado) return;
        setOrden(o);
        setEstado("lista");
      })
      .catch((e) => {
        if (!cancelado) setEstado(e instanceof ApiRequestError && e.status === 404 ? "sin_orden" : "error");
      });
    return () => {
      cancelado = true;
    };
  }, [idReserva]);

  return (
    <section aria-label="Orden de salida" className="flex flex-col gap-2">
      <h2 className="text-base font-bold text-text">Orden de salida (FGL 030)</h2>
      {estado === "cargando" && <p className="text-sm text-muted">Cargando…</p>}
      {estado === "sin_orden" && <p className="text-sm text-muted">La orden se genera cuando la reserva se aprueba.</p>}
      {estado === "error" && <p className="text-sm text-error-2">No se pudo cargar la orden de salida.</p>}
      {estado === "lista" && orden && (
        <>
          <dl className="grid grid-cols-[max-content_1fr] gap-x-4 gap-y-1 text-sm text-text">
            <dt className="font-bold">Generada</dt><dd>{fechaHora(orden.fecha_generacion)}</dd>
            <dt className="font-bold">Dependencia</dt><dd>{orden.dependencia_solicitante_snapshot}</dd>
            <dt className="font-bold">Retiro</dt><dd>{fechaCorta(orden.fecha_retiro_snapshot)}</dd>
            <dt className="font-bold">Regreso</dt><dd>{fechaCorta(orden.fecha_regreso_snapshot)}</dd>
            <dt className="font-bold">Lugar</dt><dd>{orden.lugar_nombre} — {orden.lugar_direccion}</dd>
            <dt className="font-bold">Razón</dt><dd>{orden.razon_solicitud}</dd>
            {orden.nombre_actividad_evento && (<><dt className="font-bold">Actividad</dt><dd>{orden.nombre_actividad_evento}</dd></>)}
            {orden.proyecto_codigo_snapshot && (<><dt className="font-bold">Proyecto</dt><dd>{orden.proyecto_codigo_snapshot}</dd></>)}
            <dt className="font-bold">Responsable</dt>
            <dd>{orden.responsable_nombre_snapshot} · {orden.responsable_correo_snapshot} · {orden.responsable_telefono_snapshot}</dd>
          </dl>
          <ul className="text-sm text-text">
            {orden.items.map((i) => (
              <li key={i.reserva_recurso_id}>
                {i.descripcion_snapshot}{i.placa_snapshot ? ` · placa ${i.placa_snapshot}` : ""}
              </li>
            ))}
          </ul>
          <a href={urlOrdenSalidaPdf(idReserva)} className="text-sm font-bold text-primary-2">
            Descargar la orden en PDF
          </a>
        </>
      )}
    </section>
  );
}
