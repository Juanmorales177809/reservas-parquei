"use client";

import { useState, type FormEvent } from "react";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { Select } from "@/src/components/ui/Select";
import { SelectorEntidad } from "@/src/components/selectores/SelectorEntidad";
import { SelectorEspacio, SelectorRecurso, SelectorUnidad } from "@/src/components/selectores/selectores";
import { listarProyectos, listarSemilleros } from "@/src/lib/investigacion-api";
import { ApiRequestError } from "@/src/lib/http";
import { opcionesContexto } from "@/src/lib/reservas-api";
import {
  consultarReporte,
  exportarReporte,
  type Dimension,
  type FilaReporte,
  type FiltrosReporte,
  type RespuestaReporte,
  type TipoReporte,
} from "@/src/lib/reportes-api";
import { GraficoOcupacion } from "./GraficoOcupacion";

// specs/modules/reports/screens.md: SCR-REP-01 (ocupación), SCR-REP-02 (solicitudes), SCR-REP-03 (lista de espera).

const TITULOS: Record<TipoReporte, string> = {
  ocupacion: "Ocupación",
  solicitudes: "Solicitudes",
  "lista-espera": "Lista de espera",
};

const DIMENSIONES: { valor: Dimension; etiqueta: string; plural: string }[] = [
  { valor: "laboratorio", etiqueta: "Laboratorio", plural: "Laboratorios" },
  { valor: "espacio", etiqueta: "Espacio", plural: "Espacios" },
  { valor: "recurso", etiqueta: "Recurso", plural: "Recursos" },
  { valor: "proyecto", etiqueta: "Proyecto", plural: "Proyectos" },
  { valor: "semillero", etiqueta: "Semillero", plural: "Semilleros" },
];

const NOTA: Record<TipoReporte, string> = {
  ocupacion: "Solo cuentan reservas aprobadas, en ejecución y finalizadas.",
  solicitudes: "Incluye todos los estados: mide demanda, no uso.",
  "lista-espera": "Horas por unidad; no se atribuyen a ningún recurso.",
};

function dia(d: Date): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

/** Propuesta editable (screens.md, ambigüedad 1): el mes en curso. La consulta sigue siendo explícita. */
function mesEnCurso(): { desde: string; hasta: string } {
  const hoy = new Date();
  return {
    desde: dia(new Date(hoy.getFullYear(), hoy.getMonth(), 1)),
    hasta: dia(new Date(hoy.getFullYear(), hoy.getMonth() + 1, 0)),
  };
}

const celda = (v: number | null | undefined) => (v === null || v === undefined ? "—" : String(v));
const porcentaje = (v: number | null | undefined) => (v === null || v === undefined ? "—" : `${v} %`);
const fechaLarga = (iso: string) =>
  new Date(`${iso}T00:00:00`).toLocaleDateString("es-CO", { day: "numeric", month: "short", year: "numeric" });

