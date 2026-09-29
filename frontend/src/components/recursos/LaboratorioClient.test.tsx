import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiRequestError } from "@/src/lib/http";
import { LaboratorioClient } from "@/src/components/recursos/LaboratorioClient";

const router = { push: vi.fn(), replace: vi.fn() };
vi.mock("next/navigation", () => ({ useRouter: () => router }));
vi.mock("@/src/lib/administracion-api", () => ({
  listarUnidades: () => Promise.resolve({ datos: [{ id_unidad: 7, nombre: "Laboratorio de Redes", tipo: "LABORATORIO", id_unidad_padre: null, estado: true }] }),
}));

const configMock = vi.fn();
const guardarMock = vi.fn();
vi.mock("@/src/lib/recursos-api", () => ({
  configuracionLaboratorio: (...a: unknown[]) => configMock(...a),
  guardarConfiguracion: (...a: unknown[]) => guardarMock(...a),
  guardarTiposReserva: vi.fn(),
  guardarVisibilidad: vi.fn(),
}));

const CONFIG = {
  id_unidad: 7, habilitado_reservas: true, dias_atencion: [1, 2, 3, 4, 5], hora_apertura: "07:00:00", hora_cierre: "19:00:00",
  horas_antelacion: 24, aprobacion_automatica: false, recordatorio_horas_antes: 24, mostrar_estado_reserva: false,
  mostrar_reservista: false, notificar_por_correo: false, tipos_reserva: ["ESPACIO"],
};

// FE-29 (WF-REC-03): la configuración del laboratorio se ve y se edita completa.
describe("LaboratorioClient", () => {
  beforeEach(() => {
    configMock.mockReset();
    guardarMock.mockReset();
    configMock.mockResolvedValue(CONFIG);
    guardarMock.mockResolvedValue(CONFIG);
  });

  it("muestra la configuración y guarda los cambios de días, antelación, aprobación y correo", async () => {
    const usuario = userEvent.setup();
    render(<LaboratorioClient idUnidad={7} puedeGestionar={true} />);
    expect(await screen.findByRole("heading", { name: "Laboratorio Laboratorio de Redes" })).toBeInTheDocument();
    expect(screen.getByText(/Lunes, Martes, Miércoles, Jueves, Viernes/)).toBeInTheDocument();

    await usuario.click(screen.getByRole("checkbox", { name: "Sábado" }));
    await usuario.clear(screen.getByLabelText("Antelación mínima (horas)"));
    await usuario.type(screen.getByLabelText("Antelación mínima (horas)"), "48");
    await usuario.click(screen.getByRole("checkbox", { name: /Aprobación automática/ }));
    await usuario.click(screen.getByRole("checkbox", { name: /Enviar avisos por correo/ }));
    await usuario.click(screen.getByRole("button", { name: "Guardar configuración" }));
    await waitFor(() => {
      expect(guardarMock).toHaveBeenCalledWith(7, {
        habilitado_reservas: true, dias_atencion: [1, 2, 3, 4, 5, 6], hora_apertura: "07:00", hora_cierre: "19:00",
        horas_antelacion: 48, aprobacion_automatica: true, recordatorio_horas_antes: 24, notificar_por_correo: true,
      });
    });
  });

  it("no guarda un horario invertido ni sin días", async () => {
    const usuario = userEvent.setup();
    render(<LaboratorioClient idUnidad={7} puedeGestionar={true} />);
    await screen.findByRole("button", { name: "Guardar configuración" });
    await usuario.clear(screen.getByLabelText("Cierre"));
    await usuario.type(screen.getByLabelText("Cierre"), "06:00");
    await usuario.click(screen.getByRole("button", { name: "Guardar configuración" }));
    expect(await screen.findByText("La apertura debe ser anterior al cierre.")).toBeInTheDocument();
    expect(guardarMock).not.toHaveBeenCalled();
  });

  it("un laboratorio sin configuración ofrece crearla con lunes a viernes preseleccionados", async () => {
    const usuario = userEvent.setup();
    configMock.mockRejectedValue(new ApiRequestError(404, { codigo: "NO_ENCONTRADO", mensaje: "x", detalles: [] }));
    render(<LaboratorioClient idUnidad={7} puedeGestionar={true} />);
    expect(await screen.findByText("Este laboratorio todavía no tiene configuración.")).toBeInTheDocument();
    expect(screen.getByRole("checkbox", { name: "Lunes" })).toBeChecked();
    expect(screen.getByRole("checkbox", { name: "Sábado" })).not.toBeChecked();
    await usuario.type(screen.getByLabelText("Apertura"), "08:00");
    await usuario.type(screen.getByLabelText("Cierre"), "17:00");
    await usuario.click(screen.getByRole("button", { name: "Configurar laboratorio" }));
    await waitFor(() => {
      expect(guardarMock).toHaveBeenCalledWith(7, expect.objectContaining({ hora_apertura: "08:00", hora_cierre: "17:00", dias_atencion: [1, 2, 3, 4, 5] }));
    });
  });
});
