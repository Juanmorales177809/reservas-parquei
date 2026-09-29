"use client";

import { useEffect, useRef, useState } from "react";
import { consultarDisponibilidad } from "@/src/lib/reservas-api";
import type { RecursoAsociado } from "@/src/lib/espacios-types";

type Estado = "consultando" | "disponible" | "ocupado" | "desconocido";

const hm = (t: string | null) => (t ? t.slice(0, 5) : null);

/**
 * Recursos asociados al espacio elegido, con su disponibilidad para el periodo pedido
 * (RN-TIP-PE-12, RN-TIP-PE-13). Uno no disponible no se puede incluir (RN-TIP-PE-14): la reserva del
 * espacio sigue siendo posible sin él.
 */
export function RecursosDelEspacio({
  idUnidad,
  recursos,
  fecha,
  horaInicio,
  horaFin,
  value,
  onChange,
}: {
  idUnidad: string;
  recursos: RecursoAsociado[];
  fecha: string;
  horaInicio: string;
  horaFin: string;
  value: string[];
  onChange: (ids: string[]) => void;
}) {
  const [estados, setEstados] = useState<Record<number, Estado>>({});
  const onChangeRef = useRef(onChange);
  onChangeRef.current = onChange;
  const valueRef = useRef(value);
  valueRef.current = value;
  const habilitados = recursos.filter((r) => r.habilitado);
  const periodo = Boolean(idUnidad && fecha && horaInicio && horaFin && horaInicio < horaFin);
  const clave = `${idUnidad}|${fecha}|${horaInicio}|${horaFin}|${habilitados.map((r) => r.recurso_id).join(",")}`;

  useEffect(() => {
    let cancelado = false;
    if (!periodo) {
      setEstados({});
      return;
    }
    setEstados(Object.fromEntries(habilitados.map((r) => [r.recurso_id, "consultando" as Estado])));
    Promise.all(
      habilitados.map(async (r): Promise<[number, Estado]> => {
        try {
          const d = await consultarDisponibilidad({
            id_unidad: Number(idUnidad), recurso_id: r.recurso_id, desde: fecha, hasta: fecha,
          });
          const choca = d.franjas.some((f) => {
            if (f.disponible) return false;
            const ini = hm(f.hora_inicio);
            const fin = hm(f.hora_fin);
            return ini === null || fin === null || (ini < horaFin && fin > horaInicio);
          });
          return [r.recurso_id, choca ? "ocupado" : "disponible"];
        } catch {
          return [r.recurso_id, "desconocido"];
        }
      })
    ).then((pares) => {
      if (cancelado) return;
      const mapa = Object.fromEntries(pares);
      setEstados(mapa);
      // Lo marcado que resultó no disponible se descarta.
      const utiles = valueRef.current.filter((v) => mapa[Number(v)] !== "ocupado");
      if (utiles.length !== valueRef.current.length) onChangeRef.current(utiles);
    });
    return () => {
      cancelado = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clave]);

  if (habilitados.length === 0) return null;

  return (
    <fieldset className="flex flex-col gap-1">
      <legend className="text-sm font-bold text-text">Recursos del espacio (opcional)</legend>
      {!periodo && <p className="text-sm text-muted">Elige fecha y horario para ver cuáles están disponibles.</p>}
      {habilitados.map((r) => {
        const estado = estados[r.recurso_id];
        const ocupado = estado === "ocupado";
        return (
          <label key={r.recurso_id} className={`flex items-center gap-2 text-sm ${ocupado ? "text-muted" : "text-text"}`}>
            <input
              type="checkbox"
              disabled={ocupado}
              checked={value.includes(String(r.recurso_id))}
              onChange={(e) =>
                onChange(
                  e.target.checked
                    ? [...value, String(r.recurso_id)]
                    : value.filter((v) => v !== String(r.recurso_id))
                )
              }
            />
            {r.nombre ?? "Sin nombre"}
            {periodo && estado === "consultando" && <span className="text-muted">(consultando…)</span>}
            {estado === "ocupado" && <span className="text-error-2">(no disponible en ese horario)</span>}
            {estado === "disponible" && <span className="text-muted">(disponible)</span>}
          </label>
        );
      })}
    </fieldset>
  );
}
