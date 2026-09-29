import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiRequestError } from "@/src/lib/http";
import PaginaNuevaReserva from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}));

const crearMock = vi.fn();
const disponibilidadMock = vi.fn();

vi.mock("@/src/lib/reservas-api", () => ({
  crearReserva: (...args: unknown[]) => crearMock(...args),
  consultarDisponibilidad: (...args: unknown[]) => disponibilidadMock(...args),
}));

// FE-19 (WF-RES-01): crear por tipo con el cuerpo correcto; el 409 manda.
describe("reservas/nueva/page.tsx", () => {
  beforeEach(() => {
    crearMock.mockReset();
    disponibilidadMock.mockReset();
    crearMock.mockResolvedValue({ id: 501 });
  });

  it("crea ESPACIO con detalle y contexto", async () => {
    const usuario = userEvent.setup();

    render(<PaginaNuevaReserva />);
    await usuario.type(screen.getByLabelText("Unidad (id)"), "7");
    await usuario.type(screen.getByLabelText("Espacio (id)"), "3");
    await usuario.type(screen.getByLabelText("Fecha"), "2030-08-04");
    await usuario.type(screen.getByLabelText("Hora inicio"), "10:00");
    await usuario.type(screen.getByLabelText("Hora fin"), "12:00");
    await usuario.type(screen.getByLabelText("Proyecto (id, opcional)"), "12");
    await usuario.click(screen.getByRole("button", { name: "Guardar solicitud" }));
    await waitFor(() => {
      expect(crearMock).toHaveBeenCalledWith({
        id_unidad: 7,
        tipo_reserva: "ESPACIO",
        contexto: { proyecto_id: 12 },
        detalle: { espacio_id: 3, fecha: "2030-08-04", hora_inicio: "10:00", hora_fin: "12:00" },
      });
    });
  });

  it("solapamiento muestra el mensaje del servidor", async () => {
    const usuario = userEvent.setup();
    crearMock.mockRejectedValue(
      new ApiRequestError(409, { codigo: "SOLAPAMIENTO", mensaje: "x", detalles: [] })
    );

    render(<PaginaNuevaReserva />);
    await usuario.type(screen.getByLabelText("Unidad (id)"), "7");
    await usuario.type(screen.getByLabelText("Espacio (id)"), "3");
    await usuario.type(screen.getByLabelText("Fecha"), "2030-08-04");
    await usuario.type(screen.getByLabelText("Hora inicio"), "10:00");
    await usuario.type(screen.getByLabelText("Hora fin"), "12:00");
    await usuario.click(screen.getByRole("button", { name: "Guardar solicitud" }));
    expect(await screen.findByText("Ese periodo ya está ocupado.")).toBeInTheDocument();
  });
});
