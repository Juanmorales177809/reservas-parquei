import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiRequestError } from "@/src/lib/http";
import { InicioClient } from "./InicioClient";

const resumenMock = vi.fn();
vi.mock("@/src/lib/reportes-api", () => ({
  consultarResumen: (...a: unknown[]) => resumenMock(...a),
}));
vi.mock("@/src/lib/administracion-api", () => ({
  listarUnidades: async () => ({
    datos: [
      { id_unidad: 7, nombre: "Laboratorio de Redes", tipo: "LABORATORIO", id_unidad_padre: null, estado: true },
    ],
  }),
}));
vi.mock("./GraficosInicio", () => ({
  SeriePorFecha: () => <div>serie-por-fecha</div>,
  BarrasHorizontales: ({ titulo }: { titulo: string }) => <div>barras:{titulo}</div>,
}));

const RESUMEN = {
  resumen: { desde: "2026-09-01", hasta: "2026-09-30", desde_previo: "2026-08-02", hasta_previo: "2026-08-31", filtros: {} },
  indicadores: {
    reservas: { actual: 96, previo: 80 },
    solicitadas: 12,
    horas_reservadas: { actual: 412.5, previo: 350.0 },
    porcentaje_ocupacion: { actual: 38.4, previo: null },
  },
  por_estado: { solicitada: 12, aprobada: 40, rechazada: 3, en_ejecucion: 1, finalizada: 35, cancelada: 5 },
  por_fecha: [{ fecha: "2026-09-01", reservas: 4 }],
  por_laboratorio: [
    { id_unidad: 7, nombre: "Laboratorio de Redes", reservas: 96, horas_reservadas: 412.5, porcentaje_ocupacion: 38.4 },
    { id_unidad: 8, nombre: "Bodega", reservas: 1, horas_reservadas: 3.0, porcentaje_ocupacion: null },
  ],
  recursos_mas_reservados: [{ recurso_id: 42, nombre: "Osciloscopio", reservas: 14 }],
  ocupacion_dia_hora: [{ dia: 1, hora: 9, cantidad: 6 }],
};

describe("InicioClient", () => {
  // Sin llaves el mockReset devolvería el mock y Vitest lo llamaría como
  // limpieza del beforeEach, con una promesa rechazada sin manejar.
  beforeEach(() => {
    resumenMock.mockReset();
  });

  it("el Usuario ve accesos y nunca llama al resumen", () => {
    render(<InicioClient rol="USUARIO" unidadesAutorizadas={[]} />);
    expect(screen.getByRole("link", { name: /Mis reservas/ })).toHaveAttribute("href", "/reservas");
    expect(screen.getByRole("link", { name: /Nueva reserva/ })).toHaveAttribute("href", "/reservas/nueva");
    expect(resumenMock).not.toHaveBeenCalled();
    expect(screen.queryByRole("button", { name: "Consultar" })).toBeNull();
  });

  it("quien gestiona consulta el periodo y ve indicadores, estados y mapa", async () => {
    const usuario = userEvent.setup();
    resumenMock.mockResolvedValue(RESUMEN);
    render(<InicioClient rol="TECNICO" unidadesAutorizadas={[7]} />);

    expect(resumenMock).not.toHaveBeenCalled();
    await usuario.click(screen.getByRole("button", { name: "Consultar" }));

    expect(resumenMock).toHaveBeenCalledWith(
      expect.objectContaining({ desde: expect.any(String), hasta: expect.any(String) })
    );
    await screen.findByText("serie-por-fecha");
    // Seis estados siempre presentes, en el orden del catálogo.
    const estados = screen.getByRole("region", { name: "Por estado" });
    expect(within(estados).getByText("12")).toBeInTheDocument();
    // Sin horario: horas sí, porcentaje nunca inventado.
    const laboratorios = screen.getByRole("region", { name: "Por laboratorio" });
    expect(within(laboratorios).getByText("Bodega")).toBeInTheDocument();
    expect(within(laboratorios).getByText("—")).toBeInTheDocument();
    // Mapa de calor por cantidad con su celda.
    expect(screen.getByTitle("Lunes 9:00 — 6 reservas")).toHaveTextContent("6");
    // Enlaces a los reportes de detalle.
    expect(screen.getByRole("link", { name: "Ocupación" })).toHaveAttribute("href", "/reportes/ocupacion");
  });

  it("sin permiso muestra la denegación en la misma pantalla", async () => {
    const usuario = userEvent.setup();
    resumenMock.mockRejectedValue(
      new ApiRequestError(403, { codigo: "NO_AUTORIZADO", mensaje: "x", detalles: [] })
    );
    render(<InicioClient rol="TECNICO" unidadesAutorizadas={[7]} />);
    await usuario.click(screen.getByRole("button", { name: "Consultar" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("No tienes acceso a los reportes.");
  });

  it("periodo inválido muestra el mensaje del servidor", async () => {
    const usuario = userEvent.setup();
    resumenMock.mockRejectedValue(
      new ApiRequestError(422, { codigo: "VALIDACION", mensaje: "desde no puede ser posterior a hasta.", detalles: [] })
    );
    render(<InicioClient rol="ADMINISTRADOR" unidadesAutorizadas="GLOBAL" />);
    await usuario.click(screen.getByRole("button", { name: "Consultar" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("desde no puede ser posterior a hasta.");
  });
});
