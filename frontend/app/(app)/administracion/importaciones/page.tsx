"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Select } from "@/src/components/ui/Select";
import { ApiRequestError } from "@/src/lib/http";
import {
  confirmarImportacion,
  listarUnidades,
  validarImportacion,
} from "@/src/lib/administracion-api";
import type { Unidad, ValidacionImportacion } from "@/src/lib/administracion-types";

// WF-ADM-04 — specs/modules/administration/wireframes.md
type Catalogo = "PROYECTOS" | "SEMILLEROS" | "EQUIPOS";

export default function PaginaImportaciones() {
  const router = useRouter();
  const [catalogo, setCatalogo] = useState<Catalogo>("PROYECTOS");
  const [idUnidad, setIdUnidad] = useState("");
  const [unidades, setUnidades] = useState<Unidad[]>([]);
  const [archivo, setArchivo] = useState<File | null>(null);
  const [validacion, setValidacion] = useState<ValidacionImportacion | null>(null);
  const [ocupada, setOcupada] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");

  async function cargarUnidades() {
    if (unidades.length > 0) return;
    try {
      const r = await listarUnidades();
      setUnidades(r.datos);
    } catch (error) {
      if (error instanceof ApiRequestError && error.status === 401) {
        router.replace("/login?motivo=sesion_vencida");
      }
    }
  }

  async function validar(evento: FormEvent) {
    evento.preventDefault();
    if (!archivo) {
      setMensaje("Elige un archivo Excel.");
      setTono("error");
      return;
    }
    setOcupada(true);
    setMensaje(null);
    setValidacion(null);
    try {
      const formulario = new FormData();
      formulario.append("archivo", archivo);
      formulario.append("catalogo", catalogo);
      if (catalogo === "EQUIPOS") formulario.append("id_unidad", idUnidad);
      const r = await validarImportacion(formulario);
      setValidacion(r);
      if (!r.confirmable) {
        setMensaje("La carga tiene filas en error y no se puede confirmar.");
        setTono("error");
      }
    } catch (error) {
      setMensaje(mensajeError(error));
      setTono("error");
    } finally {
      setOcupada(false);
    }
  }

  async function confirmar() {
    if (!validacion) return;
    setOcupada(true);
    try {
      const r = await confirmarImportacion(validacion.id);
      setMensaje(`Importación confirmada: ${r.creados} creados, ${r.actualizados} actualizados.`);
      setTono("exito");
      setValidacion(null);
    } catch (error) {
      setMensaje(mensajeError(error));
      setTono("error");
    } finally {
      setOcupada(false);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Importar catálogo</h1>
      <form onSubmit={(e) => void validar(e)} className="flex flex-col gap-4">
        <Select id="imp-catalogo" label="Catálogo" value={catalogo}
          onChange={(e) => setCatalogo(e.target.value as Catalogo)}>
          <option value="PROYECTOS">Proyectos</option>
          <option value="SEMILLEROS">Semilleros</option>
          <option value="EQUIPOS">Equipos</option>
        </Select>
        {catalogo === "EQUIPOS" && (
          <Select id="imp-unidad" label="Unidad destino" value={idUnidad}
            onFocus={() => void cargarUnidades()}
            onChange={(e) => setIdUnidad(e.target.value)} required>
            <option value="">Seleccionar</option>
            {unidades.map((u) => (
              <option key={u.id_unidad} value={u.id_unidad}>{u.nombre}</option>
            ))}
          </Select>
        )}
        <div className="flex flex-col gap-1">
          <label htmlFor="imp-archivo" className="text-sm font-bold text-text">
            Archivo Excel
          </label>
          <input
            id="imp-archivo"
            type="file"
            accept=".xlsx"
            onChange={(e) => setArchivo(e.target.files?.[0] ?? null)}
          />
        </div>
        <div>
          <Button type="submit" variant="primary" loading={ocupada}>Validar</Button>
        </div>
      </form>
      {validacion && (
        <section aria-label="Resultado de validación" className="flex flex-col gap-2">
          <h2 className="text-base font-bold text-text">Resultado</h2>
          <p className="text-sm text-text">
            Nuevos: {validacion.totales.a_crear} · Actualizar: {validacion.totales.a_actualizar} ·{" "}
            Desactivados: {validacion.totales.desactivados} · Errores: {validacion.totales.con_error}
          </p>
          <ul className="flex flex-col gap-1 text-sm text-text">
            {validacion.resultados
              .filter((f) => f.resultado === "ERROR")
              .map((f) => (
                <li key={f.numero_fila}>
                  Fila {f.numero_fila}: {f.detalle}
                </li>
              ))}
          </ul>
          <div>
            <Button variant="success" disabled={ocupada || !validacion.confirmable}
              onClick={() => void confirmar()}>
              Confirmar importación
            </Button>
          </div>
        </section>
      )}
      <RegionMensaje texto={mensaje} tono={mensaje ? tono : "muted"} />
    </div>
  );
}

function mensajeError(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.error.codigo === "CONFLICTO") return "Esta carga no se puede confirmar.";
    if (error.error.codigo === "VALIDACION") return "Revisa el archivo y el catálogo.";
    if (error.error.codigo === "SOLICITUD_INVALIDA") return "Falta la unidad destino para equipos.";
    if (error.status === 429) return "La operación está temporalmente limitada.";
  }
  return "No se pudo completar la operación.";
}
