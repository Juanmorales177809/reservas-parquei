"use client";

import { useEffect, useState } from "react";
import { listarRecursos } from "@/src/lib/recursos-api";

interface Opcion {
  valor: string;
  etiqueta: string;
}

const NOMBRE_TIPO: Record<string, string> = { EQUIPO: "Equipo", MOBILIARIO: "Mobiliario", OTRO: "Otro" };

/** Varios recursos a la vez (complementarios de una reserva), elegidos por nombre. */
export function SelectorRecursosVarios({
  idUnidad,
  excluir,
  value,
  onChange,
  label,
}: {
  idUnidad: string;
  /** Recursos que no se ofrecen (el principal ya elegido, o los ya asignados a la reserva). */
  excluir?: string | string[];
  value: string[];
  onChange: (ids: string[]) => void;
  label: string;
}) {
  const [opciones, setOpciones] = useState<Opcion[] | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelado = false;
    setOpciones(null);
    setError(false);
    if (!idUnidad) return;
    listarRecursos({ id_unidad: Number(idUnidad), reservable: true })
      .then((r) => {
        if (cancelado) return;
        setOpciones(
          r.datos
            .filter((x) => x.habilitado)
            .map((x) => ({
              valor: String(x.id),
              etiqueta: `${x.nombre ?? "Sin nombre"} · ${NOMBRE_TIPO[x.tipo] ?? x.tipo}`,
            }))
        );
      })
      .catch(() => {
        if (!cancelado) setError(true);
      });
    return () => {
      cancelado = true;
    };
  }, [idUnidad]);

  const excluidos = Array.isArray(excluir) ? excluir : excluir ? [excluir] : [];
  const claveExcluidos = excluidos.join(",");
  const visibles = (opciones ?? []).filter((o) => !excluidos.includes(o.valor));

  // Lo elegido que ya no se ofrece (otra unidad, o pasó a ser el principal) se descarta.
  useEffect(() => {
    if (opciones && value.some((v) => !visibles.some((o) => o.valor === v))) {
      onChange(value.filter((v) => visibles.some((o) => o.valor === v)));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [opciones, claveExcluidos]);

  return (
    <fieldset className="flex flex-col gap-1">
      <legend className="text-sm font-bold text-text">{label}</legend>
      {!idUnidad ? (
        <p className="text-sm text-muted">Elige primero la unidad.</p>
      ) : error ? (
        <p className="text-sm text-error-2">No se pudo cargar la lista.</p>
      ) : opciones === null ? (
        <p className="text-sm text-muted">Cargando…</p>
      ) : visibles.length === 0 ? (
        <p className="text-sm text-muted">No hay más recursos disponibles en esta unidad.</p>
      ) : (
        visibles.map((o) => (
          <label key={o.valor} className="flex items-center gap-2 text-sm text-text">
            <input
              type="checkbox"
              checked={value.includes(o.valor)}
              onChange={(e) =>
                onChange(e.target.checked ? [...value, o.valor] : value.filter((v) => v !== o.valor))
              }
            />
            {o.etiqueta}
          </label>
        ))
      )}
    </fieldset>
  );
}
