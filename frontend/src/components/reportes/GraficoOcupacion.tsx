"use client";

import { Bar, BarChart, CartesianGrid, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { Dimension, FilaReporte } from "@/src/lib/reportes-api";

// specs/modules/reports/screens.md «Reglas del gráfico de ocupación»: una medida, un color (--color-primary-1),
// una barra por fila con valor, y las filas sin porcentaje se enumeran aparte en lugar de dibujarse en cero.

export function medidaDelGrafico(dimension: Dimension): "porcentaje_ocupacion" | "horas_reservadas" {
  return dimension === "proyecto" || dimension === "semillero" ? "horas_reservadas" : "porcentaje_ocupacion";
}

export function GraficoOcupacion({
  dimension,
  filas,
  hayMasPaginas,
}: {
  dimension: Dimension;
  filas: FilaReporte[];
  hayMasPaginas: boolean;
}) {
  const medida = medidaDelGrafico(dimension);
  const esPorcentaje = medida === "porcentaje_ocupacion";
  const titulo = esPorcentaje ? `Ocupación por ${dimension}` : `Horas reservadas por ${dimension}`;
  const datos = filas
    .filter((f) => f[medida] !== null && f[medida] !== undefined)
    .map((f) => ({ nombre: f.nombre, valor: f[medida] as number }));
  const sinValor = filas.filter((f) => f[medida] === null || f[medida] === undefined);
  const sufijo = esPorcentaje ? " %" : " h";

  return (
    <section aria-label={titulo} className="flex flex-col gap-2 rounded-control border border-border bg-surface p-4">
      <h2 className="text-base font-bold text-text">{titulo}</h2>
      {hayMasPaginas && <p className="text-xs text-muted">El gráfico muestra las filas de la página a la vista.</p>}
      {datos.length > 0 && (
        <div
          role="img"
          aria-label={`${titulo}. Los mismos datos están en la tabla.`}
          style={{ width: "100%", height: Math.max(120, datos.length * 44 + 40) }}
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={datos} layout="vertical" margin={{ top: 4, right: 56, bottom: 4, left: 8 }}>
              <CartesianGrid horizontal={false} stroke="var(--color-border)" />
              <XAxis
                type="number"
                domain={[0, esPorcentaje ? 100 : "auto"]}
                tick={{ fill: "var(--color-muted)", fontSize: 12 }}
                stroke="var(--color-border)"
              />
              <YAxis
                type="category"
                dataKey="nombre"
                width={150}
                tick={{ fill: "var(--color-text)", fontSize: 12 }}
                stroke="var(--color-border)"
              />
              <Tooltip
                formatter={(v) => [`${v}${sufijo}`, esPorcentaje ? "Ocupación" : "Horas reservadas"]}
                cursor={{ fill: "var(--color-primary-tint)" }}
              />
              <Bar dataKey="valor" fill="var(--color-primary-1)" radius={[0, 4, 4, 0]} barSize={18} isAnimationActive={false}>
                <LabelList
                  dataKey="valor"
                  position="right"
                  formatter={(v) => `${v}${sufijo}`}
                  fill="var(--color-text)"
                  fontSize={12}
                />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
      {sinValor.length > 0 && (
        <p className="text-sm text-muted">
          Sin porcentaje: {sinValor.map((f) => f.nombre).join(", ")} (sin horario de atención definido).
        </p>
      )}
    </section>
  );
}
