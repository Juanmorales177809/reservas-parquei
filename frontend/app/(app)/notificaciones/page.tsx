"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Select } from "@/src/components/ui/Select";
import { ApiRequestError } from "@/src/lib/http";
import { bandeja, marcarLectura, tiposEvento } from "@/src/lib/notificaciones-api";
import type { NotificacionItem, TipoEventoItem } from "@/src/lib/notificaciones-types";

type Tono = "muted" | "error" | "exito";

// WF-NOT-01 — specs/modules/notifications/wireframes.md
export default function PaginaNotificaciones() {
  const router = useRouter();
  const [items, setItems] = useState<NotificacionItem[] | null>(null);
  const [tipos, setTipos] = useState<TipoEventoItem[]>([]);
  const [leida, setLeida] = useState("");
  const [tipo, setTipo] = useState("");
  const [marcando, setMarcando] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<Tono>("muted");

  const fallar = useCallback(
    (error: unknown, porDefecto: string) => {
      if (error instanceof ApiRequestError && error.status === 401) {
        router.replace("/login?motivo=sesion_vencida");
        return;
      }
      if (error instanceof ApiRequestError && error.status === 403) {
        setMensaje("No se puede realizar esta operación.");
      } else if (error instanceof ApiRequestError && error.status === 429) {
        setMensaje("La operación está temporalmente limitada.");
      } else {
        setMensaje(porDefecto);
      }
      setTono("error");
    },
    [router]
  );

  const cargar = useCallback(async () => {
    const filtros: { leida?: boolean; tipo_evento?: string } = {};
    if (leida) filtros.leida = leida === "true";
    if (tipo) filtros.tipo_evento = tipo;
    const r = await bandeja(filtros);
    setItems(r.datos);
  }, [leida, tipo]);

  useEffect(() => {
    let cancelado = false;
    cargar().catch((error) => {
      if (!cancelado) fallar(error, "No se pudieron cargar las notificaciones.");
    });
    return () => {
      cancelado = true;
    };
  }, [cargar, fallar]);

  // El catálogo de tipos solo alimenta el filtro: si falla, la bandeja sigue útil.
  useEffect(() => {
    let cancelado = false;
    tiposEvento()
      .then((r) => {
        if (!cancelado) setTipos(r.datos);
      })
      .catch(() => {});
    return () => {
      cancelado = true;
    };
  }, []);

  async function marcar(id: number) {
    setMarcando(true);
    setMensaje("Guardando…");
    setTono("muted");
    try {
      await marcarLectura(id);
      await cargar();
      setMensaje("Notificación marcada como leída.");
      setTono("exito");
    } catch (error) {
      // Ajena e inexistente responden igual (404): no se distingue cuál fue.
      if (error instanceof ApiRequestError && error.status === 404) {
        try {
          await cargar();
        } catch {}
        setMensaje("La notificación ya no está disponible.");
        setTono("error");
      } else {
        fallar(error, "No se pudo marcar la notificación.");
      }
    } finally {
      setMarcando(false);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-bold text-text">Notificaciones</h1>
      <div className="flex flex-wrap items-end gap-2">
        <Select id="not-leida" label="Estado" value={leida} onChange={(e) => setLeida(e.target.value)}>
          <option value="">Todas</option>
          <option value="false">No leídas</option>
          <option value="true">Leídas</option>
        </Select>
        <Select id="not-tipo" label="Tipo de evento" value={tipo} onChange={(e) => setTipo(e.target.value)}>
          <option value="">Todos</option>
          {tipos.map((t) => (
            <option key={t.id} value={t.codigo}>
              {t.nombre}
            </option>
          ))}
        </Select>
      </div>
      {items === null ? (
        <RegionMensaje texto={mensaje ?? "Cargando…"} tono={mensaje ? tono : "muted"} />
      ) : (
        <>
          <ul className="flex flex-col gap-2 text-sm text-text">
            {items.map((n) => (
              <li key={n.id} className="border-b border-border pb-2">
                <p className="font-bold">
                  {n.titulo} {!n.leida_at && "(sin leer)"}
                </p>
                <p className="text-muted">
                  {n.tipo_evento.nombre} · {n.created_at}
                  {n.reserva_id !== null && ` · Reserva #${n.reserva_id}`}
                </p>
                <p>{n.cuerpo}</p>
                {n.leida_at ? (
                  <p className="text-muted">Leída: {n.leida_at}</p>
                ) : (
                  <Button variant="ghost" size="sm" disabled={marcando} onClick={() => void marcar(n.id)}>
                    Marcar como leída
                  </Button>
                )}
              </li>
            ))}
            {items.length === 0 && <li className="text-muted">Sin notificaciones.</li>}
          </ul>
          <RegionMensaje texto={mensaje} tono={mensaje ? tono : "muted"} />
        </>
      )}
    </div>
  );
}
