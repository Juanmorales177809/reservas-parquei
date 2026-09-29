"use client";

import { useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { Select } from "@/src/components/ui/Select";
import { ApiRequestError } from "@/src/lib/http";
import {
  asociarProyecto,
  asociarSemillero,
  catalogoVinculaciones,
  desactivarVinculacion,
  registrarPasantia,
  registrarTrabajoGrado,
} from "@/src/lib/usuarios-api";
import type {
  CatalogoEntidad,
  Vinculaciones,
} from "@/src/lib/usuarios-types";

/**
 * Sección de vinculaciones compartida por WF-USR-01 y WF-USR-05: la misma
 * superficie en ambos recorridos (screen-flow.md). Andamiaje de FE-09, no
 * un componente cerrado del catálogo.
 */

type TipoVinculable = "proyectos" | "semilleros" | "pasantias" | "trabajos-grado";

export function SeccionVinculaciones({
  iniciales,
  permiteDesactivar,
  alCambiar,
}: {
  iniciales: Vinculaciones;
  permiteDesactivar: boolean;
  alCambiar: (vinculaciones: Vinculaciones) => void;
}) {
  const [vinculaciones, setVinculaciones] = useState(iniciales);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");
  const [ocupada, setOcupada] = useState(false);
  const [idProyecto, setIdProyecto] = useState("");
  const [idSemillero, setIdSemillero] = useState("");
  const [catalogoProyectos, setCatalogoProyectos] = useState<CatalogoEntidad[]>([]);
  const [catalogoSemilleros, setCatalogoSemilleros] = useState<CatalogoEntidad[]>([]);
  const [universidad, setUniversidad] = useState("");
  const [docenteNombre, setDocenteNombre] = useState("");
  const [docenteCorreo, setDocenteCorreo] = useState("");
  const [directorNombre, setDirectorNombre] = useState("");
  const [directorCorreo, setDirectorCorreo] = useState("");

  function tieneActiva(): boolean {
    const todas = [
      ...vinculaciones.proyectos,
      ...vinculaciones.semilleros,
      ...vinculaciones.pasantias,
      ...vinculaciones.trabajos_grado,
    ];
    return todas.some((v) => v.activa);
  }

  async function refrescar() {
    const { obtenerPerfil } = await import("@/src/lib/usuarios-api");
    const perfil = await obtenerPerfil();
    setVinculaciones(perfil.vinculaciones);
    alCambiar(perfil.vinculaciones);
  }

  async function ejecutar(accion: () => Promise<unknown>, exito: string) {
    setOcupada(true);
    setMensaje(null);
    try {
      await accion();
      await refrescar();
      setMensaje(exito);
      setTono("exito");
    } catch (error) {
      setMensaje(mensajeError(error));
      setTono("error");
    } finally {
      setOcupada(false);
    }
  }

  async function cargarCatalogos() {
    if (catalogoProyectos.length === 0) {
      const r = await catalogoVinculaciones("proyectos");
      setCatalogoProyectos(r.datos);
    }
    if (catalogoSemilleros.length === 0) {
      const r = await catalogoVinculaciones("semilleros");
      setCatalogoSemilleros(r.datos);
    }
  }

  async function desactivar(tipo: TipoVinculable, id: number) {
    setOcupada(true);
    setMensaje(null);
    try {
      const r = await desactivarVinculacion(tipo, id);
      await refrescar();
      setMensaje(
        r.sin_vinculaciones_activas
          ? "Vinculación desactivada. Ya no tienes ninguna vinculación activa: no podrás crear nuevas reservas hasta recuperar una."
          : "Vinculación desactivada."
      );
      setTono(r.sin_vinculaciones_activas ? "error" : "exito");
    } catch (error) {
      setMensaje(mensajeError(error));
      setTono("error");
    } finally {
      setOcupada(false);
    }
  }

  function enviarPasantia(evento: FormEvent) {
    evento.preventDefault();
    void ejecutar(
      () =>
        registrarPasantia({
          universidad,
          docente_itm_nombre: docenteNombre,
          docente_itm_correo: docenteCorreo,
        }),
      "Pasantía registrada."
    );
  }

  function enviarTrabajo(evento: FormEvent) {
    evento.preventDefault();
    void ejecutar(
      () =>
        registrarTrabajoGrado({
          director_nombre: directorNombre,
          director_correo: directorCorreo,
        }),
      "Trabajo de grado registrado."
    );
  }

  return (
    <section aria-label="Vinculaciones" className="flex flex-col gap-6">
      <div>
        <h3 className="text-base font-bold text-text">Proyectos</h3>
        <ul className="mt-2 flex flex-col gap-1">
          {vinculaciones.proyectos.map((v) => (
            <li key={v.id_proyecto} className="flex items-center gap-2 text-sm text-text">
              <span>
                {v.codigo} — {v.nombre} {!v.activa && "(inactiva)"}
              </span>
              {permiteDesactivar && v.activa && (
                <Button
                  variant="ghost"
                  size="sm"
                  disabled={ocupada}
                  onClick={() => void desactivar("proyectos", v.id_proyecto)}
                >
                  Desactivar
                </Button>
              )}
            </li>
          ))}
        </ul>
        <div className="mt-2 flex items-end gap-2">
          <Select
            id="asociar-proyecto"
            label="Asociar proyecto"
            value={idProyecto}
            onFocus={() => void cargarCatalogos().catch(() => { setTono("error"); setMensaje("No se pudo cargar el catálogo."); })}
            onChange={(e) => setIdProyecto(e.target.value)}
          >
            <option value="">Seleccionar del catálogo</option>
            {catalogoProyectos.map((p) => (
              <option key={p.id} value={p.id}>
                {p.codigo} — {p.nombre}
              </option>
            ))}
          </Select>
          <Button
            variant="secondary"
            size="sm"
            disabled={ocupada || !idProyecto}
            onClick={() =>
              void ejecutar(() => asociarProyecto(Number(idProyecto)), "Proyecto asociado.")
            }
          >
            Asociar
          </Button>
        </div>
      </div>

      <div>
        <h3 className="text-base font-bold text-text">Semilleros</h3>
        <ul className="mt-2 flex flex-col gap-1">
          {vinculaciones.semilleros.map((v) => (
            <li key={v.id_semillero} className="flex items-center gap-2 text-sm text-text">
              <span>
                {v.codigo} — {v.nombre} {!v.activa && "(inactiva)"}
              </span>
              {permiteDesactivar && v.activa && (
                <Button
                  variant="ghost"
                  size="sm"
                  disabled={ocupada}
                  onClick={() => void desactivar("semilleros", v.id_semillero)}
                >
                  Desactivar
                </Button>
              )}
            </li>
          ))}
        </ul>
        <div className="mt-2 flex items-end gap-2">
          <Select
            id="asociar-semillero"
            label="Asociar semillero"
            value={idSemillero}
            onFocus={() => void cargarCatalogos().catch(() => { setTono("error"); setMensaje("No se pudo cargar el catálogo."); })}
            onChange={(e) => setIdSemillero(e.target.value)}
          >
            <option value="">Seleccionar del catálogo</option>
            {catalogoSemilleros.map((s) => (
              <option key={s.id} value={s.id}>
                {s.codigo} — {s.nombre}
              </option>
            ))}
          </Select>
          <Button
            variant="secondary"
            size="sm"
            disabled={ocupada || !idSemillero}
            onClick={() =>
              void ejecutar(() => asociarSemillero(Number(idSemillero)), "Semillero asociado.")
            }
          >
            Asociar
          </Button>
        </div>
      </div>

      <form onSubmit={enviarPasantia} className="flex flex-col gap-2">
        <h3 className="text-base font-bold text-text">Pasantías</h3>
        <ul className="flex flex-col gap-1">
          {vinculaciones.pasantias.map((v) => (
            <li key={v.id_pasantia} className="flex items-center gap-2 text-sm text-text">
              <span>
                {v.universidad} {!v.activa && "(inactiva)"}
              </span>
              {permiteDesactivar && v.activa && (
                <Button
                  variant="ghost"
                  size="sm"
                  disabled={ocupada}
                  onClick={() => void desactivar("pasantias", v.id_pasantia)}
                >
                  Desactivar
                </Button>
              )}
            </li>
          ))}
        </ul>
        <Field id="pasantia-universidad" label="Universidad" value={universidad}
          onChange={(e) => setUniversidad(e.target.value)} required />
        <Field id="pasantia-docente" label="Docente ITM" value={docenteNombre}
          onChange={(e) => setDocenteNombre(e.target.value)} required />
        <Field id="pasantia-correo" label="Correo del docente" type="email"
          value={docenteCorreo} onChange={(e) => setDocenteCorreo(e.target.value)} required />
        <div>
          <Button type="submit" variant="secondary" loading={ocupada}>
            Registrar pasantía
          </Button>
        </div>
      </form>

      <form onSubmit={enviarTrabajo} className="flex flex-col gap-2">
        <h3 className="text-base font-bold text-text">Trabajos de grado</h3>
        <ul className="flex flex-col gap-1">
          {vinculaciones.trabajos_grado.map((v) => (
            <li key={v.id_trabajo_grado} className="flex items-center gap-2 text-sm text-text">
              <span>
                {v.director_nombre} {!v.activa && "(inactivo)"}
              </span>
              {permiteDesactivar && v.activa && (
                <Button
                  variant="ghost"
                  size="sm"
                  disabled={ocupada}
                  onClick={() => void desactivar("trabajos-grado", v.id_trabajo_grado)}
                >
                  Desactivar
                </Button>
              )}
            </li>
          ))}
        </ul>
        <Field id="trabajo-director" label="Director" value={directorNombre}
          onChange={(e) => setDirectorNombre(e.target.value)} required />
        <Field id="trabajo-correo" label="Correo del director" type="email"
          value={directorCorreo} onChange={(e) => setDirectorCorreo(e.target.value)} required />
        <div>
          <Button type="submit" variant="secondary" loading={ocupada}>
            Registrar trabajo de grado
          </Button>
        </div>
      </form>

      <RegionMensaje texto={ocupada ? "Guardando…" : mensaje} tono={ocupada ? "muted" : tono} />
      {!tieneActiva() && (
        <p className="text-sm text-muted">
          Aún no tienes ninguna vinculación académica o investigativa activa y válida.
        </p>
      )}
    </section>
  );
}

function mensajeError(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.error.codigo === "VINCULACION_DUPLICADA")
      return "Ya tienes una vinculación activa con este proyecto/semillero.";
    if (error.error.codigo === "NO_ENCONTRADO")
      return "El proyecto o semillero seleccionado ya no está disponible.";
    if (error.error.codigo === "VALIDACION") return "Revisa los datos ingresados.";
    if (error.status === 429) return "La operación está temporalmente limitada.";
  }
  return "No se pudo completar la operación.";
}
