"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { ApiRequestError } from "@/src/lib/http";
import { catalogoPerfiles, guardarPerfiles } from "@/src/lib/usuarios-api";
import type { PerfilCatalogoItem } from "@/src/lib/usuarios-types";

// WF-USR-04 — specs/modules/usuarios/wireframes.md
export default function PaginaPerfiles() {
  const router = useRouter();
  const [catalogo, setCatalogo] = useState<PerfilCatalogoItem[] | null>(null);
  const [seleccion, setSeleccion] = useState<number[]>([]);
  const [guardando, setGuardando] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");

  useEffect(() => {
    let cancelado = false;
    catalogoPerfiles()
      .then((r) => {
        if (!cancelado) setCatalogo(r.datos);
      })
      .catch((err) => {
        if (cancelado) return;
        if (err instanceof ApiRequestError && err.status === 401) {
          router.replace("/login?motivo=sesion_vencida");
          return;
        }
        setMensaje("No se pudo cargar el catálogo de perfiles.");
        setTono("error");
      });
    return () => {
      cancelado = true;
    };
  }, [router]);

  function alternar(id: number) {
    setSeleccion((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  }

  async function enviar(evento: FormEvent) {
    evento.preventDefault();
    setGuardando(true);
    setMensaje(null);
    try {
      const r = await guardarPerfiles(seleccion);
      setSeleccion(r.perfiles.map((p) => p.id_perfil));
      setMensaje("Perfiles actualizados.");
      setTono("exito");
    } catch (error) {
      if (error instanceof ApiRequestError && error.error.codigo === "CONFLICTO") {
        setMensaje("Esta combinación de perfiles no está permitida.");
      } else if (error instanceof ApiRequestError && error.error.codigo === "NO_ENCONTRADO") {
        setMensaje("Uno de los perfiles seleccionados ya no está disponible.");
      } else {
        setMensaje("No se pudo guardar la selección.");
      }
      setTono("error");
    } finally {
      setGuardando(false);
    }
  }

  if (!catalogo) {
    return (
      <div className="flex flex-col gap-4">
        <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Mis perfiles académicos/investigativos</h1>
        <RegionMensaje texto={mensaje ?? "Cargando perfiles…"} tono={mensaje ? tono : "muted"} />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Mis perfiles académicos/investigativos</h1>
      <form onSubmit={(e) => void enviar(e)} className="flex flex-col gap-3">
        {catalogo.map((p) => (
          <label key={p.id_perfil} className="flex items-center gap-2 text-sm text-text">
            <input
              type="checkbox"
              checked={seleccion.includes(p.id_perfil)}
              onChange={() => alternar(p.id_perfil)}
            />
            {p.nombre}
          </label>
        ))}
        <RegionMensaje texto={guardando ? "Guardando selección…" : mensaje} tono={guardando ? "muted" : tono} />
        <div>
          <Button type="submit" variant="primary" loading={guardando}>
            Guardar selección
          </Button>
        </div>
      </form>
    </div>
  );
}
