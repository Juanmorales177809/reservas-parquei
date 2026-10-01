"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { GestionReservaContenido } from "@/src/components/reservas/GestionReservaClient";
import { NuevaReservaForm } from "@/src/components/reservas/NuevaReservaForm";
import { SelectorEspacio, SelectorUnidad } from "@/src/components/selectores/selectores";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { InsigniaEstado } from "@/src/components/ui/Insignia";
import { Modal } from "@/src/components/ui/Modal";
import { Select } from "@/src/components/ui/Select";
import type { ContextoSesion } from "@/src/lib/auth-types";
import { ApiRequestError } from "@/src/lib/http";
import { listarReservas } from "@/src/lib/reservas-api";
import { accionesDe, type VistaGestion } from "@/src/lib/reservas-acciones";
import {
  NOMBRE_ESTADO_RESERVA,
  NOMBRE_TIPO_RESERVA,
  partesPeriodo,
} from "@/src/lib/reservas-nombres";
import type { PaginacionRespuesta, ReservaResumen } from "@/src/lib/reservas-types";

const ANILLO_FOCO =
  "focus-visible:outline-none focus-visible:ring-4 " +
  "focus-visible:ring-[color-mix(in_srgb,var(--color-sky)_55%,transparent)]";

// Atajos de estado: la pregunta más común («¿qué tengo pendiente?») se responde con un toque.
const ATAJOS_ESTADO: { codigo: string; etiqueta: string }[] = [
  { codigo: "", etiqueta: "Todas" },
  { codigo: "SOLICITADA", etiqueta: "Solicitadas" },
  { codigo: "APROBADA", etiqueta: "Aprobadas" },
  { codigo: "EN_EJECUCION", etiqueta: "En curso" },
  { codigo: "FINALIZADA", etiqueta: "Finalizadas" },
  { codigo: "RECHAZADA", etiqueta: "Rechazadas" },
  { codigo: "CANCELADA", etiqueta: "Canceladas" },
];

function Icono({ children }: { children: React.ReactNode }) {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" className="h-4 w-4 flex-none" fill="none" stroke="currentColor"
      strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      {children}
    </svg>
  );
}

/** El «cuándo» de una reserva como una ficha de calendario: se lee de un vistazo. */
function FichaFecha({ periodo }: { periodo: ReservaResumen["periodo"] }) {
  const p = partesPeriodo(periodo);
  if (!p) {
    return (
      <div className="flex h-[68px] w-[68px] flex-none flex-col items-center justify-center gap-0.5 rounded-control bg-disabled-bg text-muted">
        <Icono>
          <circle cx="12" cy="12" r="9" />
          <path d="M12 7v5l3 2" />
        </Icono>
        <span className="text-[11px] font-medium leading-none">Sin fecha</span>
      </div>
    );
  }
  return (
    <div className="flex h-[68px] w-[68px] flex-none flex-col items-center justify-center rounded-control bg-primary-tint text-primary-2">
      <span className="font-display text-2xl font-bold leading-none">{p.dia}</span>
      <span className="mt-0.5 text-xs font-medium capitalize leading-none">{p.mes}</span>
      <span className="mt-0.5 text-[11px] leading-none text-muted">{p.anio}</span>
    </div>
  );
}

export function TarjetaReserva({
  r,
  sesion,
  onAbrir,
}: {
  r: ReservaResumen;
  sesion: ContextoSesion;
  onAbrir: (r: ReservaResumen, vista: VistaGestion) => void;
}) {
  const p = partesPeriodo(r.periodo);
  const nombre = r.objeto ?? "Reserva sin nombre";
  const acciones = accionesDe(r, sesion);
  return (
    <li className="overflow-hidden rounded-card border border-border bg-surface shadow-card transition-[transform,border-color] duration-150 hover:-translate-y-0.5 hover:border-primary-1">
      <Link
        href={`/reservas/${r.id}`}
        aria-label={`Ver reserva de ${nombre}`}
        className={`group flex items-center gap-4 p-4 ${ANILLO_FOCO}`}
      >
        <FichaFecha periodo={r.periodo} />
        <div className="flex min-w-0 flex-1 flex-col gap-1">
          <span className="truncate font-display text-[17px] font-bold leading-snug text-text">{nombre}</span>
          <span className="text-sm text-muted">
            {r.unidad_nombre ?? "—"} · {NOMBRE_TIPO_RESERVA[r.tipo_reserva] ?? r.tipo_reserva}
          </span>
          <span className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-text">
            {p?.detalle && (
              <span className="flex items-center gap-1.5">
                <Icono>
                  <circle cx="12" cy="12" r="9" />
                  <path d="M12 7v5l3 2" />
                </Icono>
                {p.detalle}
              </span>
            )}
            <span className="flex items-center gap-1.5 text-muted">
              <Icono>
                <circle cx="12" cy="8" r="3.5" />
                <path d="M5 20a7 7 0 0114 0" />
              </Icono>
              {r.solicitante_nombre ?? "—"}
            </span>
          </span>
        </div>
        <div className="flex flex-none flex-col items-end gap-2">
          <InsigniaEstado estado={r.estado} texto={NOMBRE_ESTADO_RESERVA[r.estado] ?? r.estado} />
        </div>
      </Link>
      <div className="flex flex-wrap items-center gap-2 border-t border-border bg-[color-mix(in_srgb,var(--color-primary-tint)_35%,var(--color-surface))] px-4 py-3">
        {acciones.map((a) => (
          <Button key={a.etiqueta} variant={a.variante} size="sm" onClick={() => onAbrir(r, a.vista)}>
            {a.etiqueta}
          </Button>
        ))}
        <Button variant="ghost" size="sm" onClick={() => onAbrir(r, "todo")}>
          Ver detalle
        </Button>
      </div>
    </li>
  );
}

