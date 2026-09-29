"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { Select } from "@/src/components/ui/Select";
import { invitar, reenviarInvitacion } from "@/src/lib/auth-api";
import { ApiRequestError } from "@/src/lib/http";

type TipoCuenta = "USUARIO" | "PERSONAL";

// WF-AUTH-03 — specs/modules/auth/wireframes.md
export default function PaginaInvitar() {
  return (
    <Suspense fallback={<Tarjeta titulo="Invitar una cuenta">Cargando…</Tarjeta>}>
      <FormularioInvitar />
    </Suspense>
  );
}

function Tarjeta({ titulo, children }: { titulo: string; children: React.ReactNode }) {
  return (
    <div className="max-w-[480px] rounded-[16px] border border-border bg-surface p-[30px]">
      <h1 className="mb-5 font-display text-xl font-bold text-text">{titulo}</h1>
      {children}
    </div>
  );
}

function FormularioInvitar() {
  const searchParams = useSearchParams();
  // Reenvío: el contexto llega por parámetros de URL — no se dibuja un
  // listado ni un buscador (wireframes.md, WF-AUTH-03).
  const idReenvio = searchParams.get("reenviarId");
  const correoReenvio = searchParams.get("correo");
  const tipoReenvio = searchParams.get("tipo") as TipoCuenta | null;
  const esReenvio = Boolean(idReenvio && correoReenvio && tipoReenvio);

  // FE-11: al llegar desde identidades con ?correo=&tipo=, el formulario
  // arranca precargado. En modo reenvío esta rama no se pinta.
  const [correo, setCorreo] = useState(correoReenvio ?? "");
  const [tipoCuenta, setTipoCuenta] = useState<TipoCuenta>(tipoReenvio ?? "USUARIO");  const [idUnidad, setIdUnidad] = useState("");
  const [cargando, setCargando] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"error" | "exito">("error");

  async function emitir(evento: FormEvent) {
    evento.preventDefault();
    setCargando(true);
    setMensaje(null);
    try {
      await invitar({
        correo,
        tipo_cuenta: tipoCuenta,
        id_unidad: tipoCuenta === "PERSONAL" ? Number(idUnidad) : undefined,
      });
      setTono("exito");
      setMensaje("Invitación emitida.");
    } catch (error) {
      setTono("error");
      setMensaje(mensajeError(error));
    } finally {
      setCargando(false);
    }
  }

  async function reenviar(evento: FormEvent) {
    evento.preventDefault();
    if (!idReenvio) return;
    setCargando(true);
    setMensaje(null);
    try {
      await reenviarInvitacion(Number(idReenvio));
      setTono("exito");
      setMensaje("Invitación reenviada.");
    } catch (error) {
      setTono("error");
      setMensaje(mensajeError(error));
    } finally {
      setCargando(false);
    }
  }

  if (esReenvio) {
    return (
      <Tarjeta titulo="Reenviar invitación">
        <form onSubmit={reenviar} className="flex flex-col gap-4">
          <p className="text-sm text-muted">Correo destino: {correoReenvio}</p>
          <p className="text-sm text-muted">Tipo de cuenta: {tipoReenvio}</p>
          <RegionMensaje texto={cargando ? "Reenviando invitación…" : mensaje} tono={tono} />
          <Button type="submit" variant="primary" loading={cargando}>
            Reenviar invitación
          </Button>
        </form>
      </Tarjeta>
    );
  }

  return (
    <Tarjeta titulo="Invitar una cuenta">
      <form onSubmit={emitir} className="flex flex-col gap-4">
        <Field
          id="correo"
          label="Correo destino"
          type="email"
          required
          value={correo}
          onChange={(e) => setCorreo(e.target.value)}
        />
        <Select
          id="tipo_cuenta"
          label="Tipo de cuenta"
          required
          value={tipoCuenta}
          onChange={(e) => setTipoCuenta(e.target.value as TipoCuenta)}
        >
          <option value="USUARIO">Usuario</option>
          <option value="PERSONAL">Personal</option>
        </Select>
        {tipoCuenta === "PERSONAL" && (
          <Field
            id="id_unidad"
            label="Unidad del cargo"
            type="number"
            required
            value={idUnidad}
            onChange={(e) => setIdUnidad(e.target.value)}
          />
        )}
        <RegionMensaje texto={cargando ? "Emitiendo invitación…" : mensaje} tono={tono} />
        <Button type="submit" variant="primary" loading={cargando}>
          Emitir invitación
        </Button>
      </form>
    </Tarjeta>
  );
}

function mensajeError(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.status === 403) return "No se puede realizar esta operación.";
    if (error.status === 404) return "No se puede acceder a la invitación.";
    if (error.status === 409) return "No se puede emitir esta invitación.";
    if (error.error.codigo === "VALIDACION") return "Revisa los datos ingresados.";
  }
  return "No se pudo completar la operación.";
}
