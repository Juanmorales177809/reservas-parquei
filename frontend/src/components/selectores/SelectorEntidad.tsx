"use client";

import { useEffect, useRef, useState } from "react";
import { Select } from "@/src/components/ui/Select";

export interface OpcionSelector {
  valor: string;
  etiqueta: string;
}

interface Props {
  id: string;
  label: string;
  value: string;
  onChange: (valor: string) => void;
  /** Trae las opciones (ya con el nombre visible). El valor de cada opción es el id. */
  cargar: () => Promise<OpcionSelector[]>;
  /** Cambia cuando la lista debe volver a pedirse (p. ej. la unidad elegida). */
  clave?: string;
  requerido?: boolean;
  deshabilitado?: boolean;
  /** Texto de la opción vacía. */
  textoVacio?: string;
}

/**
 * Selector de una entidad por su nombre: el usuario nunca teclea un id. La función
 * `cargar` se guarda en una referencia para que no dispare el efecto en cada render.
 */
export function SelectorEntidad({
  id, label, value, onChange, cargar, clave = "", requerido, deshabilitado, textoVacio = "Seleccionar…",
}: Props) {
  const [opciones, setOpciones] = useState<OpcionSelector[] | null>(null);
  const [error, setError] = useState(false);
  const cargarRef = useRef(cargar);
  cargarRef.current = cargar;
  const onChangeRef = useRef(onChange);
  onChangeRef.current = onChange;

  useEffect(() => {
    let cancelado = false;
    setOpciones(null);
    setError(false);
    if (deshabilitado) return;
    cargarRef.current()
      .then((lista) => {
        if (cancelado) return;
        setOpciones(lista);
      })
      .catch(() => {
        if (!cancelado) setError(true);
      });
    return () => {
      cancelado = true;
    };
  }, [clave, deshabilitado]);

  // Una elección que ya no está en la lista (cambió la unidad) se descarta.
  useEffect(() => {
    if (opciones && value && !opciones.some((o) => o.valor === value)) onChangeRef.current("");
  }, [opciones, value]);

  return (
    <Select
      id={id}
      label={label}
      value={value}
      required={requerido}
      disabled={deshabilitado || (opciones === null && !error)}
      error={error ? "No se pudo cargar la lista." : undefined}
      onChange={(e) => onChange(e.target.value)}
    >
      <option value="">{opciones === null && !error && !deshabilitado ? "Cargando…" : textoVacio}</option>
      {(opciones ?? []).map((o) => (
        <option key={o.valor} value={o.valor}>
          {o.etiqueta}
        </option>
      ))}
    </Select>
  );
}
