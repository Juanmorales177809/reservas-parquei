"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { AuthCard } from "@/src/components/auth/AuthCard";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { activarInvitacion, validarTokenInvitacion } from "@/src/lib/auth-api";
import { ApiRequestError } from "@/src/lib/http";

type EstadoEnlace = "validando" | "vigente" | "no_utilizable";

// WF-AUTH-04 — specs/modules/auth/wireframes.md
export default function PaginaActivacion({
  params,
}: {
  params: { token: string };
}) {
  const { token } = params;
  const router = useRouter();
  const [estadoEnlace, setEstadoEnlace] = useState<EstadoEnlace>("validando");
  const [contrasena, setContrasena] = useState("");
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelado = false;
    validarTokenInvitacion(token)
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
      const sesion = await activarInvitacion(token, contrasena);
      // Activación exitosa deja la sesión iniciada; sin pedir la
      // contraseña otra vez (screens.md, SCR-AUTH-04).
      router.push(
        sesion.actualizacion_inicial_pendiente ? "/usuarios/perfil" : "/reservas"
      );
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

  if (estadoEnlace === "validando") {
    return (
      <AuthCard titulo="Activar una cuenta invitada">
        <RegionMensaje texto="Validando invitación…" />
      </AuthCard>
    );
  }

  if (estadoEnlace === "no_utilizable") {
    return (
      <AuthCard titulo="Activar una cuenta invitada">
        <p className="text-sm text-error-2">
          Esta invitación no puede utilizarse.
          <br />
          Solicita una nueva invitación.
        </p>
      </AuthCard>
    );
  }

  return (
    <AuthCard titulo="Activar una cuenta invitada">
      <form onSubmit={enviar} className="flex flex-col gap-4">
        <p className="text-sm text-muted">Define la contraseña de tu cuenta.</p>
        <Field
          id="contrasena"
          label="Contraseña"
          type="password"
          autoComplete="new-password"
          required
          minLength={8}
          hint="Mínimo 8 caracteres. Sin composición obligatoria."
          value={contrasena}
          onChange={(evento) => setContrasena(evento.target.value)}
        />
        <RegionMensaje texto={cargando ? "Activando cuenta…" : error} tono="error" />
        <Button type="submit" variant="primary" loading={cargando}>
          Activar cuenta
        </Button>
      </form>
    </AuthCard>
  );
}

function mensajeError(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.status === 429) return "La operación está temporalmente limitada.";
    if (error.status === 409) return "No se puede completar la activación.";
    if (error.error.codigo === "VALIDACION") {
      // §4.4 no distingue en la envolvente entre "contraseña fuera de
      // rango" e "identidad no válida" — ambas responden 422 VALIDACION.
      // La longitud ya se valida en el cliente (minLength), así que un
      // 422 del servidor en este punto es más probable que sea de
      // identidad: se usa el mensaje seguro, sin detalles internos.
      return "No se puede completar la activación. Corrige la ficha mediante la gestión administrativa y solicita una nueva invitación.";
    }
  }
  return "No se pudo completar la activación.";
}
