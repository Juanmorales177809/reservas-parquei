"use client";

import Link from "next/link";
import { useState, type FormEvent } from "react";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { SelectorUnidad } from "@/src/components/selectores/selectores";
import { ApiRequestError } from "@/src/lib/http";
import { consultarResumen, type ResumenRespuesta } from "@/src/lib/reportes-api";
import type { Rol } from "@/src/lib/auth-types";
import { BarrasHorizontales, SeriePorFecha } from "./GraficosInicio";

// SCR-REP-04 — specs/modules/reports/screens.md

const DIAS = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];
const ORDEN_DIAS = [1, 2, 3, 4, 5, 6, 0];
const HORAS = Array.from({ length: 13 }, (_, i) => 7 + i);

function dia(d: Date): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

/** Propuesta editable: el mes en curso. La consulta sigue siendo explícita. */
function mesEnCurso(): { desde: string; hasta: string } {
  const hoy = new Date();
  return {
    desde: dia(new Date(hoy.getFullYear(), hoy.getMonth(), 1)),
    hasta: dia(new Date(hoy.getFullYear(), hoy.getMonth() + 1, 0)),
  };
}

const guion = (v: number | null | undefined) => (v === null || v === undefined ? "—" : String(v));
const fechaLarga = (iso: string) =>
  new Date(`${iso}T00:00:00`).toLocaleDateString("es-CO", { day: "numeric", month: "short", year: "numeric" });

