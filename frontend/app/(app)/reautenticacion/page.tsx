"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { reautenticar } from "@/src/lib/auth-api";
import { ApiRequestError } from "@/src/lib/http";

// WF-AUTH-07 — specs/modules/auth/wireframes.md
export default function PaginaReautenticacion() {
  return (
    <Suspense fallback={<Tarjeta>Cargando…</Tarjeta>}>
      <FormularioReautenticacion />
    </Suspense>
  );
}

function Tarjeta({ children }: { children: React.ReactNode }) {
  return (
    <div className="mx-auto max-w-[420px] rounded-[16px] border border-border bg-surface p-[30px]">
      <h1 className="mb-5 font-display text-xl font-bold text-text">Reautenticarse</h1>
      {children}
    </div>
  );
}

function FormularioReautenticacion() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const destino = searchParams.get("next") ?? "/reservas";

  const [contrasena, setContrasena] = useState("");
  const [cargando, setCargando] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);

  async function enviar(evento: FormEvent) {
    evento.preventDefault();
    setCargando(true);
    setMensaje(null);
    try {
      await reautenticar(contrasena);
      setMensaje("Validación completada.");
      router.push(destino);
    } catch (error) {
      if (error instanceof ApiRequestError && error.error.codigo === "NO_AUTENTICADO") {
        router.push("/login?motivo=sesion_vencida");
        return;
      }
      setMensaje(mensajeError(error));
    } finally {
      setCargando(false);
    }
  }

  return (
    <Tarjeta>
      <form onSubmit={enviar} className="flex flex-col gap-4">
        <p className="text-sm text-muted">Introduce tu contraseña actual para continuar.</p>
        <Field
          id="contrasena"
          label="Contraseña actual"
          type="password"
          autoComplete="current-password"
          required
          value={contrasena}
          onChange={(evento) => setContrasena(evento.target.value)}
        />
        <RegionMensaje
          texto={cargando ? "Validando contraseña…" : mensaje}
          tono={mensaje === "Validación completada." ? "exito" : "error"}
        />
        <Button type="submit" variant="primary" loading={cargando}>
          Validar y continuar
        </Button>
      </form>
    </Tarjeta>
  );
}

function mensajeError(error: unknown): string {
  if (error instanceof ApiRequestError && error.status === 429) {
    return "La operación está temporalmente limitada.";
  }
  return "No se pudo validar la contraseña.";
}
