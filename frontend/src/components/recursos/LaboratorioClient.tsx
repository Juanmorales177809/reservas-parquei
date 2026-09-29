"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { ApiRequestError } from "@/src/lib/http";
import {
  configuracionLaboratorio,
  guardarConfiguracion,
  guardarTiposReserva,
  guardarVisibilidad,
} from "@/src/lib/recursos-api";
import type { ConfiguracionLaboratorio } from "@/src/lib/recursos-types";

/** Configuración del laboratorio (WF-REC-03). */
export function LaboratorioClient({
  idUnidad,
  puedeGestionar,
}: {
  idUnidad: number;
  puedeGestionar: boolean;
}) {
  const router = useRouter();
  const [config, setConfig] = useState<ConfiguracionLaboratorio | null>(null);
  const [horaApertura, setHoraApertura] = useState("");
  const [horaCierre, setHoraCierre] = useState("");
  const [tipos, setTipos] = useState("");
  const [ocupada, setOcupada] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");

  async function recargar() {
    const c = await configuracionLaboratorio(idUnidad);
    setConfig(c);
    setHoraApertura(c.hora_apertura);
    setHoraCierre(c.hora_cierre);
    setTipos(c.tipos_reserva.join(", "));
  }

  useEffect(() => {
    let cancelado = false;
    recargar().catch((err) => {
      if (cancelado) return;
      if (err instanceof ApiRequestError && err.status === 401) {
        router.replace("/login?motivo=sesion_vencida");
        return;
      }
      setMensaje("No se pudo cargar la configuración.");
      setTono("error");
    });
    return () => {
      cancelado = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router, idUnidad]);

  function informar(texto: string, t: "error" | "exito") {
    setMensaje(texto);
    setTono(t);
  }

  async function guardar(evento: FormEvent) {
    evento.preventDefault();
    setOcupada(true);
    try {
      await guardarConfiguracion(idUnidad, { hora_apertura: horaApertura, hora_cierre: horaCierre });
      await recargar();
      informar("Configuración guardada.", "exito");
    } catch (error) {
      informar(mensajeError(error), "error");
    } finally {
      setOcupada(false);
    }
  }

  async function guardarTipos(evento: FormEvent) {
    evento.preventDefault();
    setOcupada(true);
    try {
      await guardarTiposReserva(
        idUnidad,
        tipos.split(",").map((t) => t.trim()).filter(Boolean)
      );
      await recargar();
      informar("Tipos guardados.", "exito");
    } catch (error) {
      informar(mensajeError(error), "error");
    } finally {
      setOcupada(false);
    }
  }

  async function alternarVisibilidad(campo: "mostrar_estado_reserva" | "mostrar_reservista") {
    if (!config) return;
    setOcupada(true);
    try {
      await guardarVisibilidad(idUnidad, {
        mostrar_estado_reserva: campo === "mostrar_estado_reserva" ? !config.mostrar_estado_reserva : config.mostrar_estado_reserva,
        mostrar_reservista: campo === "mostrar_reservista" ? !config.mostrar_reservista : config.mostrar_reservista,
      });
      await recargar();
      informar("Visibilidad actualizada.", "exito");
    } catch (error) {
      informar(mensajeError(error), "error");
    } finally {
      setOcupada(false);
    }
  }

  if (!config) {
    return (
      <div className="flex flex-col gap-4">
        <h1 className="text-2xl font-bold text-text">Laboratorio</h1>
        <RegionMensaje texto={mensaje ?? "Cargando configuración…"} tono={mensaje ? tono : "muted"} />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-text">Laboratorio {config.id_unidad}</h1>
      <dl className="grid grid-cols-1 gap-1 text-sm text-text">
        <div className="flex gap-2"><dt className="font-bold">Acepta reservas:</dt><dd>{config.habilitado_reservas ? "sí" : "no"}</dd></div>
        <div className="flex gap-2"><dt className="font-bold">Horario:</dt><dd>{config.hora_apertura} – {config.hora_cierre}</dd></div>
        <div className="flex gap-2"><dt className="font-bold">Tipos:</dt><dd>{config.tipos_reserva.join(", ") || "ninguno"}</dd></div>
      </dl>
      {puedeGestionar && (
        <>
          <form onSubmit={(e) => void guardar(e)} className="flex flex-col gap-2">
            <div className="flex gap-2">
              <Field id="lab-apertura" label="Apertura" value={horaApertura}
                onChange={(e) => setHoraApertura(e.target.value)} required />
              <Field id="lab-cierre" label="Cierre" value={horaCierre}
                onChange={(e) => setHoraCierre(e.target.value)} required />
            </div>
            <div>
              <Button type="submit" variant="secondary" loading={ocupada}>Guardar horario</Button>
            </div>
          </form>
          <form onSubmit={(e) => void guardarTipos(e)} className="flex flex-col gap-2">
            <Field id="lab-tipos" label="Tipos (separados por coma)" value={tipos}
              onChange={(e) => setTipos(e.target.value)} />
            <div>
              <Button type="submit" variant="secondary" loading={ocupada}>Guardar tipos</Button>
            </div>
          </form>
          <div className="flex gap-2">
            <Button variant="ghost" size="sm" disabled={ocupada}
              onClick={() => void alternarVisibilidad("mostrar_estado_reserva")}>
              {config.mostrar_estado_reserva ? "Ocultar estado" : "Mostrar estado"}
            </Button>
            <Button variant="ghost" size="sm" disabled={ocupada}
              onClick={() => void alternarVisibilidad("mostrar_reservista")}>
              {config.mostrar_reservista ? "Ocultar reservista" : "Mostrar reservista"}
            </Button>
          </div>
        </>
      )}
      <RegionMensaje texto={mensaje} tono={mensaje ? tono : "muted"} />
    </div>
  );
}

function mensajeError(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.error.codigo === "VALIDACION") return "Revisa los valores ingresados.";
    if (error.status === 429) return "La operación está temporalmente limitada.";
  }
  return "No se pudo completar la operación.";
}
