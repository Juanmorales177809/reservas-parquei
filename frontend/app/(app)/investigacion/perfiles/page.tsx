"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { ApiRequestError } from "@/src/lib/http";
import {
  cambiarEstadoPerfil,
  crearPerfil,
  listarPerfiles,
} from "@/src/lib/investigacion-api";
import type { PerfilInv } from "@/src/lib/investigacion-types";

// WF-INV-03 — specs/modules/researchs/wireframes.md
export default function PaginaPerfiles() {
  const router = useRouter();
  const [perfiles, setPerfiles] = useState<PerfilInv[] | null>(null);
  const [nombre, setNombre] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [ocupada, setOcupada] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");

  async function recargar() {
    const r = await listarPerfiles();
    setPerfiles(r.datos);
  }

  useEffect(() => {
    let cancelado = false;
    recargar().catch((err) => {
      if (cancelado) return;
      if (err instanceof ApiRequestError && err.status === 401) {
        router.replace("/login?motivo=sesion_vencida");
        return;
      }
      setMensaje("No se pudieron cargar los perfiles.");
      setTono("error");
    });
    return () => {
      cancelado = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router]);

  async function guardar(evento: FormEvent) {
    evento.preventDefault();
    setOcupada(true);
    try {
      await crearPerfil({ nombre, ...(descripcion ? { descripcion } : {}) });
      setNombre("");
      setDescripcion("");
      await recargar();
      setMensaje("Perfil creado.");
      setTono("exito");
    } catch (error) {
      setMensaje(
        error instanceof ApiRequestError && error.error.codigo === "VALIDACION"
          ? "El nombre es obligatorio."
          : "No se pudo crear el perfil."
      );
      setTono("error");
    } finally {
      setOcupada(false);
    }
  }

  async function alternar(p: PerfilInv) {
    setOcupada(true);
    try {
      await cambiarEstadoPerfil(p.id_perfil, !p.estado);
      await recargar();
      setMensaje(p.estado ? "Perfil deshabilitado." : "Perfil habilitado.");
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
      <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Perfiles</h1>
      {perfiles === null ? (
        <RegionMensaje texto={mensaje ?? "Cargando perfiles…"} tono={mensaje ? tono : "muted"} />
      ) : (
        <ul className="flex flex-col gap-1 text-sm text-text">
          {perfiles.map((p) => (
            <li key={p.id_perfil} className="flex items-center gap-2">
              <span>{p.nombre} {!p.estado && "(deshabilitado)"}</span>
              <Button variant="ghost" size="sm" disabled={ocupada}
                onClick={() => void alternar(p)}>
                {p.estado ? "Deshabilitar" : "Habilitar"}
              </Button>
            </li>
          ))}
        </ul>
      )}
      <form onSubmit={(e) => void guardar(e)} className="flex flex-col gap-2">
        <Field id="perfil-nombre" label="Nombre" value={nombre}
          onChange={(e) => setNombre(e.target.value)} required />
        <Field id="perfil-descripcion" label="Descripción (opcional)" value={descripcion}
          onChange={(e) => setDescripcion(e.target.value)} />
        <div>
          <Button type="submit" variant="primary" loading={ocupada}>Guardar perfil</Button>
        </div>
      </form>
      <RegionMensaje texto={mensaje} tono={mensaje ? tono : "muted"} />
    </div>
  );
}
