import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiRequestError } from "@/src/lib/http";
import { elegir } from "@/src/test-utils";
import { ReporteClient } from "./ReporteClient";

const consultarMock = vi.fn();
const exportarMock = vi.fn();
vi.mock("@/src/lib/reportes-api", () => ({
  consultarReporte: (...a: unknown[]) => consultarMock(...a),
  exportarReporte: (...a: unknown[]) => exportarMock(...a),
}));
vi.mock("@/src/lib/administracion-api", () => ({
  listarUnidades: async () => ({
    datos: [
      { id_unidad: 7, nombre: "Laboratorio de Redes", tipo: "LABORATORIO", id_unidad_padre: null, estado: true },
      { id_unidad: 8, nombre: "Laboratorio de Metrología", tipo: "LABORATORIO", id_unidad_padre: null, estado: true },
    ],
  }),
}));
vi.mock("@/src/lib/espacios-api", () => ({ listarEspacios: vi.fn().mockResolvedValue({ datos: [] }) }));
vi.mock("@/src/lib/recursos-api", () => ({ listarLaboratorios: vi.fn(), listarRecursos: vi.fn().mockResolvedValue({ datos: [] }) }));
vi.mock("@/src/lib/investigacion-api", () => ({
  listarProyectos: vi.fn().mockRejectedValue(new ApiRequestError(403, { codigo: "NO_AUTORIZADO", mensaje: "x", detalles: [] })),
  listarSemilleros: vi.fn().mockResolvedValue({ datos: [] }),
}));
vi.mock("@/src/lib/reservas-api", () => ({
  opcionesContexto: vi.fn().mockResolvedValue({
    proyectos: [{ id: 128, codigo: "P-1", nombre: "Proyecto Alfa" }],
    semilleros: [],
  }),
}));
// El gráfico se dibuja con Recharts, que en jsdom no tiene tamaño; aquí solo importa que se ofrezca.
vi.mock("./GraficoOcupacion", () => ({
  GraficoOcupacion: ({ dimension }: { dimension: string }) => <div>grafico:{dimension}</div>,
}));

const RESUMEN = { desde: "2026-09-01", hasta: "2026-09-30", filtros: {} };
const PAGINACION = { pagina: 1, tamano: 20, total: 1, paginas: 1 };

