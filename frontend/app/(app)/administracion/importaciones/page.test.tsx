import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import PaginaImportaciones from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}));

const validarMock = vi.fn();
const confirmarMock = vi.fn();
const listarUnidadesMock = vi.fn();

vi.mock("@/src/lib/administracion-api", () => ({
  validarImportacion: (...args: unknown[]) => validarMock(...args),
  confirmarImportacion: (...args: unknown[]) => confirmarMock(...args),
  listarUnidades: () => listarUnidadesMock(),
}));

// FE-11 (WF-ADM-04, RN-IMP-06): filas en error → confirmar no disponible.
describe("administracion/importaciones/page.tsx", () => {
  beforeEach(() => {
    validarMock.mockReset();
    confirmarMock.mockReset();
    listarUnidadesMock.mockResolvedValue({ datos: [] });
  });

  it("carga no confirmable muestra errores y no permite confirmar", async () => {
    const usuario = userEvent.setup();
    validarMock.mockResolvedValue({
      id: 88,
      catalogo: "EQUIPOS",
      confirmable: false,
      totales: { a_crear: 1, a_actualizar: 0, desactivados: 0, con_error: 1 },
      resultados: [
        { numero_fila: 2, codigo: "EQ-1", resultado: "CREADO", detalle: null },
        { numero_fila: 3, codigo: null, resultado: "ERROR", detalle: "La fila no trae placa" },
      ],
    });

    render(<PaginaImportaciones />);
    const archivo = new File(["x"], "carga.xlsx", {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });
    await usuario.upload(screen.getByLabelText("Archivo Excel"), archivo);
    await usuario.click(screen.getByRole("button", { name: "Validar" }));
    await waitFor(() => {
      expect(validarMock).toHaveBeenCalledTimes(1);
    });
    expect(await screen.findByText(/no se puede confirmar/)).toBeInTheDocument();
    expect(await screen.findByText(/Fila 3/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Confirmar importación" })).toBeDisabled();
    expect(confirmarMock).not.toHaveBeenCalled();
  });
});
