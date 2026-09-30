"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { SelectorCuenta, SelectorUnidad } from "@/src/components/selectores/selectores";
import { Select } from "@/src/components/ui/Select";
import { ApiRequestError } from "@/src/lib/http";
import {
  asignacionesDe,
  catalogoPermisos,
  listarUnidades,
  otorgarPermiso,
  retirarPermiso,
} from "@/src/lib/administracion-api";
import type { Asignacion, PermisoCatalogo } from "@/src/lib/administracion-types";

// WF-ADM-02 — specs/modules/administration/wireframes.md
export default function PaginaPermisos() {
  const router = useRouter();
  const [catalogo, setCatalogo] = useState<PermisoCatalogo[] | null>(null);
  const [idCuenta, setIdCuenta] = useState("");
  const [asignaciones, setAsignaciones] = useState<Asignacion[] | null>(null);
  const [codigo, setCodigo] = useState("");
  const [unidad, setUnidad] = useState("");
  const [nombresUnidad, setNombresUnidad] = useState<Record<number, string>>({});
  const [ocupada, setOcupada] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");

  useEffect(() => {
    let cancelado = false;
    catalogoPermisos()
      .then((r) => {
        if (!cancelado) setCatalogo(r.datos);
      })
      .catch((err) => {
        if (cancelado) return;
        if (err instanceof ApiRequestError && err.status === 401) {
          router.replace("/login?motivo=sesion_vencida");
          return;
        }
        setMensaje("No se pudo cargar el catálogo.");
        setTono("error");
      });
    return () => {
      cancelado = true;
    };
  }, [router]);

  // Solo para mostrar el nombre de la unidad de cada asignación; si falla, se ve «unidad #id».
  useEffect(() => {
    listarUnidades()
      .then((r) => setNombresUnidad(Object.fromEntries(r.datos.map((u) => [u.id_unidad, u.nombre]))))
      .catch(() => {});
  }, []);

  async function consultar(evento: FormEvent) {
    evento.preventDefault();
    setOcupada(true);
    setMensaje(null);
    try {
      setAsignaciones(await asignacionesDe(Number(idCuenta)));
    } catch (error) {
      if (error instanceof ApiRequestError && error.status === 404) {
        setMensaje("La cuenta no existe.");
      } else {
        setMensaje("No se pudieron cargar las asignaciones.");
      }
      setTono("error");
    } finally {
      setOcupada(false);
    }
  }

  async function otorgar(evento: FormEvent) {
    evento.preventDefault();
    setOcupada(true);
    try {
      await otorgarPermiso(Number(idCuenta), codigo, unidad ? Number(unidad) : null);
      setAsignaciones(await asignacionesDe(Number(idCuenta)));
      setMensaje("Permiso otorgado.");
      setTono("exito");
    } catch (error) {
      setMensaje(mensajeError(error));
      setTono("error");
    } finally {
      setOcupada(false);
    }
  }

  async function retirar(a: Asignacion) {
    setOcupada(true);
    try {
      await retirarPermiso(a.id_cuenta, a.codigo);
      setAsignaciones(await asignacionesDe(Number(idCuenta)));
      setMensaje("Permiso retirado.");
      setTono("exito");
    } catch (error) {
      setMensaje(mensajeError(error));
      setTono("error");
    } finally {
      setOcupada(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Permisos de la cuenta</h1>
      <form onSubmit={(e) => void consultar(e)} className="flex items-end gap-2">
        <SelectorCuenta id="perm-cuenta" label="Cuenta" value={idCuenta} onChange={setIdCuenta} requerido />
        <Button type="submit" variant="secondary" loading={ocupada}>Consultar</Button>
      </form>
      {asignaciones && (
        <>
          <ul className="flex flex-col gap-1 text-sm text-text">
            {asignaciones.map((a) => (
              <li key={`${a.codigo}-${a.id_unidad ?? "global"}`} className="flex items-center gap-2">
                <span>{a.codigo} ({a.id_unidad === null ? "global" : (nombresUnidad[a.id_unidad] ?? `unidad #${a.id_unidad}`)})</span>
                <Button variant="ghost" size="sm" disabled={ocupada}
                  onClick={() => void retirar(a)}>Retirar</Button>
              </li>
            ))}
          </ul>
          <form onSubmit={(e) => void otorgar(e)} className="flex flex-col gap-2">
            <Select id="perm-codigo" label="Código" value={codigo}
              onChange={(e) => setCodigo(e.target.value)} required>
              <option value="">Seleccionar del catálogo</option>
              {(catalogo ?? []).map((p) => (
                <option key={p.codigo} value={p.codigo}>{p.codigo}</option>
              ))}
            </Select>
            <SelectorUnidad id="perm-unidad" label="Laboratorio" value={unidad} onChange={setUnidad}
              textoVacio="Global (todos los laboratorios)" />
            <div>
              <Button type="submit" variant="primary" loading={ocupada}>Otorgar permiso</Button>
            </div>
          </form>
        </>
      )}
      <RegionMensaje texto={mensaje} tono={mensaje ? tono : "muted"} />
    </div>
  );
}

function mensajeError(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.error.codigo === "CONFLICTO") {
      const detalle = JSON.stringify(error.error.detalles);
      if (detalle.includes("administradores")) {
        return "No se puede dejar al sistema sin administradores.";
      }
      return "Esa asignación ya existe.";
    }
    if (error.error.codigo === "VALIDACION") return "Revisa la cuenta, el código y la unidad.";
    if (error.status === 429) return "La operación está temporalmente limitada.";
  }
  return "No se pudo completar la operación.";
}
