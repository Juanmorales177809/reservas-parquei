import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiRequestError } from "@/src/lib/http";
import PaginaVinculacionesAjenas from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}));

const vinculacionesMock = vi.fn();
const crearMock = vi.fn();

vi.mock("@/src/lib/investigacion-api", () => ({
  vinculacionesDe: (...args: unknown[]) => vinculacionesMock(...args),
  crearVinculacionAjena: (...args: unknown[]) => crearMock(...args),
  desactivarVinculacionAjena: vi.fn(),
}));

const VACIAS = { proyectos: [], semilleros: [], pasantias: [], trabajos_grado: [] };

// FE-17 (WF-INV-04): duplicada avisa; reactivación conserva la fila.
describe("investigacion/vinculaciones/page.tsx", () => {
  beforeEach(() => {
    vinculacionesMock.mockReset();
    crearMock.mockReset();
    vinculacionesMock.mockResolvedValue(VACIAS);
  });

  it("duplicada activa muestra el mensaje sin crear otra", async () => {    const usuario = userEvent.setup();
    crearMock.mockRejectedValue(
      new ApiRequestError(409, { codigo: "CONFLICTO", mensaje: "x", detalles: [] })
    );

    render(<PaginaVinculacionesAjenas />);
    await usuario.type(screen.getByLabelText("Usuario (id)"), "1042");
    await usuario.click(screen.getByRole("button", { name: "Consultar" }));
    await waitFor(() => {
      expect(vinculacionesMock).toHaveBeenCalledWith(1042);
    });
    await usuario.type(screen.getByLabelText("Entidad (id)"), "12");
    await usuario.click(screen.getByRole("button", { name: "Crear vinculación" }));
    expect(
      await screen.findByText("Ya existe una vinculación activa con esa entidad.")
    ).toBeInTheDocument();
  });

  it("reactivar una inactiva conserva la misma fila", async () => {
    const usuario = userEvent.setup();
    crearMock.mockResolvedValue({});
    vinculacionesMock.mockResolvedValue({
      proyectos: [{ id_proyecto: 12, codigo: "PRY-001", nombre: "Ensayos", activa: true }],
      semilleros: [],
      pasantias: [],
      trabajos_grado: [],
    });

    render(<PaginaVinculacionesAjenas />);
    await usuario.type(screen.getByLabelText("Usuario (id)"), "1042");
    await usuario.click(screen.getByRole("button", { name: "Consultar" }));
    await usuario.type(screen.getByLabelText("Entidad (id)"), "12");
    await usuario.click(screen.getByRole("button", { name: "Crear vinculación" }));
    await waitFor(() => {
      expect(crearMock).toHaveBeenCalledWith(1042, "proyectos", 12);
    });
    const filas = await screen.findAllByText(/PRY-001/);
    expect(filas).toHaveLength(1);
  });
});
