import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiRequestError } from "@/src/lib/http";
import { RecursosClient } from "@/src/components/recursos/RecursosClient";
import { elegir } from "@/src/test-utils";

// Router estable: un objeto nuevo por render relanzaría el efecto sin fin.
const router = { push: vi.fn(), replace: vi.fn() };
vi.mock("next/navigation", () => ({
  useRouter: () => router,
}));


vi.mock("@/src/lib/administracion-api", () => ({
  listarUnidades: () => Promise.resolve({ datos: [{ id_unidad: 7, nombre: "Laboratorio de Redes", tipo: "LABORATORIO", id_unidad_padre: null, estado: true }] }),
}));

const listarMock = vi.fn();
const crearMock = vi.fn();

vi.mock("@/src/lib/recursos-api", () => ({
  listarRecursos: (...args: unknown[]) => listarMock(...args),
  crearRecurso: (...args: unknown[]) => crearMock(...args),
}));

// FE-13 (WF-REC-01): crear mobiliario llama con el cuerpo correcto.
describe("RecursosClient", () => {
  beforeEach(() => {
    listarMock.mockReset();
    crearMock.mockReset();
    listarMock.mockResolvedValue({ datos: [] });
  });

  it("crea mobiliario con unidad, tipo y nombre", async () => {
    const usuario = userEvent.setup();
    crearMock.mockResolvedValue({ id: 41, tipo: "MOBILIARIO", id_unidad: 7, habilitado: true });

    render(<RecursosClient puedeGestionar={true} />);
    await usuario.click(screen.getByRole("button", { name: "Registrar recurso" }));
    await elegir(usuario, "Laboratorio", "Laboratorio de Redes");
    await usuario.type(screen.getByLabelText("Nombre"), "Mesa de trabajo");
    await usuario.click(screen.getByRole("button", { name: "Guardar recurso" }));
    await waitFor(() => {
      expect(crearMock).toHaveBeenCalledWith({
        id_unidad: 7,
        tipo: "MOBILIARIO",
        especializacion: { nombre: "Mesa de trabajo" },
      });
    });
    expect(await screen.findByText("Recurso creado.")).toBeInTheDocument();
    // El modal se cierra al guardar y el catálogo se vuelve a pedir.
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(listarMock).toHaveBeenCalledTimes(2);
  });

  it("el registro vive en un modal: no está en la página hasta pedirlo, y se puede cancelar", async () => {
    const usuario = userEvent.setup();
    render(<RecursosClient puedeGestionar={true} />);
    await waitFor(() => expect(listarMock).toHaveBeenCalledTimes(1));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    await usuario.click(screen.getByRole("button", { name: "Registrar recurso" }));
    expect(screen.getByRole("dialog", { name: "Registrar recurso" })).toBeInTheDocument();
    await usuario.click(screen.getByRole("button", { name: "Cancelar" }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("muestra cada recurso con el nombre de su unidad, su tipo y si está deshabilitado", async () => {
    listarMock.mockResolvedValue({
      datos: [
        { id: 1, tipo: "EQUIPO", nombre: "Osciloscopio", id_unidad: 7, habilitado: true },
        { id: 2, tipo: "MOBILIARIO", nombre: "Silla", id_unidad: 7, habilitado: false },
      ],
    });
    render(<RecursosClient puedeGestionar={false} />);
    const lista = within(await screen.findByRole("list", { name: "Recursos" }));
    await waitFor(() => expect(lista.getAllByText("Laboratorio de Redes")).toHaveLength(2));
    expect(lista.getByText("Deshabilitado")).toBeInTheDocument();
    expect(lista.getByRole("link", { name: /Osciloscopio/ })).toHaveAttribute("href", "/recursos/1");
    expect(screen.getByText("2 recursos")).toBeInTheDocument();
  });

  it("sin permiso de gestión no ofrece registrar", async () => {
    render(<RecursosClient puedeGestionar={false} />);
    await waitFor(() => {
      expect(listarMock).toHaveBeenCalledTimes(1);
    });
    expect(screen.queryByRole("button", { name: "Registrar recurso" })).not.toBeInTheDocument();
  });

  it("403 al crear muestra denegación sin detalles internos", async () => {
    const usuario = userEvent.setup();
    crearMock.mockRejectedValue(
      new ApiRequestError(403, { codigo: "NO_AUTORIZADO", mensaje: "x", detalles: [] })
    );

    render(<RecursosClient puedeGestionar={true} />);
    await usuario.click(screen.getByRole("button", { name: "Registrar recurso" }));
    await elegir(usuario, "Laboratorio", "Laboratorio de Redes");
    await usuario.type(screen.getByLabelText("Nombre"), "Mesa");
    await usuario.click(screen.getByRole("button", { name: "Guardar recurso" }));
    expect(
      await screen.findByText("No tienes permiso para crear este recurso.")
    ).toBeInTheDocument();
  });

  // Decisión 2026-09-30: los equipos vienen de LIA y no se registran desde reservas.
  it("no ofrece registrar un equipo: solo mobiliario y otros recursos", async () => {
    const usuario = userEvent.setup();
    render(<RecursosClient puedeGestionar={true} />);
    await usuario.click(screen.getByRole("button", { name: "Registrar recurso" }));
    const tipo = screen.getByLabelText("Tipo");
    expect(within(tipo).getAllByRole("option").map((o) => o.textContent)).toEqual(["Mobiliario", "Otro"]);
    expect(screen.getByText(/Los equipos llegan de LIA/)).toBeInTheDocument();
  });

  it("filtra el catálogo por unidad y por tipo", async () => {
    const usuario = userEvent.setup();
    render(<RecursosClient puedeGestionar={false} />);
    await waitFor(() => expect(listarMock).toHaveBeenCalledTimes(1));
    await elegir(usuario, "Ver recursos del laboratorio", "Laboratorio de Redes");
    await waitFor(() => expect(listarMock).toHaveBeenLastCalledWith({ id_unidad: 7 }));
    await usuario.click(screen.getByRole("button", { name: "Equipos" }));
    await waitFor(() => expect(listarMock).toHaveBeenLastCalledWith({ id_unidad: 7, tipo: "EQUIPO" }));
  });
});
