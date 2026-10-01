"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
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
import { SelectorEspacio, SelectorRecurso, SelectorUnidad } from "@/src/components/selectores/selectores";
import { SelectorRecursosVarios } from "@/src/components/selectores/SelectorRecursosVarios";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { Select } from "@/src/components/ui/Select";
import { ACEPTA_ADJUNTOS, problemaAdjunto, tipoAdjuntoDe } from "@/src/lib/adjuntos";
import { CONTEXTO_VACIO, contextoParaEnviar, hayContexto, type ContextoElegido } from "@/src/lib/contexto-reserva";
import { detalleEspacio } from "@/src/lib/espacios-api";
import type { EspacioDetalle } from "@/src/lib/espacios-types";
import { ApiRequestError } from "@/src/lib/http";
import { detalleRecurso } from "@/src/lib/recursos-api";
import { consultarDisponibilidad, crearReserva, subirAdjunto, tiposHabilitados } from "@/src/lib/reservas-api";
import type { DisponibilidadRespuesta, TipoReservaCodigo, TipoReservaItem } from "@/src/lib/reservas-types";
import { BarraAcciones, Seccion } from "@/src/components/ui/Seccion";
import { CasillaTarjeta } from "@/src/components/ui/CasillaTarjeta";

interface Props {
  /** Dentro de un modal: sin tarjetas propias, con la barra de acciones pegada al pie y un «Cancelar». */
  enModal?: boolean;
  /** Si se da, se llama al crear la reserva en vez de navegar a su detalle. */
  onCreada?: (id: number) => void;
  onCancelar?: () => void;
}

