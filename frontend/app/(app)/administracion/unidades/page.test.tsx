import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import PaginaUnidades from "./page";

const router = { push: vi.fn(), replace: vi.fn() };
vi.mock("next/navigation", () => ({ useRouter: () => router }));

const listarUnidadesMock = vi.fn();
const listarCargosMock = vi.fn();
const estadoMock = vi.fn();

vi.mock("@/src/lib/administracion-api", () => ({
  listarUnidades: () => listarUnidadesMock(),
  listarCargos: () => listarCargosMock(),
  cambiarEstadoUnidad: (...args: unknown[]) => estadoMock(...args),
}));

// Decisión 2026-09-30: los laboratorios y los cargos vienen de otra base de datos; aquí no se crean ni se renombran.
describe("administracion/unidades/page.tsx", () => {
  beforeEach(() => {
    listarUnidadesMock.mockReset();
    listarCargosMock.mockReset();
    estadoMock.mockReset();
    listarUnidadesMock.mockResolvedValue({
      datos: [
        { id_unidad: 7, nombre: "Laboratorio de Redes", tipo: "LABORATORIO", id_unidad_padre: null, estado: true },
        { id_unidad: 8, nombre: "Facultad de Ingenierías", tipo: "FACULTAD", id_unidad_padre: null, estado: false },
      ],
    });
    listarCargosMock.mockResolvedValue({ datos: [{ id_cargo: 4, nombre_cargo: "Técnico de laboratorio", id_unidad: 7 }] });
  });

  it("lista laboratorios y cargos, y dice que vienen de la base institucional", async () => {
    render(<PaginaUnidades />);
    expect(await screen.findByRole("heading", { name: "Laboratorios y cargos" })).toBeInTheDocument();
    expect(screen.getByText(/llegan de la base de datos institucional/)).toBeInTheDocument();
    const laboratorios = within(screen.getByRole("region", { name: "Laboratorios" }));
    expect(await laboratorios.findByText("Laboratorio de Redes")).toBeInTheDocument();
    expect(laboratorios.getByText("Deshabilitado")).toBeInTheDocument();
    const cargos = within(screen.getByRole("region", { name: "Cargos" }));
    expect(await cargos.findByText("Técnico de laboratorio")).toBeInTheDocument();
    expect(cargos.getByText("Laboratorio de Redes")).toBeInTheDocument();
  });

  it("no ofrece crear ni renombrar laboratorios o cargos", async () => {
    render(<PaginaUnidades />);
    await within(screen.getByRole("region", { name: "Laboratorios" })).findByText("Laboratorio de Redes");
    expect(screen.queryByRole("button", { name: /Guardar/ })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Editar" })).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/Nombre/)).not.toBeInTheDocument();
  });

  it("solo un laboratorio se configura para reservar, y se puede deshabilitar o habilitar", async () => {
    const usuario = userEvent.setup();
    estadoMock.mockResolvedValue({});
    render(<PaginaUnidades />);
    await within(screen.getByRole("region", { name: "Laboratorios" })).findByText("Laboratorio de Redes");
    expect(screen.getAllByRole("link", { name: "Configurar" })).toHaveLength(1);
    await usuario.click(screen.getByRole("button", { name: "Deshabilitar" }));
    await waitFor(() => expect(estadoMock).toHaveBeenCalledWith(7, false));
  });
});
