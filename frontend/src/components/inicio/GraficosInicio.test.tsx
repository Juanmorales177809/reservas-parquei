import { render, screen } from "@testing-library/react";
import { beforeAll, describe, expect, it } from "vitest";
import { BarrasHorizontales, SeriePorFecha } from "./GraficosInicio";

beforeAll(() => {
  // Recharts mide su contenedor; jsdom no tiene ResizeObserver.
  globalThis.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  } as unknown as typeof ResizeObserver;
});

describe("GraficosInicio", () => {
  it("la serie por fecha se titula y usa una sola tinta de datos", () => {
    const { container } = render(
      <SeriePorFecha puntos={[{ fecha: "2026-09-01", reservas: 4 }]} />
    );
    expect(screen.getByRole("heading", { name: "Reservas por día" })).toBeInTheDocument();
    const barras = Array.from(container.querySelectorAll(".recharts-bar-rectangle path"));
    for (const b of barras) {
      expect(b.getAttribute("fill")).toBe("var(--color-primary-1)");
    }
  });

  it("las barras horizontales ordenan de mayor a menor", () => {
    render(
      <BarrasHorizontales
        titulo="Reservas por laboratorio"
        unidad=""
        filas={[
          { nombre: "B", valor: 2 },
          { nombre: "A", valor: 9 },
        ]}
      />
    );
    expect(screen.getByRole("heading", { name: "Reservas por laboratorio" })).toBeInTheDocument();
  });
});
