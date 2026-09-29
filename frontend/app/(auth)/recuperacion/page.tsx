"use client";

import { useState, type FormEvent } from "react";
import { AuthCard } from "@/src/components/auth/AuthCard";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { solicitarRecuperacion } from "@/src/lib/auth-api";
import { ApiRequestError } from "@/src/lib/http";

const MENSAJE_PUBLICO =
  "Si existe una cuenta asociada, se enviarán las instrucciones de recuperación.";

// WF-AUTH-05 — specs/modules/auth/wireframes.md
export default function PaginaRecuperacion() {
  const [correo, setCorreo] = useState("");
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [enviado, setEnviado] = useState(false);

  async function enviar(evento: FormEvent) {
    evento.preventDefault();
    setCargando(true);
    setError(null);
    try {
      await solicitarRecuperacion(correo);
      setEnviado(true);
    } catch (err) {
      setError(mensajeError(err));
    } finally {
      setCargando(false);
    }
  }

  if (enviado) {
    return (
      <AuthCard titulo="Recuperar contraseña — respuesta">
        <p className="text-sm text-text">{MENSAJE_PUBLICO}</p>
      </AuthCard>
    );
  }

  return (
    <AuthCard titulo="Recuperar contraseña">
      <form onSubmit={enviar} className="flex flex-col gap-4">
        <Field
          id="correo"
          label="Correo electrónico"
          type="email"
          autoComplete="username"
          required
          value={correo}
          onChange={(evento) => setCorreo(evento.target.value)}
        />
        <RegionMensaje texto={cargando ? "Procesando solicitud…" : error} tono="error" />
        <Button type="submit" variant="primary" loading={cargando}>
          Solicitar recuperación
        </Button>
      </form>
    </AuthCard>
  );
}

function mensajeError(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.status === 429) return "La operación está temporalmente limitada.";
    if (error.error.codigo === "VALIDACION") return "Revisa el correo ingresado.";
  }
  return "No se pudo procesar la solicitud.";
}
