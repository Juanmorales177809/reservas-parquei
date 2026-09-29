"use client";

import Link from "next/link";
import { useEffect, useState, type FormEvent } from "react";
import { AuthCard } from "@/src/components/auth/AuthCard";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { restablecerContrasena, validarTokenRecuperacion } from "@/src/lib/auth-api";
import { ApiRequestError } from "@/src/lib/http";

type EstadoEnlace = "validando" | "vigente" | "no_utilizable";

// WF-AUTH-06 — specs/modules/auth/wireframes.md
export default function PaginaRestablecer({
  params,
}: {
  params: { token: string };
}) {
  const { token } = params;
  const [estadoEnlace, setEstadoEnlace] = useState<EstadoEnlace>("validando");
  const [contrasena, setContrasena] = useState("");
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exito, setExito] = useState(false);

  useEffect(() => {
    let cancelado = false;
    validarTokenRecuperacion(token)
      .then((respuesta) => {
        if (!cancelado) setEstadoEnlace(respuesta.vigente ? "vigente" : "no_utilizable");
      })
      .catch(() => {
        if (!cancelado) setEstadoEnlace("no_utilizable");
      });
    return () => {
      cancelado = true;
    };
  }, [token]);

  async function enviar(evento: FormEvent) {
    evento.preventDefault();
    setCargando(true);
    setError(null);
    try {
      await restablecerContrasena(token, contrasena);
      setExito(true);
    } catch (err) {
      if (err instanceof ApiRequestError && err.status === 410) {
        setEstadoEnlace("no_utilizable");
      } else {
        setError(mensajeError(err));
      }
    } finally {
      setCargando(false);
    }
  }

  if (exito) {
    return (
      <AuthCard titulo="Restablecer la contraseña — resultado">
        <p className="text-sm text-text">
          Contraseña restablecida.
          <br />
          Debes iniciar sesión con la nueva contraseña.
        </p>
        <Link href="/login" className="mt-5 block">
          <Button variant="primary" fullWidth>
            Iniciar sesión
          </Button>
        </Link>
      </AuthCard>
    );
  }

  if (estadoEnlace === "validando") {
    return (
      <AuthCard titulo="Restablecer la contraseña">
        <RegionMensaje texto="Validando enlace…" />
      </AuthCard>
    );
  }

  if (estadoEnlace === "no_utilizable") {
    return (
      <AuthCard titulo="Restablecer la contraseña">
        <p className="text-sm text-error-2">
          Este enlace no puede utilizarse. La contraseña no se ha cambiado.
        </p>
      </AuthCard>
    );
  }

  return (
    <AuthCard titulo="Restablecer la contraseña">
      <form onSubmit={enviar} className="flex flex-col gap-4">
        <Field
          id="contrasena"
          label="Nueva contraseña"
          type="password"
          autoComplete="new-password"
          required
          minLength={8}
          maxLength={64}
          hint="Mínimo 8 caracteres. Sin composición obligatoria."
          value={contrasena}
          onChange={(evento) => setContrasena(evento.target.value)}
        />
        <RegionMensaje
          texto={cargando ? "Restableciendo contraseña…" : error}
          tono="error"
        />
        <Button type="submit" variant="primary" loading={cargando}>
          Restablecer contraseña
        </Button>
      </form>
    </AuthCard>
  );
}

function mensajeError(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.status === 429) return "La operación está temporalmente limitada.";
    if (error.error.codigo === "VALIDACION") return "Revisa la contraseña ingresada.";
  }
  return "No se pudo restablecer la contraseña.";
}
