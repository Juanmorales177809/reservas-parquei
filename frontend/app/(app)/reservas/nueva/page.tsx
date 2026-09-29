"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { Select } from "@/src/components/ui/Select";
import { ApiRequestError } from "@/src/lib/http";
import { consultarDisponibilidad, crearReserva } from "@/src/lib/reservas-api";
import type { DisponibilidadRespuesta, TipoReservaCodigo } from "@/src/lib/reservas-types";

// WF-RES-01 — specs/modules/reservations/wireframes.md
export default function PaginaNuevaReserva() {
  const router = useRouter();
  const [tipo, setTipo] = useState<TipoReservaCodigo>("ESPACIO");
  const [idUnidad, setIdUnidad] = useState("");
  const [espacioId, setEspacioId] = useState("");
  const [fecha, setFecha] = useState("");
  const [horaInicio, setHoraInicio] = useState("");
  const [horaFin, setHoraFin] = useState("");
  const [fechaSalida, setFechaSalida] = useState("");
  const [fechaDevolucion, setFechaDevolucion] = useState("");
  const [recursoId, setRecursoId] = useState("");
  const [proyectoId, setProyectoId] = useState("");
  const [razon, setRazon] = useState("");
  const [lugarNombre, setLugarNombre] = useState("");
  const [lugarDireccion, setLugarDireccion] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [observacion, setObservacion] = useState("");
  const [franjas, setFranjas] = useState<DisponibilidadRespuesta | null>(null);
  const [ocupada, setOcupada] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");

  function detalle(): Record<string, unknown> {
    switch (tipo) {
      case "ESPACIO":
        return { espacio_id: Number(espacioId), fecha, hora_inicio: horaInicio, hora_fin: horaFin };
      case "RECURSO_INTERNO":
        return { fecha, hora_inicio: horaInicio, hora_fin: horaFin };
      case "RECURSO_CAMPUS":
      case "RECURSO_EXTERNO":
        return {
          fecha_salida: fechaSalida, fecha_devolucion_estimada: fechaDevolucion,
          razon_solicitud: razon, lugar_nombre: lugarNombre, lugar_direccion: lugarDireccion,
        };
      case "LISTA_ESPERA":
        return { descripcion_necesidad: descripcion };
    }
  }

  async function consultar() {
    setOcupada(true);
    try {
      const r = await consultarDisponibilidad({
        id_unidad: Number(idUnidad),
        ...(espacioId ? { espacio_id: Number(espacioId) } : {}),
        ...(recursoId ? { recurso_id: Number(recursoId) } : {}),
        desde: tipo === "ESPACIO" || tipo === "RECURSO_INTERNO" ? fecha : fechaSalida,
        hasta: tipo === "ESPACIO" || tipo === "RECURSO_INTERNO" ? fecha : fechaDevolucion,
      });
      setFranjas(r);
      setMensaje(null);
    } catch {
      setMensaje("No se pudo consultar la disponibilidad.");
      setTono("error");
    } finally {
      setOcupada(false);
    }
  }

  async function guardar(evento: FormEvent) {
    evento.preventDefault();
    setOcupada(true);
    setMensaje(null);
    try {
      const r = await crearReserva({
        id_unidad: Number(idUnidad),
        tipo_reserva: tipo,
        ...(observacion ? { observacion } : {}),
        contexto: proyectoId ? { proyecto_id: Number(proyectoId) } : {},
        detalle: detalle(),
        ...(recursoId && tipo !== "ESPACIO" && tipo !== "LISTA_ESPERA"
          ? { recursos: [{ recurso_id: Number(recursoId), rol: "PRINCIPAL" as const }] }
          : {}),
      });
      router.push(`/reservas/${r.id}`);
    } catch (error) {
      setMensaje(mensajeError(error));
      setTono("error");
    } finally {
      setOcupada(false);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-bold text-text">Nueva reserva</h1>
      <form onSubmit={(e) => void guardar(e)} className="flex flex-col gap-4">
        <Select id="res-tipo" label="Tipo" value={tipo}
          onChange={(e) => setTipo(e.target.value as TipoReservaCodigo)}>
          <option value="ESPACIO">Espacio</option>
          <option value="RECURSO_INTERNO">Recurso interno</option>
          <option value="RECURSO_CAMPUS">Recurso campus</option>
          <option value="RECURSO_EXTERNO">Recurso externo</option>
          <option value="LISTA_ESPERA">Lista de espera</option>
        </Select>
        <Field id="res-unidad" label="Unidad (id)" value={idUnidad}
          onChange={(e) => setIdUnidad(e.target.value)} required />
        {tipo === "ESPACIO" && (
          <>
            <Field id="res-espacio" label="Espacio (id)" value={espacioId}
              onChange={(e) => setEspacioId(e.target.value)} required />
            <Field id="res-fecha" label="Fecha" type="date" value={fecha}
              onChange={(e) => setFecha(e.target.value)} required />
            <div className="flex gap-2">
              <Field id="res-hi" label="Hora inicio" type="time" value={horaInicio}
                onChange={(e) => setHoraInicio(e.target.value)} required />
              <Field id="res-hf" label="Hora fin" type="time" value={horaFin}
                onChange={(e) => setHoraFin(e.target.value)} required />
            </div>
          </>
        )}
        {tipo === "RECURSO_INTERNO" && (
          <>
            <Field id="res-fecha" label="Fecha" type="date" value={fecha}
              onChange={(e) => setFecha(e.target.value)} required />
            <div className="flex gap-2">
              <Field id="res-hi" label="Hora inicio" type="time" value={horaInicio}
                onChange={(e) => setHoraInicio(e.target.value)} required />
              <Field id="res-hf" label="Hora fin" type="time" value={horaFin}
                onChange={(e) => setHoraFin(e.target.value)} required />
            </div>
            <Field id="res-recurso" label="Recurso principal (id)" value={recursoId}
              onChange={(e) => setRecursoId(e.target.value)} required />
          </>
        )}
        {(tipo === "RECURSO_CAMPUS" || tipo === "RECURSO_EXTERNO") && (
          <>
            <div className="flex gap-2">
              <Field id="res-salida" label="Fecha salida" type="date" value={fechaSalida}
                onChange={(e) => setFechaSalida(e.target.value)} required />
              <Field id="res-devolucion" label="Devolución estimada" type="date" value={fechaDevolucion}
                onChange={(e) => setFechaDevolucion(e.target.value)} required />
            </div>
            <Field id="res-recurso" label="Recurso principal (id)" value={recursoId}
              onChange={(e) => setRecursoId(e.target.value)} required />
            <Field id="res-razon" label="Razón de la solicitud" value={razon}
              onChange={(e) => setRazon(e.target.value)} required />
            <Field id="res-lugar" label="Lugar" value={lugarNombre}
              onChange={(e) => setLugarNombre(e.target.value)} required />
            <Field id="res-direccion" label="Dirección" value={lugarDireccion}
              onChange={(e) => setLugarDireccion(e.target.value)} required />
          </>
        )}
        {tipo === "LISTA_ESPERA" && (
          <Field id="res-necesidad" label="Descripción de la necesidad" value={descripcion}
            onChange={(e) => setDescripcion(e.target.value)} required />
        )}
        <Field id="res-proyecto" label="Proyecto (id, opcional)" value={proyectoId}
          onChange={(e) => setProyectoId(e.target.value)} />
        <Field id="res-obs" label="Observación (opcional)" value={observacion}
          onChange={(e) => setObservacion(e.target.value)} />
        <div className="flex gap-2">
          <Button type="button" variant="secondary" disabled={ocupada}
            onClick={() => void consultar()}>
            Consultar disponibilidad
          </Button>
          <Button type="submit" variant="primary" loading={ocupada}>Guardar solicitud</Button>
        </div>
      </form>
      {franjas && (
        <ul className="text-sm text-text">
          {franjas.franjas.map((f, i) => (
            <li key={i}>
              {f.fecha} {f.hora_inicio ?? ""}–{f.hora_fin ?? ""}:{" "}
              {f.disponible ? "disponible" : "no disponible"}
            </li>
          ))}
        </ul>
      )}
      <RegionMensaje texto={mensaje} tono={mensaje ? tono : "muted"} />
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
    if (error.error.codigo === "VALIDACION") return "Revisa los datos ingresados.";
    if (error.status === 429) return "La operación está temporalmente limitada.";
  }
  return "No se pudo crear la reserva: la confirmación depende del servidor.";
}
