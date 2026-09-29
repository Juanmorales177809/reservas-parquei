"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { ApiRequestError } from "@/src/lib/http";
import {
  actualizarRecurso,
  cambiarEstadoRecurso,
  detalleRecurso,
  impactoDeshabilitacion,
  reasignarRecurso,
} from "@/src/lib/recursos-api";
import type { ImpactoDeshabilitacion, RecursoDetalle } from "@/src/lib/recursos-types";

/** Detalle, edición, estado y unidad (WF-REC-02). */
export function RecursoDetalleClient({ puedeGestionar }: { puedeGestionar: boolean }) {
  const params = useParams();
  const router = useRouter();
  const id = Number(params.id);
  const [detalle, setDetalle] = useState<RecursoDetalle | null>(null);
  const [impacto, setImpacto] = useState<ImpactoDeshabilitacion | null>(null);
  const [nombre, setNombre] = useState("");
  const [nuevaUnidad, setNuevaUnidad] = useState("");
  const [ocupada, setOcupada] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");

  async function recargar() {
    const d = await detalleRecurso(id);
    setDetalle(d);
    const actual = d.tipo === "EQUIPO" ? d.especializacion["nombre_equipo"] : d.especializacion["nombre"];
    if (typeof actual === "string") setNombre(actual);
  }

  useEffect(() => {
    let cancelado = false;
    recargar().catch((err) => {
      if (cancelado) return;
      if (err instanceof ApiRequestError && err.status === 401) {
        router.replace("/login?motivo=sesion_vencida");
        return;
      }
      setMensaje("No se pudo cargar el recurso.");
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

  async function guardar(evento: FormEvent) {
    evento.preventDefault();
    setOcupada(true);
    try {
      const campo = detalle?.tipo === "EQUIPO" ? { nombre_equipo: nombre } : { nombre };
      await actualizarRecurso(id, campo);
      await recargar();
      informar("Recurso actualizado.", "exito");
    } catch (error) {
      informar(mensajeError(error), "error");
    } finally {
      setOcupada(false);
    }
  }

  async function consultarImpacto() {
    setOcupada(true);
    try {
      setImpacto(await impactoDeshabilitacion(id));
    } catch {
      informar("No se pudo consultar el impacto.", "error");
    } finally {
      setOcupada(false);
    }
  }

  async function cambiarEstado(habilitado: boolean, confirmado: boolean) {
    setOcupada(true);
    try {
      await cambiarEstadoRecurso(id, habilitado, confirmado);
      setImpacto(null);
      await recargar();
      informar(habilitado ? "Recurso habilitado." : "Recurso deshabilitado.", "exito");
    } catch (error) {
      informar(mensajeError(error), "error");
    } finally {
      setOcupada(false);
    }
  }

  async function reasignar(evento: FormEvent) {
    evento.preventDefault();
    setOcupada(true);
    try {
      await reasignarRecurso(id, Number(nuevaUnidad));
      await recargar();
      informar("Unidad actualizada.", "exito");
    } catch (error) {
      informar(mensajeError(error), "error");
    } finally {
      setOcupada(false);
    }
  }

  if (!detalle) {
    return (
      <div className="flex flex-col gap-4">
        <h1 className="text-2xl font-bold text-text">Recurso</h1>
        <RegionMensaje texto={mensaje ?? "Cargando…"} tono={mensaje ? tono : "muted"} />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-text">
        {detalle.tipo} #{detalle.id} {!detalle.habilitado && "(deshabilitado)"}
      </h1>
      {puedeGestionar && (
        <>
          <form onSubmit={(e) => void guardar(e)} className="flex flex-col gap-2">
            <Field id="rec-nombre-editar" label="Nombre" value={nombre}
              onChange={(e) => setNombre(e.target.value)} required />
            <div>
              <Button type="submit" variant="secondary" loading={ocupada}>Guardar datos</Button>
            </div>
          </form>
          <section aria-label="Estado" className="flex flex-col gap-2">
            <div className="flex gap-2">
              <Button variant="secondary" disabled={ocupada}
                onClick={() => void cambiarEstado(true, false)}>Habilitar</Button>
              <Button variant="danger" disabled={ocupada}
                onClick={() => void consultarImpacto()}>Deshabilitar</Button>
            </div>
            {impacto && (
              <div className="text-sm text-text">
                <p>
                  Reservas a cancelar: {impacto.reservas_a_cancelar} · A retirar:{" "}
                  {impacto.reservas_a_retirar}
                </p>
                <Button variant="danger" disabled={ocupada}
                  onClick={() => void cambiarEstado(false, true)}>
                  Confirmar deshabilitación
                </Button>
              </div>
            )}
          </section>
          <form onSubmit={(e) => void reasignar(e)} className="flex items-end gap-2">
            <Field id="rec-unidad" label="Nueva unidad (id)" value={nuevaUnidad}
              onChange={(e) => setNuevaUnidad(e.target.value)} required />
            <Button type="submit" variant="secondary" loading={ocupada}>Reasignar</Button>
          </form>
        </>
      )}
      <RegionMensaje texto={mensaje} tono={mensaje ? tono : "muted"} />
    </div>
  );
}

function mensajeError(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.error.codigo === "CONFLICTO") return "Hay reservas que exigen confirmación explícita.";
    if (error.error.codigo === "UNIDAD_INCOMPATIBLE") return "La unidad no es válida para esta operación.";
    if (error.error.codigo === "VALIDACION") return "Revisa los datos ingresados.";
    if (error.status === 429) return "La operación está temporalmente limitada.";
  }
  return "No se pudo completar la operación.";
}
