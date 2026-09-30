"use client";

import { useEffect, useRef, useState } from "react";
import { opcionesAcompanantes } from "@/src/lib/reservas-api";
import type { AcompananteOpcion } from "@/src/lib/reservas-types";
import { CasillaTarjeta, GrupoCasillas } from "@/src/components/ui/CasillaTarjeta";

/**
 * Acompañantes de una reserva por espacio (RN-ACO): cuentas con vinculación activa al proyecto o
 * semillero elegido, seleccionadas por nombre. Su número es el de asistentes y no supera la capacidad.
 */
export function AcompanantesReserva({
  proyectoId,
  semilleroId,
  capacidad,
  value,
  onChange,
}: {
  proyectoId: string;
  semilleroId: string;
  capacidad?: number;
  value: string[];
  onChange: (ids: string[]) => void;
}) {
  const [opciones, setOpciones] = useState<AcompananteOpcion[] | null>(null);
  const [error, setError] = useState(false);
  const onChangeRef = useRef(onChange);
  onChangeRef.current = onChange;
  const valueRef = useRef(value);
  valueRef.current = value;
  const aplica = proyectoId !== "" || semilleroId !== "";

  useEffect(() => {
    let cancelado = false;
    setOpciones(null);
    setError(false);
    if (!aplica) {
      if (valueRef.current.length > 0) onChangeRef.current([]);
      return;
    }
    opcionesAcompanantes({
      ...(proyectoId ? { proyecto_id: Number(proyectoId) } : {}),
      ...(semilleroId ? { semillero_id: Number(semilleroId) } : {}),
    })
      .then((r) => {
        if (cancelado) return;
        setOpciones(r.datos);
        const vigentes = valueRef.current.filter((v) => r.datos.some((a) => String(a.id_cuenta) === v));
        if (vigentes.length !== valueRef.current.length) onChangeRef.current(vigentes);
      })
      .catch(() => {
        if (!cancelado) setError(true);
      });
    return () => {
      cancelado = true;
    };
  }, [proyectoId, semilleroId, aplica]);

  if (!aplica) return null;
  const excede = capacidad !== undefined && value.length > capacidad;

  return (
    <GrupoCasillas leyenda="Acompañantes (opcional)">
      {error ? (
        <p className="text-sm text-error-2">No se pudo cargar la lista de acompañantes.</p>
      ) : opciones === null ? (
        <p className="text-sm text-muted">Cargando…</p>
      ) : opciones.length === 0 ? (
        <p className="text-sm text-muted">Nadie más está vinculado a este proyecto o semillero.</p>
      ) : (
        opciones.map((a) => (
          <CasillaTarjeta
              key={a.id_cuenta}
              checked={value.includes(String(a.id_cuenta))}
              onChange={(e) =>
                onChange(
                  e.target.checked
                    ? [...value, String(a.id_cuenta)]
                    : value.filter((v) => v !== String(a.id_cuenta))
                )
              }
            >
            {a.nombre}
          </CasillaTarjeta>
        ))
      )}
      <p className={`text-sm ${excede ? "text-error-2" : "text-muted"}`}>
        Asistentes: {value.length}
        {capacidad !== undefined && ` de ${capacidad} (capacidad del espacio)`}
      </p>
    </GrupoCasillas>
  );
}
