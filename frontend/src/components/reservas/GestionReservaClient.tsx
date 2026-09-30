"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { AdjuntosListaEspera } from "@/src/components/reservas/AdjuntosListaEspera";
import { EditarReservaPanel } from "@/src/components/reservas/EditarReservaPanel";
import { ListaEsperaPanel } from "@/src/components/reservas/ListaEsperaPanel";
import { OrdenSalidaPanel } from "@/src/components/reservas/OrdenSalidaPanel";
import { ResumenReserva } from "@/src/components/reservas/ResumenReserva";
import { SelectorRecursosVarios } from "@/src/components/selectores/SelectorRecursosVarios";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import type { ContextoSesion } from "@/src/lib/auth-types";
import { fechaHora } from "@/src/lib/formato";
import { ApiRequestError } from "@/src/lib/http";
import {
  aceptarPropuesta,
  agregarRecursos,
  aprobarReserva,
  cancelarReserva,
  crearPropuesta,
  detalleReserva,
  ejecutarReserva,
  finalizarReserva,
  rechazarPropuesta,
  rechazarReserva,
  retirarRecurso,
  urlCalendario,
} from "@/src/lib/reservas-api";
import type { VistaGestion } from "@/src/lib/reservas-acciones";
import { NOMBRE_ESTADO_RESERVA, NOMBRE_ROL_RECURSO, NOMBRE_TIPO_RESERVA } from "@/src/lib/reservas-nombres";
import type { ReservaDetalleRespuesta } from "@/src/lib/reservas-types";

/**
 * Detalle y gestión por tipo, estado y rol (WF-RES-02, WF-RES-03, WF-RES-04). La pantalla solo ofrece lo
 * que el actor puede hacer: el técnico de la unidad gestiona; el reservista ve lo suyo, responde propuestas,
 * completa su parte de la lista de espera y cancela. El backend sigue autorizando cada operación.
 */
export function GestionReservaClient({ sesion }: { sesion: ContextoSesion }) {
  const params = useParams();
  return <GestionReservaContenido id={Number(params.id)} sesion={sesion} />;
}

/**
 * El mismo contenido de gestión, reutilizable: en la página de detalle muestra todo (`vista="todo"`); en el
 * modal del listado (FE-33) muestra solo la parte de la acción elegida. `onCambio` avisa al listado para que
 * se actualice cuando una acción se completó.
 */
