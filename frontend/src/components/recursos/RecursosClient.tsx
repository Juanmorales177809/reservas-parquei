"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { SelectorUnidad } from "@/src/components/selectores/selectores";
import { Field } from "@/src/components/ui/Field";
import { CamposRecurso, especializacionDe, valoresIniciales, type ValoresRecurso } from "@/src/components/recursos/CamposRecurso";
import { Select } from "@/src/components/ui/Select";
import { ApiRequestError } from "@/src/lib/http";
import { crearRecurso, listarRecursos } from "@/src/lib/recursos-api";
import type { RecursoResumen, TipoRecurso } from "@/src/lib/recursos-types";

const NOMBRE_TIPO: Record<string, string> = { EQUIPO: "Equipo", MOBILIARIO: "Mobiliario", OTRO: "Otro" };

/** Catálogo y registro (WF-REC-01). `puedeGestionar` viene del servidor. */
export function RecursosClient({ puedeGestionar }: { puedeGestionar: boolean }) {
  const router = useRouter();
  const [recursos, setRecursos] = useState<RecursoResumen[] | null>(null);
  const [tipo, setTipo] = useState<TipoRecurso>("MOBILIARIO");
  const [idUnidad, setIdUnidad] = useState("");
  const [valores, setValores] = useState<ValoresRecurso>(() => valoresIniciales("MOBILIARIO"));
  const [filtroUnidad, setFiltroUnidad] = useState("");
  const [filtroTipo, setFiltroTipo] = useState("");
  const [busqueda, setBusqueda] = useState("");
  const [ocupada, setOcupada] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");

  async function recargar() {
    const r = await listarRecursos({
      ...(filtroUnidad ? { id_unidad: Number(filtroUnidad) } : {}),
      ...(filtroTipo ? { tipo: filtroTipo } : {}),
      ...(busqueda.trim() ? { busqueda: busqueda.trim() } : {}),
    });
    setRecursos(r.datos);
  }

  useEffect(() => {
    let cancelado = false;
    const espera = window.setTimeout(() => {
      recargar().catch((err) => {
        if (cancelado) return;
        if (err instanceof ApiRequestError && err.status === 401) {
          router.replace("/login?motivo=sesion_vencida");
          return;
        }
        setMensaje("No se pudo cargar el catálogo.");
        setTono("error");
      });
    }, busqueda ? 300 : 0); // la búsqueda por texto espera a que se deje de escribir
    return () => {
      cancelado = true;
      window.clearTimeout(espera);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router, filtroUnidad, filtroTipo, busqueda]);

  async function guardar(evento: FormEvent) {
    evento.preventDefault();
    setOcupada(true);
    setMensaje(null);
    try {
      await crearRecurso({
        id_unidad: Number(idUnidad),
        tipo,
        especializacion: especializacionDe(tipo, valores),
      });
      setValores(valoresIniciales(tipo));
      await recargar();
      setMensaje("Recurso creado.");
      setTono("exito");
    } catch (error) {
      setMensaje(mensajeError(error));
      setTono("error");
    } finally {
      setOcupada(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-text">Recursos</h1>
      <div className="flex flex-wrap items-end gap-3">
        <SelectorUnidad id="rec-filtro-unidad" label="Ver recursos de la unidad" value={filtroUnidad} onChange={setFiltroUnidad} textoVacio="Todas" />
        <Select id="rec-filtro-tipo" label="Ver recursos de tipo" value={filtroTipo} onChange={(e) => setFiltroTipo(e.target.value)}>
          <option value="">Todos</option>
          {Object.entries(NOMBRE_TIPO).map(([codigo, nombre]) => (
            <option key={codigo} value={codigo}>{nombre}</option>
          ))}
        </Select>
        <Field id="rec-busqueda" label="Buscar por nombre o placa" value={busqueda} onChange={(e) => setBusqueda(e.target.value)} />
      </div>
      {recursos === null ? (
        <RegionMensaje texto={mensaje ?? "Cargando catálogo…"} tono={mensaje ? tono : "muted"} />
      ) : (
        <ul className="flex flex-col gap-1 text-sm text-text">
          {recursos.length === 0 && <li className="text-muted">No hay recursos con esos criterios.</li>}
          {recursos.map((r) => (
            <li key={r.id}>
              <Link href={`/recursos/${r.id}`} className="font-bold text-primary-2">
                {r.nombre ?? `Recurso #${r.id}`} · {NOMBRE_TIPO[r.tipo] ?? r.tipo}
              </Link>{" "}
              {!r.habilitado && "(deshabilitado)"}
            </li>
          ))}
        </ul>
      )}
      {puedeGestionar && (
        <form onSubmit={(e) => void guardar(e)} className="flex flex-col gap-4">
          <h2 className="text-base font-bold text-text">Registrar recurso</h2>
          <SelectorUnidad id="rec-unidad" label="Unidad" value={idUnidad} onChange={setIdUnidad} requerido />
          <Select id="rec-tipo" label="Tipo" value={tipo}
            onChange={(e) => {
              setTipo(e.target.value as TipoRecurso);
              setValores(valoresIniciales(e.target.value as TipoRecurso));
            }}>
            <option value="MOBILIARIO">Mobiliario</option>
            <option value="OTRO">Otro</option>
            <option value="EQUIPO">Equipo (solo Administrador global)</option>
          </Select>
          <CamposRecurso tipo={tipo} valores={valores} onChange={setValores} prefijo="rec" />
          <div>
            <Button type="submit" variant="primary" loading={ocupada}>Guardar recurso</Button>
          </div>
        </form>
      )}
      <RegionMensaje texto={mensaje} tono={mensaje ? tono : "muted"} />
    </div>
  );
}

function mensajeError(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.error.codigo === "TIPO_INCOMPATIBLE") return "Ese tipo no se puede registrar así.";
    if (error.error.codigo === "UNIDAD_INCOMPATIBLE") return "La unidad no es válida para esta operación.";
    if (error.error.codigo === "VALIDACION") return "Revisa los datos ingresados.";
    if (error.error.codigo === "NO_AUTORIZADO" || error.status === 403)
      return "No tienes permiso para crear este recurso.";
    if (error.status === 429) return "La operación está temporalmente limitada.";
  }
  return "No se pudo completar la operación.";
}
