"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { ApiRequestError } from "@/src/lib/http";
import {
  aceptarPropuesta,
  aprobarReserva,
  cancelarReserva,
  crearPropuesta,
  detalleReserva,
  ejecutarReserva,
  finalizarReserva,
  rechazarPropuesta,
  rechazarReserva,
  registrarViabilidad,
  retirarRecurso,
} from "@/src/lib/reservas-api";import type { ReservaDetalleRespuesta } from "@/src/lib/reservas-types";

/** Detalle y gestión por tipo y estado (WF-RES-02, WF-RES-03, WF-RES-04). */
export function GestionReservaClient() {
  const params = useParams();
  const router = useRouter();
  const id = Number(params.id);
  const [detalle, setDetalle] = useState<ReservaDetalleRespuesta | null>(null);
  const [motivo, setMotivo] = useState("");
  const [fechaProp, setFechaProp] = useState("");
  const [horaIniProp, setHoraIniProp] = useState("");
  const [horaFinProp, setHoraFinProp] = useState("");
  const [horasEjec, setHorasEjec] = useState("");
  const [ocupada, setOcupada] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");

  async function recargar() {
    setDetalle(await detalleReserva(id));
  }

  useEffect(() => {
    let cancelado = false;
    recargar().catch((err) => {
      if (cancelado) return;
      if (err instanceof ApiRequestError && err.status === 401) {
        router.replace("/login?motivo=sesion_vencida");
        return;
      }
      setMensaje("No se pudo cargar la reserva.");
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

  if (!detalle) {
    return (
      <div className="flex flex-col gap-4">
        <h1 className="text-2xl font-bold text-text">Reserva</h1>
        <RegionMensaje texto={mensaje ?? "Cargando…"} tono={mensaje ? tono : "muted"} />
      </div>
    );
  }

  const esTecnico = true; // El backend autoriza cada acción; la UI ofrece todas las válidas por estado.
  const { estado, tipo_reserva: tipo } = detalle;
  const esLista = tipo === "LISTA_ESPERA";
  const esEspacioInterno = tipo === "ESPACIO" || tipo === "RECURSO_INTERNO";

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold text-text">Reserva #{detalle.id}</h1>
        <p className="text-sm text-muted">{tipo} · {estado}</p>
        {detalle.observacion && <p className="text-sm text-text">{detalle.observacion}</p>}
      </div>

      {esTecnico && estado === "SOLICITADA" && (
        <section aria-label="Revisión" className="flex flex-col gap-2">
          <h2 className="text-base font-bold text-text">Revisión</h2>
          <div className="flex gap-2">
            <Button variant="success" size="sm" disabled={ocupada}
              onClick={() => void actuar(() => aprobarReserva(id), "Reserva aprobada.")}>
              Aprobar
            </Button>
          </div>
          <form
            onSubmit={(e: FormEvent) => {
              e.preventDefault();
              void actuar(() => rechazarReserva(id, motivo), "Reserva rechazada.");
            }}
            className="flex items-end gap-2"
          >
            <Field id="rechazo-motivo" label="Motivo del rechazo" value={motivo}
              onChange={(e) => setMotivo(e.target.value)} required />
            <Button type="submit" variant="danger" size="sm" loading={ocupada}>Rechazar</Button>
          </form>
        </section>
      )}

      {esTecnico && (estado === "SOLICITADA" || estado === "APROBADA") && !esLista && (
        <section aria-label="Propuestas" className="flex flex-col gap-2">
          <h2 className="text-base font-bold text-text">Propuestas de periodo</h2>
          {detalle.propuesta_vigente ? (
            <div className="flex flex-col gap-2 text-sm text-text">
              <p>Vigente ({detalle.propuesta_vigente.origen}): {detalle.propuesta_vigente.motivo}</p>
              <div className="flex gap-2">
                <Button variant="success" size="sm" disabled={ocupada}
                  onClick={() => void actuar(() => aceptarPropuesta(id), "Propuesta aceptada.")}>
                  Aceptar
                </Button>
                <Button variant="ghost" size="sm" disabled={ocupada}
                  onClick={() => void actuar(() => rechazarPropuesta(id), "Propuesta rechazada.")}>
                  Rechazar
                </Button>
              </div>
            </div>
          ) : (
            <form
              onSubmit={(e: FormEvent) => {
                e.preventDefault();
                void actuar(
                  () => crearPropuesta(id, {
                    fecha_inicio_propuesta: fechaProp,
                    fecha_fin_propuesta: fechaProp,
                    ...(horaIniProp ? { hora_inicio: horaIniProp } : {}),
                    ...(horaFinProp ? { hora_fin: horaFinProp } : {}),
                    motivo,
                  }),
                  "Propuesta registrada."
                );
              }}
              className="flex flex-col gap-2"
            >
              <div className="flex gap-2">
                <Field id="prop-fecha" label="Fecha" type="date" value={fechaProp}
                  onChange={(e) => setFechaProp(e.target.value)} required />
              </div>
              {esEspacioInterno && (
                <div className="flex gap-2">
                  <Field id="prop-hi" label="Hora inicio" type="time" value={horaIniProp}
                    onChange={(e) => setHoraIniProp(e.target.value)} />
                  <Field id="prop-hf" label="Hora fin" type="time" value={horaFinProp}
                    onChange={(e) => setHoraFinProp(e.target.value)} />
                </div>
              )}
              <Field id="prop-motivo" label="Motivo" value={motivo}
                onChange={(e) => setMotivo(e.target.value)} required />
              <div>
                <Button type="submit" variant="secondary" size="sm" loading={ocupada}>
                  Proponer periodo
                </Button>
              </div>
            </form>
          )}
        </section>
      )}

      {esTecnico && estado === "APROBADA" && !esEspacioInterno && !esLista && (
        <section aria-label="Ejecución" className="flex flex-col gap-2">
          <h2 className="text-base font-bold text-text">Ejecución</h2>
          <div>
            <Button variant="primary" size="sm" disabled={ocupada}
              onClick={() => void actuar(
                () => ejecutarReserva(id, detalle.recursos.map((r) => ({ reserva_recurso_id: r.reserva_recurso_id }))),
                "Reserva en ejecución."
              )}>
              Iniciar ejecución
            </Button>
          </div>
        </section>
      )}

      {esTecnico && estado === "EN_EJECUCION" && !esEspacioInterno && (
        <section aria-label="Finalización" className="flex flex-col gap-2">
          <h2 className="text-base font-bold text-text">Finalización</h2>
          {esLista ? (
            <form
              onSubmit={(e: FormEvent) => {
                e.preventDefault();
                void actuar(() => finalizarReserva(id, { horas_ejecucion: Number(horasEjec) }), "Reserva finalizada.");
              }}
              className="flex items-end gap-2"
            >
              <Field id="fin-horas" label="Horas de ejecución" type="number" value={horasEjec}
                onChange={(e) => setHorasEjec(e.target.value)} required />
              <Button type="submit" variant="success" size="sm" loading={ocupada}>Finalizar</Button>
            </form>
          ) : (
            <Button variant="success" size="sm" disabled={ocupada}
              onClick={() => void actuar(
                () => finalizarReserva(id, {
                  recursos: detalle.recursos.map((r) => ({ reserva_recurso_id: r.reserva_recurso_id })),
                }),
                "Reserva finalizada."
              )}>
              Finalizar con devolución completa
            </Button>
          )}
        </section>
      )}

      {esTecnico && (estado === "SOLICITADA" || estado === "APROBADA") && (
        <section aria-label="Cancelación" className="flex flex-col gap-2">
          <div>
            <Button variant="danger" size="sm" disabled={ocupada}
              onClick={() => void actuar(
                () => cancelarReserva(id, motivo || undefined), "Reserva cancelada."
              )}>
              Cancelar reserva
            </Button>
          </div>
        </section>
      )}

      {esTecnico && esLista && estado === "SOLICITADA" && (
        <section aria-label="Viabilidad" className="flex flex-col gap-2">
          <h2 className="text-base font-bold text-text">Viabilidad</h2>
          <div className="flex gap-2">
            <Button variant="success" size="sm" disabled={ocupada}
              onClick={() => void actuar(() => registrarViabilidad(id, true), "Viabilidad registrada.")}>
              Viable
            </Button>
            <Button variant="danger" size="sm" disabled={ocupada}
              onClick={() => void actuar(
                () => registrarViabilidad(id, false, motivo || "Sin motivo"), "No viable."
              )}>
              No viable
            </Button>
          </div>
        </section>
      )}

      {esTecnico && (tipo === "ESPACIO" || tipo === "RECURSO_INTERNO") && (
        <section aria-label="Recursos" className="flex flex-col gap-2">
          <h2 className="text-base font-bold text-text">Recursos asignados</h2>
          <ul className="flex flex-col gap-1 text-sm text-text">
            {detalle.recursos.map((r) => (
              <li key={r.recurso_id} className="flex items-center gap-2">
                <span>Recurso {r.recurso_id} ({r.rol}, {r.estado_asignacion})</span>
                <Button variant="ghost" size="sm" disabled={ocupada}
                  onClick={() => void actuar(() => retirarRecurso(id, r.reserva_recurso_id), "Recurso retirado.")}>
                  Retirar
                </Button>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section aria-label="Historial" className="flex flex-col gap-1">
        <h2 className="text-base font-bold text-text">Historial</h2>
        <ul className="text-sm text-muted">
          {detalle.historial.map((h, i) => (
            <li key={i}>
              {h.estado_anterior ?? "—"} → {h.estado_nuevo}{h.motivo ? ` (${h.motivo})` : ""}
            </li>
          ))}
        </ul>
      </section>

      <RegionMensaje texto={mensaje} tono={mensaje ? tono : "muted"} />
    </div>
  );
}

function mensajeError(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.error.codigo === "ESTADO_INCOMPATIBLE") return "La reserva ya no está en un estado válido para esta acción.";
    if (error.error.codigo === "TIPO_NO_ADMITIDO") return "Esta acción no aplica a este tipo de reserva.";
    if (error.error.codigo === "SOLAPAMIENTO") return "El periodo propuesto ya no está disponible.";
    if (error.error.codigo === "VALIDACION") return "Revisa los datos ingresados.";
    if (error.status === 429) return "La operación está temporalmente limitada.";
  }
  return "No se pudo completar la operación.";
}