/** Proyectos: la lista administrativa, o las opciones de la propia cuenta si no es administradora. */
function SelectorProyectoReporte({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  return (
    <SelectorEntidad
      id="rep-proyecto"
      label="Proyecto"
      value={value}
      onChange={onChange}
      textoVacio="Todos"
      cargar={async () => {
        try {
          return (await listarProyectos()).datos
            .filter((p) => p.estado)
            .map((p) => ({ valor: String(p.id_proyecto), etiqueta: `${p.nombre} (${p.codigo})` }));
        } catch (e) {
          if (!(e instanceof ApiRequestError && e.status === 403)) throw e;
          return (await opcionesContexto()).proyectos.map((p) => ({ valor: String(p.id), etiqueta: `${p.nombre} (${p.codigo})` }));
        }
      }}
    />
  );
}

function SelectorSemilleroReporte({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  return (
    <SelectorEntidad
      id="rep-semillero"
      label="Semillero"
      value={value}
      onChange={onChange}
      textoVacio="Todos"
      cargar={async () => {
        try {
          return (await listarSemilleros()).datos
            .filter((s) => s.estado)
            .map((s) => ({ valor: String(s.id_semillero), etiqueta: `${s.nombre} (${s.codigo})` }));
        } catch (e) {
          if (!(e instanceof ApiRequestError && e.status === 403)) throw e;
          return (await opcionesContexto()).semilleros.map((s) => ({ valor: String(s.id), etiqueta: `${s.nombre} (${s.codigo})` }));
        }
      }}
    />
  );
}

interface Columna {
  titulo: string;
  valor: (f: FilaReporte) => string;
}

function columnasDe(tipo: TipoReporte, dimension: Dimension): Columna[] {
  if (tipo === "solicitudes") {
    return [
      { titulo: "Laboratorio", valor: (f) => f.nombre },
      { titulo: "Solicitada", valor: (f) => celda(f.solicitada) },
      { titulo: "Aprobada", valor: (f) => celda(f.aprobada) },
      { titulo: "Rechazada", valor: (f) => celda(f.rechazada) },
      { titulo: "En ejecución", valor: (f) => celda(f.en_ejecucion) },
      { titulo: "Finalizada", valor: (f) => celda(f.finalizada) },
      { titulo: "Cancelada", valor: (f) => celda(f.cancelada) },
    ];
  }
  if (tipo === "lista-espera") {
    return [
      { titulo: "Laboratorio", valor: (f) => f.nombre },
      { titulo: "Reservas", valor: (f) => celda(f.reservas) },
      { titulo: "Horas de ejecución", valor: (f) => celda(f.horas_ejecucion) },
    ];
  }
  const etiqueta = DIMENSIONES.find((d) => d.valor === dimension)!.etiqueta;
  if (dimension === "proyecto" || dimension === "semillero") {
    return [
      { titulo: etiqueta, valor: (f) => f.nombre },
      { titulo: "Horas reservadas", valor: (f) => celda(f.horas_reservadas) },
    ];
  }
  if (dimension === "recurso") {
    return [
      { titulo: etiqueta, valor: (f) => f.nombre },
      { titulo: "Horas reservadas", valor: (f) => celda(f.horas_reservadas) },
      { titulo: "Horas de uso", valor: (f) => celda(f.horas_uso) },
      { titulo: "Ocupación", valor: (f) => porcentaje(f.porcentaje_ocupacion) },
    ];
  }
  return [
    { titulo: etiqueta, valor: (f) => f.nombre },
    { titulo: "Horas reservadas", valor: (f) => celda(f.horas_reservadas) },
    { titulo: "Horas disponibles", valor: (f) => celda(f.horas_disponibles) },
    { titulo: "Ocupación", valor: (f) => porcentaje(f.porcentaje_ocupacion) },
  ];
}

function Tabla({ tipo, dimension, filas }: { tipo: TipoReporte; dimension: Dimension; filas: FilaReporte[] }) {
  const columnas = columnasDe(tipo, dimension);
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr className="border-b border-border text-left">
            {columnas.map((c) => (
              <th key={c.titulo} scope="col" className="px-3 py-2 font-bold text-text">
                {c.titulo}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {filas.map((f, i) => (
            <tr key={i} className="border-b border-border">
              {columnas.map((c) => (
                <td key={c.titulo} className="px-3 py-2 text-text">
                  {c.valor(f)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

interface Consultado {
  filtros: FiltrosReporte;
  dimension: Dimension;
}

export function ReporteClient({ tipo, unidadesAutorizadas }: { tipo: TipoReporte; unidadesAutorizadas: number[] | "GLOBAL" }) {
  const [periodo] = useState(mesEnCurso);
  const [dimension, setDimension] = useState<Dimension>("laboratorio");
  const [desde, setDesde] = useState(periodo.desde);
  const [hasta, setHasta] = useState(periodo.hasta);
  const [unidad, setUnidad] = useState("");
  const [espacio, setEspacio] = useState("");
  const [recurso, setRecurso] = useState("");
  const [proyecto, setProyecto] = useState("");
  const [semillero, setSemillero] = useState("");

  const [estado, setEstado] = useState<"inicial" | "consultando" | "listo" | "denegado">("inicial");
  const [error, setError] = useState<string | null>(null);
  const [resultado, setResultado] = useState<RespuestaReporte | null>(null);
  const [consultado, setConsultado] = useState<Consultado | null>(null);
  const [exportando, setExportando] = useState(false);
  const [avisoExportacion, setAvisoExportacion] = useState<string | null>(null);

  const soloIds = unidadesAutorizadas === "GLOBAL" ? undefined : unidadesAutorizadas;

  async function pedir(c: Consultado, pagina: number) {
    setEstado("consultando");
    setError(null);
    setAvisoExportacion(null);
    try {
      const r = await consultarReporte(tipo, c.filtros, pagina);
      setResultado(r);
      setConsultado(c);
      setEstado("listo");
    } catch (e) {
      setResultado(null);
      setConsultado(null);
      if (e instanceof ApiRequestError && e.status === 403) {
        setEstado("denegado");
        return;
      }
      setEstado("inicial");
      setError(e instanceof ApiRequestError ? e.error.mensaje : "No se pudo consultar el reporte.");
    }
  }

  function consultar(evento: FormEvent) {
    evento.preventDefault();
    const filtros: FiltrosReporte = { desde, hasta, id_unidad: unidad };
    if (tipo === "ocupacion") {
      filtros.dimension = dimension;
      if (dimension === "espacio") filtros.espacio_id = espacio;
      if (dimension === "recurso") filtros.recurso_id = recurso;
      if (dimension === "proyecto") filtros.proyecto_id = proyecto;
      if (dimension === "semillero") filtros.semillero_id = semillero;
    } else if (tipo === "solicitudes") {
      filtros.dimension = "laboratorio";
    }
    void pedir({ filtros, dimension: tipo === "ocupacion" ? dimension : "laboratorio" }, 1);
  }

  async function exportar(formato: "csv" | "excel") {
    if (!consultado) return;
    setExportando(true);
    setAvisoExportacion(null);
    try {
      await exportarReporte(tipo, consultado.filtros, formato);
    } catch (e) {
      setAvisoExportacion(e instanceof Error ? e.message : "No se pudo preparar el archivo.");
    } finally {
      setExportando(false);
    }
  }

  const titulo = TITULOS[tipo];
  const r = resultado;

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-bold text-text">Reportes · {titulo}</h1>

      <form onSubmit={consultar} aria-label={`Consultar ${titulo.toLowerCase()}`} className="grid grid-cols-1 gap-3 md:grid-cols-3">
        {tipo === "ocupacion" && (
          <Select
            id="rep-dimension"
            label="Dimensión"
            value={dimension}
            onChange={(e) => {
              setDimension(e.target.value as Dimension);
              setEspacio("");
              setRecurso("");
              setProyecto("");
              setSemillero("");
            }}
          >
            {DIMENSIONES.map((d) => (
              <option key={d.valor} value={d.valor}>
                {d.etiqueta}
              </option>
            ))}
          </Select>
        )}
        <Field id="rep-desde" label="Desde" type="date" value={desde} onChange={(e) => setDesde(e.target.value)} />
        <Field id="rep-hasta" label="Hasta" type="date" value={hasta} onChange={(e) => setHasta(e.target.value)} />
        <SelectorUnidad
          id="rep-unidad"
          label="Unidad"
          value={unidad}
          soloIds={soloIds}
          textoVacio="Todas"
          onChange={(v) => {
            setUnidad(v);
            setEspacio("");
            setRecurso("");
          }}
        />
        {tipo === "ocupacion" && dimension === "espacio" && (
          <SelectorEspacio id="rep-espacio" label="Espacio" idUnidad={unidad} value={espacio} onChange={setEspacio} />
        )}
        {tipo === "ocupacion" && dimension === "recurso" && (
          <SelectorRecurso id="rep-recurso" label="Recurso" idUnidad={unidad} reservable={false} value={recurso} onChange={setRecurso} />
        )}
        {tipo === "ocupacion" && dimension === "proyecto" && <SelectorProyectoReporte value={proyecto} onChange={setProyecto} />}
        {tipo === "ocupacion" && dimension === "semillero" && <SelectorSemilleroReporte value={semillero} onChange={setSemillero} />}
        <div className="flex items-end">
          <Button type="submit" variant="primary" loading={estado === "consultando"}>
            Consultar
          </Button>
        </div>
      </form>

      <div aria-live="polite" className="flex flex-col gap-2">
        {estado === "consultando" && <p className="text-sm text-muted">Consultando…</p>}
        {estado === "denegado" && (
          <p role="alert" className="text-sm text-error-2">
            No tienes acceso a los reportes.
          </p>
        )}
        {error && (
          <p role="alert" className="text-sm text-error-2">
            {error}
          </p>
        )}
      </div>

      {estado === "listo" && r && consultado && (
        <section aria-label="Resultado" className="flex flex-col gap-3">
          <div className="text-sm text-text">
            <p className="font-bold">
              {tipo === "lista-espera" ? "Lista de espera" : DIMENSIONES.find((d) => d.valor === consultado.dimension)!.plural}
              {" · "}
              {r.resumen.desde && r.resumen.hasta
                ? `${fechaLarga(r.resumen.desde)} – ${fechaLarga(r.resumen.hasta)}`
                : "todo lo registrado"}
              {Object.keys(r.resumen.filtros).length > 0 && " · con filtros"}
            </p>
            <p className="text-muted">{NOTA[tipo]}</p>
          </div>

          {r.datos.length === 0 ? (
            <p className="text-sm text-muted">Sin información para los criterios seleccionados.</p>
          ) : (
            <>
              {tipo === "ocupacion" && (
                <GraficoOcupacion dimension={consultado.dimension} filas={r.datos} hayMasPaginas={r.paginacion.paginas > 1} />
              )}
              <Tabla tipo={tipo} dimension={consultado.dimension} filas={r.datos} />
              <div className="flex flex-wrap items-center gap-3 text-sm text-text">
                <Button variant="secondary" size="sm" disabled={r.paginacion.pagina <= 1} onClick={() => pedir(consultado, r.paginacion.pagina - 1)}>
                  Anterior
                </Button>
                <span>
                  Página {r.paginacion.pagina} de {Math.max(r.paginacion.paginas, 1)} · {r.paginacion.total} filas
                </span>
                <Button variant="secondary" size="sm" disabled={r.paginacion.pagina >= r.paginacion.paginas} onClick={() => pedir(consultado, r.paginacion.pagina + 1)}>
                  Siguiente
                </Button>
              </div>
              <div className="flex flex-wrap items-center gap-3 text-sm text-text">
                <span className="font-bold">Exportar:</span>
                <Button variant="secondary" size="sm" disabled={exportando} onClick={() => exportar("csv")}>
                  CSV
                </Button>
                <Button variant="secondary" size="sm" disabled={exportando} onClick={() => exportar("excel")}>
                  Excel
                </Button>
                {exportando && <span className="text-muted">Preparando el archivo…</span>}
                {avisoExportacion && (
                  <span role="alert" className="text-error-2">
                    {avisoExportacion}
                  </span>
                )}
              </div>
            </>
          )}
        </section>
      )}
    </div>
  );
}
