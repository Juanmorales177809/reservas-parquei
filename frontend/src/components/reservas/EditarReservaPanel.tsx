"use client";

import { useEffect, useState, type FormEvent } from "react";
import { AcompanantesReserva } from "@/src/components/reservas/AcompanantesReserva";
import {
  CamposAdicionalesReserva,
  camposHabilitados,
  camposParaEnviar,
  faltantes,
  type ValoresCampos,
} from "@/src/components/reservas/CamposAdicionalesReserva";
import { ContextoReserva } from "@/src/components/reservas/ContextoReserva";
import { RecursosDelEspacio } from "@/src/components/reservas/RecursosDelEspacio";
import { SelectorEspacio, SelectorRecurso } from "@/src/components/selectores/selectores";
import { SelectorRecursosVarios } from "@/src/components/selectores/SelectorRecursosVarios";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { contextoParaEnviar, hayContexto, type ContextoElegido } from "@/src/lib/contexto-reserva";
import { detalleEspacio } from "@/src/lib/espacios-api";
import type { EspacioDetalle } from "@/src/lib/espacios-types";
import { detalleRecurso } from "@/src/lib/recursos-api";
import { editarReserva } from "@/src/lib/reservas-api";
import type { ReservaDetalleRespuesta } from "@/src/lib/reservas-types";

const texto = (v: unknown) => (v === null || v === undefined ? "" : String(v));
const hora = (v: unknown) => texto(v).slice(0, 5);
const iguales = (a: unknown, b: unknown) => JSON.stringify(a) === JSON.stringify(b);
const ordenados = (l: string[]) => [...l].sort((a, b) => Number(a) - Number(b));

/** Lo que la reserva tiene hoy, en la forma de los controles del formulario. */
function estadoInicial(d: ReservaDetalleRespuesta) {
  const det = d.detalle as Record<string, unknown>;
  const ctx = d.contexto as Record<string, unknown>;
  const vigentes = d.recursos.filter((r) => r.estado_asignacion === "ASIGNADO");
  const campos: ValoresCampos = {};
  for (const c of d.campos_adicionales) {
    campos[Number(c.campo_id)] = { texto: texto(c.valor_texto), opcion: c.opcion_id ? texto(c.opcion_id) : "" };
  }
  const contexto: ContextoElegido = {
    proyecto: texto(ctx.proyecto_id),
    semillero: texto(ctx.semillero_id),
    pasantia: texto(ctx.pasantia_id),
    trabajo: texto(ctx.trabajo_grado_id),
    actividad: texto(ctx.actividad_institucional_id),
  };
  return {
    observacion: texto(d.observacion),
    espacioId: texto(det.espacio_id),
    fecha: texto(det.fecha),
    horaInicio: hora(det.hora_inicio),
    horaFin: hora(det.hora_fin),
    fechaSalida: texto(det.fecha_salida),
    fechaDevolucion: texto(det.fecha_devolucion_estimada),
    razon: texto(det.razon_solicitud),
    lugar: texto(det.lugar_nombre),
    direccion: texto(det.lugar_direccion),
    actividadEvento: texto(det.nombre_actividad_evento),
    descripcion: texto(det.descripcion_necesidad),
    principal: texto(vigentes.find((r) => r.rol === "PRINCIPAL")?.recurso_id),
    adicionales: vigentes.filter((r) => r.rol === "ADICIONAL").map((r) => String(r.recurso_id)),
    acompanantes: (d.acompanantes_detalle ?? []).map((a) => String(a.id_cuenta)),
    campos,
    contexto,
    apoyo: d.requiere_apoyo,
  };
}

/**
 * Edición de la solicitud por su reservista mientras siga `SOLICITADA` (RN-PRO-02, RN-PRO-06; contrato §2.8).
 * Conserva `SOLICITADA` y revalida todo en el servidor. Cada bloque (contexto, recursos, acompañantes, campos
 * adicionales) viaja completo y solo si cambió; los datos sueltos, solo los que cambiaron.
 */
