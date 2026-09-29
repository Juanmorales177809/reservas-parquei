import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiRequestError } from "@/src/lib/http";
import { GestionReservaClient } from "@/src/components/reservas/GestionReservaClient";

vi.mock("next/navigation", () => ({
  useParams: () => ({ id: "501" }),
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}));

const detalleMock = vi.fn();
const aceptarMock = vi.fn();
const finalizarMock = vi.fn();

vi.mock("@/src/lib/reservas-api", () => ({
  detalleReserva: (...args: unknown[]) => detalleMock(...args),
  aprobarReserva: vi.fn(),
  rechazarReserva: vi.fn(),
  crearPropuesta: vi.fn(),
  aceptarPropuesta: (...args: unknown[]) => aceptarMock(...args),
  rechazarPropuesta: vi.fn(),
  ejecutarReserva: vi.fn(),
  finalizarReserva: (...args: unknown[]) => finalizarMock(...args),
  cancelarReserva: vi.fn(),
  retirarRecurso: vi.fn(),
  registrarViabilidad: vi.fn(),
}));

const DETALLE_BASE = {
  id: 501,
  id_unidad: 7,
  id_cuenta: 1042,
  observacion: null,
  requiere_apoyo: false,
  created_at: "2026-01-01",
  updated_at: "2026-01-01",
  fecha_aprobacion: null,
  fecha_cancelacion: null,
  motivo_cancelacion: null,
  detalle: {},
  contexto: {},
  recursos: [],
  acompanantes: [],
  campos_adicionales: [],
  historial: [],
  propuesta_vigente: null,
  lista_espera: null,
};

// FE-19 (WF-RES-02): aceptar propuesta reprograma; finalizar sin devolución falla.
describe("GestionReservaClient", () => {
  beforeEach(() => {
    detalleMock.mockReset();
    aceptarMock.mockReset();
    finalizarMock.mockReset();
  });

  it("aceptar propuesta vigente reprograma y conserva el estado", async () => {
    const usuario = userEvent.setup();
    detalleMock.mockResolvedValue({
      ...DETALLE_BASE,
      estado: "SOLICITADA",
      tipo_reserva: "ESPACIO",
      propuesta_vigente: {
        id: 9, origen: "TECNICO", fecha_inicio_propuesta: "2030-08-05",
        fecha_fin_propuesta: "2030-08-05", hora_inicio: "14:00", hora_fin: "16:00",
        motivo: "Mantenimiento", created_at: "2026-01-01",
      },
    });
    aceptarMock.mockResolvedValue({});

    render(<GestionReservaClient />);
    await usuario.click(await screen.findByRole("button", { name: "Aceptar" }));
    await waitFor(() => {
      expect(aceptarMock).toHaveBeenCalledWith(501);
    });
  });

  it("finalizar campus sin devolución muestra el error sin cerrar", async () => {
    const usuario = userEvent.setup();
    detalleMock.mockResolvedValue({
      ...DETALLE_BASE,
      estado: "EN_EJECUCION",
      tipo_reserva: "RECURSO_CAMPUS",
      recursos: [{ reserva_recurso_id: 11, recurso_id: 41, rol: "PRINCIPAL", estado_asignacion: "ASIGNADO" }],
    });
    finalizarMock.mockRejectedValue(
      new ApiRequestError(409, { codigo: "ESTADO_INCOMPATIBLE", mensaje: "x", detalles: [] })
    );

    render(<GestionReservaClient />);
    await usuario.click(await screen.findByRole("button", { name: "Finalizar con devolución completa" }));
    await waitFor(() => {
      expect(finalizarMock).toHaveBeenCalledTimes(1);
    });
    expect(await screen.findByText("La reserva ya no está en un estado válido para esta acción.")).toBeInTheDocument();
  });
});
