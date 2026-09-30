"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { ApiRequestError } from "@/src/lib/http";
import {
  guardarPreferencias,
  obtenerPreferencias,
  tiposEvento,
} from "@/src/lib/notificaciones-api";
import type { TipoEventoItem } from "@/src/lib/notificaciones-types";

// WF-NOT-02 — specs/modules/notifications/wireframes.md
export default function PaginaPreferencias() {
  const router = useRouter();
  const [general, setGeneral] = useState(true);
  const [tipos, setTipos] = useState<TipoEventoItem[]>([]);
  const [porEvento, setPorEvento] = useState<Record<number, boolean>>({});
  const [cargada, setCargada] = useState(false);
  const [ocupada, setOcupada] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");

  useEffect(() => {
    let cancelado = false;
    Promise.all([obtenerPreferencias(), tiposEvento()])
      .then(([prefs, tipos]) => {
        if (cancelado) return;
        setGeneral(prefs.general.correo_habilitado);
        const mapa: Record<number, boolean> = {};
        for (const item of prefs.por_evento) {
          const tipo = tipos.datos.find((t) => t.codigo === item.tipo_evento.codigo);
          if (tipo) mapa[tipo.id] = item.correo_habilitado;
        }
        setPorEvento(mapa);
        setTipos(tipos.datos);
        setCargada(true);
      })
      .catch((err) => {
        if (cancelado) return;
        if (err instanceof ApiRequestError && err.status === 401) {
          router.replace("/login?motivo=sesion_vencida");
          return;
        }
        setMensaje("No se pudieron cargar las preferencias.");
        setTono("error");
      });
    return () => {
      cancelado = true;
    };
  }, [router]);

  function alternar(id: number) {
    setPorEvento((prev) => {
      const vigente = id in prev ? prev[id] : general;
      return { ...prev, [id]: !vigente };
    });
  }

  async function guardar(evento: FormEvent) {
    evento.preventDefault();
    setOcupada(true);
    setMensaje(null);
    try {
      const r = await guardarPreferencias({
        general: { correo_habilitado: general },
        por_evento: Object.entries(porEvento).map(([id, correo_habilitado]) => ({
          tipo_evento_id: Number(id),
          correo_habilitado,
        })),
      });
      setGeneral(r.general.correo_habilitado);
      setMensaje("Preferencias guardadas.");
      setTono("exito");
    } catch (error) {
      if (error instanceof ApiRequestError && error.status === 401) {
        router.replace("/login?motivo=sesion_vencida");
        return;
      }
      const codigo = error instanceof ApiRequestError ? error.error.codigo : null;
      setMensaje(
        codigo === "NO_ENCONTRADO"
          ? "Un tipo de evento no existe o está deshabilitado. Recarga la página."
          : codigo === "VALIDACION"
            ? "Revisa las preferencias: hay un tipo de evento repetido."
            : error instanceof ApiRequestError && error.status === 403
              ? "No se puede realizar esta operación."
              : "No se pudieron guardar las preferencias."
      );
      setTono("error");
    } finally {
      setOcupada(false);
    }
  }

  if (!cargada) {
    return (
      <div className="flex flex-col gap-4">
        <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Preferencias de correo</h1>
        <RegionMensaje texto={mensaje ?? "Cargando…"} tono={mensaje ? tono : "muted"} />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Preferencias de correo</h1>
      <form onSubmit={(e) => void guardar(e)} className="flex flex-col gap-4">
        <label className="flex items-center gap-2 text-sm text-text">
          <input
            type="checkbox"
            checked={general}
            onChange={(e) => setGeneral(e.target.checked)}
          />
          Correo habilitado en general
        </label>
        <p className="text-sm text-muted">
          Solo afecta al correo: los avisos en pantalla se generan igual.
        </p>
        <ul className="flex flex-col gap-1 text-sm text-text">
          {tipos.map((t) => {
            const explicita = t.id in porEvento;
            const vigente = explicita ? porEvento[t.id] : general;
            return (
              <li key={t.id} className="flex items-center gap-2">
                <input
                  type="checkbox"
                  aria-label={t.nombre}
                  checked={vigente}
                  onChange={() => alternar(t.id)}
                />
                <span>
                  {t.nombre} {explicita ? "(propia)" : "(general)"}
                </span>
              </li>
            );
          })}
        </ul>
        <RegionMensaje texto={ocupada ? "Guardando…" : mensaje} tono={ocupada ? "muted" : tono} />
        <div>
          <Button type="submit" variant="primary" loading={ocupada}>
            Guardar preferencias
          </Button>
        </div>
      </form>
    </div>
  );
}
