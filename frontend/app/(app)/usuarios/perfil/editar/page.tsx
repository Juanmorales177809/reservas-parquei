"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { ApiRequestError } from "@/src/lib/http";
import { actualizarPerfil, obtenerPerfil } from "@/src/lib/usuarios-api";

// WF-USR-03 — specs/modules/usuarios/wireframes.md
export default function PaginaEditarDatos() {
  const router = useRouter();
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [nombre, setNombre] = useState("");
  const [documento, setDocumento] = useState("");
  const [telefono, setTelefono] = useState("");
  const [institucion, setInstitucion] = useState("");
  const [dependencia, setDependencia] = useState("");
  const [correo, setCorreo] = useState("");
  const [errorCampo, setErrorCampo] = useState<{ campo: string; texto: string } | null>(null);
  const [mensaje, setMensaje] = useState<string | null>(null);

  useEffect(() => {
    let cancelado = false;
    obtenerPerfil()
      .then((p) => {
        if (cancelado) return;
        setNombre(p.nombre);
        setDocumento(p.documento);
        setTelefono(p.telefono);
        setInstitucion(p.institucion);
        setDependencia(p.dependencia);
        setCorreo(p.correo);
        setCargando(false);
      })
      .catch((err) => {
        if (cancelado) return;
        if (err instanceof ApiRequestError && err.status === 401) {
          router.replace("/login?motivo=sesion_vencida");
        }
      });
    return () => {
      cancelado = true;
    };
  }, [router]);

  async function enviar(evento: FormEvent) {
    evento.preventDefault();
    setGuardando(true);
    setErrorCampo(null);
    setMensaje(null);
    try {
      await actualizarPerfil({ nombre, documento, telefono, institucion, dependencia });
      setMensaje("Datos actualizados.");
    } catch (error) {
      if (error instanceof ApiRequestError) {
        if (error.error.codigo === "DOCUMENTO_DUPLICADO") {
          setErrorCampo({ campo: "documento", texto: "Este documento ya está registrado en otra identidad." });
          return;
        }
        if (error.error.codigo === "TELEFONO_DUPLICADO") {
          setErrorCampo({ campo: "telefono", texto: "Este teléfono ya está registrado en otra identidad." });
          return;
        }
        if (error.error.codigo === "VALIDACION") {
          setMensaje("Revisa los datos ingresados: todos son obligatorios.");
          return;
        }
      }
      setMensaje("No se pudieron guardar los cambios.");
    } finally {
      setGuardando(false);
    }
  }

  if (cargando) {
    return (
      <div className="flex flex-col gap-4">
        <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Editar mis datos</h1>
        <RegionMensaje texto="Cargando tus datos…" tono="muted" />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Editar mis datos</h1>
      <form onSubmit={(e) => void enviar(e)} className="flex flex-col gap-4">
        <p className="text-sm text-muted">Correo (no editable): {correo}</p>
        <Field id="nombre" label="Nombre" value={nombre}
          onChange={(e) => setNombre(e.target.value)} required
          error={errorCampo?.campo === "nombre" ? errorCampo.texto : undefined} />
        <Field id="documento" label="Documento" value={documento}
          onChange={(e) => setDocumento(e.target.value)} required
          error={errorCampo?.campo === "documento" ? errorCampo.texto : undefined} />
        <Field id="telefono" label="Teléfono" value={telefono}
          onChange={(e) => setTelefono(e.target.value)} required
          error={errorCampo?.campo === "telefono" ? errorCampo.texto : undefined} />
        <Field id="institucion" label="Institución" value={institucion}
          onChange={(e) => setInstitucion(e.target.value)} required />
        <Field id="dependencia" label="Dependencia" value={dependencia}
          onChange={(e) => setDependencia(e.target.value)} required />
        <RegionMensaje
          texto={guardando ? "Guardando cambios…" : mensaje}
          tono={mensaje === "Datos actualizados." ? "exito" : mensaje ? "error" : "muted"}
        />
        <div>
          <Button type="submit" variant="primary" loading={guardando}>
            Guardar cambios
          </Button>
        </div>
      </form>
    </div>
  );
}
