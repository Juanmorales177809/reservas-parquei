import { render, screen, waitFor } from "@testing-library/react";
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
    await elegir(usuario, "Unidad", "Laboratorio de Redes");
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
  });

  it("sin permiso de gestión no muestra el formulario", async () => {
    render(<RecursosClient puedeGestionar={false} />);
    await waitFor(() => {
      expect(listarMock).toHaveBeenCalledTimes(1);
    });
    expect(screen.queryByRole("button", { name: "Guardar recurso" })).not.toBeInTheDocument();
  });

  it("403 al crear muestra denegación sin detalles internos", async () => {
    const usuario = userEvent.setup();
    crearMock.mockRejectedValue(
      new ApiRequestError(403, { codigo: "NO_AUTORIZADO", mensaje: "x", detalles: [] })
    );

    render(<RecursosClient puedeGestionar={true} />);
    await elegir(usuario, "Unidad", "Laboratorio de Redes");
    await usuario.selectOptions(screen.getByLabelText("Tipo"), "EQUIPO");
    await usuario.type(screen.getByLabelText("Nombre del equipo"), "Analizador");
    await usuario.click(screen.getByRole("button", { name: "Guardar recurso" }));
    expect(
      await screen.findByText("No tienes permiso para crear este recurso.")
    ).toBeInTheDocument();
  });

  it("un equipo se registra con sus datos, apoyo y operatividad (RN-EQP-08, RN-REC-10)", async () => {
    const usuario = userEvent.setup();
    crearMock.mockResolvedValue({ id: 50, tipo: "EQUIPO", id_unidad: 7, habilitado: true });
    render(<RecursosClient puedeGestionar={true} />);
    await elegir(usuario, "Unidad", "Laboratorio de Redes");
    await usuario.selectOptions(screen.getByLabelText("Tipo"), "EQUIPO");
    await usuario.type(screen.getByLabelText("Nombre del equipo"), "Osciloscopio");
    await usuario.type(screen.getByLabelText("Placa"), "PL-9");
    await usuario.type(screen.getByLabelText("Marca"), "Tek");
    await usuario.click(screen.getByRole("checkbox", { name: /Exige acompañamiento técnico/ }));
    await usuario.click(screen.getByRole("button", { name: "Guardar recurso" }));
    await waitFor(() => {
      expect(crearMock).toHaveBeenCalledWith({
        id_unidad: 7,
        tipo: "EQUIPO",
        especializacion: {
          nombre_equipo: "Osciloscopio", placa: "PL-9", marca: "Tek",
          requiere_apoyo: true, acreditado: false, estado: true, requiere_calibracion: false,
        },
      });
    });
  });

  it("filtra el catálogo por unidad y por tipo", async () => {
    const usuario = userEvent.setup();
    render(<RecursosClient puedeGestionar={false} />);
    await waitFor(() => expect(listarMock).toHaveBeenCalledTimes(1));
    await elegir(usuario, "Ver recursos de la unidad", "Laboratorio de Redes");
    await waitFor(() => expect(listarMock).toHaveBeenLastCalledWith({ id_unidad: 7 }));
    await usuario.selectOptions(screen.getByLabelText("Ver recursos de tipo"), "Equipo");
    await waitFor(() => expect(listarMock).toHaveBeenLastCalledWith({ id_unidad: 7, tipo: "EQUIPO" }));
  });
});
