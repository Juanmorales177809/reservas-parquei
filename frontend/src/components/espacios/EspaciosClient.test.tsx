import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiRequestError } from "@/src/lib/http";
import { EspaciosClient } from "@/src/components/espacios/EspaciosClient";

const listarMock = vi.fn();
const crearMock = vi.fn();

vi.mock("@/src/lib/espacios-api", () => ({
  listarEspacios: (...args: unknown[]) => listarMock(...args),
  crearEspacio: (...args: unknown[]) => crearMock(...args),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}));

// FE-15 (WF-ESP-01): crear con capacidad llama con el cuerpo correcto.
describe("EspaciosClient", () => {
  beforeEach(() => {
    listarMock.mockReset();
    crearMock.mockReset();
    listarMock.mockResolvedValue({ datos: [] });
  });

  it("crea un espacio con capacidad y muestra confirmación", async () => {
    const usuario = userEvent.setup();
    crearMock.mockResolvedValue({ id: 3 });

    render(<EspaciosClient puedeGestionar={true} />);
    await usuario.type(screen.getByLabelText("Unidad (id)"), "7");
    await usuario.type(screen.getByLabelText("Nombre"), "Metrología");
    await usuario.type(screen.getByLabelText("Capacidad"), "25");
    await usuario.click(screen.getByRole("button", { name: "Guardar espacio" }));
    await waitFor(() => {
      expect(crearMock).toHaveBeenCalledWith({
        id_unidad: 7,
        nombre: "Metrología",
        capacidad: 25,
      });
    });
    expect(await screen.findByText("Espacio creado.")).toBeInTheDocument();
  });

  it("duplicado muestra el mensaje junto al flujo sin detalles internos", async () => {
    const usuario = userEvent.setup();
    crearMock.mockRejectedValue(
      new ApiRequestError(409, { codigo: "NOMBRE_DUPLICADO", mensaje: "x", detalles: [] })
    );

    render(<EspaciosClient puedeGestionar={true} />);
    await usuario.type(screen.getByLabelText("Unidad (id)"), "7");
    await usuario.type(screen.getByLabelText("Nombre"), "Metrología");
    await usuario.type(screen.getByLabelText("Capacidad"), "25");
    await usuario.click(screen.getByRole("button", { name: "Guardar espacio" }));
    expect(await screen.findByText("Ese nombre ya existe en la unidad.")).toBeInTheDocument();
  });

  it("sin permiso de gestión no muestra el formulario", async () => {
    render(<EspaciosClient puedeGestionar={false} />);
    await waitFor(() => {
      expect(listarMock).toHaveBeenCalledTimes(1);
    });
    expect(screen.queryByRole("button", { name: "Guardar espacio" })).not.toBeInTheDocument();
  });
});
