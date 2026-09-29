import { render, screen } from "@testing-library/react";
import { beforeAll, describe, expect, it } from "vitest";
import { GraficoOcupacion, medidaDelGrafico } from "./GraficoOcupacion";

beforeAll(() => {
  // Recharts mide su contenedor; jsdom no tiene ResizeObserver.
  globalThis.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  } as unknown as typeof ResizeObserver;
});

describe("GraficoOcupacion", () => {
  it("una sola medida por dimensión: porcentaje salvo proyecto y semillero", () => {
    expect(medidaDelGrafico("espacio")).toBe("porcentaje_ocupacion");
    expect(medidaDelGrafico("laboratorio")).toBe("porcentaje_ocupacion");
    expect(medidaDelGrafico("recurso")).toBe("porcentaje_ocupacion");
    expect(medidaDelGrafico("proyecto")).toBe("horas_reservadas");
    expect(medidaDelGrafico("semillero")).toBe("horas_reservadas");
  });

  it("se titula con la medida y la agrupación, y enumera las filas sin porcentaje en vez de dibujarlas en cero", () => {
    render(
      <GraficoOcupacion
        dimension="espacio"
        hayMasPaginas
        filas={[
          { nombre: "Sala", horas_reservadas: 10, porcentaje_ocupacion: 40 },
          { nombre: "Bodega", horas_reservadas: 3, porcentaje_ocupacion: null },
        ]}
      />
    );
    expect(screen.getByRole("heading", { name: "Ocupación por espacio" })).toBeInTheDocument();
    expect(screen.getByText(/Sin porcentaje: Bodega/)).toBeInTheDocument();
    expect(screen.getByText("El gráfico muestra las filas de la página a la vista.")).toBeInTheDocument();
  });

  it("proyectos se rotulan en horas", () => {
    render(<GraficoOcupacion dimension="proyecto" hayMasPaginas={false} filas={[{ nombre: "Alfa", horas_reservadas: 12 }]} />);
    expect(screen.getByRole("heading", { name: "Horas reservadas por proyecto" })).toBeInTheDocument();
  });
});
