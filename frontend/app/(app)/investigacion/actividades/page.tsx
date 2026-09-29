"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { ApiRequestError } from "@/src/lib/http";
import {
  cambiarEstadoActividad,
  crearActividad,
  editarActividad,
  listarActividades,
} from "@/src/lib/investigacion-api";
import type { Actividad } from "@/src/lib/investigacion-types";

// WF-INV-02 — specs/modules/researchs/wireframes.md
export default function PaginaActividades() {
  const router = useRouter();
  const [actividades, setActividades] = useState<Actividad[] | null>(null);
  const [nombre, setNombre] = useState("");
  const [dependencia, setDependencia] = useState("");
  const [ocupada, setOcupada] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");

  async function recargar() {
    const r = await listarActividades();
    setActividades(r.datos);
  }

  useEffect(() => {
    let cancelado = false;
    recargar().catch((err) => {
      if (cancelado) return;
      if (err instanceof ApiRequestError && err.status === 401) {
        router.replace("/login?motivo=sesion_vencida");
        return;
      }
      setMensaje("No se pudieron cargar las actividades.");
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

  async function guardar(evento: FormEvent) {
    evento.preventDefault();
    setOcupada(true);
    try {
      await crearActividad({ nombre, dependencia });
      setNombre("");
      setDependencia("");
      await recargar();
      informar("Actividad creada.", "exito");
    } catch (error) {
      informar(
        error instanceof ApiRequestError && error.error.codigo === "VALIDACION"
          ? "Nombre y dependencia son obligatorios."
          : "No se pudo crear la actividad.",
        "error"
      );
    } finally {
      setOcupada(false);
    }
  }

  async function renombrar(a: Actividad) {
    const nuevo = window.prompt("Nuevo nombre", a.nombre);
    if (!nuevo || nuevo === a.nombre) return;
    setOcupada(true);
    try {
      await editarActividad(a.id_actividad, { nombre: nuevo });
      await recargar();
      informar("Actividad actualizada.", "exito");
    } catch {
      informar("No se pudo actualizar.", "error");
    } finally {
      setOcupada(false);
    }
  }

  async function alternar(a: Actividad) {
    setOcupada(true);
    try {
      await cambiarEstadoActividad(a.id_actividad, !a.estado);
      await recargar();
      informar(a.estado ? "Actividad desactivada." : "Actividad activada.", "exito");
    } catch {
      informar("No se pudo cambiar el estado.", "error");
    } finally {
      setOcupada(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-text">Actividades institucionales</h1>
      {actividades === null ? (
        <RegionMensaje texto={mensaje ?? "Cargando actividades…"} tono={mensaje ? tono : "muted"} />
      ) : (
        <ul className="flex flex-col gap-1 text-sm text-text">
          {actividades.map((a) => (
            <li key={a.id_actividad} className="flex items-center gap-2">
              <span>{a.nombre} ({a.dependencia}) {!a.estado && "(deshabilitada)"}</span>
              <Button variant="ghost" size="sm" disabled={ocupada}
                onClick={() => void renombrar(a)}>Editar</Button>
              <Button variant="ghost" size="sm" disabled={ocupada}
                onClick={() => void alternar(a)}>
                {a.estado ? "Deshabilitar" : "Habilitar"}
              </Button>
            </li>
          ))}
        </ul>
      )}
      <form onSubmit={(e) => void guardar(e)} className="flex flex-col gap-2">
        <Field id="act-nombre" label="Nombre" value={nombre}
          onChange={(e) => setNombre(e.target.value)} required />
        <Field id="act-dependencia" label="Dependencia" value={dependencia}
          onChange={(e) => setDependencia(e.target.value)} required />
        <div>
          <Button type="submit" variant="primary" loading={ocupada}>Guardar actividad</Button>
        </div>
      </form>
      <RegionMensaje texto={mensaje} tono={mensaje ? tono : "muted"} />
    </div>
  );
}
