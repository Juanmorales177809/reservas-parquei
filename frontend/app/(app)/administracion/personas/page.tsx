"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { Select } from "@/src/components/ui/Select";
import {
  buscarPersonal,
  buscarUsuarios,
  cambiarEstadoPersonal,
  cambiarEstadoUsuario,
  editarPersonal,
  editarUsuario,
  listarCargos,
  listarUnidades,
} from "@/src/lib/administracion-api";
import type { Cargo, FichaPersonal, Unidad, UsuarioIdentidad } from "@/src/lib/administracion-types";
import { ApiRequestError } from "@/src/lib/http";

// Administración de identidades (usuarios §5 y §6; RN-USR-01 de administration): consultar, editar y activar o desactivar.
type Vista = "USUARIO" | "PERSONAL";
type Fila = UsuarioIdentidad | FichaPersonal;

const esUsuario = (f: Fila): f is UsuarioIdentidad => "id_usuario" in f;
const idDe = (f: Fila) => (esUsuario(f) ? f.id_usuario : f.id_persona);

export default function PaginaPersonas() {
  const router = useRouter();
  const [vista, setVista] = useState<Vista>("USUARIO");
  const [busqueda, setBusqueda] = useState("");
  const [estado, setEstado] = useState("");
  const [filas, setFilas] = useState<Fila[] | null>(null);
  const [cargos, setCargos] = useState<Cargo[]>([]);
  const [unidades, setUnidades] = useState<Unidad[]>([]);
  const [editando, setEditando] = useState<Fila | null>(null);
  const [valores, setValores] = useState<Record<string, string>>({});
  const [ocupada, setOcupada] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");
  const [version, setVersion] = useState(0);

  function informar(texto: string, t: "error" | "exito") {
    setMensaje(texto);
    setTono(t);
  }

  // Los cargos solo se necesitan para editar la ficha de personal.
  useEffect(() => {
    Promise.all([listarCargos(), listarUnidades()])
      .then(([c, u]) => {
        setCargos(c.datos);
        setUnidades(u.datos);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    let cancelado = false;
    setFilas(null);
    const espera = window.setTimeout(() => {
      const filtros = {
        ...(estado ? { estado: estado === "true" } : {}),
        ...(busqueda.trim() ? { busqueda: busqueda.trim() } : {}),
      };
      const peticion = vista === "USUARIO" ? buscarUsuarios(filtros) : buscarPersonal(filtros);
      peticion
        .then((r) => {
          if (!cancelado) setFilas(r.datos);
        })
        .catch((error) => {
          if (cancelado) return;
          if (error instanceof ApiRequestError && error.status === 401) {
            router.replace("/login?motivo=sesion_vencida");
            return;
          }
          setFilas([]);
          informar("No se pudieron cargar las personas.", "error");
        });
    }, busqueda ? 300 : 0);
    return () => {
      cancelado = true;
      window.clearTimeout(espera);
    };
  }, [vista, estado, busqueda, version, router]);

  function abrirEdicion(f: Fila) {
    setEditando(f);
    setMensaje(null);
    setValores(
      esUsuario(f)
        ? { nombre: f.nombre, documento: f.documento, telefono: f.telefono, institucion: f.institucion, dependencia: f.dependencia, correo: f.correo }
        : { nombre: f.nombre, documento: f.documento, telefono: f.telefono, correo: f.correo, id_cargo: String(f.id_cargo) }
    );
  }

  async function guardar(evento: FormEvent) {
    evento.preventDefault();
    if (!editando) return;
    setOcupada(true);
    try {
      // Solo viaja lo que cambió; el correo no se toca cuando la persona ya tiene cuenta (inmutable, RN-AUTH-ID-02).
      const cambios: Record<string, string | number> = {};
      const original = editando as unknown as Record<string, unknown>;
      for (const [campo, valor] of Object.entries(valores)) {
        if (campo === "correo" && editando.id_cuenta !== null) continue;
        if (String(original[campo] ?? "") !== valor.trim()) cambios[campo] = campo === "id_cargo" ? Number(valor) : valor.trim();
      }
      if (Object.keys(cambios).length === 0) {
        setEditando(null);
        return;
      }
      if (esUsuario(editando)) await editarUsuario(editando.id_usuario, cambios);
      else await editarPersonal(editando.id_persona, cambios);
      setEditando(null);
      setVersion((v) => v + 1);
      informar("Datos actualizados.", "exito");
    } catch (error) {
      informar(mensajeError(error), "error");
    } finally {
      setOcupada(false);
    }
  }

  async function alternar(f: Fila) {
    setOcupada(true);
    try {
      if (esUsuario(f)) await cambiarEstadoUsuario(f.id_usuario, !f.estado);
      else await cambiarEstadoPersonal(f.id_persona, !f.estado);
      setVersion((v) => v + 1);
      informar(f.estado ? "Se desactivó. Conserva su historial y no podrá hacer nuevas operaciones." : "Se activó de nuevo.", "exito");
    } catch (error) {
      informar(mensajeError(error), "error");
    } finally {
      setOcupada(false);
    }
  }

  const poner = (campo: string) => (e: { target: { value: string } }) => setValores({ ...valores, [campo]: e.target.value });

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Personas</h1>
        <Link href="/administracion/identidades" className="text-sm font-bold text-primary-2">
          Registrar e invitar
        </Link>
      </div>

      <div className="flex flex-wrap items-end gap-3">
        <Select id="per-vista" label="Ver" value={vista} onChange={(e) => { setVista(e.target.value as Vista); setEditando(null); }}>
          <option value="USUARIO">Usuarios</option>
          <option value="PERSONAL">Personal</option>
        </Select>
        <Field id="per-busqueda" label="Buscar por nombre, documento o correo" value={busqueda} onChange={(e) => setBusqueda(e.target.value)} />
        <Select id="per-estado" label="Estado" value={estado} onChange={(e) => setEstado(e.target.value)}>
          <option value="">Todos</option>
          <option value="true">Activos</option>
          <option value="false">Inactivos</option>
        </Select>
      </div>

      {filas === null ? (
        <RegionMensaje texto="Cargando…" tono="muted" />
      ) : filas.length === 0 ? (
        <p className="text-sm text-muted">No hay personas con esos criterios.</p>
      ) : (
        <ul className="flex flex-col divide-y divide-border text-sm text-text">
          {filas.map((f) => (
            <li key={idDe(f)} className="flex flex-wrap items-center gap-3 py-2">
              <div className="flex min-w-[16rem] flex-1 flex-col">
                <span className="font-bold">
                  {f.nombre} {!f.estado && <span className="font-normal text-muted">(inactivo)</span>}
                </span>
                <span className="text-muted">{f.correo} · doc. {f.documento} · tel. {f.telefono}</span>
                <span className="text-muted">
                  {esUsuario(f)
                    ? `${f.institucion} · ${f.dependencia}`
                    : `${f.cargo?.nombre_cargo ?? "Sin cargo"} · ${f.unidad?.nombre ?? "Sin unidad"}`}
                  {" · "}{f.id_cuenta === null ? "sin cuenta" : "con cuenta"}
                </span>
              </div>
              <Button variant="ghost" size="sm" disabled={ocupada} onClick={() => abrirEdicion(f)}>Editar</Button>
              <Button variant={f.estado ? "danger" : "secondary"} size="sm" disabled={ocupada} onClick={() => void alternar(f)}>
                {f.estado ? "Desactivar" : "Activar"}
              </Button>
            </li>
          ))}
        </ul>
      )}

      {editando && (
        <form onSubmit={(e) => void guardar(e)} aria-label="Editar persona" className="flex flex-col gap-3 rounded-control border border-border p-4">
          <h2 className="text-base font-bold text-text">Editar a {editando.nombre}</h2>
          <Field id="ed-nombre" label="Nombre" value={valores.nombre ?? ""} onChange={poner("nombre")} required />
          <Field id="ed-documento" label="Documento" value={valores.documento ?? ""} onChange={poner("documento")} required />
          <Field id="ed-telefono" label="Teléfono" value={valores.telefono ?? ""} onChange={poner("telefono")} required />
          <Field id="ed-correo" label="Correo" type="email" value={valores.correo ?? ""} onChange={poner("correo")}
            disabled={editando.id_cuenta !== null} required />
          {editando.id_cuenta !== null && (
            <p className="text-sm text-muted">El correo no se puede cambiar: ya identifica a su cuenta.</p>
          )}
          {esUsuario(editando) ? (
            <>
              <Field id="ed-institucion" label="Institución" value={valores.institucion ?? ""} onChange={poner("institucion")} required />
              <Field id="ed-dependencia" label="Dependencia" value={valores.dependencia ?? ""} onChange={poner("dependencia")} required />
            </>
          ) : (
            <>
              <Select id="ed-cargo" label="Cargo" value={valores.id_cargo ?? ""} onChange={poner("id_cargo")}>
                {cargos.map((c) => (
                  <option key={c.id_cargo} value={c.id_cargo}>
                    {c.nombre_cargo} · {unidades.find((u) => u.id_unidad === c.id_unidad)?.nombre ?? "sin unidad"}
                  </option>
                ))}
              </Select>
              <p className="text-sm text-muted">Cambiar el cargo cambia la unidad de la persona y queda en la auditoría.</p>
            </>
          )}
          <div className="flex gap-2">
            <Button type="submit" variant="primary" size="sm" loading={ocupada}>Guardar cambios</Button>
            <Button type="button" variant="ghost" size="sm" onClick={() => setEditando(null)}>Cancelar</Button>
          </div>
        </form>
      )}
      <RegionMensaje texto={mensaje} tono={mensaje ? tono : "muted"} />
    </div>
  );
}

function mensajeError(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.status === 429) return "La operación está temporalmente limitada.";
    // 409 (documento, teléfono o correo duplicados; último administrador) y 422 traen un mensaje claro.
    if (error.error.mensaje && [403, 404, 409, 422].includes(error.status)) return error.error.mensaje;
  }
  return "No se pudo completar la operación.";
}
