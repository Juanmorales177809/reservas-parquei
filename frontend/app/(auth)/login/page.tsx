"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState, type FormEvent } from "react";
import { AuthCard } from "@/src/components/auth/AuthCard";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { iniciarSesion } from "@/src/lib/auth-api";
import { ApiRequestError } from "@/src/lib/http";

// WF-AUTH-01 — specs/modules/auth/wireframes.md
export default function PaginaLogin() {
  return (
    <Suspense fallback={<AuthCard titulo="Iniciar sesión">Cargando…</AuthCard>}>
      <FormularioLogin />
    </Suspense>
  );
}

function FormularioLogin() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const sesionVencida = searchParams.get("motivo") === "sesion_vencida";

  const [correo, setCorreo] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [cargando, setCargando] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);

  async function enviar(evento: FormEvent) {
    evento.preventDefault();
    setCargando(true);
    setMensaje(null);
    try {
      const sesion = await iniciarSesion({ correo, contrasena });
      setMensaje("Inicio de sesión correcto.");
      // "La fuente no fija una pantalla de inicio de la aplicación"
      // (screens.md, SCR-AUTH-01): Reservas es el primer destino de la
      // navegación (specs/ui/layout.md) y sirve de destino por defecto
      // hasta que exista una pantalla de inicio propia.
      const destino = sesion.actualizacion_inicial_pendiente
        ? "/usuarios/perfil"
        : "/reservas";
      router.push(destino);
    } catch (error) {
      setMensaje(mensajeError(error));
    } finally {
      setCargando(false);
    }
  }

  return (
    <AuthCard titulo="Iniciar sesión">
      {sesionVencida && (
        <p className="mb-4 text-sm text-error-2">Debes iniciar sesión nuevamente.</p>
      )}
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
        <Field
          id="contrasena"
          label="Contraseña"
          type="password"
          autoComplete="current-password"
          required
          value={contrasena}
          onChange={(evento) => setContrasena(evento.target.value)}
        />
        <RegionMensaje
          texto={cargando ? "Iniciando sesión…" : mensaje}
          tono={mensaje === "Inicio de sesión correcto." ? "exito" : "error"}
        />
        <Button type="submit" variant="primary" loading={cargando}>
          Iniciar sesión
        </Button>
      </form>
      <div className="mt-5 flex flex-col gap-2">
        <Link href="/registro" className="text-sm font-bold text-primary-2">
          Autorregistrarse
        </Link>
        <Link href="/recuperacion" className="text-sm font-bold text-primary-2">
          Recuperar contraseña
        </Link>
      </div>
    </AuthCard>
  );
}

function mensajeError(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.status === 429) return "La operación está temporalmente limitada.";
    if (error.error.codigo === "VALIDACION") return "Revisa los datos ingresados.";
  }
  // 401 CREDENCIALES_INVALIDAS es idéntico para correo inexistente,
  // contraseña incorrecta, cuenta o identidad inactiva (SEC-ABU-02) — y
  // es también el mensaje de repliegue ante cualquier otro fallo, porque
  // esta pantalla no distingue causas.
  return "No se pudo iniciar sesión con las credenciales proporcionadas.";
}
