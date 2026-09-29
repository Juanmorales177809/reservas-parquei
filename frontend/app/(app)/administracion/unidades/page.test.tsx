import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiRequestError } from "@/src/lib/http";
import PaginaUnidades from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}));

const listarUnidadesMock = vi.fn();
const listarCargosMock = vi.fn();
const crearUnidadMock = vi.fn();

vi.mock("@/src/lib/administracion-api", () => ({
  listarUnidades: () => listarUnidadesMock(),
  listarCargos: () => listarCargosMock(),
  crearUnidad: (...args: unknown[]) => crearUnidadMock(...args),
  editarUnidad: vi.fn(),
  cambiarEstadoUnidad: vi.fn(),
  crearCargo: vi.fn(),
}));

// FE-11 (WF-ADM-01): el duplicado aparece junto al campo.
describe("administracion/unidades/page.tsx", () => {
  beforeEach(() => {
    listarUnidadesMock.mockReset();
    listarCargosMock.mockReset();
    crearUnidadMock.mockReset();
    listarUnidadesMock.mockResolvedValue({ datos: [] });
    listarCargosMock.mockResolvedValue({ datos: [] });
  });

  it("nombre duplicado muestra el mensaje sin identificar el registro", async () => {
    const usuario = userEvent.setup();
    crearUnidadMock.mockRejectedValue(
      new ApiRequestError(409, { codigo: "CONFLICTO", mensaje: "x", detalles: [] })
    );

    render(<PaginaUnidades />);
    await usuario.type(screen.getByLabelText("Nombre"), "Metrología");
    await usuario.click(screen.getByRole("button", { name: "Guardar unidad" }));
    await waitFor(() => {
      expect(crearUnidadMock).toHaveBeenCalledTimes(1);
    });
    expect(await screen.findByText("Ese nombre ya existe.")).toBeInTheDocument();
  });
});
