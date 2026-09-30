"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { SelectorCuenta } from "@/src/components/selectores/selectores";
import { Field } from "@/src/components/ui/Field";
import { fechaHora } from "@/src/lib/formato";
import { ApiRequestError } from "@/src/lib/http";
import { listarAuditoria } from "@/src/lib/administracion-api";
import type { AuditoriaFila } from "@/src/lib/administracion-types";

// WF-ADM-05 — specs/modules/administration/wireframes.md
export default function PaginaAuditoria() {
  const router = useRouter();
  const [filas, setFilas] = useState<AuditoriaFila[] | null>(null);
  const [entidad, setEntidad] = useState("");
  const [actor, setActor] = useState("");
  const [accion, setAccion] = useState("");
  const [mensaje, setMensaje] = useState<string | null>(null);

  async function consultar(filtros: { entidad?: string; actor_cuenta_id?: number; accion?: string } = {}) {
    try {
      const r = await listarAuditoria(filtros);
      setFilas(r.datos);
      setMensaje(null);
    } catch (error) {
      if (error instanceof ApiRequestError && error.status === 401) {
        router.replace("/login?motivo=sesion_vencida");
        return;
      }
      setMensaje("No se pudo cargar la auditoría.");
    }
  }

  useEffect(() => {
    let cancelado = false;
    listarAuditoria()
      .then((r) => {
        if (!cancelado) setFilas(r.datos);
      })
      .catch((err) => {
        if (cancelado) return;
        if (err instanceof ApiRequestError && err.status === 401) {
          router.replace("/login?motivo=sesion_vencida");
          return;
        }
        setMensaje("No se pudo cargar la auditoría.");
      });
    return () => {
      cancelado = true;
    };
  }, [router]);

  async function filtrar(evento: FormEvent) {
    evento.preventDefault();
    await consultar({
      ...(entidad ? { entidad } : {}),
      ...(actor ? { actor_cuenta_id: Number(actor) } : {}),
      ...(accion ? { accion } : {}),
    });
  }

  return (
    <div className="flex flex-col gap-4">
      <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Auditoría</h1>
      <form onSubmit={(e) => void filtrar(e)} className="flex flex-wrap items-end gap-2">
        <Field id="aud-entidad" label="Entidad" value={entidad}
          onChange={(e) => setEntidad(e.target.value)} />
        <SelectorCuenta id="aud-actor" label="Actor" value={actor} onChange={setActor}
          textoVacio="Cualquiera" />
        <Field id="aud-accion" label="Acción" value={accion}
          onChange={(e) => setAccion(e.target.value)} />
        <Button type="submit" variant="secondary">Filtrar</Button>
      </form>
      <RegionMensaje texto={mensaje} tono={mensaje ? "error" : "muted"} />
      {filas && (
        <ul className="flex flex-col gap-2 text-sm text-text">
          {filas.map((f) => (
            <li key={f.id} className="border-b border-border pb-2">
              {fechaHora(f.created_at)} · cuenta {f.actor_cuenta_id} · {f.accion} · {f.entidad} {f.entidad_id}
            </li>
          ))}
          {filas.length === 0 && <li className="text-muted">Sin resultados.</li>}
        </ul>
      )}
    </div>
  );
}
