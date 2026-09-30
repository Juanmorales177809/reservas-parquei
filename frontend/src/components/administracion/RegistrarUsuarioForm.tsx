"use client";

import Link from "next/link";
import { useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { crearUsuarioIdentidad } from "@/src/lib/administracion-api";
import { ApiRequestError } from "@/src/lib/http";

// WF-ADM-03 — specs/modules/administration/wireframes.md
// Decisión 2026-09-30: el personal y sus cargos llegan de la base institucional; aquí solo se registran usuarios.

/**
 * Registro de la identidad de un usuario y el paso siguiente (invitar su cuenta). Lo usan la pantalla de
 * identidades y el modal «Registrar usuario» de Personas.
 */
export function RegistrarUsuarioForm({ onGuardado, onCancelar }: { onGuardado?: () => void; onCancelar?: () => void }) {
  const [nombre, setNombre] = useState("");
  const [documento, setDocumento] = useState("");
  const [correo, setCorreo] = useState("");
  const [telefono, setTelefono] = useState("");
  const [institucion, setInstitucion] = useState("");
  const [dependencia, setDependencia] = useState("");
  const [ocupada, setOcupada] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");
  const [correoGuardado, setCorreoGuardado] = useState<string | null>(null);

  async function guardar(evento: FormEvent) {
    evento.preventDefault();
    setOcupada(true);
    setMensaje(null);
    setCorreoGuardado(null);
    try {
      await crearUsuarioIdentidad({ nombre, documento, correo, telefono, institucion, dependencia });
      setCorreoGuardado(correo);
      setMensaje("Identidad guardada.");
      setTono("exito");
      onGuardado?.();
    } catch (error) {
      setMensaje(mensajeError(error));
      setTono("error");
    } finally {
      setOcupada(false);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <form onSubmit={(e) => void guardar(e)} className="flex flex-col gap-4">
        <Field id="ident-nombre" label="Nombre" value={nombre} onChange={(e) => setNombre(e.target.value)} required />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field id="ident-documento" label="Documento" value={documento} onChange={(e) => setDocumento(e.target.value)} required />
          <Field id="ident-telefono" label="Teléfono" value={telefono} onChange={(e) => setTelefono(e.target.value)} required />
        </div>
        <Field id="ident-correo" label="Correo" type="email" value={correo} onChange={(e) => setCorreo(e.target.value)} required />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field id="ident-institucion" label="Institución" value={institucion} onChange={(e) => setInstitucion(e.target.value)} required />
          <Field id="ident-dependencia" label="Dependencia" value={dependencia} onChange={(e) => setDependencia(e.target.value)} required />
        </div>
        <RegionMensaje texto={ocupada ? "Guardando…" : mensaje} tono={ocupada ? "muted" : tono} />
        <div className="flex flex-wrap items-center gap-3 border-t border-border pt-4">
          <Button type="submit" variant="primary" loading={ocupada}>Guardar</Button>
          {onCancelar && (
            <Button type="button" variant="ghost" onClick={onCancelar}>
              {correoGuardado ? "Cerrar" : "Cancelar"}
            </Button>
          )}
        </div>
      </form>
      {correoGuardado && (
        <p className="rounded-control bg-primary-tint px-4 py-3 text-sm text-text">
          Para que pueda entrar, invita su cuenta:{" "}
          <Link
            href={`/administracion/cuentas/invitar?correo=${encodeURIComponent(correoGuardado)}`}
            className="font-bold text-primary-2 underline-offset-4 hover:underline"
          >
            Invitar una cuenta
          </Link>
          .
        </p>
      )}
    </div>
  );
}

function mensajeError(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.error.codigo === "CONFLICTO") return "Esos datos ya están registrados en otra identidad.";
    if (error.error.codigo === "VALIDACION") return "Revisa los datos ingresados.";
    if (error.status === 429) return "La operación está temporalmente limitada.";
  }
  return "No se pudo guardar.";
}
