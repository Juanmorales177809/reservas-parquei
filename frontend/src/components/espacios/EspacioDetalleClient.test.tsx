import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiRequestError } from "@/src/lib/http";
import { EspacioDetalleClient } from "@/src/components/espacios/EspacioDetalleClient";

const detalleMock = vi.fn();
const impactoMock = vi.fn();
const cambiarMock = vi.fn();
const crearCampoMock = vi.fn();

vi.mock("@/src/lib/espacios-api", () => ({
  detalleEspacio: (...args: unknown[]) => detalleMock(...args),
  actualizarRecurso: vi.fn(),
  cambiarEstadoEspacio: (...args: unknown[]) => cambiarMock(...args),
  impactoDeshabilitacionEspacio: (...args: unknown[]) => impactoMock(...args),
  asociarRecursos: vi.fn(),
  retirarRecurso: vi.fn(),
  crearCampo: (...args: unknown[]) => crearCampoMock(...args),
  reordenarCampos: vi.fn(),
  cambiarEstadoCampo: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  useParams: () => ({ id: "3" }),
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}));

const DETALLE = {
  id: 3,
  id_unidad: 7,
  nombre: "Metrología",
  ubicacion: null,
  capacidad: 25,
  descripcion: null,
  habilitado: true,
  horario_unidad: { hora_apertura: "07:00", hora_cierre: "19:00" },
  recursos: [],
  campos: [],
};

// FE-15 (WF-ESP-02/03): impacto con conteo y lista-sin-opciones.
describe("EspacioDetalleClient", () => {
  beforeEach(() => {
    detalleMock.mockReset();
    impactoMock.mockReset();
    cambiarMock.mockReset();
    crearCampoMock.mockReset();
    detalleMock.mockResolvedValue(DETALLE);
  });

  it("deshabilitar muestra el impacto y exige confirmar", async () => {
    const usuario = userEvent.setup();
    impactoMock.mockResolvedValue({ reservas_a_cancelar: 4 });
    cambiarMock.mockResolvedValue({ id: 3, habilitado: false, reservas_canceladas: 4 });

    render(<EspacioDetalleClient puedeGestionar={true} />);
    expect(await screen.findByText("Metrología")).toBeInTheDocument();
    await usuario.click(screen.getByRole("button", { name: "Deshabilitar" }));
    await waitFor(() => {
      expect(impactoMock).toHaveBeenCalledWith(3);
    });
    expect(await screen.findByText(/Reservas futuras a cancelar: 4/)).toBeInTheDocument();
    expect(cambiarMock).not.toHaveBeenCalled();
    await usuario.click(screen.getByRole("button", { name: "Confirmar deshabilitación" }));
    await waitFor(() => {
      expect(cambiarMock).toHaveBeenCalledWith(3, false, true);
    });
  });

  it("lista sin opciones muestra CAMPO_SIN_OPCIONES", async () => {
    const usuario = userEvent.setup();
    crearCampoMock.mockRejectedValue(
      new ApiRequestError(409, { codigo: "CAMPO_SIN_OPCIONES", mensaje: "x", detalles: [] })
    );

    render(<EspacioDetalleClient puedeGestionar={true} />);
    expect(await screen.findByText("Metrología")).toBeInTheDocument();
    await usuario.selectOptions(screen.getByLabelText("Tipo"), "SELECCION");
    await usuario.type(screen.getByLabelText("Nombre"), "Probeta");
    await usuario.click(screen.getByRole("button", { name: "Agregar campo" }));
    expect(
      await screen.findByText("Una lista necesita al menos una opción habilitada.")
    ).toBeInTheDocument();
  });
});