function EsqueletoTarjetas() {
  return (
    <ul aria-hidden="true" className="flex flex-col gap-3">
      {[0, 1, 2].map((i) => (
        <li key={i} className="flex animate-pulse items-center gap-4 rounded-card border border-border bg-surface p-4">
          <div className="h-[68px] w-[68px] rounded-control bg-disabled-bg" />
          <div className="flex flex-1 flex-col gap-2">
            <div className="h-4 w-1/3 rounded bg-disabled-bg" />
            <div className="h-3 w-1/2 rounded bg-disabled-bg" />
          </div>
        </li>
      ))}
    </ul>
  );
}

// WF-RES-04 (listado) — specs/modules/reservations/wireframes.md
export function ListadoReservas({ sesion }: { sesion: ContextoSesion }) {
  const router = useRouter();
  const [abierta, setAbierta] = useState<{ r: ReservaResumen; vista: VistaGestion } | null>(null);
  const [creando, setCreando] = useState(false);
  const [recarga, setRecarga] = useState(0);
  const silencioso = useRef(false);
  const [reservas, setReservas] = useState<ReservaResumen[] | null>(null);
  const [paginacion, setPaginacion] = useState<PaginacionRespuesta | null>(null);
  const [estado, setEstado] = useState("");
  const [tipo, setTipo] = useState("");
  const [idUnidad, setIdUnidad] = useState("");
  const [espacioId, setEspacioId] = useState("");
  const [desde, setDesde] = useState("");
  const [hasta, setHasta] = useState("");
  const [pagina, setPagina] = useState(1);
  const [mensaje, setMensaje] = useState<string | null>(null);

  const rangoInvertido = desde !== "" && hasta !== "" && desde > hasta;

  useEffect(() => {
    let cancelado = false;
    if (rangoInvertido) return;
    // Recarga tras una acción del modal: la lista se actualiza sin vaciarse ni mostrar el esqueleto.
    if (!silencioso.current) setReservas(null);
    silencioso.current = false;
    listarReservas({
      pagina,
      ...(desde ? { desde } : {}),
      ...(hasta ? { hasta } : {}),
      ...(estado ? { estado } : {}),
      ...(tipo ? { tipo_reserva: tipo } : {}),
      ...(idUnidad ? { id_unidad: Number(idUnidad) } : {}),
      ...(idUnidad && espacioId ? { espacio_id: Number(espacioId) } : {}),
    })
      .then((r) => {
        if (cancelado) return;
        setReservas(r.datos);
        setPaginacion(r.paginacion);
        setMensaje(null);
      })
      .catch((error) => {
        if (cancelado) return;
        if (error instanceof ApiRequestError && error.status === 401) {
          router.replace("/login?motivo=sesion_vencida");
          return;
        }
        setReservas([]);
        setMensaje("No se pudieron cargar las reservas.");
      });
    return () => {
      cancelado = true;
    };
  }, [estado, tipo, idUnidad, espacioId, desde, hasta, rangoInvertido, pagina, recarga, router]);

  const filtrar = <T,>(poner: (v: T) => void) => (v: T) => {
    setPagina(1);
    poner(v);
  };

  const hayFiltros = estado !== "" || tipo !== "" || idUnidad !== "" || desde !== "" || hasta !== "";

  function limpiar() {
    setPagina(1);
    setEstado("");
    setTipo("");
    setIdUnidad("");
    setEspacioId("");
    setDesde("");
    setHasta("");
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div className="flex flex-col gap-1">
          <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Reservas</h1>
          <p className="max-w-[60ch] text-[15px] text-muted">
            Sigue tus solicitudes y abre cualquiera para ver su detalle.
          </p>
        </div>
        <Button variant="primary" onClick={() => setCreando(true)}>
          Nueva reserva
        </Button>
      </div>

      <div className="flex flex-col gap-4 rounded-card border border-border bg-surface p-4 shadow-card md:p-5">
        <div role="group" aria-label="Estado" className="flex flex-wrap gap-2">
          {ATAJOS_ESTADO.map((a) => {
            const activo = estado === a.codigo;
            return (
              <button
                key={a.codigo || "todas"}
                type="button"
                aria-pressed={activo}
                onClick={() => filtrar(setEstado)(a.codigo)}
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
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Select id="res-tipo" label="Tipo" value={tipo} onChange={(e) => filtrar(setTipo)(e.target.value)}>
            <option value="">Todos</option>
            {Object.entries(NOMBRE_TIPO_RESERVA).map(([codigo, nombre]) => (
              <option key={codigo} value={codigo}>{nombre}</option>
            ))}
          </Select>
          <SelectorUnidad id="res-unidad-filtro" label="Laboratorio" value={idUnidad} textoVacio="Todos"
            onChange={(v) => {
              setPagina(1);
              setIdUnidad(v);
              setEspacioId("");
            }} />
          <Field id="res-desde" label="Desde (fecha de uso)" type="date" value={desde}
            onChange={(e) => filtrar(setDesde)(e.target.value)} />
          <Field id="res-hasta" label="Hasta (fecha de uso)" type="date" value={hasta}
            onChange={(e) => filtrar(setHasta)(e.target.value)} />
          {idUnidad && (
            <SelectorEspacio id="res-espacio-filtro" label="Espacio" idUnidad={idUnidad} value={espacioId}
              onChange={filtrar(setEspacioId)} />
          )}
        </div>
        {hayFiltros && (
          <div>
            <Button variant="ghost" size="sm" onClick={limpiar}>Quitar filtros</Button>
          </div>
        )}
      </div>

      {rangoInvertido && <p className="text-sm text-error-2">«Desde» no puede ser posterior a «Hasta».</p>}
      {reservas === null && !rangoInvertido ? (
        <>
          <RegionMensaje texto="Cargando reservas…" tono="muted" />
          <EsqueletoTarjetas />
        </>
      ) : reservas === null ? null : reservas.length === 0 ? (
        <div className="flex flex-col items-start gap-2 rounded-card border border-dashed border-border bg-surface p-8">
          <p className="font-display text-lg font-bold text-text">Sin reservas.</p>
          <p className="text-sm text-muted">
            {hayFiltros ? "Ninguna reserva coincide con esos filtros." : "Cuando pidas una, aparecerá aquí."}
          </p>
          {!hayFiltros && (
            <div>
              <Button variant="secondary" size="sm" onClick={() => setCreando(true)}>Crear una reserva</Button>
            </div>
          )}
        </div>
      ) : (
        <ul aria-label="Reservas" className="flex flex-col gap-3">
          {reservas.map((r) => (
            <TarjetaReserva key={r.id} r={r} sesion={sesion} onAbrir={(res, vista) => setAbierta({ r: res, vista })} />
          ))}
        </ul>
      )}

      {paginacion && paginacion.paginas > 1 && (
        <nav aria-label="Paginación" className="flex items-center gap-3 text-sm text-text">
          <Button variant="secondary" size="sm" disabled={pagina <= 1} onClick={() => setPagina(pagina - 1)}>
            Anterior
          </Button>
          <span>
            Página {paginacion.pagina} de {paginacion.paginas} · {paginacion.total} reservas
          </span>
          <Button variant="secondary" size="sm" disabled={pagina >= paginacion.paginas}
            onClick={() => setPagina(pagina + 1)}>
            Siguiente
          </Button>
        </nav>
      )}
      <RegionMensaje texto={mensaje} tono={mensaje ? "error" : "muted"} />

      {creando && (
        <Modal
          titulo="Nueva reserva"
          subtitulo="Cuéntanos qué necesitas y cuándo. El formulario se ajusta a lo que elijas."
          ancho="amplio"
          onClose={() => setCreando(false)}
        >
          <NuevaReservaForm
            enModal
            onCancelar={() => setCreando(false)}
            onCreada={(id) => {
              setCreando(false);
              router.push(`/reservas/${id}`);
            }}
          />
        </Modal>
      )}

      {abierta && (
        <Modal
          titulo={abierta.r.objeto ?? `Reserva #${abierta.r.id}`}
          subtitulo={`${abierta.r.unidad_nombre ?? "—"} · ${NOMBRE_TIPO_RESERVA[abierta.r.tipo_reserva] ?? abierta.r.tipo_reserva}`}
          onClose={() => setAbierta(null)}
        >
          <GestionReservaContenido
            id={abierta.r.id}
            sesion={sesion}
            vista={abierta.vista}
            enModal
            onCambio={() => {
              silencioso.current = true;
              setRecarga((n) => n + 1);
            }}
          />
          <div className="mt-5 border-t border-border pt-3">
            <Link href={`/reservas/${abierta.r.id}`} className={`rounded-control text-sm font-medium text-primary-2 underline-offset-4 hover:underline ${ANILLO_FOCO}`}>
              Abrir la página completa de la reserva
            </Link>
          </div>
        </Modal>
      )}
    </div>
  );
}
