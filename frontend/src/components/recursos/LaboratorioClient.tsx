"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import {
  CamposConfiguracion,
  CONFIG_INICIAL,
  cuerpoConfiguracion,
  desdeConfiguracion,
  errorConfiguracion,
  nombresDeDias,
  type ValoresConfig,
} from "@/src/components/recursos/CamposConfiguracion";
import { listarUnidades } from "@/src/lib/administracion-api";
import { ApiRequestError } from "@/src/lib/http";
import {
  configuracionLaboratorio,
  guardarConfiguracion,
  guardarTiposReserva,
  guardarVisibilidad,
} from "@/src/lib/recursos-api";
import type { ConfiguracionLaboratorio } from "@/src/lib/recursos-types";

// Catálogo fijo de tipos de reserva (reservations): se ofrecen por nombre, no por código.
const TIPOS_RESERVA: { codigo: string; nombre: string }[] = [
  { codigo: "ESPACIO", nombre: "Espacio" },
  { codigo: "RECURSO_INTERNO", nombre: "Recurso interno" },
  { codigo: "RECURSO_CAMPUS", nombre: "Recurso en campus" },
  { codigo: "RECURSO_EXTERNO", nombre: "Recurso fuera del campus" },
  { codigo: "LISTA_ESPERA", nombre: "Lista de espera" },
];

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
  const [valores, setValores] = useState<ValoresConfig>(CONFIG_INICIAL);
  const [tipos, setTipos] = useState<string[]>([]);
  const [sinConfig, setSinConfig] = useState(false);
  const [nombreUnidad, setNombreUnidad] = useState<string | null>(null);
  const [ocupada, setOcupada] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");

  async function recargar() {
    const c = await configuracionLaboratorio(idUnidad);
    setConfig(c);
    setValores(desdeConfiguracion(c));
    setTipos(c.tipos_reserva);
    setSinConfig(false);
  }

  useEffect(() => {
    let cancelado = false;
    recargar().catch((err) => {
      if (cancelado) return;
      if (err instanceof ApiRequestError && err.status === 401) {
        router.replace("/login?motivo=sesion_vencida");
        return;
      }
      // Un laboratorio nuevo no tiene configuración: se ofrece crearla (contrato §3.2, PATCH).
      if (err instanceof ApiRequestError && err.status === 404) {
        setSinConfig(true);
        return;
      }
      setMensaje("No se pudo cargar la configuración.");
      setTono("error");
    });
    listarUnidades()
      .then((r) => {
        if (!cancelado) setNombreUnidad(r.datos.find((u) => u.id_unidad === idUnidad)?.nombre ?? null);
      })
      .catch(() => {});
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
      const problema = errorConfiguracion(valores);
      if (problema) {
        informar(problema, "error");
        return;
      }
      const eraNueva = sinConfig;
      await guardarConfiguracion(idUnidad, cuerpoConfiguracion(valores));
      await recargar();
      informar(eraNueva ? "Laboratorio configurado. Ahora elige los tipos de reserva." : "Configuración guardada.", "exito");
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
      await guardarTiposReserva(idUnidad, tipos);
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

  const titulo = `Laboratorio${nombreUnidad ? ` ${nombreUnidad}` : ""}`;

  if (!config && sinConfig) {
    return (
      <div className="flex flex-col gap-4">
        <h1 className="text-2xl font-bold text-text">{titulo}</h1>
        <p className="text-sm text-text">Este laboratorio todavía no tiene configuración.</p>
        {puedeGestionar ? (
          <form onSubmit={(e) => void guardar(e)} className="flex flex-col gap-2">
            <CamposConfiguracion valores={valores} onChange={setValores} />
            <div>
              <Button type="submit" variant="primary" loading={ocupada}>Configurar laboratorio</Button>
            </div>
          </form>
        ) : (
          <p className="text-sm text-muted">Un administrador debe configurarlo antes de aceptar reservas.</p>
        )}
        <RegionMensaje texto={mensaje} tono={mensaje ? tono : "muted"} />
      </div>
    );
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
      <h1 className="text-2xl font-bold text-text">{titulo}</h1>
      <dl className="grid grid-cols-1 gap-1 text-sm text-text">
        <div className="flex gap-2"><dt className="font-bold">Acepta reservas:</dt><dd>{config.habilitado_reservas ? "sí" : "no"}</dd></div>
        <div className="flex gap-2"><dt className="font-bold">Horario:</dt><dd>{config.hora_apertura.slice(0, 5)} – {config.hora_cierre.slice(0, 5)} · {nombresDeDias(config.dias_atencion)}</dd></div>
        <div className="flex gap-2"><dt className="font-bold">Antelación mínima:</dt><dd>{config.horas_antelacion} h</dd></div>
        <div className="flex gap-2"><dt className="font-bold">Aprobación automática:</dt><dd>{config.aprobacion_automatica ? "sí" : "no"}</dd></div>
        <div className="flex gap-2"><dt className="font-bold">Recordatorio:</dt><dd>{config.recordatorio_horas_antes} h antes</dd></div>
        <div className="flex gap-2"><dt className="font-bold">Avisos por correo:</dt><dd>{config.notificar_por_correo ? "sí" : "no"}</dd></div>
        <div className="flex gap-2"><dt className="font-bold">Tipos:</dt><dd>{config.tipos_reserva.map((c) => TIPOS_RESERVA.find((t) => t.codigo === c)?.nombre ?? c).join(", ") || "ninguno"}</dd></div>
      </dl>
      {puedeGestionar && (
        <>
          <form onSubmit={(e) => void guardar(e)} className="flex flex-col gap-2">
            <CamposConfiguracion valores={valores} onChange={setValores} />
            <div>
              <Button type="submit" variant="secondary" loading={ocupada}>Guardar configuración</Button>
            </div>
          </form>
          <form onSubmit={(e) => void guardarTipos(e)} className="flex flex-col gap-2">
            <fieldset className="flex flex-col gap-1">
              <legend className="text-sm font-bold text-text">Tipos de reserva que ofrece</legend>
              {TIPOS_RESERVA.map((t) => (
                <label key={t.codigo} className="flex items-center gap-2 text-sm text-text">
                  <input type="checkbox" checked={tipos.includes(t.codigo)}
                    onChange={(e) =>
                      setTipos((prev) => (e.target.checked ? [...prev, t.codigo] : prev.filter((c) => c !== t.codigo)))
                    } />
                  {t.nombre}
                </label>
              ))}
            </fieldset>
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
