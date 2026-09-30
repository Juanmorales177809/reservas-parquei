"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { RegistrarUsuarioForm } from "@/src/components/administracion/RegistrarUsuarioForm";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { Insignia } from "@/src/components/ui/Insignia";
import { Modal } from "@/src/components/ui/Modal";
import {
  buscarPersonal,
  buscarUsuarios,
  cambiarEstadoPersonal,
  cambiarEstadoUsuario,
  editarUsuario,
} from "@/src/lib/administracion-api";
import type { FichaPersonal, UsuarioIdentidad } from "@/src/lib/administracion-types";
import { ApiRequestError } from "@/src/lib/http";

// Administración de identidades (usuarios §5 y §6; RN-USR-01 de administration): consultar, editar y activar o desactivar.
// Decisión 2026-09-30: el personal llega de la base institucional; aquí se consulta y se activa o desactiva su acceso,
// pero no se edita ni se registra.
type Vista = "USUARIO" | "PERSONAL";
type Fila = UsuarioIdentidad | FichaPersonal;

const esUsuario = (f: Fila): f is UsuarioIdentidad => "id_usuario" in f;
const idDe = (f: Fila) => (esUsuario(f) ? f.id_usuario : f.id_persona);

const ANILLO_FOCO =
  "focus-visible:outline-none focus-visible:ring-4 " +
  "focus-visible:ring-[color-mix(in_srgb,var(--color-sky)_55%,transparent)]";

function Chip({ activo, onClick, children }: { activo: boolean; onClick: () => void; children: string }) {
  return (
    <button
      type="button"
      aria-pressed={activo}
      onClick={onClick}
      className={`rounded-full border px-4 py-1.5 font-display text-sm font-medium transition-colors ${ANILLO_FOCO} ${
        activo
          ? "border-primary-2 bg-primary-2 text-white"
          : "border-border bg-surface text-text hover:border-primary-1 hover:bg-primary-tint"
      }`}
    >
      {children}
    </button>
  );
}

