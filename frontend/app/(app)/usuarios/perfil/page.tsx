"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { ApiRequestError } from "@/src/lib/http";
import { obtenerPerfil } from "@/src/lib/usuarios-api";
import type { Perfil } from "@/src/lib/usuarios-types";

// WF-USR-02 — specs/modules/usuarios/wireframes.md
export default function PaginaPerfil() {
  const router = useRouter();
  const [perfil, setPerfil] = useState<Perfil | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelado = false;
    obtenerPerfil()
      .then((p) => {
        if (!cancelado) setPerfil(p);
      })
      .catch((err) => {
        if (cancelado) return;
        if (err instanceof ApiRequestError && err.status === 401) {
          router.replace("/login?motivo=sesion_vencida");
          return;
        }
        setError("No se pudo cargar tu perfil.");
      });
    return () => {
      cancelado = true;
    };
  }, [router]);

  if (error) {
    return (
      <div className="flex flex-col gap-4">
        <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Mi perfil</h1>
        <RegionMensaje texto={error} tono="error" />
      </div>
    );
  }

  if (!perfil) {
    return (
      <div className="flex flex-col gap-4">
        <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Mi perfil</h1>
        <RegionMensaje texto="Cargando tu perfil…" tono="muted" />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Mi perfil</h1>
      <dl className="grid grid-cols-1 gap-2 text-sm text-text">
        <div className="flex gap-2"><dt className="font-bold">Nombre:</dt><dd>{perfil.nombre}</dd></div>
        <div className="flex gap-2"><dt className="font-bold">Documento:</dt><dd>{perfil.documento}</dd></div>
        <div className="flex gap-2"><dt className="font-bold">Teléfono:</dt><dd>{perfil.telefono}</dd></div>
        <div className="flex gap-2"><dt className="font-bold">Institución:</dt><dd>{perfil.institucion}</dd></div>
        <div className="flex gap-2"><dt className="font-bold">Dependencia:</dt><dd>{perfil.dependencia}</dd></div>
        <div className="flex gap-2"><dt className="font-bold">Correo:</dt><dd>{perfil.correo} (solo lectura)</dd></div>
        <div className="flex gap-2">
          <dt className="font-bold">Actualización inicial:</dt>
          <dd>{perfil.actualizacion_inicial_pendiente ? "pendiente" : "completada"}</dd>
        </div>
      </dl>
      <section aria-label="Perfiles">
        <h2 className="text-base font-bold text-text">Perfiles académicos/investigativos</h2>
        <ul className="mt-1 text-sm text-text">
          {perfil.perfiles.map((p) => (
            <li key={p.id_perfil}>{p.nombre}</li>
          ))}
        </ul>
      </section>
      <section aria-label="Vinculaciones">
        <h2 className="text-base font-bold text-text">Vinculaciones</h2>
        <ul className="mt-1 text-sm text-text">
          {perfil.vinculaciones.proyectos.map((v) => (
            <li key={`p-${v.id_proyecto}`}>Proyecto: {v.codigo} — {v.nombre} {!v.activa && "(inactiva)"}</li>
          ))}
          {perfil.vinculaciones.semilleros.map((v) => (
            <li key={`s-${v.id_semillero}`}>Semillero: {v.codigo} — {v.nombre} {!v.activa && "(inactiva)"}</li>
          ))}
          {perfil.vinculaciones.pasantias.map((v) => (
            <li key={`pa-${v.id_pasantia}`}>Pasantía: {v.universidad} {!v.activa && "(inactiva)"}</li>
          ))}
          {perfil.vinculaciones.trabajos_grado.map((v) => (
            <li key={`t-${v.id_trabajo_grado}`}>Trabajo de grado: {v.director_nombre} {!v.activa && "(inactivo)"}</li>
          ))}
        </ul>
      </section>
      <nav className="flex flex-col gap-2" aria-label="Acciones de perfil">
        <Link href="/usuarios/perfil/editar" className="text-sm font-bold text-primary-2">
          Editar datos
        </Link>
        <Link href="/usuarios/perfil/perfiles" className="text-sm font-bold text-primary-2">
          Actualizar perfiles
        </Link>
        <Link href="/usuarios/perfil/vinculaciones" className="text-sm font-bold text-primary-2">
          Gestionar vinculaciones
        </Link>
      </nav>
    </div>
  );
}
