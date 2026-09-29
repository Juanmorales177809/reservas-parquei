"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { SeccionVinculaciones } from "@/src/components/usuarios/SeccionVinculaciones";
import { ApiRequestError } from "@/src/lib/http";
import { obtenerPerfil } from "@/src/lib/usuarios-api";
import type { Vinculaciones } from "@/src/lib/usuarios-types";

// WF-USR-05 — specs/modules/usuarios/wireframes.md
export default function PaginaVinculaciones() {
  const router = useRouter();
  const [vinculaciones, setVinculaciones] = useState<Vinculaciones | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelado = false;
    obtenerPerfil()
      .then((p) => {
        if (!cancelado) setVinculaciones(p.vinculaciones);
      })
      .catch((err) => {
        if (cancelado) return;
        if (err instanceof ApiRequestError && err.status === 401) {
          router.replace("/login?motivo=sesion_vencida");
          return;
        }
        setError("No se pudieron cargar tus vinculaciones.");
      });
    return () => {
      cancelado = true;
    };
  }, [router]);

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-bold text-text">Mis vinculaciones</h1>
      {error && <RegionMensaje texto={error} tono="error" />}
      {!vinculaciones && !error && (
        <RegionMensaje texto="Cargando tus vinculaciones…" tono="muted" />
      )}
      {vinculaciones && (
        <SeccionVinculaciones
          iniciales={vinculaciones}
          permiteDesactivar={true}
          alCambiar={setVinculaciones}
        />
      )}
    </div>
  );
}