export default function PaginaPersonas() {
  const router = useRouter();
  const [vista, setVista] = useState<Vista>("USUARIO");
  const [busqueda, setBusqueda] = useState("");
  const [estado, setEstado] = useState("");
  const [filas, setFilas] = useState<Fila[] | null>(null);
  const [editando, setEditando] = useState<UsuarioIdentidad | null>(null);
  const [registrando, setRegistrando] = useState(false);
  const [valores, setValores] = useState<Record<string, string>>({});
  const [ocupada, setOcupada] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");
  const [version, setVersion] = useState(0);

  function informar(texto: string, t: "error" | "exito") {
    setMensaje(texto);
    setTono(t);
  }

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

  function abrirEdicion(f: UsuarioIdentidad) {
    setEditando(f);
    setMensaje(null);
    setValores({
      nombre: f.nombre, documento: f.documento, telefono: f.telefono,
      institucion: f.institucion, dependencia: f.dependencia, correo: f.correo,
    });
  }

  async function guardar(evento: FormEvent) {
    evento.preventDefault();
    if (!editando) return;
    setOcupada(true);
    try {
      // Solo viaja lo que cambió; el correo no se toca cuando la persona ya tiene cuenta (inmutable, RN-AUTH-ID-02).
      const cambios: Record<string, string> = {};
      const original = editando as unknown as Record<string, unknown>;
      for (const [campo, valor] of Object.entries(valores)) {
        if (campo === "correo" && editando.id_cuenta !== null) continue;
        if (String(original[campo] ?? "") !== valor.trim()) cambios[campo] = valor.trim();
      }
      if (Object.keys(cambios).length === 0) {
        setEditando(null);
        return;
      }
      await editarUsuario(editando.id_usuario, cambios);
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
  const hayFiltros = estado !== "" || busqueda.trim() !== "";

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div className="flex flex-col gap-1">
          <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Personas</h1>
          <p className="max-w-[60ch] text-[15px] text-muted">
            Usuarios registrados y personal de los laboratorios. El personal llega de la base institucional: aquí se consulta
            y se activa o desactiva su acceso.
          </p>
        </div>
        <Button variant="primary" onClick={() => { setMensaje(null); setRegistrando(true); }}>
          Registrar usuario
        </Button>
      </div>

      <div className="flex flex-col gap-4 rounded-card border border-border bg-surface p-4 shadow-card md:p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div role="group" aria-label="Ver" className="flex flex-wrap gap-2">
            <Chip activo={vista === "USUARIO"} onClick={() => { setVista("USUARIO"); setEditando(null); }}>Usuarios</Chip>
            <Chip activo={vista === "PERSONAL"} onClick={() => { setVista("PERSONAL"); setEditando(null); }}>Personal</Chip>
          </div>
          <div role="group" aria-label="Estado" className="flex flex-wrap gap-2">
            <Chip activo={estado === ""} onClick={() => setEstado("")}>Todos</Chip>
            <Chip activo={estado === "true"} onClick={() => setEstado("true")}>Activos</Chip>
            <Chip activo={estado === "false"} onClick={() => setEstado("false")}>Inactivos</Chip>
          </div>
        </div>
        <Field id="per-busqueda" label="Buscar por nombre, documento o correo" value={busqueda} onChange={(e) => setBusqueda(e.target.value)} />
        {hayFiltros && (
          <div>
            <Button variant="ghost" size="sm" onClick={() => { setEstado(""); setBusqueda(""); }}>Quitar filtros</Button>
          </div>
        )}
      </div>

      {filas === null ? (
        <RegionMensaje texto="Cargando…" tono="muted" />
      ) : filas.length === 0 ? (
        <div className="flex flex-col items-start gap-2 rounded-card border border-dashed border-border bg-surface p-8">
          <p className="font-display text-lg font-bold text-text">No hay personas con esos criterios.</p>
          <p className="text-sm text-muted">
            {hayFiltros ? "Prueba con otro nombre o estado." : vista === "USUARIO" ? "Cuando registres usuarios, aparecerán aquí." : "El personal aparecerá cuando llegue de la base institucional."}
          </p>
        </div>
      ) : (
        <>
          <p className="text-sm text-muted">
            {filas.length} {filas.length === 1 ? "persona" : "personas"}
          </p>
          <ul aria-label="Personas" className="flex flex-col gap-3">
            {filas.map((f) => (
              <li key={idDe(f)} className="flex flex-wrap items-center gap-4 rounded-card border border-border bg-surface p-4 shadow-card">
                <span
                  aria-hidden="true"
                  className="flex h-12 w-12 flex-none items-center justify-center rounded-full bg-primary-tint font-display text-lg font-bold text-primary-2"
                >
                  {f.nombre.charAt(0).toUpperCase()}
                </span>
                <div className="flex min-w-[16rem] flex-1 flex-col gap-1">
                  <span className="font-display text-[17px] font-bold leading-snug text-text">{f.nombre}</span>
                  <span className="text-sm text-muted">{f.correo} · doc. {f.documento} · tel. {f.telefono}</span>
                  <span className="flex flex-wrap items-center gap-2 text-sm text-text">
                    {esUsuario(f)
                      ? `${f.institucion} · ${f.dependencia}`
                      : `${f.cargo?.nombre_cargo ?? "Sin cargo"} · ${f.unidad?.nombre ?? "Sin laboratorio"}`}
                    <Insignia tono={f.id_cuenta === null ? "atencion" : "marca"}>{f.id_cuenta === null ? "Sin cuenta" : "Con cuenta"}</Insignia>
                    {!f.estado && <Insignia tono="error">Inactivo</Insignia>}
                  </span>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  {f.id_cuenta === null && (
                    <Link
                      href={`/administracion/cuentas/invitar?correo=${encodeURIComponent(f.correo)}${esUsuario(f) ? "" : "&tipo=PERSONAL"}`}
                      className={`rounded-control px-3 py-1.5 text-sm font-bold text-primary-2 hover:bg-primary-tint ${ANILLO_FOCO}`}
                    >
                      Invitar cuenta
                    </Link>
                  )}
                  {esUsuario(f) && (
                    <Button variant="secondary" size="sm" disabled={ocupada} onClick={() => abrirEdicion(f)}>Editar</Button>
                  )}
                  <Button variant={f.estado ? "ghost" : "secondary"} size="sm" disabled={ocupada} onClick={() => void alternar(f)}>
                    {f.estado ? "Desactivar" : "Activar"}
                  </Button>
                </div>
              </li>
            ))}
          </ul>
        </>
      )}

      {!editando && !registrando && <RegionMensaje texto={mensaje} tono={mensaje ? tono : "muted"} />}

      {editando && (
        <Modal titulo={`Editar a ${editando.nombre}`} subtitulo="Solo se envía lo que cambies." onClose={() => setEditando(null)}>
          <form onSubmit={(e) => void guardar(e)} aria-label="Editar persona" className="flex flex-col gap-4">
            <Field id="ed-nombre" label="Nombre" value={valores.nombre ?? ""} onChange={poner("nombre")} required />
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <Field id="ed-documento" label="Documento" value={valores.documento ?? ""} onChange={poner("documento")} required />
              <Field id="ed-telefono" label="Teléfono" value={valores.telefono ?? ""} onChange={poner("telefono")} required />
            </div>
            <Field id="ed-correo" label="Correo" type="email" value={valores.correo ?? ""} onChange={poner("correo")}
              disabled={editando.id_cuenta !== null} required
              hint={editando.id_cuenta !== null ? "El correo no se puede cambiar: ya identifica a su cuenta." : undefined} />
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <Field id="ed-institucion" label="Institución" value={valores.institucion ?? ""} onChange={poner("institucion")} required />
              <Field id="ed-dependencia" label="Dependencia" value={valores.dependencia ?? ""} onChange={poner("dependencia")} required />
            </div>
            <RegionMensaje texto={mensaje} tono={mensaje ? tono : "muted"} />
            <div className="flex flex-wrap items-center gap-3 border-t border-border pt-4">
              <Button type="submit" variant="primary" loading={ocupada}>Guardar cambios</Button>
              <Button type="button" variant="ghost" onClick={() => setEditando(null)}>Cancelar</Button>
            </div>
          </form>
        </Modal>
      )}

      {registrando && (
        <Modal
          titulo="Registrar usuario"
          subtitulo="Estudiante, docente o externo. Después podrás invitar su cuenta."
          onClose={() => setRegistrando(false)}
        >
          <RegistrarUsuarioForm onGuardado={() => setVersion((v) => v + 1)} onCancelar={() => setRegistrando(false)} />
        </Modal>
      )}
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
