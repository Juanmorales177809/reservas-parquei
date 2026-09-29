import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { RecursoDetalleClient } from "@/src/components/recursos/RecursoDetalleClient";

const detalleMock = vi.fn();
const impactoMock = vi.fn();
const cambiarMock = vi.fn();
const actualizarMock = vi.fn();

vi.mock("@/src/lib/recursos-api", () => ({
  detalleRecurso: (...args: unknown[]) => detalleMock(...args),
  cambiarEstadoRecurso: (...args: unknown[]) => cambiarMock(...args),
  actualizarRecurso: (...args: unknown[]) => actualizarMock(...args),
  impactoDeshabilitacion: (...args: unknown[]) => impactoMock(...args),
  reasignarRecurso: vi.fn(),
}));

const router = { push: vi.fn(), replace: vi.fn() };
vi.mock("next/navigation", () => ({
  useParams: () => ({ id: "41" }),
  useRouter: () => router,
}));

const DETALLE = {
  id: 41,
  tipo: "MOBILIARIO",
  id_unidad: 7,
  habilitado: true,
  created_at: "2026-01-01",
  updated_at: "2026-01-01",
  especializacion: { nombre: "Mesa" },
};

// FE-13 (WF-REC-02, RN-DES-06): impacto previo con conteos y confirmación explícita.
describe("RecursoDetalleClient", () => {
  beforeEach(() => {
    detalleMock.mockReset();
    impactoMock.mockReset();
    cambiarMock.mockReset();
    actualizarMock.mockReset();
    detalleMock.mockResolvedValue(DETALLE);
  });

  it("deshabilitar muestra el impacto y exige confirmar", async () => {
    const usuario = userEvent.setup();
    impactoMock.mockResolvedValue({ reservas_a_cancelar: 2, reservas_a_retirar: 3 });
    cambiarMock.mockResolvedValue({ id: 41, habilitado: false, reservas_canceladas: 2, reservas_afectadas: 5 });

    render(<RecursoDetalleClient puedeGestionar={true} />);
    expect(await screen.findByRole("heading", { name: /Mesa/ })).toBeInTheDocument();
    await usuario.click(screen.getByRole("button", { name: "Deshabilitar" }));
    await waitFor(() => {
      expect(impactoMock).toHaveBeenCalledWith(41);
    });
    expect(await screen.findByText(/Reservas a cancelar: 2/)).toBeInTheDocument();
    // Sin confirmar no se llama al cambio.
    expect(cambiarMock).not.toHaveBeenCalled();
    await usuario.click(screen.getByRole("button", { name: "Confirmar deshabilitación" }));
    await waitFor(() => {
      expect(cambiarMock).toHaveBeenCalledWith(41, false, true);
    });
    expect(await screen.findByText("Recurso deshabilitado.")).toBeInTheDocument();
  });

  it("un equipo muestra y edita todos sus campos; solo viaja lo que cambió (RN-EQP-08, RN-EQP-09)", async () => {
    const usuario = userEvent.setup();
    detalleMock.mockResolvedValue({
      ...DETALLE, tipo: "EQUIPO",
      especializacion: {
        nombre_equipo: "Osciloscopio", placa: "PL-9", serial: "S1", marca: "Tek", modelo: "X",
        requiere_apoyo: false, acreditado: false, estado: true, requiere_calibracion: false,
        bodega: "B-3", centro_costo: "CC-7", fecha_compra: "2024-05-01",
      },
    });
    actualizarMock.mockResolvedValue({});
    render(<RecursoDetalleClient puedeGestionar={true} />);
    expect(await screen.findByRole("heading", { name: /Osciloscopio/ })).toBeInTheDocument();
    // Datos de inventario que llegan por importación: solo lectura.
    expect(screen.getByText("B-3")).toBeInTheDocument();
    expect(screen.getByText("CC-7")).toBeInTheDocument();

    await usuario.click(screen.getByRole("checkbox", { name: /Exige acompañamiento técnico/ }));
    await usuario.click(screen.getByRole("checkbox", { name: /^Operativo/ }));
    await usuario.clear(screen.getByLabelText("Serial"));
    await usuario.click(screen.getByRole("button", { name: "Guardar datos" }));
    await waitFor(() => {
      expect(actualizarMock).toHaveBeenCalledWith(41, { requiere_apoyo: true, estado: false, serial: null });
    });
  });
});
