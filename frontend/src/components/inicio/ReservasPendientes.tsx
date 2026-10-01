"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { GestionReservaContenido } from "@/src/components/reservas/GestionReservaClient";
import { TarjetaReserva } from "@/src/components/reservas/ListadoReservas";
import { Modal } from "@/src/components/ui/Modal";
import type { ContextoSesion } from "@/src/lib/auth-types";
import { ApiRequestError } from "@/src/lib/http";
import { listarReservas } from "@/src/lib/reservas-api";
import type { VistaGestion } from "@/src/lib/reservas-acciones";
import { NOMBRE_TIPO_RESERVA } from "@/src/lib/reservas-nombres";
import type { ReservaResumen } from "@/src/lib/reservas-types";

// SCR-REP-04, «Pendientes de decisión» (FE-51): lo que espera una respuesta, con las acciones del listado.

const VISIBLES = 5;

export function ReservasPendientes({ sesion }: { sesion: ContextoSesion }) {
  const router = useRouter();
  const [reservas, setReservas] = useState<ReservaResumen[] | null>(null);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState(false);
  const [abierta, setAbierta] = useState<{ r: ReservaResumen; vista: VistaGestion } | null>(null);
  const [recarga, setRecarga] = useState(0);
  const silencioso = useRef(false);

  useEffect(() => {
    let cancelado = false;
    if (!silencioso.current) setReservas(null);
    silencioso.current = false;
    listarReservas({ estado: "SOLICITADA", tamano: VISIBLES })
      .then((r) => {
        if (cancelado) return;
        setReservas(r.datos);
        setTotal(r.paginacion.total);
        setError(false);
      })
      .catch((e) => {
        if (cancelado) return;
        if (e instanceof ApiRequestError && e.status === 401) {
          router.replace("/login?motivo=sesion_vencida");
          return;
        }
        setReservas([]);
        setError(true);
      });
    return () => {
      cancelado = true;
    };
  }, [recarga, router]);

  return (
    <section aria-label="Pendientes de decisión" className="flex flex-col gap-3">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="font-display text-xl font-bold text-text">
          Pendientes de decisión
          {reservas !== null && total > 0 && <span className="ml-2 text-base font-medium text-muted">({total})</span>}
        </h2>
        {total > VISIBLES && (
          <Link href="/reservas" className="text-sm font-bold text-primary-2 underline-offset-4 hover:underline">
            Ver todas ({total})
          </Link>
        )}
      </div>

      {reservas === null && <p className="text-sm text-muted">Cargando pendientes…</p>}
      {error && (
        <p role="alert" className="text-sm text-error-2">
          No se pudieron cargar las reservas pendientes.
        </p>
      )}
      {reservas !== null && !error && reservas.length === 0 && (
        <p className="text-sm text-muted">No hay reservas pendientes.</p>
      )}
      {reservas !== null && reservas.length > 0 && (
        <ul className="flex flex-col gap-3">
          {reservas.map((r) => (
            <TarjetaReserva key={r.id} r={r} sesion={sesion} onAbrir={(res, vista) => setAbierta({ r: res, vista })} />
          ))}
        </ul>
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
            <Link href={`/reservas/${abierta.r.id}`} className="rounded-control text-sm font-medium text-primary-2 underline-offset-4 hover:underline">
              Abrir la página completa de la reserva
            </Link>
          </div>
        </Modal>
      )}
    </section>
  );
}
