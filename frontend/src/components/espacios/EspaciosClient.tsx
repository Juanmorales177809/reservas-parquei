"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { SelectorUnidad } from "@/src/components/selectores/selectores";
import { Field } from "@/src/components/ui/Field";
import { Select } from "@/src/components/ui/Select";
import { ApiRequestError } from "@/src/lib/http";
import { crearEspacio, listarEspacios } from "@/src/lib/espacios-api";
import type { EspacioResumen } from "@/src/lib/espacios-types";

/** Catálogo y registro (WF-ESP-04, WF-ESP-01). */
export function EspaciosClient({ puedeGestionar }: { puedeGestionar: boolean }) {
  const router = useRouter();
  const [espacios, setEspacios] = useState<EspacioResumen[] | null>(null);
  const [idUnidad, setIdUnidad] = useState("");
  const [nombre, setNombre] = useState("");
  const [capacidad, setCapacidad] = useState("");
  const [ubicacion, setUbicacion] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [filtroUnidad, setFiltroUnidad] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("");
  const [filtroCapacidad, setFiltroCapacidad] = useState("");
  const [ocupada, setOcupada] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");

  async function recargar() {
    const r = await listarEspacios({
      ...(filtroUnidad ? { id_unidad: Number(filtroUnidad) } : {}),
      ...(filtroEstado ? { habilitado: filtroEstado === "true" } : {}),
      ...(filtroCapacidad && Number(filtroCapacidad) > 0 ? { capacidad_minima: Number(filtroCapacidad) } : {}),
    });
    setEspacios(r.datos);
  }

  useEffect(() => {
    let cancelado = false;
    const espera = window.setTimeout(() => {
      recargar().catch((err) => {
        if (cancelado) return;
        if (err instanceof ApiRequestError && err.status === 401) {
          router.replace("/login?motivo=sesion_vencida");
          return;
        }
        setMensaje("No se pudieron cargar los espacios.");
        setTono("error");
      });
    }, filtroCapacidad ? 300 : 0); // la capacidad espera a que se deje de escribir
    return () => {
      cancelado = true;
      window.clearTimeout(espera);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router, filtroUnidad, filtroEstado, filtroCapacidad]);

  async function guardar(evento: FormEvent) {
    evento.preventDefault();
    setOcupada(true);
    setMensaje(null);
    try {
      await crearEspacio({
        id_unidad: Number(idUnidad),
        nombre: nombre.trim(),
        capacidad: Number(capacidad),
        ...(ubicacion.trim() ? { ubicacion: ubicacion.trim() } : {}),
        ...(descripcion.trim() ? { descripcion: descripcion.trim() } : {}),
      });
      setNombre("");
      setCapacidad("");
      setUbicacion("");
      setDescripcion("");
      await recargar();
      setMensaje("Espacio creado.");
      setTono("exito");
    } catch (error) {
      setMensaje(mensajeError(error));
      setTono("error");
    } finally {
      setOcupada(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Espacios</h1>
      <div className="flex flex-wrap items-end gap-3">
        <SelectorUnidad id="esp-filtro-unidad" label="Ver espacios de la unidad" value={filtroUnidad}
          onChange={setFiltroUnidad} textoVacio="Todas" />
        <Select id="esp-filtro-estado" label="Estado" value={filtroEstado} onChange={(e) => setFiltroEstado(e.target.value)}>
          <option value="">Todos</option>
          <option value="true">Habilitados</option>
          <option value="false">Deshabilitados</option>
        </Select>
        <Field id="esp-filtro-capacidad" label="Capacidad mínima" type="number" value={filtroCapacidad}
          onChange={(e) => setFiltroCapacidad(e.target.value)} />
      </div>
      {espacios === null ? (
        <RegionMensaje texto={mensaje ?? "Cargando espacios…"} tono={mensaje ? tono : "muted"} />
      ) : (
        <ul className="flex flex-col gap-1 text-sm text-text">
          {espacios.length === 0 && <li className="text-muted">No hay espacios con esos criterios.</li>}
          {espacios.map((e) => (
            <li key={e.id}>
              <Link href={`/espacios/${e.id}`} className="font-bold text-primary-2">
                {e.nombre}
              </Link>{" "}
              (cap. {e.capacidad}) {!e.habilitado && "(deshabilitado)"}
            </li>
          ))}
        </ul>
      )}
      {puedeGestionar && (
        <form onSubmit={(e) => void guardar(e)} className="flex flex-col gap-4">
          <h2 className="text-base font-bold text-text">Registrar espacio</h2>
          <SelectorUnidad id="esp-unidad" label="Unidad" value={idUnidad} onChange={setIdUnidad} requerido />
          <Field id="esp-nombre" label="Nombre" value={nombre}
            onChange={(e) => setNombre(e.target.value)} required />
          <Field id="esp-capacidad" label="Capacidad" type="number" value={capacidad}
            onChange={(e) => setCapacidad(e.target.value)} required />
          <Field id="esp-ubicacion" label="Ubicación (opcional)" value={ubicacion}
            onChange={(e) => setUbicacion(e.target.value)} />
          <Field id="esp-descripcion" label="Descripción (opcional)" value={descripcion}
            onChange={(e) => setDescripcion(e.target.value)} />
          <div>
            <Button type="submit" variant="primary" loading={ocupada}>Guardar espacio</Button>
          </div>
        </form>
      )}
      <RegionMensaje texto={mensaje} tono={mensaje ? tono : "muted"} />
    </div>
  );
}

function mensajeError(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.error.codigo === "NOMBRE_DUPLICADO") return "Ese nombre ya existe en la unidad.";
    if (error.error.codigo === "VALIDACION") return "Revisa los datos ingresados.";
    if (error.status === 429) return "La operación está temporalmente limitada.";
  }
  return "No se pudo completar la operación.";
}
