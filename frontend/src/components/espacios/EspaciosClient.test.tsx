import { render, screen, waitFor } from "@testing-library/react";
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
    await elegir(usuario, "Unidad", "Laboratorio de Redes");
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
    await elegir(usuario, "Unidad", "Laboratorio de Redes");
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

  it("registra ubicación y descripción junto con la capacidad (RN-ESP-02)", async () => {
    const usuario = userEvent.setup();
    crearMock.mockResolvedValue({ id: 4 });
    render(<EspaciosClient puedeGestionar={true} />);
    await elegir(usuario, "Unidad", "Laboratorio de Redes");
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
    await elegir(usuario, "Ver espacios de la unidad", "Laboratorio de Redes");
    await waitFor(() => expect(listarMock).toHaveBeenLastCalledWith({ id_unidad: 7 }));
    await usuario.selectOptions(screen.getByLabelText("Estado"), "Deshabilitados");
    await waitFor(() => expect(listarMock).toHaveBeenLastCalledWith({ id_unidad: 7, habilitado: false }));
    await usuario.type(screen.getByLabelText("Capacidad mínima"), "20");
    await waitFor(() => expect(listarMock).toHaveBeenLastCalledWith({ id_unidad: 7, habilitado: false, capacidad_minima: 20 }));
  });
});
