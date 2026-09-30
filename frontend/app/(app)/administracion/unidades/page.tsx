"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { Select } from "@/src/components/ui/Select";
import { ApiRequestError } from "@/src/lib/http";
import {
  cambiarEstadoUnidad,
  crearCargo,
  crearUnidad,
  editarUnidad,
  listarCargos,
  listarUnidades,
} from "@/src/lib/administracion-api";
import type { Cargo, Unidad } from "@/src/lib/administracion-types";

// WF-ADM-01 — specs/modules/administration/wireframes.md
export default function PaginaUnidades() {
  const router = useRouter();
  const [unidades, setUnidades] = useState<Unidad[]>([]);
  const [cargos, setCargos] = useState<Cargo[]>([]);
  const [nombre, setNombre] = useState("");
  const [tipo, setTipo] = useState("LABORATORIO");
  const [padre, setPadre] = useState("");
  const [nombreCargo, setNombreCargo] = useState("");
  const [unidadCargo, setUnidadCargo] = useState("");
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
      setMensaje("No se pudieron cargar las unidades.");
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

  async function guardarUnidad(evento: FormEvent) {
    evento.preventDefault();
    setOcupada(true);
    try {
      await crearUnidad({
        nombre,
        tipo,
        ...(padre ? { id_unidad_padre: Number(padre) } : {}),
      });
      setNombre("");
      setPadre("");
      await recargar();
      informar("Unidad creada.", "exito");
    } catch (error) {
      informar(mensajeError(error, "No se pudo crear la unidad."), "error");
    } finally {
      setOcupada(false);
    }
  }

  async function cambiarEstado(u: Unidad) {
    setOcupada(true);
    try {
      await cambiarEstadoUnidad(u.id_unidad, !u.estado);
      await recargar();
      informar(u.estado ? "Unidad deshabilitada. Conserva todo lo asociado." : "Unidad habilitada.", "exito");
    } catch (error) {
      informar(mensajeError(error, "No se pudo cambiar el estado."), "error");
    } finally {
      setOcupada(false);
    }
  }

  async function guardarCargo(evento: FormEvent) {
    evento.preventDefault();
    setOcupada(true);
    try {
      await crearCargo({ nombre_cargo: nombreCargo, id_unidad: Number(unidadCargo) });
      setNombreCargo("");
      await recargar();
      informar("Cargo creado.", "exito");
    } catch (error) {
      informar(mensajeError(error, "No se pudo crear el cargo."), "error");
    } finally {
      setOcupada(false);
    }
  }

  async function renombrarUnidad(u: Unidad) {
    const nuevo = window.prompt("Nuevo nombre", u.nombre);
    if (!nuevo || nuevo === u.nombre) return;
    setOcupada(true);
    try {
      await editarUnidad(u.id_unidad, { nombre: nuevo });
      await recargar();
      informar("Unidad actualizada.", "exito");
    } catch (error) {
      informar(mensajeError(error, "No se pudo actualizar."), "error");
    } finally {
      setOcupada(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Unidades y cargos</h1>
      <section aria-label="Unidades" className="flex flex-col gap-3">
        <h2 className="text-base font-bold text-text">Unidades</h2>
        <ul className="flex flex-col gap-1 text-sm text-text">
          {unidades.map((u) => (
            <li key={u.id_unidad} className="flex items-center gap-2">
              <span>{u.nombre} ({u.tipo}) {!u.estado && "(deshabilitada)"}</span>
              <Button variant="ghost" size="sm" disabled={ocupada}
                onClick={() => void renombrarUnidad(u)}>Editar</Button>
              {u.tipo === "LABORATORIO" && (
                <Link href={`/laboratorios/${u.id_unidad}`} className="text-sm font-bold text-primary-2">
                  Configurar
                </Link>
              )}
              <Button variant="ghost" size="sm" disabled={ocupada}
                onClick={() => void cambiarEstado(u)}>
                {u.estado ? "Deshabilitar" : "Habilitar"}
              </Button>
            </li>
          ))}
        </ul>
        <form onSubmit={(e) => void guardarUnidad(e)} className="flex flex-col gap-2">
          <Field id="unidad-nombre" label="Nombre" value={nombre}
            onChange={(e) => setNombre(e.target.value)} required />
          <Select id="unidad-tipo" label="Tipo" value={tipo}
            onChange={(e) => setTipo(e.target.value)}>
            <option value="LABORATORIO">Laboratorio</option>
            <option value="FACULTAD">Facultad</option>
            <option value="DEPENDENCIA">Dependencia</option>
          </Select>
          <Select id="unidad-padre" label="Unidad padre (opcional)" value={padre}
            onChange={(e) => setPadre(e.target.value)}>
            <option value="">Sin padre</option>
            {unidades.map((u) => (
              <option key={u.id_unidad} value={u.id_unidad}>{u.nombre}</option>
            ))}
          </Select>
          <div>
            <Button type="submit" variant="primary" loading={ocupada}>Guardar unidad</Button>
          </div>
        </form>
      </section>
      <section aria-label="Cargos" className="flex flex-col gap-3">
        <h2 className="text-base font-bold text-text">Cargos</h2>
        <ul className="flex flex-col gap-1 text-sm text-text">
          {cargos.map((c) => (
            <li key={c.id_cargo}>{c.nombre_cargo}</li>
          ))}
        </ul>
        <form onSubmit={(e) => void guardarCargo(e)} className="flex flex-col gap-2">
          <Field id="cargo-nombre" label="Nombre del cargo" value={nombreCargo}
            onChange={(e) => setNombreCargo(e.target.value)} required />
          <Select id="cargo-unidad" label="Unidad" value={unidadCargo}
            onChange={(e) => setUnidadCargo(e.target.value)} required>
            <option value="">Seleccionar</option>
            {unidades.map((u) => (
              <option key={u.id_unidad} value={u.id_unidad}>{u.nombre}</option>
            ))}
          </Select>
          <div>
            <Button type="submit" variant="primary" loading={ocupada}>Guardar cargo</Button>
          </div>
        </form>
      </section>
      <RegionMensaje texto={mensaje} tono={mensaje ? tono : "muted"} />
    </div>
  );
}

function mensajeError(error: unknown, repliegue: string): string {
  if (error instanceof ApiRequestError) {
    if (error.error.codigo === "CONFLICTO") return "Ese nombre ya existe.";
    if (error.error.codigo === "NO_ENCONTRADO") return "La unidad ya no existe.";
    if (error.error.codigo === "VALIDACION") return "Revisa los datos ingresados.";
    if (error.status === 429) return "La operación está temporalmente limitada.";
  }
  return repliegue;
}
