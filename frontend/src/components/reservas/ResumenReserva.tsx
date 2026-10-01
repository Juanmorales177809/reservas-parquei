import { fechaHora } from "@/src/lib/formato";
import { fechaCorta } from "@/src/lib/reservas-nombres";
import type { ReservaDetalleRespuesta } from "@/src/lib/reservas-types";

const hora = (v: unknown) => (typeof v === "string" ? v.slice(0, 5) : "");
const texto = (v: unknown) => (v === null || v === undefined ? "" : String(v));

function Dato({ etiqueta, valor }: { etiqueta: string; valor: string | null | undefined }) {
  if (!valor) return null;
  return (
    <div className="contents">
      <dt className="font-medium text-muted">{etiqueta}</dt>
      <dd className="text-text">{valor}</dd>
    </div>
  );
}

/** Lo que dice la reserva, con nombres y sin identificadores (SCR-RES-04). */
export function ResumenReserva({ detalle }: { detalle: ReservaDetalleRespuesta }) {
  const d = detalle.detalle as Record<string, unknown>;
  const c = detalle.contexto as Record<string, unknown>;
  const tipo = detalle.tipo_reserva;

  const contexto: [string, string][] = [
    ["Proyecto", c.proyecto_nombre ? `${texto(c.proyecto_nombre)} (${texto(c.proyecto_codigo)})` : ""],
    ["Semillero", c.semillero_nombre ? `${texto(c.semillero_nombre)} (${texto(c.semillero_codigo)})` : ""],
    ["Pasantía", c.pasantia_universidad ? `${texto(c.pasantia_universidad)} · docente ${texto(c.pasantia_docente_nombre)}` : ""],
    ["Trabajo de grado", c.trabajo_grado_director_nombre ? `Dirige ${texto(c.trabajo_grado_director_nombre)}` : ""],
    ["Actividad institucional", texto(c.actividad_nombre)],
  ];

  return (
    <div className="flex flex-col gap-4">
      <dl className="grid grid-cols-[max-content_1fr] gap-x-6 gap-y-2 text-sm">
        <Dato etiqueta="Unidad" valor={detalle.unidad_nombre} />
        <Dato etiqueta="Solicitante" valor={detalle.solicitante_nombre} />
        <Dato etiqueta="Solicitada" valor={fechaHora(detalle.created_at)} />
        {tipo === "ESPACIO" && (
          <>
            <Dato etiqueta="Espacio" valor={texto(d.espacio_nombre)} />
            <Dato etiqueta="Fecha" valor={fechaCorta(texto(d.fecha))} />
            <Dato etiqueta="Horario" valor={`${hora(d.hora_inicio)}–${hora(d.hora_fin)}`} />
            <Dato etiqueta="Asistentes" valor={texto(d.asistentes)} />
          </>
        )}
        {tipo === "RECURSO_INTERNO" && (
          <>
            <Dato etiqueta="Fecha" valor={fechaCorta(texto(d.fecha))} />
            <Dato etiqueta="Horario" valor={`${hora(d.hora_inicio)}–${hora(d.hora_fin)}`} />
          </>
        )}
        {(tipo === "RECURSO_CAMPUS" || tipo === "RECURSO_EXTERNO") && (
          <>
            <Dato etiqueta="Salida" valor={fechaCorta(texto(d.fecha_salida))} />
            <Dato etiqueta="Devolución estimada" valor={fechaCorta(texto(d.fecha_devolucion_estimada))} />
            <Dato etiqueta="Razón" valor={texto(d.razon_solicitud)} />
            <Dato etiqueta="Lugar" valor={[texto(d.lugar_nombre), texto(d.lugar_direccion)].filter(Boolean).join(" — ")} />
            <Dato etiqueta="Actividad o evento" valor={texto(d.nombre_actividad_evento)} />
          </>
        )}
        {tipo === "LISTA_ESPERA" && <Dato etiqueta="Necesidad" valor={texto(d.descripcion_necesidad)} />}
        <Dato etiqueta="Apoyo técnico" valor={detalle.requiere_apoyo ? "Sí" : null} />
        <Dato etiqueta="Observación" valor={detalle.observacion} />
      </dl>

      {contexto.some(([, v]) => v) && (
        <div className="flex flex-col gap-1">
          <h2 className="font-display text-lg font-bold text-text">Contexto</h2>
          <dl className="grid grid-cols-[max-content_1fr] gap-x-6 gap-y-2 text-sm">
            {contexto.map(([etiqueta, valor]) => (
              <Dato key={etiqueta} etiqueta={etiqueta} valor={valor} />
            ))}
          </dl>
        </div>
      )}

      {(detalle.acompanantes_detalle?.length ?? 0) > 0 && (
        <div className="flex flex-col gap-1">
          <h2 className="font-display text-lg font-bold text-text">Acompañantes</h2>
          <ul className="text-sm text-text">
            {detalle.acompanantes_detalle!.map((a) => (
              <li key={a.id_cuenta}>{a.nombre ?? "Cuenta sin nombre"}</li>
            ))}
          </ul>
        </div>
      )}

      {detalle.campos_adicionales.length > 0 && (
        <div className="flex flex-col gap-1">
          <h2 className="font-display text-lg font-bold text-text">Información del espacio</h2>
          <dl className="grid grid-cols-[max-content_1fr] gap-x-6 gap-y-2 text-sm">
            {detalle.campos_adicionales.map((campo, i) => (
              <Dato
                key={i}
                etiqueta={texto(campo.campo_nombre)}
                valor={texto(campo.opcion_nombre) || texto(campo.valor_texto) || "—"}
              />
            ))}
          </dl>
        </div>
      )}
    </div>
  );
}
