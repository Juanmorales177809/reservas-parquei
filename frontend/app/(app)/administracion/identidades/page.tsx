"use client";

import { RegistrarUsuarioForm } from "@/src/components/administracion/RegistrarUsuarioForm";

// WF-ADM-03 — specs/modules/administration/wireframes.md
// Decisión 2026-09-30: el personal y sus cargos llegan de la base institucional; aquí solo se registran usuarios.
export default function PaginaIdentidades() {
  return (
    <div className="flex max-w-[640px] flex-col gap-4">
      <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Identidades</h1>
      <p className="max-w-[64ch] text-[15px] text-muted">
        Registra a un usuario (estudiante, docente o externo) para poder invitar su cuenta. El personal y sus cargos
        llegan de la base institucional: no se registran aquí.
      </p>
      <RegistrarUsuarioForm />
    </div>
  );
}