export function EditarReservaPanel({
  detalle, ocupada, actuar,
}: {
  detalle: ReservaDetalleRespuesta;
  ocupada: boolean;
  actuar: (accion: () => Promise<unknown>, exito: string) => Promise<void>;
}) {
  const tipo = detalle.tipo_reserva;
  const inicial = estadoInicial(detalle);
  const [abierto, setAbierto] = useState(false);
  const [v, setV] = useState(inicial);
  const [error, setError] = useState<string | null>(null);
  const [espacio, setEspacio] = useState<EspacioDetalle | null>(null);
  const [apoyoObligatorio, setApoyoObligatorio] = useState(false);
  const idUnidad = String(detalle.id_unidad);
  const cambia = (parcial: Partial<typeof inicial>) => setV((actual) => ({ ...actual, ...parcial }));

  // Al abrir y al cambiar de espacio: sus campos adicionales y sus recursos asociados.
  useEffect(() => {
    if (!abierto || tipo !== "ESPACIO" || !v.espacioId) return;
    let cancelado = false;
    detalleEspacio(Number(v.espacioId))
      .then((d) => {
        if (!cancelado) setEspacio(d);
      })
      .catch(() => {
        if (!cancelado) setError("No se pudo cargar la información del espacio.");
      });
    return () => {
      cancelado = true;
    };
  }, [abierto, tipo, v.espacioId]);

  // RN-RES-09: un equipo que exige apoyo obliga a pedirlo.
  const idsRecursos = [...(tipo !== "ESPACIO" && v.principal ? [v.principal] : []), ...v.adicionales].join(",");
  useEffect(() => {
    if (!abierto) return;
    let cancelado = false;
    if (!idsRecursos) {
      setApoyoObligatorio(false);
      return;
    }
    Promise.all(idsRecursos.split(",").map((id) => detalleRecurso(Number(id))))
      .then((ds) => {
        if (!cancelado) setApoyoObligatorio(ds.some((d) => d.especializacion?.requiere_apoyo === true));
      })
      .catch(() => {
        if (!cancelado) setApoyoObligatorio(false);
      });
    return () => {
      cancelado = true;
    };
  }, [abierto, idsRecursos]);

  const camposEspacio = camposHabilitados(espacio?.campos);
  const cambioEspacio = v.espacioId !== inicial.espacioId;

  function cambiarEspacio(nuevo: string) {
    // Otro espacio pide otros campos y otra capacidad: no se arrastra lo del anterior.
    setEspacio(null);
    cambia({ espacioId: nuevo, campos: {}, adicionales: [] });
  }

  function guardar(evento: FormEvent) {
    evento.preventDefault();
    setError(null);
    const cuerpo: Parameters<typeof editarReserva>[1] = {};
    const det: Record<string, unknown> = {};
    const dato = (campo: string, nuevo: string, previo: string) => {
      if (nuevo !== previo) det[campo] = nuevo;
    };

    if (tipo === "ESPACIO" || tipo === "RECURSO_INTERNO") {
      if (tipo === "ESPACIO" && cambioEspacio) det.espacio_id = Number(v.espacioId);
      dato("fecha", v.fecha, inicial.fecha);
      dato("hora_inicio", v.horaInicio, inicial.horaInicio);
      dato("hora_fin", v.horaFin, inicial.horaFin);
    } else if (tipo === "LISTA_ESPERA") {
      dato("descripcion_necesidad", v.descripcion, inicial.descripcion);
    } else {
      dato("fecha_salida", v.fechaSalida, inicial.fechaSalida);
      dato("fecha_devolucion_estimada", v.fechaDevolucion, inicial.fechaDevolucion);
      dato("razon_solicitud", v.razon, inicial.razon);
      dato("lugar_nombre", v.lugar, inicial.lugar);
      dato("lugar_direccion", v.direccion, inicial.direccion);
      dato("nombre_actividad_evento", v.actividadEvento, inicial.actividadEvento);
    }
    if (Object.keys(det).length > 0) cuerpo.detalle = det;
    if (v.observacion !== inicial.observacion) cuerpo.observacion = v.observacion;

    // RN-CTX-01: el contexto nunca queda vacío.
    if (!hayContexto(v.contexto)) {
      setError("Elige el proyecto, semillero, pasantía, trabajo de grado o actividad institucional de la reserva.");
      return;
    }
    if (!iguales(v.contexto, inicial.contexto)) cuerpo.contexto = contextoParaEnviar(v.contexto);

    if (tipo !== "LISTA_ESPERA") {
      const recursosAhora = tipo === "ESPACIO" ? ordenados(v.adicionales) : [v.principal, ...ordenados(v.adicionales)];
      const recursosAntes = tipo === "ESPACIO" ? ordenados(inicial.adicionales) : [inicial.principal, ...ordenados(inicial.adicionales)];
      if (tipo !== "ESPACIO" && !v.principal) {
        setError("Elige el recurso principal.");
        return;
      }
      if (!iguales(recursosAhora, recursosAntes)) {
        cuerpo.recursos = [
          ...(tipo !== "ESPACIO" ? [{ recurso_id: Number(v.principal), rol: "PRINCIPAL" as const }] : []),
          ...v.adicionales.map((id) => ({ recurso_id: Number(id), rol: "ADICIONAL" as const })),
        ];
      }
      if (v.apoyo !== inicial.apoyo && !apoyoObligatorio) cuerpo.requiere_apoyo = v.apoyo;
    }

    if (tipo === "ESPACIO") {
      const sinLlenar = faltantes(camposEspacio, v.campos);
      if (sinLlenar.length > 0) {
        setError(`Completa la información que pide el espacio: ${sinLlenar.join(", ")}.`);
        return;
      }
      if (espacio && v.acompanantes.length > espacio.capacidad) {
        setError(`Los asistentes (${v.acompanantes.length}) superan la capacidad del espacio (${espacio.capacidad}).`);
        return;
      }
      if (!iguales(ordenados(v.acompanantes), ordenados(inicial.acompanantes))) cuerpo.acompanantes = v.acompanantes.map(Number);
      const camposAhora = camposParaEnviar(camposEspacio, v.campos);
      // Con otro espacio los campos se envían siempre: los del anterior no valen.
      if (cambioEspacio || !iguales(camposAhora, camposParaEnviar(camposEspacio, inicial.campos))) {
        cuerpo.campos_adicionales = camposAhora;
      }
    }

    if (Object.keys(cuerpo).length === 0) {
      setAbierto(false);
      return;
    }
    void actuar(
      () => editarReserva(detalle.id, cuerpo),
      tipo === "LISTA_ESPERA" && detalle.lista_espera?.viable != null && cuerpo.detalle
        ? "La solicitud se actualizó. El técnico tendrá que evaluar de nuevo la viabilidad."
        : "La solicitud se actualizó y sigue pendiente de aprobación."
    ).then(() => setAbierto(false));
  }

  if (!abierto) {
    return (
      <div>
        <Button variant="secondary" size="sm" onClick={() => { setV(estadoInicial(detalle)); setError(null); setAbierto(true); }}>
          Editar solicitud
        </Button>
      </div>
    );
  }

  return (
    <form onSubmit={guardar} aria-label="Editar solicitud" className="flex flex-col gap-4">
      <h2 className="text-base font-bold text-text">Editar solicitud</h2>

      {tipo === "ESPACIO" && (
        <SelectorEspacio id="ed-espacio" label="Espacio" idUnidad={idUnidad} value={v.espacioId} onChange={cambiarEspacio} requerido />
      )}
      {(tipo === "ESPACIO" || tipo === "RECURSO_INTERNO") && (
        <>
          <Field id="ed-fecha" label="Fecha" type="date" value={v.fecha} onChange={(e) => cambia({ fecha: e.target.value })} required />
          <div className="flex gap-2">
            <Field id="ed-hi" label="Hora inicio" type="time" value={v.horaInicio} onChange={(e) => cambia({ horaInicio: e.target.value })} required />
            <Field id="ed-hf" label="Hora fin" type="time" value={v.horaFin} onChange={(e) => cambia({ horaFin: e.target.value })} required />
          </div>
        </>
      )}
      {(tipo === "RECURSO_CAMPUS" || tipo === "RECURSO_EXTERNO") && (
        <>
          <div className="flex gap-2">
            <Field id="ed-salida" label="Fecha salida" type="date" value={v.fechaSalida} onChange={(e) => cambia({ fechaSalida: e.target.value })} required />
            <Field id="ed-devolucion" label="Devolución estimada" type="date" value={v.fechaDevolucion} onChange={(e) => cambia({ fechaDevolucion: e.target.value })} required />
          </div>
          <Field id="ed-razon" label="Razón de la solicitud" value={v.razon} onChange={(e) => cambia({ razon: e.target.value })} required />
          <Field id="ed-lugar" label="Lugar" value={v.lugar} onChange={(e) => cambia({ lugar: e.target.value })} required />
          <Field id="ed-direccion" label="Dirección" value={v.direccion} onChange={(e) => cambia({ direccion: e.target.value })} required />
          <Field id="ed-actividad" label="Nombre de la actividad o evento" value={v.actividadEvento} onChange={(e) => cambia({ actividadEvento: e.target.value })} />
        </>
      )}
      {tipo === "LISTA_ESPERA" && (
        <>
          <Field id="ed-necesidad" label="Descripción de la necesidad" value={v.descripcion} onChange={(e) => cambia({ descripcion: e.target.value })} required />
          {detalle.lista_espera?.viable != null && v.descripcion !== inicial.descripcion && (
            <p className="text-sm text-muted">
              Cambiar la descripción invalida la evaluación de viabilidad y la revisión técnica del formulario
              (RN-TIP-PLE-09); tus adjuntos y tu parte del formulario se conservan.
            </p>
          )}
        </>
      )}

      {(tipo === "RECURSO_INTERNO" || tipo === "RECURSO_CAMPUS" || tipo === "RECURSO_EXTERNO") && (
        <>
          <SelectorRecurso id="ed-principal" label="Recurso principal" idUnidad={idUnidad} value={v.principal}
            onChange={(p) => cambia({ principal: p })} requerido />
          <SelectorRecursosVarios label="Recursos adicionales (opcional)" idUnidad={idUnidad} excluir={v.principal}
            value={v.adicionales} onChange={(a) => cambia({ adicionales: a })} />
        </>
      )}
      {tipo === "ESPACIO" && espacio && (
        <>
          <RecursosDelEspacio idUnidad={idUnidad} recursos={espacio.recursos ?? []} fecha={v.fecha}
            horaInicio={v.horaInicio} horaFin={v.horaFin} value={v.adicionales} onChange={(a) => cambia({ adicionales: a })} />
          <CamposAdicionalesReserva campos={camposEspacio} valores={v.campos} onChange={(c) => cambia({ campos: c })} />
        </>
      )}

      <ContextoReserva value={v.contexto} onChange={(c) => cambia({ contexto: c })} />
      {tipo === "ESPACIO" && (
        <AcompanantesReserva proyectoId={v.contexto.proyecto} semilleroId={v.contexto.semillero}
          capacidad={espacio?.capacidad} value={v.acompanantes} onChange={(a) => cambia({ acompanantes: a })} />
      )}
      {tipo !== "LISTA_ESPERA" && (
        <label className="flex items-center gap-2 text-sm text-text">
          <input type="checkbox" checked={v.apoyo || apoyoObligatorio} disabled={apoyoObligatorio}
            onChange={(e) => cambia({ apoyo: e.target.checked })} />
          Necesito acompañamiento de un técnico
          {apoyoObligatorio && <span className="text-muted">(obligatorio: un equipo elegido lo exige)</span>}
        </label>
      )}
      <Field id="ed-observacion" label="Observación (opcional)" value={v.observacion} onChange={(e) => cambia({ observacion: e.target.value })} />

      {error && <p role="alert" className="text-sm text-error-2">{error}</p>}
      <div className="flex gap-2">
        <Button type="submit" variant="primary" size="sm" loading={ocupada}>Guardar cambios</Button>
        <Button type="button" variant="ghost" size="sm" onClick={() => setAbierto(false)}>Descartar</Button>
      </div>
    </form>
  );
}
