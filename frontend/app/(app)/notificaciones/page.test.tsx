import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiRequestError } from "@/src/lib/http";
import PaginaNotificaciones from "./page";

// Router estable: un objeto nuevo por render relanzaría el efecto sin fin.
const router = { push: vi.fn(), replace: vi.fn() };
vi.mock("next/navigation", () => ({
  useRouter: () => router,
}));

const bandejaMock = vi.fn();
const marcarMock = vi.fn();
const tiposMock = vi.fn();

vi.mock("@/src/lib/notificaciones-api", () => ({
  tiposEvento: () => tiposMock(),
  bandeja: (...args: unknown[]) => bandejaMock(...args),
  marcarLectura: (...args: unknown[]) => marcarMock(...args),
}));

const NOTIF = {
  id: 8841,
  tipo_evento: { codigo: "RESERVA_APROBADA", nombre: "Reserva aprobada" },
  titulo: "Tu reserva fue aprobada",
  cuerpo: "La reserva quedó aprobada.",
  reserva_id: 1042,
  leida_at: null,
  created_at: "2026-10-09T15:20:11Z",
};

// FE-21 (WF-NOT-01): marcar registra el instante sin tocar nada más.
describe("notificaciones/page.tsx", () => {
  beforeEach(() => {
    bandejaMock.mockReset();
    marcarMock.mockReset();
    tiposMock.mockReset();
    tiposMock.mockResolvedValue({ datos: [] });
    bandejaMock.mockResolvedValue({ datos: [NOTIF] });
  });

  it("marcar como leída registra el instante y conserva el texto", async () => {
    marcarMock.mockResolvedValue({ id: 8841, leida_at: "2026-10-09T16:02:44Z" });
    bandejaMock.mockResolvedValueOnce({ datos: [NOTIF] }).mockResolvedValueOnce({
      datos: [{ ...NOTIF, leida_at: "2026-10-09T16:02:44Z" }],
    });

    render(<PaginaNotificaciones />);
    expect(await screen.findByText("La reserva quedó aprobada.")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Marcar como leída" }));
    await waitFor(() => {
      expect(marcarMock).toHaveBeenCalledWith(8841);
    });
    // El texto comunicado no se recalcula: sigue visible tras marcar.
    expect(await screen.findByText("La reserva quedó aprobada.")).toBeInTheDocument();
  });

  it("una notificación ajena o inexistente se ve igual: 404 sin revelar cuál fue", async () => {
    marcarMock.mockRejectedValue(
      new ApiRequestError(404, { codigo: "NO_ENCONTRADO", mensaje: "No encontrado.", detalles: [] })
    );
    bandejaMock.mockResolvedValueOnce({ datos: [NOTIF] }).mockResolvedValueOnce({ datos: [] });

    render(<PaginaNotificaciones />);
    await userEvent.click(await screen.findByRole("button", { name: "Marcar como leída" }));
    expect(await screen.findByText("La notificación ya no está disponible.")).toBeInTheDocument();
    expect(screen.queryByText("No encontrado.")).not.toBeInTheDocument();
  });

  it("una notificación ya leída muestra su instante y no ofrece marcarla otra vez", async () => {
    bandejaMock.mockResolvedValue({ datos: [{ ...NOTIF, leida_at: "2026-10-09T16:02:44Z" }] });

    render(<PaginaNotificaciones />);
    expect(await screen.findByText("Leída: 2026-10-09T16:02:44Z")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Marcar como leída" })).not.toBeInTheDocument();
  });
});
