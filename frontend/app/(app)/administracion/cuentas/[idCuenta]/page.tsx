"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { Select } from "@/src/components/ui/Select";
import { cambiarEstadoCuenta, cambiarIdentidadCuenta } from "@/src/lib/auth-api";
import { ApiRequestError } from "@/src/lib/http";

type TipoCuenta = "USUARIO" | "PERSONAL";

// WF-AUTH-09 — specs/modules/auth/wireframes.md
//
// El contrato de auth no expone una consulta de cuenta ajena (§10, "lo que
// este contrato no expone"): los datos de la cuenta objetivo llegan por el
// contexto, aquí representado con parámetros de URL — el mismo mecanismo
// que WF-AUTH-03 usa para el reenvío de invitaciones. No es un catálogo ni
// un buscador nuevo, es el "contexto existente" que ya deja pendiente el
// propio wireframe.
export default function PaginaGestionarCuenta({
  params,
}: {
  params: { idCuenta: string };
}) {
  return (
    <Suspense fallback={<Tarjeta>Cargando…</Tarjeta>}>
      <ContenidoGestionarCuenta idCuenta={Number(params.idCuenta)} />
    </Suspense>
  );
}

function Tarjeta({ children }: { children: React.ReactNode }) {
  return (
    <div className="max-w-[560px] rounded-[16px] border border-border bg-surface p-[30px]">
      <h1 className="mb-5 font-display text-xl font-bold text-text">Gestionar cuenta</h1>
      {children}
    </div>
  );
}

function ContenidoGestionarCuenta({ idCuenta }: { idCuenta: number }) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const correo = searchParams.get("correo") ?? "(no suministrado por el contexto)";
  const tipo = (searchParams.get("tipo") as TipoCuenta | null) ?? "USUARIO";
  const identidad = searchParams.get("identidad") ?? "(no suministrada por el contexto)";

  const [activa, setActiva] = useState(searchParams.get("estado") !== "inactiva");
  const [cargandoEstado, setCargandoEstado] = useState(false);
  const [mensajeEstado, setMensajeEstado] = useState<string | null>(null);
  const [tonoEstado, setTonoEstado] = useState<"error" | "exito">("error");

  const [tipoDestino, setTipoDestino] = useState<TipoCuenta>("USUARIO");
  const [idDestino, setIdDestino] = useState("");
  const [cargandoTipo, setCargandoTipo] = useState(false);
  const [mensajeTipo, setMensajeTipo] = useState<string | null>(null);
  const [tonoTipo, setTonoTipo] = useState<"error" | "exito">("error");

  function volverTrasReautenticacion() {
    const siguiente = `${pathname}?${searchParams.toString()}`;
    router.push(`/reautenticacion?next=${encodeURIComponent(siguiente)}`);
  }

  async function cambiarEstado(evento: FormEvent) {
    evento.preventDefault();
    setCargandoEstado(true);
    setMensajeEstado(null);
    try {
      const respuesta = await cambiarEstadoCuenta(idCuenta, !activa);
      setActiva(respuesta.estado);
      setTonoEstado("exito");
      setMensajeEstado("Estado de cuenta actualizado.");
    } catch (error) {
      setTonoEstado("error");
      setMensajeEstado(mensajeErrorEstado(error));
    } finally {
      setCargandoEstado(false);
    }
  }

  async function aplicarCambioTipo(evento: FormEvent) {
    evento.preventDefault();
    setCargandoTipo(true);
    setMensajeTipo(null);
    try {
      await cambiarIdentidadCuenta(
        idCuenta,
        tipoDestino === "PERSONAL"
          ? { tipo_cuenta: "PERSONAL", id_persona: Number(idDestino) }
          : { tipo_cuenta: "USUARIO", id_usuario: Number(idDestino) }
      );
      setTonoTipo("exito");
      setMensajeTipo("Tipo de identidad actualizado.");
    } catch (error) {
      if (error instanceof ApiRequestError && error.error.codigo === "REAUTENTICACION_REQUERIDA") {
        volverTrasReautenticacion();
        return;
      }
      setTonoTipo("error");
      setMensajeTipo(mensajeErrorTipo(error));
    } finally {
      setCargandoTipo(false);
    }
  }

  return (
    <Tarjeta>
      <dl className="mb-6 flex flex-col gap-1 text-sm">
        <div className="flex justify-between">
          <dt className="text-muted">Cuenta</dt>
          <dd className="text-text">{idCuenta}</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-muted">Correo</dt>
          <dd className="text-text">{correo}</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-muted">Estado</dt>
          <dd className="text-text">{activa ? "Activa" : "Inactiva"}</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-muted">Tipo</dt>
          <dd className="text-text">{tipo}</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-muted">Identidad</dt>
          <dd className="text-text">{identidad}</dd>
        </div>
      </dl>

      <form onSubmit={cambiarEstado} className="flex flex-col gap-3 border-t border-border pt-5">
        <h2 className="font-display text-sm font-bold text-text">Estado de cuenta</h2>
        <Button
          type="submit"
          variant={activa ? "danger" : "success"}
          loading={cargandoEstado}
          fullWidth
        >
          {activa ? "Desactivar cuenta" : "Reactivar cuenta"}
        </Button>
        <RegionMensaje texto={mensajeEstado} tono={tonoEstado} />
      </form>

      <form
        onSubmit={aplicarCambioTipo}
        className="mt-6 flex flex-col gap-4 border-t border-border pt-5"
      >
        <h2 className="font-display text-sm font-bold text-text">Cambiar tipo de identidad</h2>
        <Select
          id="tipo_destino"
          label="Tipo destino"
          required
          value={tipoDestino}
          onChange={(e) => setTipoDestino(e.target.value as TipoCuenta)}
        >
          <option value="USUARIO">Usuario</option>
          <option value="PERSONAL">Personal</option>
        </Select>
        <Field
          id="id_destino"
          label={tipoDestino === "PERSONAL" ? "Identidad destino (id_persona)" : "Identidad destino (id_usuario)"}
          type="number"
          required
          value={idDestino}
          onChange={(e) => setIdDestino(e.target.value)}
        />
        <RegionMensaje texto={cargandoTipo ? "Aplicando cambio…" : mensajeTipo} tono={tonoTipo} />
        <Button type="submit" variant="primary" loading={cargandoTipo}>
          Aplicar cambio de tipo
        </Button>
      </form>
    </Tarjeta>
  );
}

function mensajeErrorEstado(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.status === 403) return "No se puede realizar esta operación.";
    if (error.status === 404) return "No se puede acceder a esta cuenta.";
    if (error.status === 409) {
      return "No se puede aplicar el cambio: debe conservarse al menos una cuenta administrativa válida.";
    }
  }
  return "No se pudo actualizar el estado de la cuenta.";
}

function mensajeErrorTipo(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.status === 403) return "No se puede realizar esta operación.";
    if (error.status === 404) return "No se puede acceder a esta cuenta.";
    if (error.status === 409) return "No se puede vincular la identidad seleccionada.";
    if (error.error.codigo === "VALIDACION") return "Revisa los datos ingresados.";
  }
  return "No se pudo aplicar el cambio de tipo.";
}