describe("ReporteClient", () => {
  beforeEach(() => {
    consultarMock.mockReset();
    exportarMock.mockReset();
  });

  it("propone el mes en curso y no consulta hasta que se pide", async () => {
    render(<ReporteClient tipo="ocupacion" unidadesAutorizadas="GLOBAL" />);
    expect((screen.getByLabelText("Desde") as HTMLInputElement).value).toMatch(/^\d{4}-\d{2}-01$/);
    expect(consultarMock).not.toHaveBeenCalled();
    expect(screen.queryByRole("button", { name: "CSV" })).not.toBeInTheDocument();
  });

  it("consulta la ocupación por espacio con la unidad elegida por nombre y muestra tabla y gráfico", async () => {
    const usuario = userEvent.setup();
    consultarMock.mockResolvedValue({
      resumen: { ...RESUMEN, dimension: "espacio", filtros: { id_unidad: 7 } },
      datos: [
        { nombre: "Sala de ensayos", horas_reservadas: 84.5, horas_disponibles: 220, porcentaje_ocupacion: 38.4 },
        { nombre: "Bodega", horas_reservadas: 3, horas_disponibles: null, porcentaje_ocupacion: null },
      ],
      paginacion: { ...PAGINACION, total: 2 },
    });
    render(<ReporteClient tipo="ocupacion" unidadesAutorizadas="GLOBAL" />);
    await elegir(usuario, "Dimensión", "Espacio");
    await elegir(usuario, "Unidad", "Laboratorio de Redes");
    await usuario.click(screen.getByRole("button", { name: "Consultar" }));

    const [tipo, filtros, pagina] = consultarMock.mock.calls[0];
    expect(tipo).toBe("ocupacion");
    expect(filtros).toMatchObject({ dimension: "espacio", id_unidad: "7" });
    expect(pagina).toBe(1);

    const tabla = await screen.findByRole("table");
    expect(within(tabla).getByText("38.4 %")).toBeInTheDocument();
    // Sin porcentaje calculable: solo horas, nunca un porcentaje inventado (RN-OCU-06).
    const filaBodega = within(tabla).getByText("Bodega").closest("tr")!;
    expect(within(filaBodega).getAllByText("—")).toHaveLength(2);
    expect(screen.getByText("grafico:espacio")).toBeInTheDocument();
    expect(screen.getByText("Solo cuentan reservas aprobadas, en ejecución y finalizadas.")).toBeInTheDocument();
  });

  it("solicitudes es solo tabla, con una columna por estado", async () => {
    const usuario = userEvent.setup();
    consultarMock.mockResolvedValue({
      resumen: { ...RESUMEN, dimension: "laboratorio" },
      datos: [{ nombre: "Metrología", solicitada: 12, aprobada: 40, rechazada: 3, en_ejecucion: 1, finalizada: 35, cancelada: 5 }],
      paginacion: PAGINACION,
    });
    render(<ReporteClient tipo="solicitudes" unidadesAutorizadas="GLOBAL" />);
    expect(screen.queryByLabelText("Dimensión")).not.toBeInTheDocument();
    await usuario.click(screen.getByRole("button", { name: "Consultar" }));
    const tabla = await screen.findByRole("table");
    for (const estado of ["Solicitada", "Aprobada", "Rechazada", "En ejecución", "Finalizada", "Cancelada"]) {
      expect(within(tabla).getByRole("columnheader", { name: estado })).toBeInTheDocument();
    }
    expect(screen.queryByText(/grafico:/)).not.toBeInTheDocument();
  });

  it("un resultado vacío no es un error y no ofrece exportar", async () => {
    const usuario = userEvent.setup();
    consultarMock.mockResolvedValue({ resumen: RESUMEN, datos: [], paginacion: { ...PAGINACION, total: 0, paginas: 0 } });
    render(<ReporteClient tipo="lista-espera" unidadesAutorizadas="GLOBAL" />);
    await usuario.click(screen.getByRole("button", { name: "Consultar" }));
    expect(await screen.findByText("Sin información para los criterios seleccionados.")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "CSV" })).not.toBeInTheDocument();
  });

  it("muestra el mensaje del servidor si el periodo es inválido", async () => {
    const usuario = userEvent.setup();
    consultarMock.mockRejectedValue(new ApiRequestError(422, { codigo: "VALIDACION", mensaje: "desde no puede ser posterior a hasta.", detalles: [] }));
    render(<ReporteClient tipo="lista-espera" unidadesAutorizadas="GLOBAL" />);
    await usuario.click(screen.getByRole("button", { name: "Consultar" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("desde no puede ser posterior a hasta.");
  });

  it("sin permiso muestra la denegación en la misma pantalla", async () => {
    const usuario = userEvent.setup();
    consultarMock.mockRejectedValue(new ApiRequestError(403, { codigo: "NO_AUTORIZADO", mensaje: "no", detalles: [] }));
    render(<ReporteClient tipo="ocupacion" unidadesAutorizadas="GLOBAL" />);
    await usuario.click(screen.getByRole("button", { name: "Consultar" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("No tienes acceso a los reportes.");
  });

  it("exporta con los filtros de la última consulta aunque el formulario haya cambiado", async () => {
    const usuario = userEvent.setup();
    consultarMock.mockResolvedValue({
      resumen: { ...RESUMEN, dimension: "laboratorio" },
      datos: [{ nombre: "Redes", horas_reservadas: 1, horas_disponibles: 10, porcentaje_ocupacion: 10 }],
      paginacion: PAGINACION,
    });
    exportarMock.mockResolvedValue(undefined);
    render(<ReporteClient tipo="ocupacion" unidadesAutorizadas="GLOBAL" />);
    await usuario.click(screen.getByRole("button", { name: "Consultar" }));
    await screen.findByRole("table");
    await elegir(usuario, "Unidad", "Laboratorio de Metrología"); // cambia el filtro sin volver a consultar
    await usuario.click(screen.getByRole("button", { name: "Excel" }));
    expect(exportarMock).toHaveBeenCalledWith("ocupacion", expect.not.objectContaining({ id_unidad: "8" }), "excel");
  });

  it("ofrece solo las unidades del alcance de la cuenta", async () => {
    render(<ReporteClient tipo="solicitudes" unidadesAutorizadas={[8]} />);
    const unidad = await screen.findByLabelText("Unidad");
    await within(unidad).findByRole("option", { name: "Laboratorio de Metrología" });
    expect(within(unidad).queryByRole("option", { name: "Laboratorio de Redes" })).not.toBeInTheDocument();
  });

  it("un técnico sin acceso a la lista de proyectos los elige de sus opciones, por nombre", async () => {
    const usuario = userEvent.setup();
    render(<ReporteClient tipo="ocupacion" unidadesAutorizadas={[7]} />);
    await elegir(usuario, "Dimensión", "Proyecto");
    await elegir(usuario, "Proyecto", "Proyecto Alfa (P-1)");
    expect((screen.getByLabelText("Proyecto") as HTMLSelectElement).value).toBe("128");
  });
});
