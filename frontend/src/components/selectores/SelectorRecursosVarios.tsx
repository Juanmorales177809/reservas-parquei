"use client";

import { useEffect, useState } from "react";
import { CasillaTarjeta, GrupoCasillas } from "@/src/components/ui/CasillaTarjeta";
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
  reservable = true,
}: {
  idUnidad: string;
  /** Recursos que no se ofrecen (el principal ya elegido, o los ya asignados a la reserva). */
  excluir?: string | string[];
  value: string[];
  onChange: (ids: string[]) => void;
  label: string;
  /** `true` (por defecto) ofrece solo lo reservable; `false` ofrece todos los recursos del laboratorio. */
  reservable?: boolean;
}) {
  const [opciones, setOpciones] = useState<Opcion[] | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelado = false;
    setOpciones(null);
    setError(false);
    if (!idUnidad) return;
    listarRecursos({ id_unidad: Number(idUnidad), ...(reservable ? { reservable: true } : {}) })
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
  }, [idUnidad, reservable]);

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
    <GrupoCasillas leyenda={label}>
      {!idUnidad ? (
        <p className="text-sm text-muted">Elige primero el laboratorio.</p>
      ) : error ? (
        <p className="text-sm text-error-2">No se pudo cargar la lista.</p>
      ) : opciones === null ? (
        <p className="text-sm text-muted">Cargando…</p>
      ) : visibles.length === 0 ? (
        <p className="text-sm text-muted">No hay más recursos disponibles en este laboratorio.</p>
      ) : (
        visibles.map((o) => (
          <CasillaTarjeta
            key={o.valor}
            checked={value.includes(o.valor)}
            onChange={(e) =>
              onChange(e.target.checked ? [...value, o.valor] : value.filter((v) => v !== o.valor))
            }
          >
            {o.etiqueta}
          </CasillaTarjeta>
        ))
      )}
    </GrupoCasillas>
  );
}
