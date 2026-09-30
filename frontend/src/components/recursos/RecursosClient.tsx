"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { nombresDeUnidades, SelectorUnidad } from "@/src/components/selectores/selectores";
import { Field } from "@/src/components/ui/Field";
import { CamposRecurso, especializacionDe, valoresIniciales, type ValoresRecurso } from "@/src/components/recursos/CamposRecurso";
import { Insignia } from "@/src/components/ui/Insignia";
import { Modal } from "@/src/components/ui/Modal";
import { Select } from "@/src/components/ui/Select";
import { ApiRequestError } from "@/src/lib/http";
import { crearRecurso, listarRecursos } from "@/src/lib/recursos-api";
import type { RecursoResumen, TipoRecurso } from "@/src/lib/recursos-types";

const NOMBRE_TIPO: Record<string, string> = { EQUIPO: "Equipo", MOBILIARIO: "Mobiliario", OTRO: "Otro" };
const NOMBRE_TIPO_PLURAL: Record<string, string> = { "": "Todos", EQUIPO: "Equipos", MOBILIARIO: "Mobiliario", OTRO: "Otros" };

const ANILLO_FOCO =
  "focus-visible:outline-none focus-visible:ring-4 " +
  "focus-visible:ring-[color-mix(in_srgb,var(--color-sky)_55%,transparent)]";

const ICONO_TIPO: Record<string, ReactNode> = {
  EQUIPO: (
    <>
      <rect x="7" y="7" width="10" height="10" rx="2" />
      <path d="M9 3v4M15 3v4M9 17v4M15 17v4M3 9h4M3 15h4M17 9h4M17 15h4" />
    </>
  ),
  MOBILIARIO: <path d="M4 10h16M6 10v9M18 10v9M8 10V6h8v4" />,
  OTRO: <path d="M21 8l-9-5-9 5 9 5 9-5zM3 8v8l9 5 9-5V8" />,
};

function Ficha({ tipo }: { tipo: string }) {
  return (
    <span
      aria-hidden="true"
      className="flex h-14 w-14 flex-none items-center justify-center rounded-control bg-primary-tint text-primary-2"
    >
      <svg viewBox="0 0 24 24" className="h-7 w-7" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
        {ICONO_TIPO[tipo] ?? ICONO_TIPO.OTRO}
      </svg>
    </span>
  );
}

