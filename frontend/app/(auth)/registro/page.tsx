"use client";

import Link from "next/link";
import { useState, type ChangeEvent, type FormEvent } from "react";
import { AuthCard } from "@/src/components/auth/AuthCard";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { registrar } from "@/src/lib/auth-api";
import { ApiRequestError } from "@/src/lib/http";

const MENSAJE_PUBLICO =
  "Si el correo puede registrarse, la cuenta quedará disponible para iniciar sesión.";

// WF-AUTH-02 — specs/modules/auth/wireframes.md
export default function PaginaRegistro() {
  const [datos, setDatos] = useState({
    correo: "",
    contrasena: "",
    nombre: "",
    documento: "",
    telefono: "",
    institucion: "",
    dependencia: "",
  });
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [enviado, setEnviado] = useState(false);

  function actualizar(campo: keyof typeof datos) {
    return (evento: ChangeEvent<HTMLInputElement>) =>
      setDatos((previo) => ({ ...previo, [campo]: evento.target.value }));
  }

  async function enviar(evento: FormEvent) {
    evento.preventDefault();
    setCargando(true);
    setError(null);
    try {
      await registrar(datos);
      // El 202 es idéntico ante alta creada y ante duplicado de correo,
      // documento o teléfono — no hay una segunda variante que distinguir.
      setEnviado(true);
    } catch (err) {
      setError(mensajeError(err));
    } finally {
      setCargando(false);
    }
  }

  if (enviado) {
    return (
      <AuthCard titulo="Autorregistrarse — respuesta">
        <p className="text-sm text-text">{MENSAJE_PUBLICO}</p>
        <div className="mt-5 flex flex-col gap-2">
          <Link href="/login">
            <Button variant="secondary" fullWidth>
              Continuar al inicio de sesión
            </Button>
          </Link>
          <Link href="/recuperacion">
            <Button variant="ghost" fullWidth>
              Recuperar contraseña
            </Button>
          </Link>
        </div>
      </AuthCard>
    );
  }

  return (
    <AuthCard titulo="Autorregistrarse">
      <p className="mb-4 text-sm text-muted">Todos los datos solicitados son obligatorios.</p>
      <form onSubmit={enviar} className="flex flex-col gap-4">
        <Field
          id="correo"
          label="Correo electrónico"
          type="email"
          autoComplete="email"
          required
          value={datos.correo}
          onChange={actualizar("correo")}
        />
        <Field
          id="contrasena"
          label="Contraseña"
          type="password"
          autoComplete="new-password"
          required
          minLength={8}
          maxLength={64}
          hint="8 a 64 caracteres. Sin composición obligatoria."
          value={datos.contrasena}
          onChange={actualizar("contrasena")}
        />
        <Field
          id="nombre"
          label="Nombre"
          required
          maxLength={150}
          value={datos.nombre}
          onChange={actualizar("nombre")}
        />
        <Field
          id="documento"
          label="Documento"
          required
          maxLength={20}
          value={datos.documento}
          onChange={actualizar("documento")}
        />
        <Field
          id="telefono"
          label="Teléfono"
          required
          maxLength={20}
          value={datos.telefono}
          onChange={actualizar("telefono")}
        />
        <Field
          id="institucion"
          label="Institución"
          required
          maxLength={255}
          value={datos.institucion}
          onChange={actualizar("institucion")}
        />
        <Field
          id="dependencia"
          label="Dependencia"
          required
          maxLength={255}
          value={datos.dependencia}
          onChange={actualizar("dependencia")}
        />
        <RegionMensaje texto={cargando ? "Procesando registro…" : error} tono="error" />
        <Button type="submit" variant="primary" loading={cargando}>
          Enviar registro
        </Button>
      </form>
    </AuthCard>
  );
}

function mensajeError(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.status === 429) return "La operación está temporalmente limitada.";
    if (error.error.codigo === "VALIDACION") return "Revisa los datos ingresados.";
  }
  return "No se pudo procesar el registro.";
}
