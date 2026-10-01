import { act, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { CentroDeAlertas } from "./CentroDeAlertas";

const router = { push: vi.fn(), replace: vi.fn() };
vi.mock("next/navigation", () => ({ useRouter: () => router }));

const bandejaMock = vi.fn();
const lecturaMock = vi.fn();
vi.mock("@/src/lib/notificaciones-api", () => ({
  bandeja: (...a: unknown[]) => bandejaMock(...a),
  marcarLectura: (...a: unknown[]) => lecturaMock(...a),
}));

const nota = (id: number, extra: Record<string, unknown> = {}) => ({
  id,
  tipo_evento: { codigo: "RESERVA_APROBADA", nombre: "Reserva aprobada" },
  titulo: `Aviso ${id}`,
  cuerpo: `Tu reserva número ${id} quedó aprobada.`,
  reserva_id: id,
  leida_at: null,
  created_at: "2026-10-01T12:00:00Z",
  ...extra,
});

// Decisión 2026-10-01: las notificaciones son una campanita en la cabecera con avisos abajo a la derecha.
describe("CentroDeAlertas", () => {
  beforeEach(() => {
    bandejaMock.mockReset();
    lecturaMock.mockReset();
    lecturaMock.mockResolvedValue({});
    router.push.mockReset();
    window.sessionStorage.clear();
  });
  afterEach(() => vi.useRealTimers());

  it("cuenta lo que falta por leer en la campanita", async () => {
    bandejaMock.mockResolvedValue({ datos: [nota(1), nota(2), nota(3, { leida_at: "2026-10-01T12:05:00Z" })] });
    render(<CentroDeAlertas />);
    expect(await screen.findByRole("button", { name: "Notificaciones, 2 sin leer" })).toBeInTheDocument();
  });

  it("al entrar avisa lo nuevo, abajo a la derecha, y no lo repite en la misma sesión", async () => {
    bandejaMock.mockResolvedValue({ datos: [nota(1), nota(2)] });
    const primera = render(<CentroDeAlertas />);
    const avisos = await screen.findAllByText(/quedó aprobada/);
    expect(avisos).toHaveLength(2);
    primera.unmount();

    render(<CentroDeAlertas />); // recarga de la pantalla: ya se avisaron
    await screen.findByRole("button", { name: /Notificaciones/ });
    expect(screen.queryByText(/quedó aprobada/)).not.toBeInTheDocument();
  });

  it("muestra a lo sumo tres avisos aunque haya más sin leer, y el aviso se cierra solo", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    bandejaMock.mockResolvedValue({ datos: [nota(5), nota(4), nota(3), nota(2), nota(1)] });
    render(<CentroDeAlertas />);
    await waitFor(() => expect(screen.getAllByText(/quedó aprobada/)).toHaveLength(3));
    await act(async () => {
      await vi.advanceTimersByTimeAsync(10_000);
    });
    expect(screen.queryByText(/quedó aprobada/)).not.toBeInTheDocument();
    // Lo demás sigue sin leer y se ve en la campanita.
    expect(screen.getByRole("button", { name: "Notificaciones, 5 sin leer" })).toBeInTheDocument();
  });

  it("el panel lista lo último; abrir una notificación la marca leída y lleva a su reserva", async () => {
    const usuario = userEvent.setup();
    bandejaMock.mockResolvedValue({ datos: [nota(7)] });
    render(<CentroDeAlertas />);
    await usuario.click(await screen.findByRole("button", { name: "Notificaciones, 1 sin leer" }));
    const panel = within(screen.getByRole("region", { name: "Últimas notificaciones" }));
    await usuario.click(panel.getByRole("button", { name: /Aviso 7/ }));
    expect(lecturaMock).toHaveBeenCalledWith(7);
    expect(router.push).toHaveBeenCalledWith("/reservas/7");
    expect(screen.getByRole("button", { name: "Notificaciones" })).toBeInTheDocument(); // ya sin contador
  });

  it("«Marcar todas como leídas» marca cada una y apaga el contador", async () => {
    const usuario = userEvent.setup();
    bandejaMock.mockResolvedValue({ datos: [nota(1), nota(2)] });
    render(<CentroDeAlertas />);
    await usuario.click(await screen.findByRole("button", { name: "Notificaciones, 2 sin leer" }));
    await usuario.click(screen.getByRole("button", { name: "Marcar todas como leídas" }));
    await waitFor(() => expect(lecturaMock).toHaveBeenCalledTimes(2));
    expect(screen.getByRole("button", { name: "Notificaciones" })).toBeInTheDocument();
  });

  it("sin notificaciones lo dice, y el panel ofrece el historial completo", async () => {
    const usuario = userEvent.setup();
    bandejaMock.mockResolvedValue({ datos: [] });
    render(<CentroDeAlertas />);
    await usuario.click(await screen.findByRole("button", { name: "Notificaciones" }));
    expect(screen.getByText("No tienes notificaciones.")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Ver todas las notificaciones" })).toHaveAttribute("href", "/notificaciones");
  });

  it("si la bandeja falla, la campanita no rompe la pantalla", async () => {
    bandejaMock.mockRejectedValue(new Error("sin red"));
    render(<CentroDeAlertas />);
    expect(await screen.findByRole("button", { name: "Notificaciones" })).toBeInTheDocument();
  });

  it("Escape cierra el panel", async () => {
    const usuario = userEvent.setup();
    bandejaMock.mockResolvedValue({ datos: [] });
    render(<CentroDeAlertas />);
    await usuario.click(await screen.findByRole("button", { name: "Notificaciones" }));
    expect(screen.getByRole("region", { name: "Últimas notificaciones" })).toBeInTheDocument();
    await usuario.keyboard("{Escape}");
    expect(screen.queryByRole("region", { name: "Últimas notificaciones" })).not.toBeInTheDocument();
  });
});
