"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Insignia } from "@/src/components/ui/Insignia";
import { ApiRequestError } from "@/src/lib/http";
import { cambiarEstadoUnidad, listarCargos, listarUnidades } from "@/src/lib/administracion-api";
import type { Cargo, Unidad } from "@/src/lib/administracion-types";

const NOMBRE_TIPO: Record<string, string> = { LABORATORIO: "Laboratorio", FACULTAD: "Facultad", DEPENDENCIA: "Dependencia" };

const ANILLO_FOCO =
  "focus-visible:outline-none focus-visible:ring-4 " +
  "focus-visible:ring-[color-mix(in_srgb,var(--color-sky)_55%,transparent)]";

// WF-ADM-01 — specs/modules/administration/wireframes.md
// Decisión 2026-09-30: los laboratorios y los cargos vienen de otra base de datos; aquí se consultan y se
// configuran para reservar, pero no se crean ni se renombran.
export default function PaginaUnidades() {
  const router = useRouter();
  const [unidades, setUnidades] = useState<Unidad[] | null>(null);
  const [cargos, setCargos] = useState<Cargo[]>([]);
  const [ocupada, setOcupada] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");

  async function recargar() {
    const [u, c] = await Promise.all([listarUnidades(), listarCargos()]);
    setUnidades(u.datos);
    setCargos(c.datos);
  }

  useEffect(() => {
    let cancelado = false;
    recargar().catch((err) => {
      if (cancelado) return;
      if (err instanceof ApiRequestError && err.status === 401) {
        router.replace("/login?motivo=sesion_vencida");
        return;
      }
      setUnidades([]);
      setMensaje("No se pudieron cargar los laboratorios.");
      setTono("error");
    });
    return () => {
      cancelado = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router]);

  function informar(texto: string, t: "error" | "exito") {
    setMensaje(texto);
    setTono(t);
  }

  async function cambiarEstado(u: Unidad) {
    setOcupada(true);
    try {
      await cambiarEstadoUnidad(u.id_unidad, !u.estado);
      await recargar();
      informar(u.estado ? "Laboratorio deshabilitado. Conserva todo lo asociado." : "Laboratorio habilitado.", "exito");
    } catch (error) {
      informar(mensajeError(error), "error");
    } finally {
      setOcupada(false);
    }
  }

  const nombreDe = (id: number) => unidades?.find((u) => u.id_unidad === id)?.nombre ?? "—";

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-1">
        <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Laboratorios y cargos</h1>
        <p className="max-w-[64ch] text-[15px] text-muted">
          Los laboratorios y los cargos llegan de la base de datos institucional, así que aquí no se crean. Desde aquí
          se configura cómo se reserva cada laboratorio.
        </p>
      </div>

      <section aria-label="Laboratorios" className="flex flex-col gap-3">
        <h2 className="text-lg font-bold text-text">Laboratorios</h2>
        {unidades === null ? (
          <RegionMensaje texto="Cargando…" tono="muted" />
        ) : unidades.length === 0 ? (
          <p className="text-sm text-muted">Todavía no hay laboratorios cargados.</p>
        ) : (
          <ul className="flex flex-col gap-3">
            {unidades.map((u) => (
              <li
                key={u.id_unidad}
                className="flex flex-wrap items-center gap-3 rounded-card border border-border bg-surface p-4 shadow-card"
              >
                <div className="flex min-w-[14rem] flex-1 flex-col gap-1">
                  <span className="font-display text-[17px] font-bold text-text">{u.nombre}</span>
                  <span className="flex flex-wrap items-center gap-2">
                    <Insignia tono="neutro">{NOMBRE_TIPO[u.tipo] ?? u.tipo}</Insignia>
                    {!u.estado && <Insignia tono="error">Deshabilitado</Insignia>}
                  </span>
                </div>
                {u.tipo === "LABORATORIO" && (
                  <Link href={`/laboratorios/${u.id_unidad}`} className={`rounded-control text-sm font-bold text-primary-2 hover:underline ${ANILLO_FOCO}`}>
                    Configurar
                  </Link>
                )}
                <Button variant="ghost" size="sm" disabled={ocupada} onClick={() => void cambiarEstado(u)}>
                  {u.estado ? "Deshabilitar" : "Habilitar"}
                </Button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-label="Cargos" className="flex flex-col gap-3">
        <h2 className="text-lg font-bold text-text">Cargos</h2>
        {cargos.length === 0 ? (
          <p className="text-sm text-muted">Todavía no hay cargos cargados.</p>
        ) : (
          <ul className="grid grid-cols-1 gap-2 md:grid-cols-2">
            {cargos.map((c) => (
              <li key={c.id_cargo} className="flex flex-col rounded-control border border-border bg-surface px-4 py-3 text-sm">
                <span className="font-bold text-text">{c.nombre_cargo}</span>
                <span className="text-muted">{nombreDe(c.id_unidad)}</span>
              </li>
            ))}
          </ul>
        )}
      </section>
      <RegionMensaje texto={mensaje} tono={mensaje ? tono : "muted"} />
    </div>
  );
}

function mensajeError(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.error.codigo === "NO_ENCONTRADO") return "El laboratorio ya no existe.";
    if (error.status === 429) return "La operación está temporalmente limitada.";
  }
  return "No se pudo cambiar el estado.";
}
