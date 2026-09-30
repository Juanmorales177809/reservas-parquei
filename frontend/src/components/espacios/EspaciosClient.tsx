"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { SelectorRecursosVarios } from "@/src/components/selectores/SelectorRecursosVarios";
import { nombresDeUnidades, SelectorUnidad } from "@/src/components/selectores/selectores";
import { Field } from "@/src/components/ui/Field";
import { Insignia } from "@/src/components/ui/Insignia";
import { Modal } from "@/src/components/ui/Modal";
import { ApiRequestError } from "@/src/lib/http";
import { crearEspacio, listarEspacios } from "@/src/lib/espacios-api";
import type { EspacioResumen } from "@/src/lib/espacios-types";

const ANILLO_FOCO =
  "focus-visible:outline-none focus-visible:ring-4 " +
  "focus-visible:ring-[color-mix(in_srgb,var(--color-sky)_55%,transparent)]";

const ATAJOS_ESTADO: { valor: string; etiqueta: string }[] = [
  { valor: "", etiqueta: "Todos" },
  { valor: "true", etiqueta: "Habilitados" },
  { valor: "false", etiqueta: "Deshabilitados" },
];

/** Catálogo (WF-ESP-04) con el registro de un espacio (WF-ESP-01) en un modal, igual que el de recursos. */
export function EspaciosClient({ puedeGestionar }: { puedeGestionar: boolean }) {
  const router = useRouter();
  const [espacios, setEspacios] = useState<EspacioResumen[] | null>(null);
  const [laboratorios, setLaboratorios] = useState<Record<string, string>>({});
  const [registrando, setRegistrando] = useState(false);
  const [idUnidad, setIdUnidad] = useState("");
  const [nombre, setNombre] = useState("");
  const [capacidad, setCapacidad] = useState("");
  const [ubicacion, setUbicacion] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [recursos, setRecursos] = useState<string[]>([]);
  const [filtroUnidad, setFiltroUnidad] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("");
  const [filtroCapacidad, setFiltroCapacidad] = useState("");
  const [ocupada, setOcupada] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");

  async function recargar() {
    const r = await listarEspacios({
      ...(filtroUnidad ? { id_unidad: Number(filtroUnidad) } : {}),
      ...(filtroEstado ? { habilitado: filtroEstado === "true" } : {}),
      ...(filtroCapacidad && Number(filtroCapacidad) > 0 ? { capacidad_minima: Number(filtroCapacidad) } : {}),
    });
    setEspacios(r.datos);
  }

  useEffect(() => {
    // El listado muestra el nombre del laboratorio, no su número (un fallo aquí no impide ver los espacios).
    nombresDeUnidades().then(setLaboratorios).catch(() => undefined);
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
        setMensaje("No se pudieron cargar los espacios.");
        setTono("error");
      });
    }, filtroCapacidad ? 300 : 0); // la capacidad espera a que se deje de escribir
    return () => {
      cancelado = true;
      window.clearTimeout(espera);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router, filtroUnidad, filtroEstado, filtroCapacidad]);

  function abrirRegistro() {
    setMensaje(null);
    setRegistrando(true);
  }

  async function guardar(evento: FormEvent) {
    evento.preventDefault();
    setOcupada(true);
    setMensaje(null);
    try {
      await crearEspacio({
        id_unidad: Number(idUnidad),
        nombre: nombre.trim(),
        capacidad: Number(capacidad),
        ...(ubicacion.trim() ? { ubicacion: ubicacion.trim() } : {}),
        ...(descripcion.trim() ? { descripcion: descripcion.trim() } : {}),
        ...(recursos.length > 0 ? { recursos: recursos.map(Number) } : {}),
      });
      setNombre("");
      setCapacidad("");
      setUbicacion("");
      setDescripcion("");
      setRecursos([]);
      await recargar();
      setRegistrando(false);
      setMensaje("Espacio creado.");
      setTono("exito");
    } catch (error) {
      setMensaje(mensajeError(error));
      setTono("error");
    } finally {
      setOcupada(false);
    }
  }

  const hayFiltros = filtroUnidad !== "" || filtroEstado !== "" || filtroCapacidad !== "";

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div className="flex flex-col gap-1">
          <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Espacios</h1>
          <p className="max-w-[60ch] text-[15px] text-muted">
            Salas y áreas que se pueden reservar. Abre una para ver sus datos, sus recursos y la información que pide al reservar.
          </p>
        </div>
        {puedeGestionar && (
          <Button variant="primary" onClick={abrirRegistro}>
            Registrar espacio
          </Button>
        )}
      </div>

      <div className="flex flex-col gap-4 rounded-card border border-border bg-surface p-4 shadow-card md:p-5">
        <div role="group" aria-label="Estado" className="flex flex-wrap gap-2">
          {ATAJOS_ESTADO.map((a) => {
            const activo = filtroEstado === a.valor;
            return (
              <button
                key={a.valor || "todos"}
                type="button"
                aria-pressed={activo}
                onClick={() => setFiltroEstado(a.valor)}
                className={`rounded-full border px-4 py-1.5 font-display text-sm font-medium transition-colors ${ANILLO_FOCO} ${
                  activo
                    ? "border-primary-2 bg-primary-2 text-white"
                    : "border-border bg-surface text-text hover:border-primary-1 hover:bg-primary-tint"
                }`}
              >
                {a.etiqueta}
              </button>
            );
          })}
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <SelectorUnidad id="esp-filtro-unidad" label="Ver espacios del laboratorio" value={filtroUnidad}
            onChange={setFiltroUnidad} textoVacio="Todos" />
          <Field id="esp-filtro-capacidad" label="Capacidad mínima" type="number" value={filtroCapacidad}
            onChange={(e) => setFiltroCapacidad(e.target.value)} />
        </div>
        {hayFiltros && (
          <div>
            <Button variant="ghost" size="sm" onClick={() => { setFiltroUnidad(""); setFiltroEstado(""); setFiltroCapacidad(""); }}>
              Quitar filtros
            </Button>
          </div>
        )}
      </div>

      {espacios === null ? (
        <RegionMensaje texto={mensaje ?? "Cargando espacios…"} tono={mensaje ? tono : "muted"} />
      ) : espacios.length === 0 ? (
        <div className="flex flex-col items-start gap-2 rounded-card border border-dashed border-border bg-surface p-8">
          <p className="font-display text-lg font-bold text-text">No hay espacios con esos criterios.</p>
          <p className="text-sm text-muted">
            {hayFiltros ? "Prueba con otro laboratorio, estado o capacidad." : "Cuando se registren, aparecerán aquí."}
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
            {espacios.length} {espacios.length === 1 ? "espacio" : "espacios"}
          </p>
          <ul aria-label="Espacios" className="grid grid-cols-1 gap-3 md:grid-cols-2">
            {espacios.map((e) => (
              <li key={e.id}>
                <Link
                  href={`/espacios/${e.id}`}
                  className={`group flex h-full items-center gap-4 rounded-card border border-border bg-surface p-4 shadow-card transition-[transform,border-color] duration-150 hover:-translate-y-0.5 hover:border-primary-1 ${ANILLO_FOCO}`}
                >
                  <span
                    aria-hidden="true"
                    className="flex h-14 w-14 flex-none items-center justify-center rounded-control bg-primary-tint text-primary-2"
                  >
                    <svg viewBox="0 0 24 24" className="h-7 w-7" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M3 21h18M5 21V5a2 2 0 012-2h10a2 2 0 012 2v16" />
                      <path d="M9 7h2M13 7h2M9 11h2M13 11h2M10 21v-4h4v4" />
                    </svg>
                  </span>
                  <span className="flex min-w-0 flex-1 flex-col gap-1">
                    <span className="truncate font-display text-[17px] font-bold leading-snug text-text">{e.nombre}</span>
                    <span className="truncate text-sm text-muted">{laboratorios[String(e.id_unidad)] ?? "—"}</span>
                    <span className="flex flex-wrap items-center gap-2">
                      <Insignia tono="neutro">Capacidad {e.capacidad}</Insignia>
                      {!e.habilitado && <Insignia tono="error">Deshabilitado</Insignia>}
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
          titulo="Registrar espacio"
          subtitulo="Elige el laboratorio, completa sus datos y asocia sus equipos y recursos. Los campos adicionales se agregan después, desde el espacio."
          onClose={() => setRegistrando(false)}
        >
          <form onSubmit={(e) => void guardar(e)} className="flex flex-col gap-4">
            <SelectorUnidad id="esp-unidad" label="Laboratorio" value={idUnidad} onChange={(v) => { setIdUnidad(v); setRecursos([]); }} requerido />
            <Field id="esp-nombre" label="Nombre" value={nombre}
              onChange={(e) => setNombre(e.target.value)} required />
            <Field id="esp-capacidad" label="Capacidad" type="number" value={capacidad}
              onChange={(e) => setCapacidad(e.target.value)} required />
            <Field id="esp-ubicacion" label="Ubicación (opcional)" value={ubicacion}
              onChange={(e) => setUbicacion(e.target.value)} />
            <Field id="esp-descripcion" label="Descripción (opcional)" value={descripcion}
              onChange={(e) => setDescripcion(e.target.value)} />
            <SelectorRecursosVarios label="Equipos y recursos del espacio (opcional)" idUnidad={idUnidad}
              reservable={false} value={recursos} onChange={setRecursos} />
            <RegionMensaje texto={mensaje} tono={mensaje ? tono : "muted"} />
            <div className="flex flex-wrap items-center gap-3 border-t border-border pt-4">
              <Button type="submit" variant="primary" loading={ocupada}>Guardar espacio</Button>
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
    if (error.error.codigo === "NOMBRE_DUPLICADO") return "Ese nombre ya existe en el laboratorio.";
    // Un recurso solo puede estar asociado a un espacio a la vez (contrato §2.1).
    if (error.error.codigo === "CONFLICTO") return "Alguno de los recursos elegidos ya está asociado a otro espacio. Quítalo de la selección o retíralo de ese espacio.";
    if (error.error.codigo === "UNIDAD_INCOMPATIBLE") return "Un recurso elegido es de otro laboratorio.";
    if (error.error.codigo === "VALIDACION") return "Revisa los datos ingresados.";
    if (error.status === 429) return "La operación está temporalmente limitada.";
  }
  return "No se pudo completar la operación.";
}
