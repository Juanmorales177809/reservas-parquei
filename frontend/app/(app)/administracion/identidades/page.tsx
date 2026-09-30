"use client";

import Link from "next/link";
import { useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { ApiRequestError } from "@/src/lib/http";
import { crearUsuarioIdentidad } from "@/src/lib/administracion-api";

// WF-ADM-03 — specs/modules/administration/wireframes.md
// Decisión 2026-09-30: el personal y sus cargos llegan de la base institucional; aquí solo se registran usuarios.

export default function PaginaIdentidades() {
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
    } catch (error) {
      setMensaje(mensajeError(error));
      setTono("error");
    } finally {
      setOcupada(false);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Identidades</h1>
      <p className="max-w-[64ch] text-[15px] text-muted">
        Registra a un usuario (estudiante, docente o externo) para poder invitar su cuenta. El personal y sus cargos
        llegan de la base institucional: no se registran aquí.
      </p>
      <form onSubmit={(e) => void guardar(e)} className="flex flex-col gap-4">
        <Field id="ident-nombre" label="Nombre" value={nombre}
          onChange={(e) => setNombre(e.target.value)} required />
        <Field id="ident-documento" label="Documento" value={documento}
          onChange={(e) => setDocumento(e.target.value)} required />
        <Field id="ident-correo" label="Correo" type="email" value={correo}
          onChange={(e) => setCorreo(e.target.value)} required />
        <Field id="ident-telefono" label="Teléfono" value={telefono}
          onChange={(e) => setTelefono(e.target.value)} required />
        <Field id="ident-institucion" label="Institución" value={institucion}
          onChange={(e) => setInstitucion(e.target.value)} required />
        <Field id="ident-dependencia" label="Dependencia" value={dependencia}
          onChange={(e) => setDependencia(e.target.value)} required />
        <RegionMensaje texto={ocupada ? "Guardando…" : mensaje} tono={ocupada ? "muted" : tono} />
        <div>
          <Button type="submit" variant="primary" loading={ocupada}>Guardar</Button>
        </div>
      </form>
      {correoGuardado && (
        <p className="text-sm text-text">
          Para invitar su cuenta, continúe en{" "}
          <Link
            href={`/administracion/cuentas/invitar?correo=${encodeURIComponent(correoGuardado)}`}
            className="font-bold text-primary-2"
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
