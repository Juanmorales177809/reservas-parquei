import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiRequestError } from "@/src/lib/http";
import PaginaVinculacionesAjenas from "./page";
import { elegir } from "@/src/test-utils";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}));

vi.mock("@/src/lib/administracion-api", () => ({
  listarUsuarios: () =>
    Promise.resolve({
      datos: [{ id_usuario: 1042, id_cuenta: 9, nombre: "Ana Pérez", correo: "ana@itm.edu.co", estado: true }],
    }),
}));

const vinculacionesMock = vi.fn();
const crearMock = vi.fn();

vi.mock("@/src/lib/investigacion-api", () => ({
  vinculacionesDe: (...args: unknown[]) => vinculacionesMock(...args),
  crearVinculacionAjena: (...args: unknown[]) => crearMock(...args),
  desactivarVinculacionAjena: vi.fn(),
  listarProyectos: () =>
    Promise.resolve({ datos: [{ id_proyecto: 12, codigo: "PRY-001", nombre: "Ensayos", estado: true }] }),
  listarSemilleros: () => Promise.resolve({ datos: [] }),
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
    await elegir(usuario, "Usuario", "Ana Pérez · ana@itm.edu.co");
    await usuario.click(screen.getByRole("button", { name: "Consultar" }));
    await waitFor(() => {
      expect(vinculacionesMock).toHaveBeenCalledWith(1042);
    });
    await elegir(usuario, "Proyecto", "Ensayos (PRY-001)");
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
    await elegir(usuario, "Usuario", "Ana Pérez · ana@itm.edu.co");
    await usuario.click(screen.getByRole("button", { name: "Consultar" }));
    await elegir(usuario, "Proyecto", "Ensayos (PRY-001)");
    await usuario.click(screen.getByRole("button", { name: "Crear vinculación" }));
    await waitFor(() => {
      expect(crearMock).toHaveBeenCalledWith(1042, "proyectos", 12);
    });
    const filas = await screen.findAllByText(/PRY-001/, { selector: "span" });
    expect(filas).toHaveLength(1);
  });
});
