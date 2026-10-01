"use client";

import { Bar, BarChart, CartesianGrid, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

// SCR-REP-04 (FE-47): los gráficos del inicio usan una sola medida y un solo
// color (--color-primary-1); `por_estado` es tabla y el mapa de calor es una
// rejilla de una sola tinta (vive en InicioClient, sin Recharts).

const TINTA = "var(--color-primary-1)";

function contenedor(alto: number, etiqueta: string, children: React.ReactNode) {
  return (
    <div role="img" aria-label={`${etiqueta}. Los mismos datos están en la tabla.`} style={{ width: "100%", height: alto }}>
      <ResponsiveContainer width="100%" height="100%">{children}</ResponsiveContainer>
    </div>
  );
}

export function SeriePorFecha({ puntos }: { puntos: { fecha: string; reservas: number }[] }) {
  const datos = puntos.map((p) => ({
    fecha: new Date(`${p.fecha}T00:00:00`).toLocaleDateString("es-CO", { day: "numeric", month: "short" }),
    reservas: p.reservas,
  }));
  return (
    <section aria-label="Reservas por día" className="flex flex-col gap-2 rounded-control border border-border bg-surface p-4">
      <h2 className="text-base font-bold text-text">Reservas por día</h2>
      {contenedor(
        220,
        "Reservas por día",
        <BarChart data={datos} margin={{ top: 4, right: 8, bottom: 4, left: -12 }}>
          <CartesianGrid vertical={false} stroke="var(--color-border)" />
          <XAxis dataKey="fecha" tick={{ fill: "var(--color-muted)", fontSize: 11 }} stroke="var(--color-border)" interval="preserveStartEnd" />
          <YAxis allowDecimals={false} tick={{ fill: "var(--color-muted)", fontSize: 12 }} stroke="var(--color-border)" />
          <Tooltip formatter={(v) => [`${v}`, "Reservas"]} cursor={{ fill: "var(--color-primary-tint)" }} />
          <Bar dataKey="reservas" fill={TINTA} radius={[4, 4, 0, 0]} barSize={16} isAnimationActive={false} />
        </BarChart>
      )}
    </section>
  );
}

export function BarrasHorizontales({
  titulo,
  filas,
  unidad,
}: {
  titulo: string;
  filas: { nombre: string; valor: number }[];
  unidad: string;
}) {
  const datos = [...filas].sort((a, b) => b.valor - a.valor);
  return (
    <section aria-label={titulo} className="flex flex-col gap-2 rounded-control border border-border bg-surface p-4">
      <h2 className="text-base font-bold text-text">{titulo}</h2>
      {contenedor(
        Math.max(120, datos.length * 44 + 40),
        titulo,
        <BarChart data={datos} layout="vertical" margin={{ top: 4, right: 56, bottom: 4, left: 8 }}>
          <CartesianGrid horizontal={false} stroke="var(--color-border)" />
          <XAxis type="number" tick={{ fill: "var(--color-muted)", fontSize: 12 }} stroke="var(--color-border)" />
          <YAxis type="category" dataKey="nombre" width={150} tick={{ fill: "var(--color-text)", fontSize: 12 }} stroke="var(--color-border)" />
          <Tooltip formatter={(v) => [`${v}${unidad}`, titulo]} cursor={{ fill: "var(--color-primary-tint)" }} />
          <Bar dataKey="valor" fill={TINTA} radius={[0, 4, 4, 0]} barSize={18} isAnimationActive={false}>
            <LabelList dataKey="valor" position="right" formatter={(v) => `${v}${unidad}`} fill="var(--color-text)" fontSize={12} />
          </Bar>
        </BarChart>
      )}
    </section>
  );
}
