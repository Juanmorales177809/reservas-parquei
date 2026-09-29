import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiRequestError } from "@/src/lib/http";
import { EspacioDetalleClient } from "@/src/components/espacios/EspacioDetalleClient";

const detalleMock = vi.fn();
const impactoMock = vi.fn();
const cambiarMock = vi.fn();
const crearCampoMock = vi.fn();
const editarEspacioMock = vi.fn();
const editarCampoMock = vi.fn();
const editarOpcionMock = vi.fn();
const agregarOpcionesMock = vi.fn();
const reordenarMock = vi.fn();

vi.mock("@/src/lib/espacios-api", () => ({
  detalleEspacio: (...args: unknown[]) => detalleMock(...args),
  actualizarRecurso: vi.fn(),
  cambiarEstadoEspacio: (...args: unknown[]) => cambiarMock(...args),
  impactoDeshabilitacionEspacio: (...args: unknown[]) => impactoMock(...args),
  asociarRecursos: vi.fn(),
  retirarRecurso: vi.fn(),
  crearCampo: (...args: unknown[]) => crearCampoMock(...args),
  reordenarCampos: (...args: unknown[]) => reordenarMock(...args),
  cambiarEstadoCampo: vi.fn(),
  editarEspacio: (...args: unknown[]) => editarEspacioMock(...args),
  editarCampo: (...args: unknown[]) => editarCampoMock(...args),
  editarOpcion: (...args: unknown[]) => editarOpcionMock(...args),
  agregarOpciones: (...args: unknown[]) => agregarOpcionesMock(...args),
}));

// Router estable: un objeto nuevo por render relanzaría el efecto sin fin.
const router = { push: vi.fn(), replace: vi.fn() };
vi.mock("next/navigation", () => ({
  useParams: () => ({ id: "3" }),
  useRouter: () => router,
}));

const DETALLE = {
  id: 3,
  id_unidad: 7,
  nombre: "Metrología",
  ubicacion: null,
  capacidad: 25,
  descripcion: null,
  habilitado: true,
  horario_unidad: { hora_apertura: "07:00", hora_cierre: "19:00" },
  recursos: [],
  campos: [],
};

