import type { ReactNode } from "react";

type Tono = "neutro" | "marca" | "atencion" | "error" | "info";

const TONOS: Record<Tono, string> = {
  neutro: "bg-disabled-bg text-muted",
  marca: "bg-primary-tint text-primary-2",
  atencion: "bg-[color-mix(in_srgb,var(--color-warning-1)_18%,var(--color-surface))] text-warning-2",
  error: "bg-[color-mix(in_srgb,var(--color-error-1)_12%,var(--color-surface))] text-error-2",
  info: "bg-[color-mix(in_srgb,var(--color-success-1)_16%,var(--color-surface))] text-success-2",
};

/** Estado de una reserva: el color ayuda, pero el texto siempre lo dice. */
const TONO_DE_ESTADO: Record<string, Tono> = {
  SOLICITADA: "atencion",
  APROBADA: "marca",
  EN_EJECUCION: "info",
  FINALIZADA: "neutro",
  RECHAZADA: "error",
  CANCELADA: "neutro",
};

export function Insignia({ tono = "neutro", children }: { tono?: Tono; children: ReactNode }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${TONOS[tono]}`}>
      {children}
    </span>
  );
}

export function InsigniaEstado({ estado, texto }: { estado: string; texto: string }) {
  return <Insignia tono={TONO_DE_ESTADO[estado] ?? "neutro"}>{texto}</Insignia>;
}
