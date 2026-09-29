"use client";

import { useState } from "react";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { fechaHora } from "@/src/lib/formato";
import { aprobarReserva, diligenciarFormulario, registrarViabilidad } from "@/src/lib/reservas-api";
import type { ReservaDetalleRespuesta } from "@/src/lib/reservas-types";

type Fila = { campo: string; valor: string };

const aFilas = (datos: Record<string, unknown> | null | undefined): Fila[] =>
  Object.entries(datos ?? {}).map(([campo, valor]) => ({ campo, valor: String(valor ?? "") }));

/** Editor de una parte del formulario: pares campo/valor (el contrato no fija un catálogo de campos). */
function EditorParte({
  titulo, datos, editable, ocupada, avisoAlGuardar, onGuardar,
}: {
  titulo: string;
  datos: Record<string, unknown> | null | undefined;
  editable: boolean;
  ocupada: boolean;
  avisoAlGuardar?: string;
  onGuardar: (datos: Record<string, string>) => void;
}) {
  const [filas, setFilas] = useState<Fila[]>(() => {
    const previas = aFilas(datos);
    return previas.length > 0 ? previas : [{ campo: "", valor: "" }];
  });
  const validas = filas.filter((f) => f.campo.trim() !== "");

  if (!editable) {
    const previas = aFilas(datos);
    return (
      <div className="flex flex-col gap-1 text-sm text-text">
        <h3 className="font-bold">{titulo}</h3>
        {previas.length === 0 ? (
          <p className="text-muted">Todavía no se ha diligenciado.</p>
        ) : (
          <dl className="grid grid-cols-[max-content_1fr] gap-x-3">
            {previas.map((f) => (
              <div key={f.campo} className="contents">
                <dt className="font-bold">{f.campo}</dt>
                <dd>{f.valor}</dd>
              </div>
            ))}
          </dl>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-2">
      <h3 className="text-sm font-bold text-text">{titulo}</h3>
      {filas.map((f, i) => (
        <div key={i} className="flex items-end gap-2">
          <Field id={`${titulo}-campo-${i}`} label="Campo" value={f.campo}
            onChange={(e) => setFilas(filas.map((x, j) => (j === i ? { ...x, campo: e.target.value } : x)))} />
          <Field id={`${titulo}-valor-${i}`} label="Valor" value={f.valor}
            onChange={(e) => setFilas(filas.map((x, j) => (j === i ? { ...x, valor: e.target.value } : x)))} />
          {filas.length > 1 && (
            <Button variant="ghost" size="sm" onClick={() => setFilas(filas.filter((_, j) => j !== i))}>Quitar</Button>
          )}
        </div>
      ))}
      <div className="flex gap-2">
        <Button variant="ghost" size="sm" onClick={() => setFilas([...filas, { campo: "", valor: "" }])}>
          Agregar campo
        </Button>
        <Button variant="secondary" size="sm" disabled={ocupada || validas.length === 0}
          onClick={() => onGuardar(Object.fromEntries(validas.map((f) => [f.campo.trim(), f.valor.trim()])))}>
          Guardar {titulo.toLowerCase()}
        </Button>
      </div>
      {avisoAlGuardar && <p className="text-sm text-muted">{avisoAlGuardar}</p>}
    </div>
  );
}

/**
 * Lista de espera (WF-RES-03): viabilidad, formulario por partes y aprobación con recepción de material.
 * Cada actor toca solo lo suyo: el técnico evalúa, completa su parte y aprueba; el reservista diligencia la suya.
 */
export function ListaEsperaPanel({
  detalle, esPropietario, puedeGestionar, ocupada, actuar,
}: {
  detalle: ReservaDetalleRespuesta;
  esPropietario: boolean;
  puedeGestionar: boolean;
  ocupada: boolean;
  actuar: (accion: () => Promise<unknown>, exito: string) => Promise<void>;
}) {
  const [motivoNoViable, setMotivoNoViable] = useState("");
  const [materialRecibido, setMaterialRecibido] = useState(false);
  const [observacion, setObservacion] = useState("");
  const id = detalle.id;
  const le = detalle.lista_espera;
  const solicitada = detalle.estado === "SOLICITADA";
  const viable = le?.viable ?? null;
  const formulario = le?.formulario ?? null;
  const parteUsuario = formulario?.datos_usuario ?? null;
  const parteTecnica = formulario?.datos_tecnico ?? null;
  const revisada = Boolean(formulario?.revisado_at);
  const listaParaAprobar = viable === true && Boolean(parteUsuario) && Boolean(parteTecnica) && revisada;

  return (
    <section aria-label="Lista de espera" className="flex flex-col gap-4">
      <h2 className="text-base font-bold text-text">Lista de espera</h2>

      <div className="flex flex-col gap-1 text-sm text-text">
        <h3 className="font-bold">Viabilidad</h3>
        {viable === null && <p className="text-muted">Pendiente de evaluación del técnico.</p>}
        {viable === true && (
          <p>Viable{le?.fecha_evaluacion_viabilidad ? ` · evaluada el ${fechaHora(le.fecha_evaluacion_viabilidad)}` : ""}.</p>
        )}
        {viable === false && <p>No viable.</p>}
        {puedeGestionar && solicitada && viable === null && (
          <div className="flex flex-col gap-2">
            <div className="flex flex-wrap items-end gap-2">
              <Button variant="success" size="sm" disabled={ocupada}
                onClick={() => void actuar(() => registrarViabilidad(id, true), "Viabilidad registrada.")}>
                Es viable
              </Button>
            </div>
            <div className="flex flex-wrap items-end gap-2">
              <Field id="viab-motivo" label="Motivo si no es viable" value={motivoNoViable}
                onChange={(e) => setMotivoNoViable(e.target.value)} />
              <Button variant="danger" size="sm" disabled={ocupada || motivoNoViable.trim() === ""}
                onClick={() => void actuar(() => registrarViabilidad(id, false, motivoNoViable.trim()), "Se registró que no es viable y la reserva quedó rechazada.")}>
                No es viable
              </Button>
            </div>
            <p className="text-muted">Si no es viable, la reserva se rechaza y se conserva lo que ya se cargó.</p>
          </div>
        )}
      </div>

      {viable === true && solicitada && (
        <div className="flex flex-col gap-4">
          <h3 className="text-sm font-bold text-text">Formulario técnico</h3>
          <EditorParte
            titulo="Parte del reservista"
            datos={parteUsuario}
            editable={esPropietario}
            ocupada={ocupada}
            avisoAlGuardar={revisada ? "Si la cambias, el técnico tendrá que revisarla y completar su parte de nuevo." : undefined}
            onGuardar={(datos) => void actuar(() => diligenciarFormulario(id, { datos_usuario: datos }), "Tu parte del formulario quedó guardada.")}
          />
          {parteUsuario || puedeGestionar ? (
            <EditorParte
              titulo="Parte técnica"
              datos={parteTecnica}
              editable={puedeGestionar && Boolean(parteUsuario)}
              ocupada={ocupada}
              onGuardar={(datos) => void actuar(() => diligenciarFormulario(id, { datos_tecnico: datos }), "La parte técnica quedó guardada.")}
            />
          ) : null}
          {puedeGestionar && !parteUsuario && (
            <p className="text-sm text-muted">La parte técnica se completa cuando el reservista diligencie la suya.</p>
          )}
          {revisada && formulario?.revisado_at && (
            <p className="text-sm text-muted">Revisado por el técnico el {fechaHora(formulario.revisado_at)}.</p>
          )}
        </div>
      )}

      {puedeGestionar && solicitada && (
        <div className="flex flex-col gap-2">
          <h3 className="text-sm font-bold text-text">Aprobación</h3>
          <p className="text-sm text-muted">
            Aprobar registra la recepción del material. Requiere viabilidad positiva y el formulario completo y revisado.
          </p>
          <label className="flex items-center gap-2 text-sm text-text">
            <input type="checkbox" checked={materialRecibido} onChange={(e) => setMaterialRecibido(e.target.checked)} />
            Confirmo que el material fue recibido
          </label>
          <Field id="apr-observacion" label="Observación (opcional)" value={observacion}
            onChange={(e) => setObservacion(e.target.value)} />
          <div>
            <Button variant="success" size="sm" disabled={ocupada || !materialRecibido || !listaParaAprobar}
              onClick={() => void actuar(
                () => aprobarReserva(id, { material_recibido: true, ...(observacion ? { observacion } : {}) }),
                "Reserva aprobada y material recibido."
              )}>
              Registrar recepción y aprobar
            </Button>
          </div>
          {!listaParaAprobar && (
            <p className="text-sm text-muted">
              Falta: {[
                viable !== true && "la viabilidad positiva",
                viable === true && !parteUsuario && "la parte del reservista",
                viable === true && parteUsuario && !parteTecnica && "la parte técnica",
                viable === true && parteUsuario && parteTecnica && !revisada && "la revisión técnica vigente",
              ].filter(Boolean).join(", ")}.
            </p>
          )}
        </div>
      )}

      {le?.fecha_recepcion_material && (
        <p className="text-sm text-text">Material recibido el {fechaHora(le.fecha_recepcion_material)}.</p>
      )}
      {le?.horas_ejecucion !== null && le?.horas_ejecucion !== undefined && (
        <p className="text-sm text-text">Horas de ejecución registradas: {le.horas_ejecucion}.</p>
      )}
    </section>
  );
}
