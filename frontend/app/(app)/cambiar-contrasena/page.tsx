"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import type { ContextoSesion } from "@/src/lib/auth-types";
import { cambiarContrasenaPropia } from "@/src/lib/auth-api";
import { apiRequest, ApiRequestError } from "@/src/lib/http";

type Fase = "verificando" | "listo" | "exito";

// WF-AUTH-08 — specs/modules/auth/wireframes.md
export default function PaginaCambiarContrasena() {
  const router = useRouter();
  const [fase, setFase] = useState<Fase>("verificando");
  const [contrasena, setContrasena] = useState("");
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelado = false;
    apiRequest<ContextoSesion>("/api/auth/sesiones/actual")
      .then((sesion) => {
        if (cancelado) return;
        if (!sesion.autenticacion_reciente) {
          router.replace("/reautenticacion?next=/cambiar-contrasena");
          return;
        }
        setFase("listo");
      })
      .catch(() => {
        if (!cancelado) router.replace("/login?motivo=sesion_vencida");
      });
    return () => {
      cancelado = true;
    };
  }, [router]);

  useEffect(() => {
    if (fase !== "exito") return;
    const temporizador = setTimeout(() => router.push("/login"), 1500);
    return () => clearTimeout(temporizador);
  }, [fase, router]);

  async function enviar(evento: FormEvent) {
    evento.preventDefault();
    setCargando(true);
    setError(null);
    try {
      await cambiarContrasenaPropia(contrasena);
      // Revoca todas las sesiones, incluida la actual, y no crea una
      // nueva — hay que iniciar sesión de nuevo (SEC-SES-10).
      setFase("exito");
    } catch (err) {
      if (err instanceof ApiRequestError && err.error.codigo === "REAUTENTICACION_REQUERIDA") {
        router.push("/reautenticacion?next=/cambiar-contrasena");
        return;
      }
      if (err instanceof ApiRequestError && err.error.codigo === "NO_AUTENTICADO") {
        router.push("/login?motivo=sesion_vencida");
        return;
      }
      setError(mensajeError(err));
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="mx-auto max-w-[420px] rounded-[16px] border border-border bg-surface p-[30px]">
      <h1 className="mb-5 font-display text-xl font-bold text-text">Cambiar contraseña</h1>

      {fase === "verificando" && <RegionMensaje texto="Verificando…" />}

      {fase === "listo" && (
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
          <RegionMensaje texto={cargando ? "Cambiando contraseña…" : error} tono="error" />
          <Button type="submit" variant="primary" loading={cargando}>
            Cambiar contraseña
          </Button>
        </form>
      )}

      {fase === "exito" && (
        <p className="text-sm text-text">
          Contraseña actualizada.
          <br />
          Debes iniciar sesión con la nueva contraseña.
        </p>
      )}
    </div>
  );
}

function mensajeError(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.status === 429) return "La operación está temporalmente limitada.";
    if (error.error.codigo === "VALIDACION") return "Revisa la contraseña ingresada.";
  }
  return "No se pudo cambiar la contraseña.";
}