/** Catálogo (WF-REC-01) con el registro de un recurso en un modal. `puedeGestionar` viene del servidor. */
export function RecursosClient({ puedeGestionar }: { puedeGestionar: boolean }) {
  const router = useRouter();
  const [recursos, setRecursos] = useState<RecursoResumen[] | null>(null);
  const [unidades, setUnidades] = useState<Record<string, string>>({});
  const [registrando, setRegistrando] = useState(false);
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
    // El listado muestra el nombre de la unidad, no su número (un fallo aquí no impide ver los recursos).
    nombresDeUnidades().then(setUnidades).catch(() => undefined);
  }, []);

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

  function abrirRegistro() {
    setMensaje(null);
    setRegistrando(true);
  }

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
      setRegistrando(false);
      setMensaje("Recurso creado.");
      setTono("exito");
    } catch (error) {
      setMensaje(mensajeError(error));
      setTono("error");
    } finally {
      setOcupada(false);
    }
  }

  const hayFiltros = filtroUnidad !== "" || filtroTipo !== "" || busqueda.trim() !== "";

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div className="flex flex-col gap-1">
          <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Recursos</h1>
          <p className="max-w-[60ch] text-[15px] text-muted">
            Equipos, mobiliario y otros elementos que se pueden reservar. Abre uno para ver o editar sus datos.
          </p>
        </div>
        {puedeGestionar && (
          <Button variant="primary" onClick={abrirRegistro}>
            Registrar recurso
          </Button>
        )}
      </div>

      <div className="flex flex-col gap-4 rounded-card border border-border bg-surface p-4 shadow-card md:p-5">
        <div role="group" aria-label="Ver recursos de tipo" className="flex flex-wrap gap-2">
          {["", "EQUIPO", "MOBILIARIO", "OTRO"].map((codigo) => {
            const activo = filtroTipo === codigo;
            return (
              <button
                key={codigo || "todos"}
                type="button"
                aria-pressed={activo}
                onClick={() => setFiltroTipo(codigo)}
                className={`rounded-full border px-4 py-1.5 font-display text-sm font-medium transition-colors ${ANILLO_FOCO} ${
                  activo
                    ? "border-primary-2 bg-primary-2 text-white"
                    : "border-border bg-surface text-text hover:border-primary-1 hover:bg-primary-tint"
                }`}
              >
                {NOMBRE_TIPO_PLURAL[codigo]}
              </button>
            );
          })}
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <Field id="rec-busqueda" label="Buscar por nombre o placa" value={busqueda} onChange={(e) => setBusqueda(e.target.value)} />
          <SelectorUnidad id="rec-filtro-unidad" label="Ver recursos del laboratorio" value={filtroUnidad} onChange={setFiltroUnidad} textoVacio="Todos" />
        </div>
        {hayFiltros && (
          <div>
            <Button variant="ghost" size="sm" onClick={() => { setFiltroTipo(""); setFiltroUnidad(""); setBusqueda(""); }}>
              Quitar filtros
            </Button>
          </div>
        )}
      </div>

      {recursos === null ? (
        <RegionMensaje texto={mensaje ?? "Cargando catálogo…"} tono={mensaje ? tono : "muted"} />
      ) : recursos.length === 0 ? (
        <div className="flex flex-col items-start gap-2 rounded-card border border-dashed border-border bg-surface p-8">
          <p className="font-display text-lg font-bold text-text">No hay recursos con esos criterios.</p>
          <p className="text-sm text-muted">
            {hayFiltros ? "Prueba con otro nombre, tipo o laboratorio." : "Cuando se registren, aparecerán aquí."}
          </p>
          {puedeGestionar && !hayFiltros && (
            <Button variant="secondary" size="sm" onClick={abrirRegistro}>
              Registrar el primero
            </Button>
          )}
        </div>
      ) : (
        <>
          <p className="text-sm text-muted">
            {recursos.length} {recursos.length === 1 ? "recurso" : "recursos"}
          </p>
          <ul aria-label="Recursos" className="grid grid-cols-1 gap-3 md:grid-cols-2">
            {recursos.map((r) => (
              <li key={r.id}>
                <Link
                  href={`/recursos/${r.id}`}
                  className={`group flex h-full items-center gap-4 rounded-card border border-border bg-surface p-4 shadow-card transition-[transform,border-color] duration-150 hover:-translate-y-0.5 hover:border-primary-1 ${ANILLO_FOCO}`}
                >
                  <Ficha tipo={r.tipo} />
                  <span className="flex min-w-0 flex-1 flex-col gap-1">
                    <span className="truncate font-display text-[17px] font-bold leading-snug text-text">
                      {r.nombre ?? `Recurso #${r.id}`}
                    </span>
                    <span className="truncate text-sm text-muted">{unidades[String(r.id_unidad)] ?? "—"}</span>
                    <span className="flex flex-wrap items-center gap-2">
                      <Insignia tono="neutro">{NOMBRE_TIPO[r.tipo] ?? r.tipo}</Insignia>
                      {!r.habilitado && <Insignia tono="error">Deshabilitado</Insignia>}
                    </span>
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </>
      )}

      {!registrando && <RegionMensaje texto={mensaje} tono={mensaje ? tono : "muted"} />}

      {registrando && (
        <Modal
          titulo="Registrar recurso"
          subtitulo="Mobiliario y otros recursos. Los equipos llegan de LIA y no se registran aquí."
          onClose={() => setRegistrando(false)}
          ancho="amplio"
        >
          <form onSubmit={(e) => void guardar(e)} className="flex flex-col gap-4">
            <SelectorUnidad id="rec-unidad" label="Laboratorio" value={idUnidad} onChange={setIdUnidad} requerido />
            <Select id="rec-tipo" label="Tipo" value={tipo}
              onChange={(e) => {
                setTipo(e.target.value as TipoRecurso);
                setValores(valoresIniciales(e.target.value as TipoRecurso));
              }}>
              <option value="MOBILIARIO">Mobiliario</option>
              <option value="OTRO">Otro</option>
            </Select>
            <CamposRecurso tipo={tipo} valores={valores} onChange={setValores} prefijo="rec" />
            <RegionMensaje texto={mensaje} tono={mensaje ? tono : "muted"} />
            <div className="flex flex-wrap items-center gap-3 border-t border-border pt-4">
              <Button type="submit" variant="primary" loading={ocupada}>Guardar recurso</Button>
              <Button type="button" variant="ghost" onClick={() => setRegistrando(false)}>Cancelar</Button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}

function mensajeError(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.error.codigo === "TIPO_INCOMPATIBLE") return "Ese tipo no se puede registrar así.";
    if (error.error.codigo === "UNIDAD_INCOMPATIBLE") return "El laboratorio no es válido para esta operación.";
    if (error.error.codigo === "VALIDACION") return "Revisa los datos ingresados.";
    if (error.error.codigo === "NO_AUTORIZADO" || error.status === 403)
      return "No tienes permiso para crear este recurso.";
    if (error.status === 429) return "La operación está temporalmente limitada.";
  }
  return "No se pudo completar la operación.";
}
