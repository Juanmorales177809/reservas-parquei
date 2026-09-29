"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { SelectorEspacio, SelectorUnidad } from "@/src/components/selectores/selectores";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { Select } from "@/src/components/ui/Select";
import { ApiRequestError } from "@/src/lib/http";
import { listarReservas } from "@/src/lib/reservas-api";
import {
  NOMBRE_ESTADO_RESERVA,
  NOMBRE_TIPO_RESERVA,
  periodoLegible,
} from "@/src/lib/reservas-nombres";
import type { PaginacionRespuesta, ReservaResumen } from "@/src/lib/reservas-types";

// WF-RES-04 (listado) — specs/modules/reservations/wireframes.md
export default function PaginaReservas() {
  const router = useRouter();
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
    setReservas(null);
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
  }, [estado, tipo, idUnidad, espacioId, desde, hasta, rangoInvertido, pagina, router]);

  const filtrar = <T,>(poner: (v: T) => void) => (v: T) => {
    setPagina(1);
    poner(v);
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-text">Reservas</h1>
        <Link href="/reservas/nueva">
          <Button variant="primary">Nueva reserva</Button>
        </Link>
      </div>

      <div className="flex flex-wrap items-end gap-3">
        <Select id="res-estado" label="Estado" value={estado} onChange={(e) => filtrar(setEstado)(e.target.value)}>
          <option value="">Todos</option>
          {Object.entries(NOMBRE_ESTADO_RESERVA).map(([codigo, nombre]) => (
            <option key={codigo} value={codigo}>{nombre}</option>
          ))}
        </Select>
        <Select id="res-tipo" label="Tipo" value={tipo} onChange={(e) => filtrar(setTipo)(e.target.value)}>
          <option value="">Todos</option>
          {Object.entries(NOMBRE_TIPO_RESERVA).map(([codigo, nombre]) => (
            <option key={codigo} value={codigo}>{nombre}</option>
          ))}
        </Select>
        <SelectorUnidad id="res-unidad-filtro" label="Unidad" value={idUnidad} textoVacio="Todas"
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

      {rangoInvertido && <p className="text-sm text-error-2">«Desde» no puede ser posterior a «Hasta».</p>}
      {reservas === null && !rangoInvertido ? (
        <RegionMensaje texto="Cargando reservas…" tono="muted" />
      ) : reservas === null ? null : reservas.length === 0 ? (
        <p className="text-sm text-muted">Sin reservas.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-text">
            <thead>
              <tr className="border-b border-border text-muted">
                <th className="py-2 pr-4">Cuándo</th>
                <th className="py-2 pr-4">Qué</th>
                <th className="py-2 pr-4">Tipo</th>
                <th className="py-2 pr-4">Unidad</th>
                <th className="py-2 pr-4">Solicitante</th>
                <th className="py-2 pr-4">Estado</th>
                <th className="py-2"><span className="sr-only">Abrir</span></th>
              </tr>
            </thead>
            <tbody>
              {reservas.map((r) => (
                <tr key={r.id} className="border-b border-border">
                  <td className="py-2 pr-4">{periodoLegible(r.periodo)}</td>
                  <td className="py-2 pr-4">{r.objeto ?? "—"}</td>
                  <td className="py-2 pr-4">{NOMBRE_TIPO_RESERVA[r.tipo_reserva] ?? r.tipo_reserva}</td>
                  <td className="py-2 pr-4">{r.unidad_nombre ?? "—"}</td>
                  <td className="py-2 pr-4">{r.solicitante_nombre ?? "—"}</td>
                  <td className="py-2 pr-4">{NOMBRE_ESTADO_RESERVA[r.estado] ?? r.estado}</td>
                  <td className="py-2">
                    <Link href={`/reservas/${r.id}`} className="font-bold text-primary-2">
                      Ver reserva
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
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
    </div>
  );
}
