"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { ACEPTA_ADJUNTOS, NOMBRE_TIPO_ADJUNTO, problemaAdjunto, tipoAdjuntoDe } from "@/src/lib/adjuntos";
import { fechaHora } from "@/src/lib/formato";
import { ApiRequestError } from "@/src/lib/http";
import { listarAdjuntos, subirAdjunto, urlAdjunto } from "@/src/lib/reservas-api";
import type { AdjuntoItem } from "@/src/lib/reservas-types";

/** Adjuntos de una lista de espera (WF-RES-03): ver, descargar y subir archivos técnicos. */
export function AdjuntosListaEspera({ idReserva, puedeSubir }: { idReserva: number; puedeSubir: boolean }) {
  const [adjuntos, setAdjuntos] = useState<AdjuntoItem[] | null>(null);
  const [elegidos, setElegidos] = useState<File[]>([]);
  const [subiendo, setSubiendo] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");
  const entrada = useRef<HTMLInputElement>(null);

  const cargar = useCallback(async () => {
    try {
      setAdjuntos((await listarAdjuntos(idReserva)).datos);
    } catch {
      setAdjuntos([]);
      setMensaje("No se pudieron cargar los adjuntos.");
      setTono("error");
    }
  }, [idReserva]);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  function elegir(archivos: FileList | null) {
    const lista = Array.from(archivos ?? []);
    const problema = lista.map(problemaAdjunto).find((p) => p !== null);
    if (problema) {
      setElegidos([]);
      if (entrada.current) entrada.current.value = "";
      setMensaje(problema);
      setTono("error");
      return;
    }
    setElegidos(lista);
    setMensaje(null);
  }

  async function subir() {
    setSubiendo(true);
    setMensaje("Subiendo…");
    setTono("muted");
    const fallidos: string[] = [];
    for (const archivo of elegidos) {
      try {
        await subirAdjunto(idReserva, archivo, tipoAdjuntoDe(archivo.name) ?? "DOCUMENTO");
      } catch (error) {
        fallidos.push(
          error instanceof ApiRequestError && error.error.mensaje
            ? `«${archivo.name}»: ${error.error.mensaje}`
            : `«${archivo.name}»: no se pudo subir.`
        );
      }
    }
    setElegidos([]);
    if (entrada.current) entrada.current.value = "";
    await cargar();
    if (fallidos.length > 0) {
      setMensaje(fallidos.join(" "));
      setTono("error");
    } else {
      setMensaje("Archivos subidos.");
      setTono("exito");
    }
    setSubiendo(false);
  }

  return (
    <section aria-label="Adjuntos" className="flex flex-col gap-2">
      <h2 className="text-base font-bold text-text">Adjuntos</h2>
      {adjuntos === null ? (
        <p className="text-sm text-muted">Cargando…</p>
      ) : adjuntos.length === 0 ? (
        <p className="text-sm text-muted">Todavía no hay archivos adjuntos.</p>
      ) : (
        <ul className="flex flex-col gap-1 text-sm text-text">
          {adjuntos.map((a) => (
            <li key={a.id} className="flex flex-wrap items-center gap-2">
              <a href={urlAdjunto(idReserva, a.id)} className="font-bold text-primary-2">
                {a.nombre_original}
              </a>
              <span className="text-muted">
                {NOMBRE_TIPO_ADJUNTO[a.tipo_adjunto]} · {Math.max(1, Math.round(a.size_bytes / 1024))} KB ·{" "}
                {fechaHora(a.created_at)}
              </span>
            </li>
          ))}
        </ul>
      )}
      {puedeSubir && (
        <div className="flex flex-col gap-2">
          <label htmlFor="adjunto-archivo" className="text-sm font-bold text-text">
            Adjuntar archivos (DWG, DXF, STEP, STL, PNG, JPG o PDF; máximo 5 MB cada uno)
          </label>
          <input
            id="adjunto-archivo"
            ref={entrada}
            type="file"
            multiple
            accept={ACEPTA_ADJUNTOS}
            onChange={(e) => elegir(e.target.files)}
            className="text-sm text-text"
          />
          <div>
            <Button variant="secondary" size="sm" disabled={subiendo || elegidos.length === 0}
              onClick={() => void subir()}>
              Subir {elegidos.length > 1 ? `${elegidos.length} archivos` : "archivo"}
            </Button>
          </div>
        </div>
      )}
      <RegionMensaje texto={mensaje} tono={mensaje ? tono : "muted"} />
    </section>
  );
}