export function GestionReservaContenido({
  id,
  sesion,
  vista = "todo",
  enModal = false,
  onCambio,
}: {
  id: number;
  sesion: ContextoSesion;
  vista?: VistaGestion;
  enModal?: boolean;
  onCambio?: () => void;
}) {
  const router = useRouter();
  const ver = (v: VistaGestion) => vista === "todo" || vista === v;
  const [detalle, setDetalle] = useState<ReservaDetalleRespuesta | null>(null);
  const [motivoRechazo, setMotivoRechazo] = useState("");
  const [motivoPropuesta, setMotivoPropuesta] = useState("");
  const [motivoCancelacion, setMotivoCancelacion] = useState("");
  const [fechaProp, setFechaProp] = useState("");
  const [horaIniProp, setHoraIniProp] = useState("");
  const [horaFinProp, setHoraFinProp] = useState("");
  const [horasEjec, setHorasEjec] = useState("");
  const [nuevosRecursos, setNuevosRecursos] = useState<string[]>([]);
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
      setMensaje(
        err instanceof ApiRequestError && err.status === 404
          ? "La reserva no existe o no está a tu alcance."
          : "No se pudo cargar la reserva."
      );
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
      onCambio?.();
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
        <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Reserva</h1>
        <RegionMensaje texto={mensaje ?? "Cargando…"} tono={mensaje ? tono : "muted"} />
      </div>
    );
  }

  const { estado, tipo_reserva: tipo } = detalle;
  const esLista = tipo === "LISTA_ESPERA";
  const esEspacioInterno = tipo === "ESPACIO" || tipo === "RECURSO_INTERNO";
  const esPropietario = detalle.id_cuenta === sesion.id_cuenta;
  // El servidor decide con el permiso real; aquí solo se evita ofrecer lo que a este rol no le corresponde.
  const puedeGestionar =
    sesion.rol !== "USUARIO" &&
    (sesion.unidades_autorizadas === "GLOBAL" || sesion.unidades_autorizadas.includes(detalle.id_unidad));
  const propuesta = detalle.propuesta_vigente;
  // RN-PROP-03, RN-PROP-04: el reservista responde a la propuesta del técnico; solo el técnico responde a la contrapropuesta.
  const puedeResponderPropuesta =
    propuesta !== null && (propuesta.origen === "TECNICO" ? esPropietario : puedeGestionar);
  const puedeProponer = esEspacioInterno || tipo === "RECURSO_CAMPUS" || tipo === "RECURSO_EXTERNO";
  // RN-CAN-02: se cancela mientras no haya iniciado la ejecución.
  const puedeCancelar = (esPropietario || puedeGestionar) && (estado === "SOLICITADA" || estado === "APROBADA");

  return (
    <div className="flex flex-col gap-6">
      {!enModal && (
        <div>
          <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Reserva #{detalle.id}</h1>
          <p className="text-sm text-muted">
            {NOMBRE_TIPO_RESERVA[tipo] ?? tipo} · {NOMBRE_ESTADO_RESERVA[estado] ?? estado}
          </p>
        </div>
      )}

      <ResumenReserva detalle={detalle} />

      {esPropietario && estado === "SOLICITADA" && ver("editar") && (
        <EditarReservaPanel detalle={detalle} ocupada={ocupada} actuar={actuar} />
      )}

      {/* RN-CAL-01: el calendario solo existe para espacio e interno aprobados. */}
      {vista === "todo" && esEspacioInterno && estado === "APROBADA" && (
        <a href={urlCalendario(id)} className="text-sm font-bold text-primary-2">
          Agregar al calendario (.ics)
        </a>
      )}

      {vista === "todo" && (tipo === "RECURSO_CAMPUS" || tipo === "RECURSO_EXTERNO") &&
        ["APROBADA", "EN_EJECUCION", "FINALIZADA"].includes(estado) && <OrdenSalidaPanel idReserva={id} />}

      {puedeGestionar && estado === "SOLICITADA" && ver("revision") && (
        <section aria-label="Revisión" className="flex flex-col gap-2">
          <h2 className="text-base font-bold text-text">Revisión</h2>
          {!esLista && (
            <div className="flex gap-2">
              <Button variant="success" size="sm" disabled={ocupada}
                onClick={() => void actuar(() => aprobarReserva(id), "Reserva aprobada.")}>
                Aprobar
              </Button>
            </div>
          )}
          <form
            onSubmit={(e: FormEvent) => {
              e.preventDefault();
              void actuar(() => rechazarReserva(id, motivoRechazo), "Reserva rechazada.");
            }}
            className="grid grid-cols-[1fr_auto] items-end gap-3"
          >
            <Field id="rechazo-motivo" label="Motivo del rechazo" value={motivoRechazo}
              onChange={(e) => setMotivoRechazo(e.target.value)} required />
            <Button type="submit" variant="danger" size="sm" loading={ocupada}>Rechazar</Button>
          </form>
        </section>
      )}

      {esLista && ver("lista") && (
        <ListaEsperaPanel detalle={detalle} esPropietario={esPropietario} puedeGestionar={puedeGestionar}
          ocupada={ocupada} actuar={actuar} />
      )}
      {esLista && ver("lista") && <AdjuntosListaEspera idReserva={id} puedeSubir={esPropietario && estado === "SOLICITADA"} />}

      {ver("propuestas") && (estado === "SOLICITADA" || estado === "APROBADA") && puedeProponer &&
        (propuesta !== null || puedeGestionar || esPropietario) && (
        <section aria-label="Propuestas" className="flex flex-col gap-2">
          <h2 className="text-base font-bold text-text">Propuestas de periodo</h2>
          {propuesta ? (
            <div className="flex flex-col gap-2 text-sm text-text">
              <p>
                Propuesta vigente de {propuesta.origen === "TECNICO" ? "el técnico" : "el reservista"}: {propuesta.motivo}
              </p>
              {puedeResponderPropuesta ? (
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
              ) : (
                <p className="text-muted">Esperando la respuesta de {propuesta.origen === "TECNICO" ? "el reservista" : "el técnico"}.</p>
              )}
            </div>
          ) : null}
          {(puedeGestionar && !propuesta) || (esPropietario && propuesta?.origen === "TECNICO") ? (
            <form
              onSubmit={(e: FormEvent) => {
                e.preventDefault();
                void actuar(
                  () => crearPropuesta(id, {
                    fecha_inicio_propuesta: fechaProp,
                    fecha_fin_propuesta: fechaProp,
                    ...(horaIniProp ? { hora_inicio: horaIniProp } : {}),
                    ...(horaFinProp ? { hora_fin: horaFinProp } : {}),
                    motivo: motivoPropuesta,
                  }),
                  propuesta ? "Contrapropuesta registrada." : "Propuesta registrada."
                );
              }}
              className="flex flex-col gap-2"
            >
              <h3 className="text-sm font-bold text-text">{propuesta ? "Contraproponer otro periodo" : "Proponer otro periodo"}</h3>
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
              <Field id="prop-motivo" label="Motivo" value={motivoPropuesta}
                onChange={(e) => setMotivoPropuesta(e.target.value)} required />
              <div>
                <Button type="submit" variant="secondary" size="sm" loading={ocupada}>
                  {propuesta ? "Enviar contrapropuesta" : "Proponer periodo"}
                </Button>
              </div>
            </form>
          ) : null}
        </section>
      )}

      {ver("ejecucion") && puedeGestionar && estado === "APROBADA" && !esEspacioInterno && !esLista && (
        <section aria-label="Ejecución" className="flex flex-col gap-2">
          <h2 className="text-base font-bold text-text">Ejecución</h2>
          <div>
            <Button variant="primary" size="sm" disabled={ocupada}
              onClick={() => void actuar(
                () => ejecutarReserva(id, detalle.recursos.map((r) => ({ reserva_recurso_id: r.reserva_recurso_id }))),
                "Reserva en ejecución."
              )}>
              Registrar entrega e iniciar ejecución
            </Button>
          </div>
        </section>
      )}

      {ver("ejecucion") && puedeGestionar && esLista && estado === "APROBADA" && (
        <section aria-label="Ejecución" className="flex flex-col gap-2">
          <h2 className="text-base font-bold text-text">Ejecución</h2>
          <div>
            <Button variant="primary" size="sm" disabled={ocupada}
              onClick={() => void actuar(() => ejecutarReserva(id), "Reserva en ejecución.")}>
              Iniciar fabricación o prestación
            </Button>
          </div>
        </section>
      )}

      {ver("finalizacion") && puedeGestionar && estado === "EN_EJECUCION" && !esEspacioInterno && (
        <section aria-label="Finalización" className="flex flex-col gap-2">
          <h2 className="text-base font-bold text-text">Finalización</h2>
          {esLista ? (
            <form
              onSubmit={(e: FormEvent) => {
                e.preventDefault();
                void actuar(() => finalizarReserva(id, { horas_ejecucion: Number(horasEjec) }), "Reserva finalizada.");
              }}
              className="grid grid-cols-[1fr_auto] items-end gap-3"
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
              Registrar devolución completa y finalizar
            </Button>
          )}
        </section>
      )}

      {ver("cancelacion") && puedeCancelar && (
        <section aria-label="Cancelación" className="flex flex-col gap-2">
          <Field id="cancel-motivo" label="Motivo de la cancelación (opcional)" value={motivoCancelacion}
            onChange={(e) => setMotivoCancelacion(e.target.value)} />
          <div>
            <Button variant="danger" size="sm" disabled={ocupada}
              onClick={() => void actuar(
                () => cancelarReserva(id, motivoCancelacion || undefined), "Reserva cancelada."
              )}>
              Cancelar reserva
            </Button>
          </div>
        </section>
      )}

      {ver("recursos") && detalle.recursos.length > 0 && (
        <section aria-label="Recursos" className="flex flex-col gap-2">
          <h2 className="text-base font-bold text-text">Recursos</h2>
          <ul className="flex flex-col gap-1 text-sm text-text">
            {detalle.recursos.map((r) => (
              <li key={r.reserva_recurso_id} className="flex items-center gap-2">
                <span>
                  {r.nombre ?? "Recurso sin nombre"} · {NOMBRE_ROL_RECURSO[r.rol] ?? r.rol}
                  {r.estado_asignacion !== "ASIGNADO" && ` · ${ESTADO_ASIGNACION[r.estado_asignacion] ?? r.estado_asignacion}`}
                </span>
                {puedeGestionar && esEspacioInterno && r.estado_asignacion !== "RETIRADO" &&
                  /* RN-TIP-RI-10: el principal de un recurso interno no se retira. */
                  !(tipo === "RECURSO_INTERNO" && r.rol === "PRINCIPAL") && (
                  <Button variant="ghost" size="sm" disabled={ocupada}
                    onClick={() => void actuar(() => retirarRecurso(id, r.reserva_recurso_id), "Recurso retirado.")}>
                    Retirar
                  </Button>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}

      {ver("recursos") && puedeGestionar && esEspacioInterno && ["SOLICITADA", "APROBADA", "EN_EJECUCION"].includes(estado) && (
        <section aria-label="Agregar recursos" className="flex flex-col gap-2">
          <SelectorRecursosVarios
            label="Agregar recursos a la reserva"
            idUnidad={String(detalle.id_unidad)}
            excluir={detalle.recursos.filter((r) => r.estado_asignacion !== "RETIRADO").map((r) => String(r.recurso_id))}
            value={nuevosRecursos}
            onChange={setNuevosRecursos}
          />
          <div>
            <Button variant="secondary" size="sm" disabled={ocupada || nuevosRecursos.length === 0}
              onClick={() => void actuar(
                () => agregarRecursos(id, nuevosRecursos.map((n) => ({ recurso_id: Number(n), rol: "ADICIONAL" as const }))),
                "Recursos agregados."
              ).then(() => setNuevosRecursos([]))}>
              Agregar
            </Button>
          </div>
        </section>
      )}

      {vista === "todo" && (
      <section aria-label="Historial" className="flex flex-col gap-1">
        <h2 className="text-base font-bold text-text">Historial</h2>
        <ul className="text-sm text-muted">
          {detalle.historial.map((h, i) => (
            <li key={i}>
              {fechaHora(h.created_at)} · {h.estado_anterior ? `${NOMBRE_ESTADO_RESERVA[h.estado_anterior] ?? h.estado_anterior} → ` : ""}
              {NOMBRE_ESTADO_RESERVA[h.estado_nuevo] ?? h.estado_nuevo}
              {h.actor_nombre ? ` · ${h.actor_nombre}` : ""}{h.motivo ? ` (${h.motivo})` : ""}
            </li>
          ))}
        </ul>
      </section>
      )}

      <RegionMensaje texto={mensaje} tono={mensaje ? tono : "muted"} />
    </div>
  );
}

const ESTADO_ASIGNACION: Record<string, string> = { NO_DISPONIBLE: "no disponible", RETIRADO: "retirado" };

function mensajeError(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.error.codigo === "ESTADO_INCOMPATIBLE") return "La reserva ya no está en un estado válido para esta acción.";
    if (error.error.codigo === "TIPO_NO_ADMITIDO") return "Esta acción no aplica a este tipo de reserva.";
    if (error.error.codigo === "SOLAPAMIENTO") return "El periodo propuesto ya no está disponible.";
    if (error.status === 429) return "La operación está temporalmente limitada.";
    // Los 403, 409 y 422 restantes traen un mensaje pensado para la persona (p. ej. qué falta para aprobar).
    if (error.error.mensaje && [403, 404, 409, 422].includes(error.status)) return error.error.mensaje;
  }
  return "No se pudo completar la operación.";
}
