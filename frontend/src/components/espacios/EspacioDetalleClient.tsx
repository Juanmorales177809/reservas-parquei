"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { Select } from "@/src/components/ui/Select";
import { ApiRequestError } from "@/src/lib/http";
import {
  asociarRecursos,
  cambiarEstadoCampo,
  cambiarEstadoEspacio,
  crearCampo,
  detalleEspacio,
  impactoDeshabilitacionEspacio,
  reordenarCampos,
  retirarRecurso,
} from "@/src/lib/espacios-api";
import type { EspacioDetalle, TipoCampo } from "@/src/lib/espacios-types";

/** Detalle, estado, asociados y campos (WF-ESP-02, WF-ESP-03). */
export function EspacioDetalleClient({ puedeGestionar }: { puedeGestionar: boolean }) {
  const params = useParams();
  const router = useRouter();
  const id = Number(params.id);
  const [detalle, setDetalle] = useState<EspacioDetalle | null>(null);
  const [impacto, setImpacto] = useState<number | null>(null);
  const [recursoId, setRecursoId] = useState("");
  const [nombreCampo, setNombreCampo] = useState("");
  const [tipoCampo, setTipoCampo] = useState<TipoCampo>("TEXTO");
  const [opcion, setOpcion] = useState("");
  const [ocupada, setOcupada] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");

  async function recargar() {
    setDetalle(await detalleEspacio(id));
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

  async function agregarCampo(evento: FormEvent) {
    evento.preventDefault();
    setOcupada(true);
    try {
      await crearCampo(id, {
        nombre: nombreCampo,
        tipo: tipoCampo,
        ...(tipoCampo === "SELECCION" && opcion ? { opciones: [{ valor: opcion }] } : {}),
      });
      setNombreCampo("");
      setOpcion("");
      await recargar();
      informar("Campo creado.", "exito");
    } catch (error) {
      informar(mensajeError(error), "error");
    } finally {
      setOcupada(false);
    }
  }

  async function subir(campoId: number, orden: number) {
    if (orden === 0 || !detalle?.campos) return;
    setOcupada(true);
    try {
      const ordenada = [...detalle.campos].sort((a, b) => a.orden - b.orden);
      const anterior = ordenada[orden - 1];
      const actual = ordenada[orden];
      await reordenarCampos(id, [
        { campo_id: actual.id, orden: anterior.orden },
        { campo_id: anterior.id, orden: actual.orden },
      ]);
      await recargar();
      informar("Orden actualizado.", "exito");
    } catch {
      informar("No se pudo reordenar.", "error");
    } finally {
      setOcupada(false);
    }
  }

  async function alternarCampo(campoId: number, habilitado: boolean) {
    setOcupada(true);
    try {
      await cambiarEstadoCampo(id, campoId, !habilitado);
      await recargar();
      informar("Campo actualizado.", "exito");
    } catch (error) {
      informar(mensajeError(error), "error");
    } finally {
      setOcupada(false);
    }
  }

  if (!detalle) {
    return (
      <div className="flex flex-col gap-4">
        <h1 className="text-2xl font-bold text-text">Espacio</h1>
        <RegionMensaje texto={mensaje ?? "Cargando…"} tono={mensaje ? tono : "muted"} />
      </div>
    );
  }

  const campos = [...(detalle.campos ?? [])].sort((a, b) => a.orden - b.orden);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold text-text">{detalle.nombre}</h1>
        <p className="text-sm text-muted">
          Capacidad {detalle.capacidad} {!detalle.habilitado && "· deshabilitado"}
        </p>
        {detalle.horario_unidad && (
          <p className="text-sm text-muted">
            Horario de la unidad: {detalle.horario_unidad.hora_apertura} – {detalle.horario_unidad.hora_cierre}
          </p>
        )}
      </div>
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
            <Field id="asoc-recurso" label="Recurso (id)" value={recursoId}
              onChange={(e) => setRecursoId(e.target.value)} required />
            <Button type="submit" variant="secondary" loading={ocupada}>Asociar</Button>
          </form>
        )}
      </section>
      <section aria-label="Campos adicionales" className="flex flex-col gap-2">
        <h2 className="text-base font-bold text-text">Campos adicionales</h2>
        <ul className="flex flex-col gap-1 text-sm text-text">
          {campos.map((c, i) => (
            <li key={c.id} className="flex items-center gap-2">
              <span>{c.nombre} ({c.tipo}){c.obligatorio ? " *" : ""} {!c.habilitado && "(deshabilitado)"}</span>
              {puedeGestionar && (
                <>
                  <Button variant="ghost" size="sm" disabled={ocupada || i === 0}
                    onClick={() => void subir(c.id, i)}>Subir</Button>
                  <Button variant="ghost" size="sm" disabled={ocupada}
                    onClick={() => void alternarCampo(c.id, c.habilitado)}>
                    {c.habilitado ? "Deshabilitar" : "Habilitar"}
                  </Button>
                </>
              )}
            </li>
          ))}
        </ul>
        {puedeGestionar && (
          <form onSubmit={(e) => void agregarCampo(e)} className="flex flex-col gap-2">
            <Field id="campo-nombre" label="Nombre" value={nombreCampo}
              onChange={(e) => setNombreCampo(e.target.value)} required />
            <Select id="campo-tipo" label="Tipo" value={tipoCampo}
              onChange={(e) => setTipoCampo(e.target.value as TipoCampo)}>
              <option value="TEXTO">Texto</option>
              <option value="TEXTO_LARGO">Texto largo</option>
              <option value="NUMERO">Número</option>
              <option value="BOOLEANO">Sí / no</option>
              <option value="SELECCION">Lista de opciones</option>
            </Select>
            {tipoCampo === "SELECCION" && (
              <Field id="campo-opcion" label="Primera opción (obligatoria para listas)"
                value={opcion} onChange={(e) => setOpcion(e.target.value)} />
            )}
            <div>
              <Button type="submit" variant="secondary" loading={ocupada}>Agregar campo</Button>
            </div>
          </form>
        )}
      </section>
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
