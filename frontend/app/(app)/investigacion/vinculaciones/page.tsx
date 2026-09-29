"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import Link from "next/link";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { SelectorProyecto, SelectorSemillero, SelectorUsuario } from "@/src/components/selectores/selectores";
import { Select } from "@/src/components/ui/Select";
import { ApiRequestError } from "@/src/lib/http";
import {
  crearVinculacionAjena,
  desactivarVinculacionAjena,
  vinculacionesDe,
} from "@/src/lib/investigacion-api";
import type { VinculacionAjenas } from "@/src/lib/investigacion-types";

// WF-INV-04 — specs/modules/researchs/wireframes.md
export default function PaginaVinculacionesAjenas() {
  const router = useRouter();
  const [idUsuario, setIdUsuario] = useState("");
  const [vinc, setVinc] = useState<VinculacionAjenas | null>(null);
  const [tipo, setTipo] = useState<"proyectos" | "semilleros">("proyectos");
  const [idEntidad, setIdEntidad] = useState("");
  const [ocupada, setOcupada] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");

  function informar(texto: string, t: "error" | "exito") {
    setMensaje(texto);
    setTono(t);
  }

  async function consultar(evento: FormEvent) {
    evento.preventDefault();
    setOcupada(true);
    try {
      setVinc(await vinculacionesDe(Number(idUsuario)));
      setMensaje(null);
    } catch (error) {
      if (error instanceof ApiRequestError && error.status === 401) {
        router.replace("/login?motivo=sesion_vencida");
        return;
      }
      informar("No se pudieron cargar las vinculaciones.", "error");
    } finally {
      setOcupada(false);
    }
  }

  async function crear(evento: FormEvent) {
    evento.preventDefault();
    setOcupada(true);
    try {
      await crearVinculacionAjena(Number(idUsuario), tipo, Number(idEntidad));
      setVinc(await vinculacionesDe(Number(idUsuario)));
      setIdEntidad("");
      informar("Vinculación registrada.", "exito");
    } catch (error) {
      informar(mensajeError(error), "error");
    } finally {
      setOcupada(false);
    }
  }

  async function desactivar(tipoActual: "proyectos" | "semilleros", id: number) {
    setOcupada(true);
    try {
      await desactivarVinculacionAjena(Number(idUsuario), tipoActual, id);
      setVinc(await vinculacionesDe(Number(idUsuario)));
      informar("Vinculación desactivada.", "exito");
    } catch (error) {
      informar(mensajeError(error), "error");
    } finally {
      setOcupada(false);
    }
  }

  const todas = vinc
    ? [
        ...vinc.proyectos.map((v) => ({ tipo: "proyectos" as const, id: v.id_proyecto, nombre: `${v.codigo} — ${v.nombre}`, activa: v.activa })),
        ...vinc.semilleros.map((v) => ({ tipo: "semilleros" as const, id: v.id_semillero, nombre: `${v.codigo} — ${v.nombre}`, activa: v.activa })),
      ]
    : [];

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-text">Vinculaciones de terceros</h1>
      <p className="text-sm text-muted">
        Las vinculaciones propias se gestionan en{" "}
        <Link href="/usuarios/perfil/vinculaciones" className="font-bold text-primary-2">
          Mis vinculaciones
        </Link>
        .
      </p>
      <form onSubmit={(e) => void consultar(e)} className="flex items-end gap-2">
        <SelectorUsuario id="vinc-usuario" label="Usuario" value={idUsuario} onChange={setIdUsuario} requerido />
        <Button type="submit" variant="secondary" loading={ocupada}>Consultar</Button>
      </form>
      {vinc && (
        <>
          <ul className="flex flex-col gap-1 text-sm text-text">
            {todas.map((v) => (
              <li key={`${v.tipo}-${v.id}`} className="flex items-center gap-2">
                <span>{v.nombre} {!v.activa && "(inactiva)"}</span>
                {v.activa && (
                  <Button variant="ghost" size="sm" disabled={ocupada}
                    onClick={() => void desactivar(v.tipo, v.id)}>
                    Desactivar
                  </Button>
                )}
              </li>
            ))}
          </ul>
          <form onSubmit={(e) => void crear(e)} className="flex flex-col gap-2">
            <Select id="vinc-tipo" label="Tipo" value={tipo}
              onChange={(e) => {
                setTipo(e.target.value as "proyectos" | "semilleros");
                setIdEntidad("");
              }}>
              <option value="proyectos">Proyectos</option>
              <option value="semilleros">Semilleros</option>
            </Select>
            {tipo === "proyectos" ? (
              <SelectorProyecto id="vinc-entidad" label="Proyecto" value={idEntidad} onChange={setIdEntidad}
                textoVacio="Seleccionar proyecto" requerido />
            ) : (
              <SelectorSemillero id="vinc-entidad" label="Semillero" value={idEntidad} onChange={setIdEntidad} requerido />
            )}
            <div>
              <Button type="submit" variant="primary" loading={ocupada}>Crear vinculación</Button>
            </div>
          </form>
          <p className="text-sm text-muted">
            La importación masiva vive en{" "}
            <Link href="/administracion/importaciones" className="font-bold text-primary-2">
              Importar catálogo
            </Link>
            .
          </p>
        </>
      )}
      <RegionMensaje texto={mensaje} tono={mensaje ? tono : "muted"} />
    </div>
  );
}

function mensajeError(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.error.codigo === "CONFLICTO") return "Ya existe una vinculación activa con esa entidad.";
    if (error.error.codigo === "NO_ENCONTRADO") return "La entidad no existe o está deshabilitada.";
    if (error.error.codigo === "VALIDACION") return "Revisa los datos ingresados.";
    if (error.status === 429) return "La operación está temporalmente limitada.";
  }
  return "No se pudo completar la operación.";
}
