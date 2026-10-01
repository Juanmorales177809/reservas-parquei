"use client";

import { NuevaReservaForm } from "@/src/components/reservas/NuevaReservaForm";

// WF-RES-01 — specs/modules/reservations/wireframes.md. También se abre como modal desde el listado de reservas;
// esta dirección sigue existiendo para enlaces directos.
export default function PaginaNuevaReserva() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-1">
        <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Nueva reserva</h1>
        <p className="max-w-[60ch] text-[15px] text-muted">
          Cuéntanos qué necesitas y cuándo. El formulario se ajusta a lo que elijas.
        </p>
      </div>
      <NuevaReservaForm />
    </div>
  );
}
