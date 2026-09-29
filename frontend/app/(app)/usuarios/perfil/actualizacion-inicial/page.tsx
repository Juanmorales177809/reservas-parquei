"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { SeccionVinculaciones } from "@/src/components/usuarios/SeccionVinculaciones";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { ApiRequestError } from "@/src/lib/http";
import { actualizarPerfil, confirmarActualizacionInicial, obtenerPerfil } from "@/src/lib/usuarios-api";
import type { Perfil } from "@/src/lib/usuarios-types";

// WF-USR-01 — specs/modules/usuarios/wireframes.md
export default function PaginaActualizacionInicial() {
  const router = useRouter();
  const [perfil, setPerfil] = useState<Perfil | null>(null);
  const [nombre, setNombre] = useState("");
  const [documento, setDocumento] = useState("");
  const [telefono, setTelefono] = useState("");
  const [institucion, setInstitucion] = useState("");
  const [dependencia, setDependencia] = useState("");
  const [guardando, setGuardando] = useState(false);
  const [confirmando, setConfirmando] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");

  async function cargar(): Promise<Perfil> {
    const p = await obtenerPerfil();
    setPerfil(p);
    setNombre(p.nombre);
    setDocumento(p.documento);
    setTelefono(p.telefono);
    setInstitucion(p.institucion);
    setDependencia(p.dependencia);
    return p;
  }

  useEffect(() => {
    let cancelado = false;
    cargar().catch((err) => {
      if (cancelado) return;
      if (err instanceof ApiRequestError && err.status === 401) {
        router.replace("/login?motivo=sesion_vencida");
        return;
      }
      setMensaje("No se pudo cargar tu perfil.");
      setTono("error");
    });
    return () => {
      cancelado = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router]);

  async function guardarDatos() {
    setGuardando(true);
    setMensaje(null);
    try {
      const p = await actualizarPerfil({ nombre, documento, telefono, institucion, dependencia });
      setPerfil(p);
      setMensaje("Datos guardados.");
      setTono("exito");
    } catch (error) {
      if (error instanceof ApiRequestError && (error.error.codigo === "DOCUMENTO_DUPLICADO" || error.error.codigo === "TELEFONO_DUPLICADO")) {
        setMensaje("El documento o teléfono ya está registrado en otra identidad.");
      } else {
        setMensaje("No se pudieron guardar los datos.");
      }
      setTono("error");
    } finally {
      setGuardando(false);
    }
  }

  async function continuar() {
    setConfirmando(true);
    setMensaje(null);
    try {
      await guardarDatosSilenciosos();
      await confirmarActualizacionInicial();
      setMensaje("Perfil completado.");
      setTono("exito");
    } catch (error) {
      if (error instanceof ApiRequestError && error.error.codigo === "CONFLICTO") {
        setMensaje("Completa los datos obligatorios y registra al menos una vinculación válida antes de continuar.");
      } else {
        setMensaje("No se pudo completar la actualización.");
      }
      setTono("error");
    } finally {
      setConfirmando(false);
    }
  }

  async function guardarDatosSilenciosos() {
    await actualizarPerfil({ nombre, documento, telefono, institucion, dependencia });
  }

  if (!perfil) {
    return (
      <div className="flex flex-col gap-4">
        <h1 className="text-2xl font-bold text-text">Completa tu perfil</h1>
        <RegionMensaje texto={mensaje ?? "Cargando tu perfil…"} tono={mensaje ? tono : "muted"} />
      </div>
    );
  }

  const vinculos = perfil.vinculaciones;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold text-text">Completa tu perfil</h1>
        <p className="mt-1 text-sm text-muted">
          Revisa tus datos y agrega al menos una vinculación académica o investigativa para continuar.
        </p>
      </div>
      <div className="flex flex-col gap-4">
        <Field id="nombre" label="Nombre" value={nombre}
          onChange={(e) => setNombre(e.target.value)} required />
        <Field id="documento" label="Documento" value={documento}
          onChange={(e) => setDocumento(e.target.value)} required />
        <Field id="telefono" label="Teléfono" value={telefono}
          onChange={(e) => setTelefono(e.target.value)} required />
        <Field id="institucion" label="Institución" value={institucion}
          onChange={(e) => setInstitucion(e.target.value)} required />
        <Field id="dependencia" label="Dependencia" value={dependencia}
          onChange={(e) => setDependencia(e.target.value)} required />
        <div>
          <Button variant="secondary" loading={guardando} onClick={() => void guardarDatos()}>
            Guardar datos
          </Button>
        </div>
      </div>
      <SeccionVinculaciones
        iniciales={vinculos}
        permiteDesactivar={true}
        alCambiar={(v) => setPerfil((p) => (p ? { ...p, vinculaciones: v } : p))}
      />
      <RegionMensaje texto={confirmando ? "Confirmando…" : mensaje} tono={confirmando ? "muted" : tono} />
      <div>
        <Button variant="primary" loading={confirmando} onClick={() => void continuar()}>
          Continuar
        </Button>
      </div>
    </div>
  );
}
