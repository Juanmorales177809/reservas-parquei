import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiRequestError } from "@/src/lib/http";
import { EspaciosClient } from "@/src/components/espacios/EspaciosClient";
import { elegir } from "@/src/test-utils";


vi.mock("@/src/lib/administracion-api", () => ({
  listarUnidades: () => Promise.resolve({ datos: [{ id_unidad: 7, nombre: "Laboratorio de Redes", tipo: "LABORATORIO", id_unidad_padre: null, estado: true }] }),
}));

const listarMock = vi.fn();
const crearMock = vi.fn();

vi.mock("@/src/lib/espacios-api", () => ({
  listarEspacios: (...args: unknown[]) => listarMock(...args),
  crearEspacio: (...args: unknown[]) => crearMock(...args),
}));

// Router estable: un objeto nuevo por render relanzaría el efecto sin fin.
const router = { push: vi.fn(), replace: vi.fn() };
vi.mock("next/navigation", () => ({
  useRouter: () => router,
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
    await usuario.click(screen.getByRole("button", { name: "Registrar espacio" }));
    await elegir(usuario, "Laboratorio", "Laboratorio de Redes");
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
    // El modal se cierra al guardar y el catálogo se vuelve a pedir.
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(listarMock).toHaveBeenCalledTimes(2);
  });

  it("el registro vive en un modal: no está en la página hasta pedirlo, y se puede cancelar", async () => {
    const usuario = userEvent.setup();
    render(<EspaciosClient puedeGestionar={true} />);
    await waitFor(() => expect(listarMock).toHaveBeenCalledTimes(1));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    await usuario.click(screen.getByRole("button", { name: "Registrar espacio" }));
    expect(screen.getByRole("dialog", { name: "Registrar espacio" })).toBeInTheDocument();
    await usuario.click(screen.getByRole("button", { name: "Cancelar" }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("muestra cada espacio con el nombre de su laboratorio, su capacidad y si está deshabilitado", async () => {
    listarMock.mockResolvedValue({
      datos: [
        { id: 3, id_unidad: 7, nombre: "Sala 3", capacidad: 10, habilitado: true },
        { id: 4, id_unidad: 7, nombre: "Sala 4", capacidad: 20, habilitado: false },
      ],
    });
    render(<EspaciosClient puedeGestionar={false} />);
    const lista = within(await screen.findByRole("list", { name: "Espacios" }));
    await waitFor(() => expect(lista.getAllByText("Laboratorio de Redes")).toHaveLength(2));
    expect(lista.getByText("Capacidad 10")).toBeInTheDocument();
    expect(lista.getByText("Deshabilitado")).toBeInTheDocument();
    expect(lista.getByRole("link", { name: /Sala 3/ })).toHaveAttribute("href", "/espacios/3");
    expect(screen.getByText("2 espacios")).toBeInTheDocument();
  });

  it("duplicado muestra el mensaje junto al flujo sin detalles internos", async () => {
    const usuario = userEvent.setup();
    crearMock.mockRejectedValue(
      new ApiRequestError(409, { codigo: "NOMBRE_DUPLICADO", mensaje: "x", detalles: [] })
    );

    render(<EspaciosClient puedeGestionar={true} />);
    await usuario.click(screen.getByRole("button", { name: "Registrar espacio" }));
    await elegir(usuario, "Laboratorio", "Laboratorio de Redes");
    await usuario.type(screen.getByLabelText("Nombre"), "Metrología");
    await usuario.type(screen.getByLabelText("Capacidad"), "25");
    await usuario.click(screen.getByRole("button", { name: "Guardar espacio" }));
    expect(await screen.findByText("Ese nombre ya existe en el laboratorio.")).toBeInTheDocument();
  });

  it("sin permiso de gestión no ofrece registrar", async () => {
    render(<EspaciosClient puedeGestionar={false} />);
    await waitFor(() => {
      expect(listarMock).toHaveBeenCalledTimes(1);
    });
    expect(screen.queryByRole("button", { name: "Registrar espacio" })).not.toBeInTheDocument();
  });

  it("registra ubicación y descripción junto con la capacidad (RN-ESP-02)", async () => {
    const usuario = userEvent.setup();
    crearMock.mockResolvedValue({ id: 4 });
    render(<EspaciosClient puedeGestionar={true} />);
    await usuario.click(screen.getByRole("button", { name: "Registrar espacio" }));
    await elegir(usuario, "Laboratorio", "Laboratorio de Redes");
    await usuario.type(screen.getByLabelText("Nombre"), "Sala de ensayos");
    await usuario.type(screen.getByLabelText("Capacidad"), "12");
    await usuario.type(screen.getByLabelText("Ubicación (opcional)"), "Bloque 4");
    await usuario.type(screen.getByLabelText("Descripción (opcional)"), "Bancos de ensayo");
    await usuario.click(screen.getByRole("button", { name: "Guardar espacio" }));
    await waitFor(() => {
      expect(crearMock).toHaveBeenCalledWith({
        id_unidad: 7, nombre: "Sala de ensayos", capacidad: 12, ubicacion: "Bloque 4", descripcion: "Bancos de ensayo",
      });
    });
  });

  it("filtra por unidad, estado y capacidad mínima", async () => {
    const usuario = userEvent.setup();
    render(<EspaciosClient puedeGestionar={false} />);
    await waitFor(() => expect(listarMock).toHaveBeenCalledTimes(1));
    await elegir(usuario, "Ver espacios del laboratorio", "Laboratorio de Redes");
    await waitFor(() => expect(listarMock).toHaveBeenLastCalledWith({ id_unidad: 7 }));
    await usuario.click(screen.getByRole("button", { name: "Deshabilitados" }));
    await waitFor(() => expect(listarMock).toHaveBeenLastCalledWith({ id_unidad: 7, habilitado: false }));
    await usuario.type(screen.getByLabelText("Capacidad mínima"), "20");
    await waitFor(() => expect(listarMock).toHaveBeenLastCalledWith({ id_unidad: 7, habilitado: false, capacidad_minima: 20 }));
  });
});
