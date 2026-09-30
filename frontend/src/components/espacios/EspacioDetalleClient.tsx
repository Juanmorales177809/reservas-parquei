"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { SelectorRecurso } from "@/src/components/selectores/selectores";
import { Field } from "@/src/components/ui/Field";
import { CamposDelEspacio } from "@/src/components/espacios/CamposDelEspacio";
import { ApiRequestError } from "@/src/lib/http";
import {
  asociarRecursos,
  cambiarEstadoEspacio,
  detalleEspacio,
  editarEspacio,
  impactoDeshabilitacionEspacio,
  retirarRecurso,
} from "@/src/lib/espacios-api";
import type { EspacioDetalle } from "@/src/lib/espacios-types";

/** Detalle, estado, asociados y campos (WF-ESP-02, WF-ESP-03). */
export function EspacioDetalleClient({ puedeGestionar }: { puedeGestionar: boolean }) {
  const params = useParams();
  const router = useRouter();
  const id = Number(params.id);
  const [detalle, setDetalle] = useState<EspacioDetalle | null>(null);
  const [impacto, setImpacto] = useState<number | null>(null);
  const [recursoId, setRecursoId] = useState("");
  const [datos, setDatos] = useState({ nombre: "", ubicacion: "", capacidad: "", descripcion: "" });
  const [ocupada, setOcupada] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");

  async function recargar() {
    const d = await detalleEspacio(id);
    setDetalle(d);
    setDatos({ nombre: d.nombre, ubicacion: d.ubicacion ?? "", capacidad: String(d.capacidad), descripcion: d.descripcion ?? "" });
  }

  /** Ejecuta una operación del detalle, recarga y avisa; los errores del servidor se muestran. */
  async function actuar(accion: () => Promise<unknown>, exito: string) {
    setOcupada(true);
    try {
      await accion();
      await recargar();
      informar(exito, "exito");
    } catch (error) {
      informar(mensajeError(error), "error");
    } finally {
      setOcupada(false);
    }
  }

  function guardarDatos(evento: FormEvent) {
    evento.preventDefault();
    if (!detalle) return;
    const cambios: { nombre?: string; ubicacion?: string; capacidad?: number; descripcion?: string } = {};
    if (datos.nombre.trim() !== detalle.nombre) cambios.nombre = datos.nombre.trim();
    if (datos.ubicacion.trim() !== (detalle.ubicacion ?? "")) cambios.ubicacion = datos.ubicacion.trim();
    if (datos.descripcion.trim() !== (detalle.descripcion ?? "")) cambios.descripcion = datos.descripcion.trim();
    if (Number(datos.capacidad) !== detalle.capacidad) cambios.capacidad = Number(datos.capacidad);
    if (Object.keys(cambios).length === 0) {
      informar("No hay cambios que guardar.", "exito");
      return;
    }
    void actuar(() => editarEspacio(id, cambios), "Datos del espacio actualizados.");
  }

  useEffect(() => {
    let cancelado = false;
    recargar().catch((err) => {
      if (cancelado) return;
      if (err instanceof ApiRequestError && err.status === 401) {
        router.replace("/login?motivo=sesion_vencida");
        return;
      }
      setMensaje("No se pudo cargar el espacio.");
      setTono("error");
    });
    return () => {
      cancelado = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router, id]);

  function informar(texto: string, t: "error" | "exito") {
    setMensaje(texto);
    setTono(t);
  }

  async function consultarImpacto() {
    setOcupada(true);
    try {
      const r = await impactoDeshabilitacionEspacio(id);
      setImpacto(r.reservas_a_cancelar);
    } catch {
      informar("No se pudo consultar el impacto.", "error");
    } finally {
      setOcupada(false);
    }
  }

  async function cambiarEstado(habilitado: boolean, confirmado: boolean) {
    setOcupada(true);
    try {
      await cambiarEstadoEspacio(id, habilitado, confirmado);
      setImpacto(null);
      await recargar();
      informar(habilitado ? "Espacio habilitado." : "Espacio deshabilitado.", "exito");
    } catch (error) {
      informar(mensajeError(error), "error");
    } finally {
      setOcupada(false);
    }
  }

  async function asociar(evento: FormEvent) {
    evento.preventDefault();
    setOcupada(true);
    try {
      await asociarRecursos(id, [Number(recursoId)]);
      setRecursoId("");
      await recargar();
      informar("Recurso asociado.", "exito");
    } catch (error) {
      informar(mensajeError(error), "error");
    } finally {
      setOcupada(false);
    }
  }

  async function retirar(recursoIdActual: number) {
    setOcupada(true);
    try {
      await retirarRecurso(id, recursoIdActual);
      await recargar();
      informar("Asociación retirada.", "exito");
    } catch (error) {
      informar(mensajeError(error), "error");
    } finally {
      setOcupada(false);
    }
  }

  if (!detalle) {
    return (
      <div className="flex flex-col gap-4">
        <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Espacio</h1>
        <RegionMensaje texto={mensaje ?? "Cargando…"} tono={mensaje ? tono : "muted"} />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">{detalle.nombre}</h1>
        <p className="text-sm text-muted">
          Capacidad {detalle.capacidad} {!detalle.habilitado && "· deshabilitado"}
          {detalle.ubicacion ? ` · ${detalle.ubicacion}` : ""}
        </p>
        {detalle.descripcion && <p className="text-sm text-text">{detalle.descripcion}</p>}
        {detalle.horario_unidad && (
          <p className="text-sm text-muted">
            Horario de la unidad: {detalle.horario_unidad.hora_apertura.slice(0, 5)} – {detalle.horario_unidad.hora_cierre.slice(0, 5)}
          </p>
        )}
      </div>
      {puedeGestionar && (
        <form onSubmit={guardarDatos} aria-label="Datos del espacio" className="flex flex-col gap-3">
          <h2 className="text-base font-bold text-text">Datos del espacio</h2>
          <Field id="esp-ed-nombre" label="Nombre" value={datos.nombre} onChange={(e) => setDatos({ ...datos, nombre: e.target.value })} required />
          <Field id="esp-ed-ubicacion" label="Ubicación" value={datos.ubicacion} onChange={(e) => setDatos({ ...datos, ubicacion: e.target.value })} />
          <Field id="esp-ed-capacidad" label="Capacidad" type="number" value={datos.capacidad} onChange={(e) => setDatos({ ...datos, capacidad: e.target.value })} required />
          <Field id="esp-ed-descripcion" label="Descripción" value={datos.descripcion} onChange={(e) => setDatos({ ...datos, descripcion: e.target.value })} />
          <div>
            <Button type="submit" variant="secondary" loading={ocupada}>Guardar datos</Button>
          </div>
        </form>
      )}
      {puedeGestionar && (
        <section aria-label="Estado" className="flex flex-col gap-2">
          <div className="flex gap-2">
            <Button variant="secondary" size="sm" disabled={ocupada}
              onClick={() => void cambiarEstado(true, false)}>Habilitar</Button>
            <Button variant="danger" size="sm" disabled={ocupada}
              onClick={() => void consultarImpacto()}>Deshabilitar</Button>
          </div>
          {impacto !== null && (
            <div className="text-sm text-text">
              <p>Reservas futuras a cancelar: {impacto}</p>
              <Button variant="danger" size="sm" disabled={ocupada}
                onClick={() => void cambiarEstado(false, true)}>
                Confirmar deshabilitación
              </Button>
            </div>
          )}
        </section>
      )}
      <section aria-label="Recursos asociados" className="flex flex-col gap-2">
        <h2 className="text-base font-bold text-text">Recursos asociados</h2>
        <ul className="flex flex-col gap-1 text-sm text-text">
          {(detalle.recursos ?? []).map((r) => (
            <li key={r.recurso_id} className="flex items-center gap-2">
              <span>{r.nombre ?? `Recurso ${r.recurso_id}`}</span>
              {puedeGestionar && (
                <Button variant="ghost" size="sm" disabled={ocupada}
                  onClick={() => void retirar(r.recurso_id)}>Retirar</Button>
              )}
            </li>
          ))}
        </ul>
        {puedeGestionar && (
          <form onSubmit={(e) => void asociar(e)} className="flex items-end gap-2">
            <SelectorRecurso id="asoc-recurso" label="Recurso" idUnidad={String(detalle.id_unidad)}
              reservable={false} value={recursoId} onChange={setRecursoId} requerido />
            <Button type="submit" variant="secondary" loading={ocupada}>Asociar</Button>
          </form>
        )}
      </section>
      <CamposDelEspacio espacioId={id} campos={detalle.campos ?? []} puedeGestionar={puedeGestionar} ocupada={ocupada} actuar={actuar} />
      <RegionMensaje texto={mensaje} tono={mensaje ? tono : "muted"} />
    </div>
  );
}

function mensajeError(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.error.codigo === "CAMPO_SIN_OPCIONES")
      return "Una lista necesita al menos una opción habilitada.";
    if (error.error.codigo === "CONFLICTO") return "Ese nombre ya existe en este espacio.";
    if (error.error.codigo === "UNIDAD_INCOMPATIBLE") return "El recurso es de otra unidad o ya está asociado.";
    if (error.error.codigo === "VALIDACION") return "Revisa los datos ingresados.";
    if (error.status === 429) return "La operación está temporalmente limitada.";
  }
  return "No se pudo completar la operación.";
}