// FE-15 (WF-ESP-02/03): impacto con conteo y lista-sin-opciones.
describe("EspacioDetalleClient", () => {
  beforeEach(() => {
    detalleMock.mockReset();
    impactoMock.mockReset();
    cambiarMock.mockReset();
    crearCampoMock.mockReset();
    for (const m of [editarEspacioMock, editarCampoMock, editarOpcionMock, agregarOpcionesMock, reordenarMock]) m.mockReset();
    detalleMock.mockResolvedValue(DETALLE);
  });

  it("deshabilitar muestra el impacto y exige confirmar", async () => {
    const usuario = userEvent.setup();
    impactoMock.mockResolvedValue({ reservas_a_cancelar: 4 });
    cambiarMock.mockResolvedValue({ id: 3, habilitado: false, reservas_canceladas: 4 });

    render(<EspacioDetalleClient puedeGestionar={true} />);
    expect(await screen.findByText("Metrología")).toBeInTheDocument();
    await usuario.click(screen.getByRole("button", { name: "Deshabilitar" }));
    await waitFor(() => {
      expect(impactoMock).toHaveBeenCalledWith(3);
    });
    expect(await screen.findByText(/Reservas futuras a cancelar: 4/)).toBeInTheDocument();
    expect(cambiarMock).not.toHaveBeenCalled();
    await usuario.click(screen.getByRole("button", { name: "Confirmar deshabilitación" }));
    await waitFor(() => {
      expect(cambiarMock).toHaveBeenCalledWith(3, false, true);
    });
  });

  it("lista sin opciones muestra CAMPO_SIN_OPCIONES", async () => {
    const usuario = userEvent.setup();
    crearCampoMock.mockRejectedValue(
      new ApiRequestError(409, { codigo: "CAMPO_SIN_OPCIONES", mensaje: "x", detalles: [] })
    );

    render(<EspacioDetalleClient puedeGestionar={true} />);
    expect(await screen.findByText("Metrología")).toBeInTheDocument();
    await usuario.selectOptions(screen.getByLabelText("Tipo"), "SELECCION");
    await usuario.type(screen.getByLabelText("Nombre", { selector: "#campo-nombre" }), "Probeta");
    await usuario.click(screen.getByRole("button", { name: "Agregar campo" }));
    expect(
      await screen.findByText("Una lista necesita al menos una opción habilitada.")
    ).toBeInTheDocument();
  });

  it("edita los datos del espacio y solo viaja lo que cambió (RN-ESP-01, RN-ESP-02)", async () => {
    const usuario = userEvent.setup();
    editarEspacioMock.mockResolvedValue({});
    render(<EspacioDetalleClient puedeGestionar={true} />);
    await screen.findByRole("heading", { name: "Metrología" });
    await usuario.type(screen.getByLabelText("Ubicación"), "Bloque 4, piso 2");
    const capacidad = screen.getByLabelText("Capacidad");
    await usuario.clear(capacidad);
    await usuario.type(capacidad, "30");
    await usuario.click(screen.getByRole("button", { name: "Guardar datos" }));
    await waitFor(() => {
      expect(editarEspacioMock).toHaveBeenCalledWith(3, { ubicacion: "Bloque 4, piso 2", capacidad: 30 });
    });
  });

  it("un campo adicional se marca obligatorio y se reordena en ambos sentidos (RN-ESP-CAM-02)", async () => {
    const usuario = userEvent.setup();
    detalleMock.mockResolvedValue({
      ...DETALLE,
      campos: [
        { id: 5, nombre: "Ensayo", tipo: "TEXTO", obligatorio: false, orden: 0, habilitado: true },
        { id: 6, nombre: "Norma", tipo: "TEXTO", obligatorio: true, orden: 1, habilitado: true },
      ],
    });
    editarCampoMock.mockResolvedValue({});
    reordenarMock.mockResolvedValue({});
    render(<EspacioDetalleClient puedeGestionar={true} />);
    const filaEnsayo = (await screen.findByLabelText("Texto", { selector: "#campo-5" })).closest("li")!;
    await usuario.click(within(filaEnsayo).getByRole("checkbox", { name: "Obligatorio" }));
    await waitFor(() => expect(editarCampoMock).toHaveBeenCalledWith(3, 5, { obligatorio: true }));
    await usuario.click(within(filaEnsayo).getByRole("button", { name: "Bajar" }));
    await waitFor(() =>
      expect(reordenarMock).toHaveBeenCalledWith(3, [{ campo_id: 5, orden: 1 }, { campo_id: 6, orden: 0 }])
    );
  });

  it("las opciones de una lista se renombran, deshabilitan y agregan (RN-ESP-CAM-03)", async () => {
    const usuario = userEvent.setup();
    detalleMock.mockResolvedValue({
      ...DETALLE,
      campos: [{
        id: 7, nombre: "Tipo de ensayo", tipo: "SELECCION", obligatorio: true, orden: 0, habilitado: true,
        opciones: [{ id: 70, valor: "Tracción", orden: 0, habilitado: true }],
      }],
    });
    editarOpcionMock.mockResolvedValue({});
    agregarOpcionesMock.mockResolvedValue({});
    render(<EspacioDetalleClient puedeGestionar={true} />);
    const opcion = await screen.findByLabelText("Opción");
    await usuario.clear(opcion);
    await usuario.type(opcion, "Compresión");
    await usuario.click(within(opcion.closest("li")!).getByRole("button", { name: "Guardar nombre" }));
    await waitFor(() => expect(editarOpcionMock).toHaveBeenCalledWith(3, 7, 70, { valor: "Compresión" }));
    await usuario.click(within(opcion.closest("li")!).getByRole("button", { name: "Deshabilitar" }));
    await waitFor(() => expect(editarOpcionMock).toHaveBeenCalledWith(3, 7, 70, { habilitado: false }));
    await usuario.type(screen.getByLabelText("Agregar opción"), "Flexión");
    await usuario.click(screen.getByRole("button", { name: "Agregar" }));
    await waitFor(() => expect(agregarOpcionesMock).toHaveBeenCalledWith(3, 7, [{ valor: "Flexión" }]));
  });

  it("un campo nuevo puede nacer obligatorio", async () => {
    const usuario = userEvent.setup();
    crearCampoMock.mockResolvedValue({});
    render(<EspacioDetalleClient puedeGestionar={true} />);
    await usuario.type(await screen.findByLabelText("Nombre", { selector: "#campo-nombre" }), "Ensayo previsto");
    await usuario.click(screen.getByRole("checkbox", { name: "Obligatorio al reservar" }));
    await usuario.click(screen.getByRole("button", { name: "Agregar campo" }));
    await waitFor(() =>
      expect(crearCampoMock).toHaveBeenCalledWith(3, { nombre: "Ensayo previsto", tipo: "TEXTO", obligatorio: true })
    );
  });
});
