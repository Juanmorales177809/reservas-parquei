"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Select } from "@/src/components/ui/Select";
import { ApiRequestError } from "@/src/lib/http";
import { listarReservas } from "@/src/lib/reservas-api";
import type { ReservaResumen } from "@/src/lib/reservas-types";

// WF-RES-04 (listado) — specs/modules/reservations/wireframes.md
export default function PaginaReservas() {
  const router = useRouter();
  const [reservas, setReservas] = useState<ReservaResumen[] | null>(null);
  const [estado, setEstado] = useState("");
  const [mensaje, setMensaje] = useState<string | null>(null);

  async function recargar(filtroEstado: string) {
    try {
      const r = await listarReservas(filtroEstado ? { estado: filtroEstado } : {});
      setReservas(r.datos);
      setMensaje(null);
    } catch (error) {
      if (error instanceof ApiRequestError && error.status === 401) {
        router.replace("/login?motivo=sesion_vencida");
        return;
      }
      setMensaje("No se pudieron cargar las reservas.");
    }
  }

  useEffect(() => {
    void recargar("");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router]);

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-text">Reservas</h1>
        <Link href="/reservas/nueva">
          <Button variant="primary">Nueva reserva</Button>
        </Link>
      </div>
      <div className="flex items-end gap-2">
        <Select id="res-estado" label="Estado" value={estado}
          onChange={(e) => {
            setEstado(e.target.value);
            void recargar(e.target.value);
          }}>
          <option value="">Todos</option>
          {["SOLICITADA", "APROBADA", "RECHAZADA", "EN_EJECUCION", "FINALIZADA", "CANCELADA"].map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </Select>
      </div>
      {reservas === null ? (
        <RegionMensaje texto={mensaje ?? "Cargando reservas…"} tono={mensaje ? "error" : "muted"} />
      ) : (
        <ul className="flex flex-col gap-1 text-sm text-text">
          {reservas.map((r) => (
            <li key={r.id}>
              <Link href={`/reservas/${r.id}`} className="font-bold text-primary-2">
                Reserva #{r.id}
              </Link>{" "}
              {r.tipo_reserva} · {r.estado}
            </li>
          ))}
          {reservas.length === 0 && <li className="text-muted">Sin reservas.</li>}
        </ul>
      )}
      <RegionMensaje texto={mensaje} tono={mensaje ? "error" : "muted"} />
    </div>
  );
}
