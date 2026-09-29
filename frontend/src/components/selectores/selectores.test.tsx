import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiRequestError } from "@/src/lib/http";
import { elegir } from "@/src/test-utils";
import { reiniciarCatalogoDeUnidades, SelectorUnidad } from "./selectores";

const unidadesMock = vi.fn();
const laboratoriosMock = vi.fn();
vi.mock("@/src/lib/administracion-api", () => ({ listarUnidades: () => unidadesMock() }));
vi.mock("@/src/lib/recursos-api", () => ({ listarLaboratorios: () => laboratoriosMock(), listarRecursos: vi.fn() }));

const SIN_PERMISO = new ApiRequestError(403, { codigo: "NO_AUTORIZADO", mensaje: "x", detalles: [] });

// Una cuenta sin permisos de administración también tiene que poder elegir la unidad por su nombre.
describe("SelectorUnidad", () => {
  beforeEach(() => {
    unidadesMock.mockReset();
    laboratoriosMock.mockReset();
    reiniciarCatalogoDeUnidades();
    laboratoriosMock.mockResolvedValue({ datos: [{ id_unidad: 7, nombre: "Laboratorio de Redes", habilitado_reservas: true }] });
  });

  it("con permiso de administración lista todas las unidades activas", async () => {
    const usuario = userEvent.setup();
    unidadesMock.mockResolvedValue({ datos: [
      { id_unidad: 1, nombre: "Facultad", tipo: "FACULTAD", id_unidad_padre: null, estado: true },
      { id_unidad: 2, nombre: "Vieja", tipo: "LABORATORIO", id_unidad_padre: null, estado: false },
    ] });
    render(<SelectorUnidad id="u" label="Unidad" value="" onChange={() => {}} />);
    await elegir(usuario, "Unidad", "Facultad");
    expect(screen.queryByRole("option", { name: "Vieja" })).not.toBeInTheDocument();
    expect(laboratoriosMock).not.toHaveBeenCalled();
  });

  it("sin ese permiso (403) usa el catálogo de laboratorios y no vuelve a intentar la lista administrativa", async () => {
    const usuario = userEvent.setup();
    unidadesMock.mockRejectedValue(SIN_PERMISO);
    const { unmount } = render(<SelectorUnidad id="u" label="Unidad" value="" onChange={() => {}} />);
    await elegir(usuario, "Unidad", "Laboratorio de Redes");
    unmount();
    render(<SelectorUnidad id="u2" label="Unidad" value="" onChange={() => {}} />);
    await elegir(usuario, "Unidad", "Laboratorio de Redes");
    expect(unidadesMock).toHaveBeenCalledTimes(1);
  });

  it("otro error no se disfraza: el selector avisa que no pudo cargar", async () => {
    unidadesMock.mockRejectedValue(new ApiRequestError(500, { codigo: "ERROR_INTERNO", mensaje: "x", detalles: [] }));
    render(<SelectorUnidad id="u" label="Unidad" value="" onChange={() => {}} />);
    expect(await screen.findByText("No se pudo cargar la lista.")).toBeInTheDocument();
    expect(laboratoriosMock).not.toHaveBeenCalled();
  });
});
