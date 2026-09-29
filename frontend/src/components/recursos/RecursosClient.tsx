"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { Select } from "@/src/components/ui/Select";
import { ApiRequestError } from "@/src/lib/http";
import { crearRecurso, listarRecursos } from "@/src/lib/recursos-api";
import type { RecursoResumen, TipoRecurso } from "@/src/lib/recursos-types";

/** Catálogo y registro (WF-REC-01). `puedeGestionar` viene del servidor. */
export function RecursosClient({ puedeGestionar }: { puedeGestionar: boolean }) {
  const router = useRouter();
  const [recursos, setRecursos] = useState<RecursoResumen[] | null>(null);
  const [tipo, setTipo] = useState<TipoRecurso>("MOBILIARIO");
  const [idUnidad, setIdUnidad] = useState("");
  const [nombre, setNombre] = useState("");
  const [placa, setPlaca] = useState("");
  const [ocupada, setOcupada] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");

  async function recargar() {
    const r = await listarRecursos();
    setRecursos(r.datos);
  }

  useEffect(() => {
    let cancelado = false;
    recargar().catch((err) => {
      if (cancelado) return;
      if (err instanceof ApiRequestError && err.status === 401) {
        router.replace("/login?motivo=sesion_vencida");
        return;
      }
      setMensaje("No se pudo cargar el catálogo.");
      setTono("error");
    });
    return () => {
      cancelado = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router]);

  async function guardar(evento: FormEvent) {
    evento.preventDefault();
    setOcupada(true);
    setMensaje(null);
    try {
      await crearRecurso({
        id_unidad: Number(idUnidad),
        tipo,
        especializacion:
          tipo === "EQUIPO"
            ? { nombre_equipo: nombre, placa: placa || undefined }
            : { nombre },
      });
      setNombre("");
      setPlaca("");
      await recargar();
      setMensaje("Recurso creado.");
      setTono("exito");
    } catch (error) {
      setMensaje(mensajeError(error));
      setTono("error");
    } finally {
      setOcupada(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-text">Recursos</h1>
      {recursos === null ? (
        <RegionMensaje texto={mensaje ?? "Cargando catálogo…"} tono={mensaje ? tono : "muted"} />
      ) : (
        <ul className="flex flex-col gap-1 text-sm text-text">
          {recursos.map((r) => (
            <li key={r.id}>
              <Link href={`/recursos/${r.id}`} className="font-bold text-primary-2">
                {r.tipo} #{r.id}
              </Link>{" "}
              {!r.habilitado && "(deshabilitado)"}
            </li>
          ))}
        </ul>
      )}
      {puedeGestionar && (
        <form onSubmit={(e) => void guardar(e)} className="flex flex-col gap-4">
          <h2 className="text-base font-bold text-text">Registrar recurso</h2>
          <Field id="rec-unidad" label="Unidad (id)" value={idUnidad}
            onChange={(e) => setIdUnidad(e.target.value)} required />
          <Select id="rec-tipo" label="Tipo" value={tipo}
            onChange={(e) => setTipo(e.target.value as TipoRecurso)}>
            <option value="MOBILIARIO">Mobiliario</option>
            <option value="OTRO">Otro</option>
            <option value="EQUIPO">Equipo (solo Administrador global)</option>
          </Select>
          <Field id="rec-nombre" label={tipo === "EQUIPO" ? "Nombre del equipo" : "Nombre"}
            value={nombre} onChange={(e) => setNombre(e.target.value)} required />
          {tipo === "EQUIPO" && (
            <Field id="rec-placa" label="Placa" value={placa}
              onChange={(e) => setPlaca(e.target.value)} />
          )}
          <div>
            <Button type="submit" variant="primary" loading={ocupada}>Guardar recurso</Button>
          </div>
        </form>
      )}
      <RegionMensaje texto={mensaje} tono={mensaje ? tono : "muted"} />
    </div>
  );
}

function mensajeError(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.error.codigo === "TIPO_INCOMPATIBLE") return "Ese tipo no se puede registrar así.";
    if (error.error.codigo === "UNIDAD_INCOMPATIBLE") return "La unidad no es válida para esta operación.";
    if (error.error.codigo === "VALIDACION") return "Revisa los datos ingresados.";
    if (error.error.codigo === "NO_AUTORIZADO" || error.status === 403)
      return "No tienes permiso para crear este recurso.";
    if (error.status === 429) return "La operación está temporalmente limitada.";
  }
  return "No se pudo completar la operación.";
}