// WF-RES-01 — specs/modules/reservations/wireframes.md
export function NuevaReservaForm({ enModal = false, onCreada, onCancelar }: Props) {
  const router = useRouter();
  const [idUnidad, setIdUnidad] = useState("");
  const [tipos, setTipos] = useState<TipoReservaItem[] | null>(null);
  const [tipo, setTipo] = useState<TipoReservaCodigo | "">("");
  const [espacioId, setEspacioId] = useState("");
  const [espacio, setEspacio] = useState<EspacioDetalle | null>(null);
  const [valoresCampos, setValoresCampos] = useState<ValoresCampos>({});
  const [fecha, setFecha] = useState("");
  const [horaInicio, setHoraInicio] = useState("");
  const [horaFin, setHoraFin] = useState("");
  const [fechaSalida, setFechaSalida] = useState("");
  const [fechaDevolucion, setFechaDevolucion] = useState("");
  const [recursoId, setRecursoId] = useState("");
  const [adicionales, setAdicionales] = useState<string[]>([]);
  const [acompanantes, setAcompanantes] = useState<string[]>([]);
  const [contexto, setContexto] = useState<ContextoElegido>(CONTEXTO_VACIO);
  const [pideApoyo, setPideApoyo] = useState(false);
  const [apoyoObligatorio, setApoyoObligatorio] = useState(false);
  const [archivos, setArchivos] = useState<File[]>([]);
  const [reservaCreada, setReservaCreada] = useState<number | null>(null);
  const [razon, setRazon] = useState("");
  const [lugarNombre, setLugarNombre] = useState("");
  const [lugarDireccion, setLugarDireccion] = useState("");
  const [nombreActividad, setNombreActividad] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [observacion, setObservacion] = useState("");
  const [franjas, setFranjas] = useState<DisponibilidadRespuesta | null>(null);
  const [ocupada, setOcupada] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");

  const campos = camposHabilitados(espacio?.campos);

  // Una sesión caducada no es un error del formulario: se vuelve al inicio de sesión, como en las demás pantallas.
  function sesionVencida(e: unknown): boolean {
    if (e instanceof ApiRequestError && e.status === 401) {
      router.replace("/login?motivo=sesion_vencida");
      return true;
    }
    return false;
  }

  function informar(texto: string | null, t: "error" | "exito" | "muted" = "error") {
    setMensaje(texto);
    setTono(t);
  }

  // RN-TIP-02, RN-TIP-03, RN-TIP-05, RN-TIP-06: los tipos salen del laboratorio elegido.
  useEffect(() => {
    let cancelado = false;
    setTipos(null);
    setTipo("");
    if (!idUnidad) return;
    tiposHabilitados(Number(idUnidad))
      .then((r) => {
        if (cancelado) return;
        setTipos(r.datos);
        if (r.datos.length === 1) setTipo(r.datos[0].codigo as TipoReservaCodigo);
      })
      .catch((e) => {
        if (cancelado || sesionVencida(e)) return;
        setTipos([]);
        informar("No se pudieron cargar los tipos de reserva de este laboratorio.");
      });
    return () => {
      cancelado = true;
    };
  }, [idUnidad]);

  // RN-TIP-PE-12: al elegir un espacio se cargan sus recursos asociados y sus campos adicionales.
  useEffect(() => {
    let cancelado = false;
    setEspacio(null);
    setValoresCampos({});
    if (!espacioId) return;
    detalleEspacio(Number(espacioId))
      .then((d) => {
        if (!cancelado) setEspacio(d);
      })
      .catch((e) => {
        if (!cancelado && !sesionVencida(e)) informar("No se pudo cargar la información del espacio.");
      });
    return () => {
      cancelado = true;
    };
  }, [espacioId]);

  // RN-RES-09: si algún equipo elegido exige apoyo, la reserva lo lleva y no puede desmarcarse.
  const idsRecursos = [...(tipo !== "ESPACIO" && recursoId ? [recursoId] : []), ...adicionales].join(",");
  useEffect(() => {
    let cancelado = false;
    if (!idsRecursos) {
      setApoyoObligatorio(false);
      return;
    }
    Promise.all(idsRecursos.split(",").map((id) => detalleRecurso(Number(id))))
      .then((detalles) => {
        if (!cancelado) setApoyoObligatorio(detalles.some((d) => d.especializacion?.requiere_apoyo === true));
      })
      .catch(() => {
        if (!cancelado) setApoyoObligatorio(false);
      });
    return () => {
      cancelado = true;
    };
  }, [idsRecursos]);

  function detalle(): Record<string, unknown> {
    switch (tipo) {
      case "ESPACIO":
        return {
          espacio_id: Number(espacioId), fecha, hora_inicio: horaInicio, hora_fin: horaFin,
          asistentes: acompanantes.length,
        };
      case "RECURSO_INTERNO":
        return { fecha, hora_inicio: horaInicio, hora_fin: horaFin };
      case "RECURSO_CAMPUS":
      case "RECURSO_EXTERNO":
        return {
          fecha_salida: fechaSalida, fecha_devolucion_estimada: fechaDevolucion,
          razon_solicitud: razon, lugar_nombre: lugarNombre, lugar_direccion: lugarDireccion,
          ...(nombreActividad ? { nombre_actividad_evento: nombreActividad } : {}),
        };
      case "LISTA_ESPERA":
        return { descripcion_necesidad: descripcion };
      default:
        return {};
    }
  }

  function recursosDeLaSolicitud() {
    const principal =
      recursoId && tipo !== "ESPACIO" && tipo !== "LISTA_ESPERA"
        ? [{ recurso_id: Number(recursoId), rol: "PRINCIPAL" as const }]
        : [];
    const extras =
      tipo === "LISTA_ESPERA" ? [] : adicionales.map((id) => ({ recurso_id: Number(id), rol: "ADICIONAL" as const }));
    return [...principal, ...extras];
  }

  async function consultar() {
    const porFecha = tipo === "ESPACIO" || tipo === "RECURSO_INTERNO";
    const faltan =
      !idUnidad ||
      (tipo === "ESPACIO" ? !espacioId : !recursoId) ||
      (porFecha ? !fecha : !fechaSalida || !fechaDevolucion);
    if (faltan) {
      informar(
        tipo === "ESPACIO"
          ? "Elige el laboratorio, el espacio y la fecha para consultar la disponibilidad."
          : porFecha
            ? "Elige el laboratorio, el recurso y la fecha para consultar la disponibilidad."
            : "Elige el laboratorio, el recurso y las fechas de salida y devolución para consultar la disponibilidad."
      );
      return;
    }
    setOcupada(true);
    try {
      const r = await consultarDisponibilidad({
        id_unidad: Number(idUnidad),
        ...(tipo === "ESPACIO" ? { espacio_id: Number(espacioId) } : { recurso_id: Number(recursoId) }),
        desde: porFecha ? fecha : fechaSalida,
        hasta: porFecha ? fecha : fechaDevolucion,
      });
      setFranjas(r);
      informar(null, "muted");
    } catch (error) {
      informar(
        error instanceof ApiRequestError && error.error.mensaje
          ? error.error.mensaje
          : "No se pudo consultar la disponibilidad."
      );
    } finally {
      setOcupada(false);
    }
  }

  async function guardar(evento: FormEvent) {
    evento.preventDefault();
    if (!tipo) return;
    // RN-CTX-01: toda reserva, de cualquier tipo, lleva un contexto.
    if (!hayContexto(contexto)) {
      informar("Elige un proyecto, un semillero, una pasantía, un trabajo de grado o una actividad institucional.");
      return;
    }
    if (tipo === "ESPACIO") {
      const sinLlenar = faltantes(campos, valoresCampos);
      if (sinLlenar.length > 0) {
        informar(`Completa la información que pide el espacio: ${sinLlenar.join(", ")}.`);
        return;
      }
      if (espacio && acompanantes.length > espacio.capacidad) {
        informar(`Los asistentes (${acompanantes.length}) superan la capacidad del espacio (${espacio.capacidad}).`);
        return;
      }
    }
    setOcupada(true);
    informar(null, "muted");
    try {
      const recursos = recursosDeLaSolicitud();
      const r = await crearReserva({
        id_unidad: Number(idUnidad),
        tipo_reserva: tipo,
        ...(observacion ? { observacion } : {}),
        ...(pideApoyo || apoyoObligatorio ? { requiere_apoyo: true } : {}),
        contexto: contextoParaEnviar(contexto),
        detalle: detalle(),
        ...(recursos.length > 0 ? { recursos } : {}),
        ...(tipo === "ESPACIO" && acompanantes.length > 0 ? { acompanantes: acompanantes.map(Number) } : {}),
        ...(tipo === "ESPACIO" && campos.length > 0
          ? { campos_adicionales: camposParaEnviar(campos, valoresCampos) }
          : {}),
      });
      // Los adjuntos se cargan después de crear la solicitud (contrato reservations §2.5).
      const fallidos: string[] = [];
      for (const archivo of tipo === "LISTA_ESPERA" ? archivos : []) {
        try {
          await subirAdjunto(r.id, archivo, tipoAdjuntoDe(archivo.name) ?? "DOCUMENTO");
        } catch {
          fallidos.push(archivo.name);
        }
      }
      if (fallidos.length > 0) {
        setReservaCreada(r.id);
        informar(
          `La solicitud se creó, pero no se pudo subir: ${fallidos.join(", ")}. Puedes adjuntarlos de nuevo en la reserva.`
        );
        return;
      }
      if (onCreada) onCreada(r.id);
      else router.push(`/reservas/${r.id}`);
    } catch (error) {
      informar(mensajeError(error));
    } finally {
      setOcupada(false);
    }
  }

  const sinTipos = tipos !== null && tipos.length === 0;

  return (
    <div className="flex flex-col gap-6">
      <form onSubmit={(e) => void guardar(e)} className="flex flex-col gap-5">
        <Seccion numero={1} plana={enModal} titulo="¿Qué quieres reservar?" descripcion="Elige el laboratorio y el tipo de reserva." destacada>
        <SelectorUnidad id="res-unidad" label="Laboratorio" value={idUnidad} onChange={setIdUnidad} requerido />
        {idUnidad && sinTipos && (
          <p className="text-sm text-error-2">Este laboratorio no admite reservas en este momento.</p>
        )}
        {tipos !== null && tipos.length > 1 && (
          <Select id="res-tipo" label="Tipo" value={tipo} required
            onChange={(e) => {
              setTipo(e.target.value as TipoReservaCodigo);
              // Cada tipo usa un objetivo distinto: no arrastrar el del anterior.
              setEspacioId("");
              setRecursoId("");
              setAdicionales([]);
              setAcompanantes([]);
              setArchivos([]);
              setFranjas(null);
            }}>
            <option value="">Seleccionar tipo</option>
            {tipos.map((t) => (
              <option key={t.codigo} value={t.codigo}>{t.nombre}</option>
            ))}
          </Select>
        )}
        {tipos !== null && tipos.length === 1 && (
          <p className="text-sm text-muted">Tipo de reserva: {tipos[0].nombre}</p>
        )}
        </Seccion>

        {tipo && (
          <Seccion numero={2} plana={enModal} titulo="Detalles de la reserva" descripcion="Cuándo y qué necesitas.">

        {tipo === "ESPACIO" && (
          <>
            <SelectorEspacio id="res-espacio" label="Espacio" idUnidad={idUnidad} value={espacioId}
              onChange={setEspacioId} requerido />
            <Field id="res-fecha" label="Fecha" type="date" value={fecha}
              onChange={(e) => setFecha(e.target.value)} required />
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <Field id="res-hi" label="Hora inicio" type="time" value={horaInicio}
                onChange={(e) => setHoraInicio(e.target.value)} required />
              <Field id="res-hf" label="Hora fin" type="time" value={horaFin}
                onChange={(e) => setHoraFin(e.target.value)} required />
            </div>
            {espacio && (
              <RecursosDelEspacio idUnidad={idUnidad} recursos={espacio.recursos ?? []} fecha={fecha}
                horaInicio={horaInicio} horaFin={horaFin} value={adicionales} onChange={setAdicionales} />
            )}
            <CamposAdicionalesReserva campos={campos} valores={valoresCampos} onChange={setValoresCampos} />
          </>
        )}
        {tipo === "RECURSO_INTERNO" && (
          <>
            <Field id="res-fecha" label="Fecha" type="date" value={fecha}
              onChange={(e) => setFecha(e.target.value)} required />
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <Field id="res-hi" label="Hora inicio" type="time" value={horaInicio}
                onChange={(e) => setHoraInicio(e.target.value)} required />
              <Field id="res-hf" label="Hora fin" type="time" value={horaFin}
                onChange={(e) => setHoraFin(e.target.value)} required />
            </div>
            <SelectorRecurso id="res-recurso" label="Recurso principal" idUnidad={idUnidad} value={recursoId}
              onChange={setRecursoId} requerido />
            <SelectorRecursosVarios label="Recursos adicionales (opcional)" idUnidad={idUnidad}
              excluir={recursoId} value={adicionales} onChange={setAdicionales} />
          </>
        )}
        {(tipo === "RECURSO_CAMPUS" || tipo === "RECURSO_EXTERNO") && (
          <>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <Field id="res-salida" label="Fecha salida" type="date" value={fechaSalida}
                onChange={(e) => setFechaSalida(e.target.value)} required />
              <Field id="res-devolucion" label="Devolución estimada" type="date" value={fechaDevolucion}
                onChange={(e) => setFechaDevolucion(e.target.value)} required />
            </div>
            <SelectorRecurso id="res-recurso" label="Recurso principal" idUnidad={idUnidad} value={recursoId}
              onChange={setRecursoId} requerido />
            <SelectorRecursosVarios label="Recursos adicionales (opcional)" idUnidad={idUnidad}
              excluir={recursoId} value={adicionales} onChange={setAdicionales} />
            <Field id="res-razon" label="Razón de la solicitud" value={razon}
              onChange={(e) => setRazon(e.target.value)} required />
            <Field id="res-lugar" label="Lugar" value={lugarNombre}
              onChange={(e) => setLugarNombre(e.target.value)} required />
            <Field id="res-direccion" label="Dirección" value={lugarDireccion}
              onChange={(e) => setLugarDireccion(e.target.value)} required />
            <Field id="res-actividad-evento" label="Nombre de la actividad o evento (si aplica)" value={nombreActividad}
              onChange={(e) => setNombreActividad(e.target.value)} />
          </>
        )}
        {tipo === "LISTA_ESPERA" && (
          <>
            <Field id="res-necesidad" label="Descripción de la necesidad" value={descripcion}
              onChange={(e) => setDescripcion(e.target.value)} required />
            <div className="flex flex-col gap-1">
              <label htmlFor="res-adjuntos" className="text-sm font-bold text-text">
                Archivos técnicos (opcional)
              </label>
              <input id="res-adjuntos" type="file" multiple accept={ACEPTA_ADJUNTOS}
                className="text-sm text-text file:mr-3 file:cursor-pointer file:rounded-control file:border-0 file:bg-primary-tint file:px-4 file:py-2.5 file:font-display file:text-sm file:font-bold file:text-primary-2 hover:file:bg-[color-mix(in_srgb,var(--color-primary-tint)_60%,var(--color-primary-1)_15%)]"
                onChange={(e) => {
                  const lista = Array.from(e.target.files ?? []);
                  const problema = lista.map(problemaAdjunto).find((p) => p !== null);
                  if (problema) {
                    e.target.value = "";
                    setArchivos([]);
                    informar(problema);
                    return;
                  }
                  setArchivos(lista);
                  informar(null, "muted");
                }} />
              <p className="text-sm text-muted">
                DWG, DXF, STEP, STL, PNG, JPG o PDF; máximo 5 MB cada uno. Se suben al guardar la solicitud
                y también podrás agregar más después, desde la reserva.
              </p>
            </div>
          </>
        )}

          </Seccion>
        )}

        {tipo && (
          <>
            <Seccion numero={3} plana={enModal} titulo="¿Para quién es?" descripcion="Vincula la reserva a tu proyecto o semillero.">
            <ContextoReserva value={contexto} onChange={setContexto} />
            {tipo === "ESPACIO" && (
              <AcompanantesReserva proyectoId={contexto.proyecto} semilleroId={contexto.semillero}
                capacidad={espacio?.capacidad} value={acompanantes} onChange={setAcompanantes} />
            )}
            </Seccion>
            <Seccion numero={4} plana={enModal} titulo="Últimos detalles">
            {tipo !== "LISTA_ESPERA" && (
              <CasillaTarjeta checked={pideApoyo || apoyoObligatorio} disabled={apoyoObligatorio}
                onChange={(e) => setPideApoyo(e.target.checked)}>
                Necesito acompañamiento de un técnico
                {apoyoObligatorio && <span className="text-muted">(obligatorio: un equipo elegido lo exige)</span>}
              </CasillaTarjeta>
            )}
            <Field id="res-obs" label="Observación (opcional)" value={observacion}
              onChange={(e) => setObservacion(e.target.value)} />
            </Seccion>
            <BarraAcciones plana={enModal}>
              {onCancelar && (
                <Button type="button" variant="ghost" onClick={onCancelar}>
                  Cancelar
                </Button>
              )}
              {tipo !== "LISTA_ESPERA" && (
                <Button type="button" variant="secondary" disabled={ocupada}
                  onClick={() => void consultar()}>
                  Consultar disponibilidad
                </Button>
              )}
              <Button type="submit" variant="primary" loading={ocupada}>Guardar solicitud</Button>
            </BarraAcciones>
          </>
        )}
        {/* Aún sin tipo elegido no hay barra de acciones: dentro del modal, salir siempre es posible. */}
        {enModal && !tipo && onCancelar && (
          <BarraAcciones plana>
            <Button type="button" variant="ghost" onClick={onCancelar}>
              Cancelar
            </Button>
          </BarraAcciones>
        )}
      </form>
      {franjas && (
        <div className="rounded-card border border-border bg-surface p-4 text-sm text-text">
          <p className="font-display text-base font-bold">Disponibilidad</p>
          <p className="text-muted">
            Horario de atención: {franjas.horario_unidad.hora_apertura.slice(0, 5)}–
            {franjas.horario_unidad.hora_cierre.slice(0, 5)}
          </p>
          <ul>
            {franjas.franjas.map((f, i) => (
              <li key={i}>
                {f.fecha} {f.hora_inicio?.slice(0, 5) ?? ""}–{f.hora_fin?.slice(0, 5) ?? ""}:{" "}
                {f.disponible ? "disponible" : "no disponible"}
              </li>
            ))}
            {franjas.franjas.length === 0 && <li>Sin reservas en el periodo consultado.</li>}
          </ul>
        </div>
      )}
      <RegionMensaje texto={mensaje} tono={mensaje ? tono : "muted"} />
      {reservaCreada !== null && (
        <Link href={`/reservas/${reservaCreada}`} className="text-sm font-bold text-primary-2">
          Ver la reserva #{reservaCreada}
        </Link>
      )}
    </div>
  );
}

function mensajeError(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.error.codigo === "SOLAPAMIENTO") return "Ese periodo ya está ocupado.";
    if (error.error.codigo === "VINCULACION_REQUERIDA")
      return "Necesitas una vinculación activa para reservar.";
    if (error.error.codigo === "PERFIL_INICIAL_PENDIENTE")
      return "Completa tu perfil antes de reservar.";
    if (error.status === 429) return "La operación está temporalmente limitada.";
    // El resto de rechazos del servidor (403 unidad ajena, 409 fuera de horario, 422 campo obligatorio...)
    // traen un mensaje pensado para la persona: se muestra tal cual.
    if (error.error.mensaje && [403, 404, 409, 422].includes(error.status)) return error.error.mensaje;
  }
  return "No se pudo crear la reserva: la confirmación depende del servidor.";
}
