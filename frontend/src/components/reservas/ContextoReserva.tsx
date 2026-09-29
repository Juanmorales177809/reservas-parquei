"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { Select } from "@/src/components/ui/Select";
import { CONTEXTO_VACIO, hayContexto, type ContextoElegido } from "@/src/lib/contexto-reserva";
import { opcionesContexto } from "@/src/lib/reservas-api";
import type { OpcionesContexto } from "@/src/lib/reservas-types";

/**
 * Contexto de la reserva (RN-CTX): lo que justifica el uso. Una cuenta USUARIO elige entre sus
 * vinculaciones activas o una actividad institucional; una cuenta PERSONAL, proyecto y/o semillero
 * del catálogo general. Una actividad institucional no convive con el resto (RN-CTX-04).
 */
export function ContextoReserva({
  value,
  onChange,
}: {
  value: ContextoElegido;
  onChange: (c: ContextoElegido) => void;
}) {
  const [opciones, setOpciones] = useState<OpcionesContexto | null>(null);
  const [error, setError] = useState(false);
  const valueRef = useRef(value);
  valueRef.current = value;
  const onChangeRef = useRef(onChange);
  onChangeRef.current = onChange;

  useEffect(() => {
    let cancelado = false;
    opcionesContexto()
      .then((o) => {
        if (cancelado) return;
        setOpciones(o);
        // RN-TIP-PE-08: a una cuenta USUARIO con una única vinculación válida de un tipo se le preselecciona.
        // Solo si todavía no hay nada elegido: al editar, el contexto actual manda.
        if (o.tipo_cuenta === "USUARIO" && !hayContexto(valueRef.current)) {
          const auto = { ...CONTEXTO_VACIO, ...valueRef.current };
          if (o.proyectos.length === 1 && !auto.proyecto) auto.proyecto = String(o.proyectos[0].id);
          if (o.semilleros.length === 1 && !auto.semillero) auto.semillero = String(o.semilleros[0].id);
          if (o.pasantias.length === 1 && !auto.pasantia) auto.pasantia = String(o.pasantias[0].id);
          if (o.trabajos_grado.length === 1 && !auto.trabajo) auto.trabajo = String(o.trabajos_grado[0].id);
          onChangeRef.current(auto);
        }
      })
      .catch(() => {
        if (!cancelado) setError(true);
      });
    return () => {
      cancelado = true;
    };
  }, []);

  if (error) return <p className="text-sm text-error-2">No se pudieron cargar los contextos disponibles.</p>;
  if (!opciones) return <p className="text-sm text-muted">Cargando contexto…</p>;

  const esUsuario = opciones.tipo_cuenta === "USUARIO";
  const academico = (campo: keyof ContextoElegido, valor: string) =>
    onChange({ ...value, [campo]: valor, actividad: valor ? "" : value.actividad });
  const sinOpciones =
    opciones.proyectos.length + opciones.semilleros.length + opciones.pasantias.length +
      opciones.trabajos_grado.length + opciones.actividades.length === 0;

  if (sinOpciones) {
    return (
      <p className="text-sm text-error-2">
        {esUsuario ? (
          <>
            No tienes vinculaciones activas para justificar la reserva.{" "}
            <Link href="/usuarios/perfil/vinculaciones" className="font-bold text-primary-2">
              Agrégalas en Mis vinculaciones
            </Link>
            .
          </>
        ) : (
          "No hay proyectos ni semilleros activos en el catálogo."
        )}
      </p>
    );
  }

  return (
    <fieldset className="flex flex-col gap-3">
      <legend className="text-sm font-bold text-text">
        {esUsuario ? "¿Para qué es la reserva?" : "Proyecto o semillero"}
      </legend>
      <p className="text-sm text-muted">
        {esUsuario
          ? "Elige al menos una de tus vinculaciones, o una actividad institucional."
          : "Elige al menos un proyecto o un semillero."}
      </p>
      {opciones.proyectos.length > 0 && (
        <Select id="res-proyecto" label="Proyecto" value={value.proyecto} onChange={(e) => academico("proyecto", e.target.value)}>
          <option value="">Sin proyecto</option>
          {opciones.proyectos.map((p) => (
            <option key={p.id} value={p.id}>{`${p.nombre} (${p.codigo})`}</option>
          ))}
        </Select>
      )}
      {opciones.semilleros.length > 0 && (
        <Select id="res-semillero" label="Semillero" value={value.semillero} onChange={(e) => academico("semillero", e.target.value)}>
          <option value="">Sin semillero</option>
          {opciones.semilleros.map((s) => (
            <option key={s.id} value={s.id}>{`${s.nombre} (${s.codigo})`}</option>
          ))}
        </Select>
      )}
      {opciones.pasantias.length > 0 && (
        <Select id="res-pasantia" label="Pasantía" value={value.pasantia} onChange={(e) => academico("pasantia", e.target.value)}>
          <option value="">Sin pasantía</option>
          {opciones.pasantias.map((p) => (
            <option key={p.id} value={p.id}>{`${p.universidad} · ${p.docente_nombre}`}</option>
          ))}
        </Select>
      )}
      {opciones.trabajos_grado.length > 0 && (
        <Select id="res-trabajo" label="Trabajo de grado" value={value.trabajo} onChange={(e) => academico("trabajo", e.target.value)}>
          <option value="">Sin trabajo de grado</option>
          {opciones.trabajos_grado.map((t) => (
            <option key={t.id} value={t.id}>{`Dirige ${t.director_nombre}`}</option>
          ))}
        </Select>
      )}
      {opciones.actividades.length > 0 && (
        <Select
          id="res-actividad"
          label="Actividad institucional (reemplaza a lo anterior)"
          value={value.actividad}
          onChange={(e) =>
            onChange(
              e.target.value
                ? { ...CONTEXTO_VACIO, actividad: e.target.value }
                : { ...value, actividad: "" }
            )
          }
        >
          <option value="">Ninguna</option>
          {opciones.actividades.map((a) => (
            <option key={a.id} value={a.id}>{`${a.nombre} (${a.dependencia})`}</option>
          ))}
        </Select>
      )}
    </fieldset>
  );
}
