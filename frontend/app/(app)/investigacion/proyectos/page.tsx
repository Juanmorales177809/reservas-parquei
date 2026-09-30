"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { ApiRequestError } from "@/src/lib/http";
import { cambiarEstadoProyecto, cambiarEstadoSemillero, listarProyectos, listarSemilleros } from "@/src/lib/investigacion-api";
import type { Proyecto, Semillero } from "@/src/lib/investigacion-types";

// WF-INV-01 — specs/modules/researchs/wireframes.md
export default function PaginaCatalogos() {
  const router = useRouter();
  const [proyectos, setProyectos] = useState<Proyecto[] | null>(null);
  const [semilleros, setSemilleros] = useState<Semillero[] | null>(null);
  const [ocupada, setOcupada] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");

  async function recargar() {
    const [p, s] = await Promise.all([listarProyectos(), listarSemilleros()]);
    setProyectos(p.datos);
    setSemilleros(s.datos);
  }

  useEffect(() => {
    let cancelado = false;
    recargar().catch((err) => {
      if (cancelado) return;
      if (err instanceof ApiRequestError && err.status === 401) {
        router.replace("/login?motivo=sesion_vencida");
        return;
      }
      setMensaje("No se pudieron cargar los catálogos.");
      setTono("error");
    });
    return () => {
      cancelado = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router]);

  async function alternar(kind: "proyecto" | "semillero", id: number, estado: boolean) {
    setOcupada(true);
    try {
      if (kind === "proyecto") await cambiarEstadoProyecto(id, !estado);
      else await cambiarEstadoSemillero(id, !estado);
      await recargar();
      setMensaje("Estado actualizado.");
      setTono("exito");
    } catch {
      setMensaje("No se pudo cambiar el estado.");
      setTono("error");
    } finally {
      setOcupada(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Proyectos y semilleros</h1>
      {proyectos === null ? (
        <RegionMensaje texto={mensaje ?? "Cargando catálogos…"} tono={mensaje ? tono : "muted"} />
      ) : (
        <>
          <section aria-label="Proyectos" className="flex flex-col gap-2">
            <h2 className="text-base font-bold text-text">Proyectos</h2>
            <ul className="flex flex-col gap-1 text-sm text-text">
              {proyectos.map((p) => (
                <li key={p.id_proyecto} className="flex items-center gap-2">
                  <span>{p.codigo} — {p.nombre} {!p.estado && "(deshabilitado)"}</span>
                  <Button variant="ghost" size="sm" disabled={ocupada}
                    onClick={() => void alternar("proyecto", p.id_proyecto, p.estado)}>
                    {p.estado ? "Deshabilitar" : "Habilitar"}
                  </Button>
                </li>
              ))}
            </ul>
          </section>
          <section aria-label="Semilleros" className="flex flex-col gap-2">
            <h2 className="text-base font-bold text-text">Semilleros</h2>
            <ul className="flex flex-col gap-1 text-sm text-text">
              {semilleros?.map((s) => (
                <li key={s.id_semillero} className="flex items-center gap-2">
                  <span>{s.codigo} — {s.nombre} {!s.estado && "(deshabilitado)"}</span>
                  <Button variant="ghost" size="sm" disabled={ocupada}
                    onClick={() => void alternar("semillero", s.id_semillero, s.estado)}>
                    {s.estado ? "Deshabilitar" : "Habilitar"}
                  </Button>
                </li>
              ))}
            </ul>
          </section>
        </>
      )}
      <RegionMensaje texto={mensaje} tono={mensaje ? tono : "muted"} />
    </div>
  );
}