function MapaDeCalor({ celdas }: { celdas: ResumenRespuesta["ocupacion_dia_hora"] }) {
  const maximo = Math.max(1, ...celdas.map((c) => c.cantidad));
  const porCelda = new Map(celdas.map((c) => [`${c.dia}-${c.hora}`, c.cantidad]));
  return (
    <section aria-label="Mapa de calor por día y hora" className="flex flex-col gap-2 rounded-control border border-border bg-surface p-4">
      <h2 className="text-base font-bold text-text">Mapa de calor por día y hora</h2>
      <p className="text-xs text-muted">Cantidad de reservas de uso por día y hora, de 7 a 19. Las horas fuera de ese rango cuentan en la ocupación pero no se dibujan.</p>
      <div className="overflow-x-auto">
        <table className="border-collapse text-center text-xs">
          <thead>
            <tr>
              <th scope="col" className="px-2 py-1 text-left font-bold text-text">Día</th>
              {HORAS.map((h) => (
                <th key={h} scope="col" className="px-2 py-1 font-bold text-muted">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ORDEN_DIAS.map((d) => (
              <tr key={d}>
                <th scope="row" className="px-2 py-1 text-left font-bold text-text">{DIAS[d]}</th>
                {HORAS.map((h) => {
                  const valor = porCelda.get(`${d}-${h}`) ?? 0;
                  return (
                    <td
                      key={h}
                      className="h-7 min-w-9 border border-border px-1"
                      title={`${DIAS[d]} ${h}:00 — ${valor} reservas`}
                      style={
                        valor > 0
                          ? { backgroundColor: `color-mix(in srgb, var(--color-primary-1) ${(25 + Math.round((valor / maximo) * 75)).toString()}%, transparent)` }
                          : undefined
                      }
                    >
                      {valor > 0 ? valor : <span className="text-muted">·</span>}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function TarjetaIndicador({ titulo, actual, previo, sufijo = "" }: { titulo: string; actual: string; previo: string; sufijo?: string }) {
  return (
    <div className="rounded-card border border-border bg-surface p-4 shadow-card">
      <p className="text-sm text-muted">{titulo}</p>
      <p className="font-display text-2xl font-bold text-text">
        {actual}
        {sufijo && <span className="text-base font-medium text-muted"> {sufijo}</span>}
      </p>
      <p className="text-xs text-muted">Antes: {previo}</p>
    </div>
  );
}

export function InicioClient({ rol, unidadesAutorizadas }: { rol: Rol; unidadesAutorizadas: number[] | "GLOBAL" }) {
  // El Usuario no ejerce ningún permiso (FE-41): ve accesos y nunca llama al resumen.
  if (rol === "USUARIO") {
    return (
      <div className="flex flex-col gap-4">
        <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Inicio</h1>
        <p className="text-sm text-muted">Tus reservas, en un vistazo.</p>
        <nav aria-label="Accesos directos" className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {[
            { href: "/reservas", titulo: "Mis reservas", descripcion: "Ver y seguir tus solicitudes." },
            { href: "/reservas/nueva", titulo: "Nueva reserva", descripcion: "Pedir un espacio o un recurso." },
            { href: "/usuarios/perfil", titulo: "Mi perfil", descripcion: "Tus datos y vinculaciones." },
          ].map((a) => (
            <Link key={a.href} href={a.href} className="rounded-card border border-border bg-surface p-5 shadow-card hover:border-primary-1">
              <span className="font-display text-base font-bold text-primary-2">{a.titulo}</span>
              <span className="mt-1 block text-sm text-muted">{a.descripcion}</span>
            </Link>
          ))}
        </nav>
      </div>
    );
  }

  return <PanelGestion unidadesAutorizadas={unidadesAutorizadas} />;
}

function PanelGestion({ unidadesAutorizadas }: { unidadesAutorizadas: number[] | "GLOBAL" }) {
  const [periodo] = useState(mesEnCurso);
  const [desde, setDesde] = useState(periodo.desde);
  const [hasta, setHasta] = useState(periodo.hasta);
  const [unidad, setUnidad] = useState("");

  const [estado, setEstado] = useState<"inicial" | "consultando" | "listo" | "denegado">("inicial");
  const [error, setError] = useState<string | null>(null);
  const [resultado, setResultado] = useState<ResumenRespuesta | null>(null);

  const soloIds = unidadesAutorizadas === "GLOBAL" ? undefined : unidadesAutorizadas;

  async function consultar(evento: FormEvent) {
    evento.preventDefault();
    setEstado("consultando");
    setError(null);
    try {
      const r = await consultarResumen({ desde, hasta, id_unidad: unidad });
      setResultado(r);
      setEstado("listo");
    } catch (e) {
      setResultado(null);
      if (e instanceof ApiRequestError && e.status === 403) {
        setEstado("denegado");
        return;
      }
      setEstado("inicial");
      setError(e instanceof ApiRequestError ? e.error.mensaje : "No se pudo consultar el resumen.");
    }
  }

  const r = resultado;

  return (
    <div className="flex flex-col gap-4">
      <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Inicio</h1>

      <form onSubmit={consultar} aria-label="Consultar resumen" className="grid grid-cols-1 gap-4 rounded-card border border-border bg-surface p-5 shadow-card md:grid-cols-4">
        <Field id="inicio-desde" label="Desde" type="date" value={desde} onChange={(e) => setDesde(e.target.value)} />
        <Field id="inicio-hasta" label="Hasta" type="date" value={hasta} onChange={(e) => setHasta(e.target.value)} />
        <SelectorUnidad id="inicio-unidad" label="Laboratorio" value={unidad} soloIds={soloIds} textoVacio="Todos" onChange={setUnidad} />
        <div className="flex items-end">
          <Button type="submit" variant="primary" loading={estado === "consultando"}>
            Consultar
          </Button>
        </div>
      </form>

      <div aria-live="polite" className="flex flex-col gap-2">
        {estado === "consultando" && <p className="text-sm text-muted">Consultando…</p>}
        {estado === "denegado" && (
          <p role="alert" className="text-sm text-error-2">No tienes acceso a los reportes.</p>
        )}
        {error && (
          <p role="alert" className="text-sm text-error-2">{error}</p>
        )}
      </div>

      {estado === "listo" && r && (
        <section aria-label="Resumen del periodo" className="flex flex-col gap-4">
          <p className="text-sm font-bold text-text">
            {fechaLarga(r.resumen.desde)} – {fechaLarga(r.resumen.hasta)}
            <span className="font-normal text-muted"> · previo {fechaLarga(r.resumen.desde_previo)} – {fechaLarga(r.resumen.hasta_previo)}</span>
          </p>

          {r.indicadores.reservas.actual === 0 ? (
            <p className="text-sm text-muted">Sin información para los criterios seleccionados.</p>
          ) : (
            <>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <TarjetaIndicador
                  titulo="Reservas"
                  actual={String(r.indicadores.reservas.actual)}
                  previo={String(r.indicadores.reservas.previo)}
                />
                <TarjetaIndicador titulo="Solicitadas" actual={String(r.indicadores.solicitadas)} previo="esperan decisión" />
                <TarjetaIndicador
                  titulo="Horas reservadas"
                  actual={String(r.indicadores.horas_reservadas.actual)}
                  previo={String(r.indicadores.horas_reservadas.previo)}
                  sufijo="h"
                />
                <TarjetaIndicador
                  titulo="Ocupación"
                  actual={r.indicadores.porcentaje_ocupacion.actual === null ? "—" : String(r.indicadores.porcentaje_ocupacion.actual)}
                  previo={r.indicadores.porcentaje_ocupacion.previo === null ? "sin horario" : String(r.indicadores.porcentaje_ocupacion.previo)}
                  sufijo={r.indicadores.porcentaje_ocupacion.actual === null ? "" : "%"}
                />
              </div>

              <section aria-label="Por estado" className="flex flex-col gap-2 rounded-control border border-border bg-surface p-4">
                <h2 className="text-base font-bold text-text">Por estado</h2>
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse text-sm">
                    <thead>
                      <tr className="border-b border-border text-left">
                        {["Solicitada", "Aprobada", "Rechazada", "En ejecución", "Finalizada", "Cancelada"].map((t) => (
                          <th key={t} scope="col" className="px-3 py-2 font-bold text-text">{t}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-border">
                        {["solicitada", "aprobada", "rechazada", "en_ejecucion", "finalizada", "cancelada"].map((k) => (
                          <td key={k} className="px-3 py-2 text-text">{guion(r.por_estado[k])}</td>
                        ))}
                      </tr>
                    </tbody>
                  </table>
                </div>
              </section>

              {r.por_fecha.length > 0 && <SeriePorFecha puntos={r.por_fecha} />}

              <section aria-label="Por laboratorio" className="flex flex-col gap-2 rounded-control border border-border bg-surface p-4">
                <h2 className="text-base font-bold text-text">Por laboratorio</h2>
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse text-sm">
                    <thead>
                      <tr className="border-b border-border text-left">
                        <th scope="col" className="px-3 py-2 font-bold text-text">Laboratorio</th>
                        <th scope="col" className="px-3 py-2 font-bold text-text">Reservas</th>
                        <th scope="col" className="px-3 py-2 font-bold text-text">Horas reservadas</th>
                        <th scope="col" className="px-3 py-2 font-bold text-text">Ocupación</th>
                      </tr>
                    </thead>
                    <tbody>
                      {r.por_laboratorio.map((f) => (
                        <tr key={f.id_unidad} className="border-b border-border">
                          <td className="px-3 py-2 text-text">{f.nombre}</td>
                          <td className="px-3 py-2 text-text">{f.reservas}</td>
                          <td className="px-3 py-2 text-text">{f.horas_reservadas}</td>
                          <td className="px-3 py-2 text-text">{f.porcentaje_ocupacion === null ? "—" : `${f.porcentaje_ocupacion} %`}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
              {r.por_laboratorio.length > 0 && (
                <BarrasHorizontales
                  titulo="Reservas por laboratorio"
                  filas={r.por_laboratorio.map((f) => ({ nombre: f.nombre, valor: f.reservas }))}
                  unidad=""
                />
              )}

              {r.recursos_mas_reservados.length > 0 && (
                <BarrasHorizontales
                  titulo="Recursos más reservados"
                  filas={r.recursos_mas_reservados.map((f) => ({ nombre: f.nombre, valor: f.reservas }))}
                  unidad=""
                />
              )}

              {r.ocupacion_dia_hora.length > 0 && <MapaDeCalor celdas={r.ocupacion_dia_hora} />}
            </>
          )}

          <nav aria-label="Ver reportes" className="flex flex-wrap gap-3 text-sm">
            <span className="font-bold text-text">Ver:</span>
            <Link href="/reportes/ocupacion" className="font-bold text-primary-2 underline-offset-4 hover:underline">Ocupación</Link>
            <Link href="/reportes/solicitudes" className="font-bold text-primary-2 underline-offset-4 hover:underline">Solicitudes</Link>
            <Link href="/reportes/lista-espera" className="font-bold text-primary-2 underline-offset-4 hover:underline">Lista de espera</Link>
          </nav>
        </section>
      )}
    </div>
  );
}
